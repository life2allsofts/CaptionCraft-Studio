"""
Unified Audio Processor for CaptionCraft Studio
Enhanced version with direct video support and fallback audio extraction
"""

import os
import sys
from typing import Dict, Any, Optional, List

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import audio extractor
try:
    from .audio_extractor import AudioExtractor
    AUDIO_EXTRACTOR_AVAILABLE = True
    print("✅ Audio extractor available")
except ImportError as e:
    print(f"⚠️ Audio extractor not available: {e}")
    AUDIO_EXTRACTOR_AVAILABLE = False

# Try to import Whisper
try:
    import whisper
    from whisper.utils import get_writer
    WHISPER_AVAILABLE = True
    print("✅ OpenAI Whisper available")
except ImportError:
    WHISPER_AVAILABLE = False
    print("❌ OpenAI Whisper not available")
    whisper = None


class WhisperTranscriber:
    """
    Modern speech-to-text using OpenAI's Whisper model.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size (str): Whisper model size - 
                            "tiny", "base", "small", "medium", "large"
        """
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "OpenAI Whisper not installed. "
                "Install with: pip install openai-whisper"
            )
        
        self.model_size = model_size
        self.model = None
        self.temp_files = []
    
    def load_model(self):
        """Load the Whisper model (lazy loading)."""
        if not WHISPER_AVAILABLE:
            raise ImportError("Whisper is not available")
        if self.model is None:
            if whisper is None:
                raise ImportError("Whisper module is not available.")
            print(f"🔧 Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print("✅ Whisper model loaded")
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.
        FIXED: Better file validation and error handling
        """
        # Enhanced file validation
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file permissions and readability
        if not os.access(audio_path, os.R_OK):
            raise PermissionError(f"Cannot read audio file: {audio_path}")
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        if file_size == 0:
            raise ValueError(f"Audio file is empty: {audio_path}")
        
        print(f"🔍 Audio file validation passed:")
        print(f"   📍 Path: {audio_path}")
        print(f"   📊 Size: {file_size / (1024 * 1024):.2f} MB")
        print(f"   ✅ Readable: {os.access(audio_path, os.R_OK)}")
        
        self.load_model()
        
        try:
            print("🎤 Starting Whisper transcription...")
            # Transcribe audio with verbose for debugging
            result = self.model.transcribe(
                audio_path,
                language=language,
                verbose=True,  # Enable verbose for debugging
                fp16=False     # Force FP32 since we're on CPU
            )
            
            print("✅ Whisper transcription completed successfully")
            return result
            
        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            
            # Additional debugging: Check if it's a file format issue
            try:
                import wave
                with wave.open(audio_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = frames / float(rate)
                    print(f"🔍 WAV file details: {duration:.2f}s duration, {rate}Hz")
            except Exception as wav_error:
                print(f"🔍 Not a valid WAV file: {wav_error}")
            
            raise e
    
    def transcribe_to_srt(self, audio_path: str, output_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio and save as SRT subtitle file.
        
        Args:
            audio_path (str): Path to audio file
            output_path (str): Path for output SRT file
            language (Optional[str]): Language code
            
        Returns:
            str: Path to generated SRT file
        """
        result = self.transcribe_audio(audio_path, language)
        
        # Write SRT file
        srt_writer = get_writer("srt", ".")
        srt_writer(result, output_path)
        
        return output_path
    
    def transcribe_to_vtt(self, audio_path: str, output_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio and save as VTT subtitle file.
        
        Args:
            audio_path (str): Path to audio file
            output_path (str): Path for output VTT file
            language (Optional[str]): Language code
            
        Returns:
            str: Path to generated VTT file
        """
        result = self.transcribe_audio(audio_path, language)
        
        # Write VTT file
        vtt_writer = get_writer("vtt", ".")
        vtt_writer(result, output_path)
        
        return output_path
    
    def get_available_models(self) -> List[str]:
        """Get list of available Whisper model sizes."""
        return ["tiny", "base", "small", "medium", "large"]
    
    def is_available(self) -> bool:
        """Check if Whisper is available."""
        return WHISPER_AVAILABLE


class UnifiedAudioProcessor:
    """
    Unified audio processor that tries the best available method.
    
    Priority:
    1. OpenAI Whisper (most accurate, modern)
    2. Traditional speech recognition (fallback)
    3. Manual audio extraction (last resort)
    """
    
    def __init__(self, preferred_method: str = "whisper"):
        """
        Initialize unified audio processor.
        
        Args:
            preferred_method (str): Preferred processing method
                                  "whisper", "speech_recognition", "auto"
        """
        self.preferred_method = preferred_method
        self.whisper = None
        self.audio_extractor = None
        self.temp_files = []
        
        # Initialize Whisper if available
        if WHISPER_AVAILABLE and preferred_method in ["whisper", "auto"]:
            try:
                self.whisper = WhisperTranscriber("base")
                print("✅ Whisper transcriber initialized")
            except Exception as e:
                print(f"⚠️ Whisper initialization failed: {e}")
        
        # Initialize audio extractor if available
        if AUDIO_EXTRACTOR_AVAILABLE:
            try:
                self.audio_extractor = AudioExtractor()
                print("✅ Audio extractor initialized")
            except Exception as e:
                print(f"⚠️ Audio extractor initialization failed: {e}")
    
    def transcribe_media(self, media_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhanced transcription with direct video support and fallback audio extraction
        """
        if not os.path.exists(media_path):
            raise FileNotFoundError(f"Media file not found: {media_path}")
        
        print(f"🎬 Processing: {media_path}")
        
        # Try direct video transcription with Whisper
        if self.whisper and self.whisper.is_available():
            try:
                print("🎤 Attempting direct video transcription with Whisper...")
                
                # Use absolute path
                absolute_path = os.path.abspath(media_path)
                
                result = self.whisper.transcribe_audio(absolute_path, language)
                
                print(f"✅ Direct transcription successful!")
                return {
                    "method": "whisper",
                    "success": True,
                    "text": result["text"],
                    "segments": result.get("segments", []),
                    "language": result.get("language", "en")
                }
                
            except Exception as e:
                print(f"⚠️ Direct transcription failed: {e}")
                
                # Fallback: Extract audio first, then transcribe
                if self.audio_extractor:
                    try:
                        print("🔄 Falling back to audio extraction method...")
                        audio_path = self.audio_extractor.extract_audio_for_whisper(media_path)
                        
                        print(f"🎤 Transcribing extracted audio...")
                        result = self.whisper.transcribe_audio(audio_path, language)
                        
                        print(f"✅ Fallback transcription successful!")
                        return {
                            "method": "whisper",
                            "success": True,
                            "text": result["text"],
                            "segments": result.get("segments", []),
                            "language": result.get("language", "en")
                        }
                        
                    except Exception as fallback_error:
                        print(f"❌ Fallback also failed: {fallback_error}")
        
        return {
            "method": "none",
            "success": False,
            "error": "No audio transcription methods available",
            "text": "",
            "segments": []
        }
    
    def generate_subtitles(self, media_path: str, output_path: str, 
                          format: str = "vtt", language: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate subtitle file directly from media.
        
        Args:
            media_path (str): Path to media file
            output_path (str): Path for output subtitle file
            format (str): Output format - "vtt", "srt"
            language (Optional[str]): Language code
            
        Returns:
            Dict with generation results
        """
        if not self.whisper or not self.whisper.is_available():
            return {
                "success": False,
                "error": "Whisper not available for subtitle generation",
                "output_path": ""
            }
        
        try:
            if format.lower() == "vtt":
                output_path = self.whisper.transcribe_to_vtt(media_path, output_path, language)
            else:
                output_path = self.whisper.transcribe_to_srt(media_path, output_path, language)
            
            return {
                "success": True,
                "output_path": output_path,
                "method": "whisper"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_path": ""
            }
    
    def get_available_methods(self) -> List[str]:
        """Get list of available audio processing methods."""
        methods = []
        
        if self.whisper and self.whisper.is_available():
            methods.append("whisper")
        
        if self.audio_extractor and self.audio_extractor.is_audio_available():
            methods.append("speech_recognition")
        
        return methods
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all audio processing methods."""
        return {
            "whisper_available": self.whisper and self.whisper.is_available(),
            "audio_extractor_available": self.audio_extractor and self.audio_extractor.is_audio_available(),
            "preferred_method": self.preferred_method,
            "available_methods": self.get_available_methods()
        }
    
    def cleanup(self):
        """Clean up temporary files."""
        # Clean up whisper temp files
        if self.whisper:
            for temp_file in self.whisper.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception:
                    pass
            self.whisper.temp_files = []
        
        # Clean up audio extractor temp files
        if self.audio_extractor:
            self.audio_extractor.cleanup()
        
        # Clean up processor temp files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass
        self.temp_files = []


# Test the unified processor
if __name__ == "__main__":
    processor = UnifiedAudioProcessor()
    
    print("🔍 Audio Processing Status:")
    status = processor.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    if not status["available_methods"]:
        print("\n❌ No audio processing methods available")
        print("💡 Install: pip install moviepy openai-whisper SpeechRecognition")
        exit(1)
    
    print(f"\n✅ Available methods: {', '.join(status['available_methods'])}")
    
    # Test with video file - look for common video files
    test_files = [
        "test_video.mp4",  # Your actual file
        "test_video.mp4",      # Common name
        "text_video.mp4",      # Common typo
        "video.mp4",           # Generic name
    ]
    
    test_file = None
    for filename in test_files:
        if os.path.exists(filename):
            test_file = filename
            break
    
    if test_file:
        try:
            print(f"\n🎬 Testing with {test_file}...")
            result = processor.transcribe_media(test_file)
            
            if result["success"]:
                print(f"✅ Transcription successful using {result['method']}")
                print(f"📝 Text length: {len(result['text'])} characters")
                print(f"🔤 Language: {result.get('language', 'unknown')}")
                print(f"📊 Segments: {len(result.get('segments', []))}")
                print(f"📄 Sample: {result['text'][:200]}...")
                
                # Show first few segments with timing
                print(f"\n⏱️ First 3 segments:")
                for i, segment in enumerate(result.get('segments', [])[:3]):
                    print(f"  {i+1}. [{segment['start']:.1f}s - {segment['end']:.1f}s]: {segment['text']}")
                
                # Generate VTT file
                print(f"\n📄 Generating VTT file...")
                vtt_result = processor.generate_subtitles(test_file, "ai_generated_subtitles.vtt")
                if vtt_result["success"]:
                    print(f"✅ VTT file created: {vtt_result['output_path']}")
                else:
                    print(f"❌ VTT generation failed: {vtt_result.get('error')}")
                    
            else:
                print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print(f"\n⚠️ No test video file found")
        print("📁 Available files in directory:")
        for file in os.listdir('.'):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wav', '.mp3')):
                print(f"   - {file}")
    
    processor.cleanup()


# pyright: reportMissingImports=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportAssignmentType=false
# pyright: reportUnusedImport=false