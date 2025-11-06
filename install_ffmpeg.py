# pyright: reportMissingImports=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportAssignmentType=false
# pyright: reportUnusedImport=false

"""
Unified Audio Processor for CaptionCraft Studio
Uses MoviePy for reliable audio extraction + Whisper for transcription
"""

import os
import tempfile
import warnings
from typing import Dict, Any, Optional, List

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

# Try to import MoviePy for audio extraction
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
    print("✅ MoviePy available for audio extraction")
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("❌ MoviePy not available")
    VideoFileClip = None


class WhisperTranscriber:
    """
    Modern speech-to-text using OpenAI's Whisper model.
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper transcriber.
        """
        if not WHISPER_AVAILABLE:
            raise ImportError(
                "OpenAI Whisper not installed. "
                "Install with: pip install openai-whisper"
            )
        
        self.model_size = model_size
        self.model = None
    
    def load_model(self):
        """Load the Whisper model (lazy loading)."""
        if self.model is None:
            print(f"🔧 Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            print("✅ Whisper model loaded")
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        self.load_model()
        
        try:
            # Suppress Whisper warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # Transcribe audio
                result = self.model.transcribe(
                    audio_path,
                    language=language,
                    verbose=False
                )
            
            return result
            
        except Exception as e:
            # Provide helpful error message
            error_msg = str(e)
            if "ffmpeg" in error_msg.lower():
                raise Exception(
                    "Whisper requires FFmpeg for audio processing. "
                    "Please install FFmpeg or use the MoviePy audio extraction method."
                )
            else:
                raise e
    
    def transcribe_to_vtt(self, audio_path: str, output_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio and save as VTT subtitle file.
        """
        result = self.transcribe_audio(audio_path, language)
        
        # Write VTT file
        vtt_writer = get_writer("vtt", ".")
        vtt_writer(result, output_path)
        
        return output_path
    
    def is_available(self) -> bool:
        """Check if Whisper is available."""
        return WHISPER_AVAILABLE


class UnifiedAudioProcessor:
    """
    Unified audio processor that uses MoviePy for reliable audio extraction.
    """
    
    def __init__(self, preferred_method: str = "moviepy_extraction"):
        """
        Initialize unified audio processor.
        """
        self.preferred_method = preferred_method
        self.whisper = None
        self.temp_files = []
        
        # Initialize Whisper if available
        if WHISPER_AVAILABLE:
            try:
                self.whisper = WhisperTranscriber("base")
                print("✅ Whisper transcriber initialized")
            except Exception as e:
                print(f"⚠️ Whisper initialization failed: {e}")
    
    def transcribe_media(self, media_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Transcribe media file using MoviePy extraction + Whisper.
        """
        if not os.path.exists(media_path):
            raise FileNotFoundError(f"Media file not found: {media_path}")
        
        # Always use MoviePy extraction first (most reliable)
        return self._transcribe_with_moviepy_extraction(media_path, language)
    
    def _transcribe_with_moviepy_extraction(self, media_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract audio using MoviePy, then transcribe with Whisper.
        This is the most reliable method.
        """
        if not MOVIEPY_AVAILABLE:
            return {
                "success": False,
                "error": "MoviePy not available for audio extraction",
                "method": "moviepy_unavailable"
            }
        
        if not self.whisper or not self.whisper.is_available():
            return {
                "success": False,
                "error": "Whisper not available for transcription",
                "method": "whisper_unavailable"
            }
        
        temp_audio_path = None
        
        try:
            print("🔊 Step 1: Extracting audio with MoviePy...")
            
            # Create temporary audio file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio_path = temp_file.name
            self.temp_files.append(temp_audio_path)
            temp_file.close()
            
            # Extract audio using MoviePy (this we know works!)
            with VideoFileClip(media_path) as video:
                if video.audio is None:
                    return {
                        "success": False,
                        "error": "No audio track found in video file",
                        "method": "no_audio_track"
                    }
                
                video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            
            print("✅ Audio extraction successful")
            
            print("🎤 Step 2: Transcribing with Whisper...")
            # Transcribe the extracted audio with Whisper
            result = self.whisper.transcribe_audio(temp_audio_path, language)
            
            return {
                "method": "moviepy_extraction",
                "success": True,
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language", "en")
            }
            
        except Exception as e:
            return {
                "method": "extraction_failed",
                "success": False,
                "error": f"Processing failed: {e}",
                "text": "",
                "segments": []
            }
        finally:
            # Clean up temporary file immediately
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                    self.temp_files.remove(temp_audio_path)
                except:
                    pass
    
    def generate_subtitles(self, media_path: str, output_path: str, 
                          format: str = "vtt", language: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate subtitle file using MoviePy extraction + Whisper.
        """
        if not self.whisper or not self.whisper.is_available():
            return {
                "success": False,
                "error": "Whisper not available for subtitle generation",
                "output_path": ""
            }
        
        try:
            # First transcribe to get segments
            result = self.transcribe_media(media_path, language)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Transcription failed"),
                    "output_path": ""
                }
            
            # Generate VTT file from segments
            if format.lower() == "vtt":
                vtt_content = self._segments_to_vtt(result["segments"])
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(vtt_content)
            else:
                # For other formats, use Whisper's writer
                temp_audio = self._extract_audio_temp(media_path)
                if temp_audio:
                    self.whisper.transcribe_to_vtt(temp_audio, output_path, language)
                else:
                    return {
                        "success": False,
                        "error": "Could not extract audio for subtitle generation",
                        "output_path": ""
                    }
            
            return {
                "success": True,
                "output_path": output_path,
                "method": "moviepy_extraction"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "output_path": ""
            }
    
    def _extract_audio_temp(self, media_path: str) -> Optional[str]:
        """Extract audio to temporary file for subtitle generation."""
        if not MOVIEPY_AVAILABLE:
            return None
        
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_audio_path = temp_file.name
            self.temp_files.append(temp_audio_path)
            temp_file.close()
            
            with VideoFileClip(media_path) as video:
                if video.audio:
                    video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
                    return temp_audio_path
            return None
        except Exception:
            return None
    
    def _segments_to_vtt(self, segments: list) -> str:
        """Convert Whisper segments to VTT format."""
        vtt_content = "WEBVTT\n\n"
        
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            vtt_content += f"{i}\n"
            vtt_content += f"{start} --> {end}\n"
            vtt_content += f"{text}\n\n"
        
        return vtt_content
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to VTT timestamp."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_remainder = seconds % 60
        milliseconds = int((seconds_remainder - int(seconds_remainder)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d}.{milliseconds:03d}"
    
    def get_available_methods(self) -> List[str]:
        """Get list of available audio processing methods."""
        methods = []
        
        if MOVIEPY_AVAILABLE:
            methods.append("moviepy_extraction")
        
        if self.whisper and self.whisper.is_available():
            methods.append("whisper_transcription")
        
        return methods
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all audio processing methods."""
        return {
            "moviepy_available": MOVIEPY_AVAILABLE,
            "whisper_available": self.whisper and self.whisper.is_available(),
            "preferred_method": self.preferred_method,
            "available_methods": self.get_available_methods()
        }
    
    def cleanup(self):
        """Clean up temporary files."""
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
        print("💡 Install: pip install moviepy openai-whisper")
        exit(1)
    
    print(f"\n✅ Available methods: {', '.join(status['available_methods'])}")
    
    # Test with video file
    test_file = "test_video.mp4"
    if os.path.exists(test_file):
        try:
            print(f"\n🎬 Testing with {test_file}...")
            result = processor.transcribe_media(test_file)
            
            if result["success"]:
                print(f"✅ Transcription successful using {result['method']}")
                print(f"📝 Text length: {len(result['text'])} characters")
                print(f"🔤 Language: {result.get('language', 'unknown')}")
                print(f"📊 Segments: {len(result.get('segments', []))}")
                print(f"📄 Sample: {result['text'][:200]}...")
            else:
                print(f"❌ Transcription failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
    else:
        print(f"\n⚠️ No test file found: {test_file}")
    
    processor.cleanup()