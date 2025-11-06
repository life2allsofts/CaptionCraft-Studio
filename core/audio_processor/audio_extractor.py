# pyright: reportMissingImports=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportAssignmentType=false
# pyright: reportUnusedImport=false

"""
Audio Processor for CaptionCraft Studio
Fixed version with proper file handling
"""

import os
import tempfile
import sys
from typing import Optional, Tuple

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from moviepy.editor import VideoFileClip
    import speech_recognition as sr
    print("✅ Audio processor dependencies loaded successfully")
    MOVIEPY_AVAILABLE = True
    SPEECHRECOGNITION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Missing audio processing dependency: {e}")
    MOVIEPY_AVAILABLE = False
    SPEECHRECOGNITION_AVAILABLE = False
    VideoFileClip = None
    sr = None


class AudioExtractor:
    """
    Fixed audio extractor with proper file handling.
    """
    
    def __init__(self):
        """Initialize the audio extractor."""
        if SPEECHRECOGNITION_AVAILABLE and sr is not None:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None
        self.temp_files = []
    
    def extract_audio_from_video(self, video_path: str, output_audio_path: Optional[str] = None) -> str:
        """
        Extract audio from video file and save as WAV format.
        """
        if not MOVIEPY_AVAILABLE:
            raise ValueError("MoviePy not available. Install moviepy.")
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create a persistent temporary file
        if output_audio_path is None:
            # Use a more persistent temp file location
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_audio")
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.wav', 
                delete=False,  # Don't auto-delete!
                dir=temp_dir   # Use our custom temp directory
            )
            output_audio_path = temp_file.name
            self.temp_files.append(output_audio_path)
            temp_file.close()
        
        try:
            print(f"🔊 Loading video: {video_path}")
            
            if VideoFileClip is None:
                raise ImportError("MoviePy's VideoFileClip is not available")
                
            # Load video and extract audio
            with VideoFileClip(video_path) as video:
                print(f"📊 Video loaded: {video.duration:.2f}s duration")
                
                audio = video.audio
                if audio is None:
                    raise ValueError("No audio track found in video file")
                
                print(f"🔊 Audio track found: {audio.duration:.2f}s")
                print(f"💾 Writing audio to: {output_audio_path}")
                
                # Write audio to file with better error handling
                audio.write_audiofile(
                    output_audio_path, 
                    verbose=False, 
                    logger=None,
                    fps=44100  # Standard audio sample rate
                )
                
            # Verify the file was created
            if os.path.exists(output_audio_path):
                file_size = os.path.getsize(output_audio_path)
                print(f"✅ Audio extracted successfully: {output_audio_path} ({file_size} bytes)")
                return output_audio_path
            else:
                raise Exception("Audio file was not created")
                
        except Exception as e:
            # Clean up on error
            self.cleanup()
            raise e
    
    def get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file in seconds - FIXED VERSION.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Method 1: Try using MoviePy
            if VideoFileClip is not None:
                with VideoFileClip(audio_path) as audio:
                    return audio.duration
            raise ImportError("MoviePy's VideoFileClip is not available")
        except Exception as e:
            print(f"⚠️ MoviePy duration failed: {e}")
            
            # Method 2: Use file size estimation for WAV files
            try:
                file_size = os.path.getsize(audio_path)
                # WAV file duration estimation: file_size / (sample_rate * channels * bits_per_sample / 8)
                # For standard 44.1kHz, 2 channels, 16-bit WAV:
                duration = file_size / (44100 * 2 * 2)  # Rough estimation
                print(f"📏 Estimated duration: {duration:.2f}s from file size")
                return max(duration, 1.0)
            except:
                return 5.0  # Default fallback
    
    def transcribe_audio(self, audio_path: str, language: str = "en") -> str:
        """
        Transcribe audio file to text using speech recognition.
        """
        if self.recognizer is None:
            raise ValueError("Speech recognition not available.")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Ensure the sr module is available (helps static type checkers)
        speech_module = sr
        if speech_module is None:
            raise ValueError("SpeechRecognition module not available.")
        
        print(f"🎤 Transcribing audio: {audio_path}")
        
        try:
            # Load audio file
            with speech_module.AudioFile(audio_path) as source:
                print("🔊 Audio file loaded, adjusting for noise...")
                
                # Adjust for ambient noise and record audio
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio_data = self.recognizer.record(source)
                
                print("🎤 Performing speech recognition...")
                # Perform speech recognition
                text = self.recognizer.recognize_google(audio_data, language=language)
                
                print(f"✅ Transcription successful: {len(text)} characters")
                return text
                
        except speech_module.UnknownValueError:
            raise Exception("Speech recognition could not understand audio")
        except speech_module.RequestError as e:
            raise Exception(f"Speech recognition service error: {e}")
    
    def is_audio_available(self) -> bool:
        """
        Check if audio processing is available.
        """
        return MOVIEPY_AVAILABLE and SPEECHRECOGNITION_AVAILABLE
    
    def cleanup(self):
        """Clean up temporary files with better error handling."""
        print(f"🧹 Cleaning up {len(self.temp_files)} temporary files...")
        
        files_removed = 0
        for temp_file in self.temp_files[:]:  # Use copy to avoid modification during iteration
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    self.temp_files.remove(temp_file)
                    files_removed += 1
                    print(f"   ✅ Removed: {temp_file}")
            except Exception as e:
                print(f"   ⚠️ Could not remove {temp_file}: {e}")
        
        print(f"🧹 Cleanup complete: {files_removed} files removed")
    
    def __del__(self):
        """Destructor to ensure temporary files are cleaned up."""
        self.cleanup()


# Example usage and testing - FIXED VERSION
if __name__ == "__main__":
    print("🎬 Audio Extractor Test - Fixed Version")
    print("=" * 50)
    
    extractor = AudioExtractor()
    
    # Check if audio processing is available
    if not extractor.is_audio_available():
        print("❌ Audio processing dependencies not available.")
        print("💡 Please install: pip install moviepy SpeechRecognition")
        exit(1)
    
    # Look for test video files
    test_files = [
        "test_video.mp4",      # Your renamed file
        "test_video.mp4",  # Original name
        "text_video.mp4",      # Common typo
    ]
    
    video_path = None
    for filename in test_files:
        if os.path.exists(filename):
            video_path = filename
            break
    
    if not video_path:
        print("❌ No test video file found.")
        print("📁 Available files in directory:")
        for file in os.listdir('.'):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                print(f"   - {file}")
        extractor.cleanup()
        exit(1)
    
    print(f"🎬 Found video: {video_path}")
    
    try:
        # Step 1: Extract audio
        print("\n🔊 Step 1: Extracting audio from video...")
        audio_path = extractor.extract_audio_from_video(video_path)
        
        # Step 2: Get duration
        print("\n⏱️ Step 2: Getting audio duration...")
        duration = extractor.get_audio_duration(audio_path)
        print(f"✅ Audio duration: {duration:.2f} seconds")
        
        # Step 3: Transcribe
        print("\n🎤 Step 3: Transcribing audio...")
        transcription = extractor.transcribe_audio(audio_path)
        print(f"📝 Transcription: {transcription}")
        
        # Save transcription to file
        transcript_file = "audio_transcription.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcription)
        print(f"💾 Transcription saved to: {transcript_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Final cleanup...")
        extractor.cleanup()
        print("✅ Test completed")