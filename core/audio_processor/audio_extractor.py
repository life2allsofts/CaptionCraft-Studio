"""
Audio Extractor for CaptionCraft Studio
REVERTED to working version with targeted beginning audio fix
"""

import os
import tempfile
import sys
import uuid
from typing import Optional

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from moviepy.editor import VideoFileClip
    import speech_recognition as sr
    print("✅ Audio extractor dependencies loaded successfully")
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
    Audio extractor - REVERTED to working version with targeted fix for beginning audio.
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
        SIMPLE AND WORKING VERSION.
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
            video = VideoFileClip(video_path)
            try:
                print(f"📊 Video loaded: {video.duration:.2f}s duration")
                
                audio = video.audio
                if audio is None:
                    raise ValueError("No audio track found in video file")
                print(f"🔊 Audio track found: {audio.duration:.2f}s")
                print(f"💾 Writing audio to: {output_audio_path}")
                
                # SIMPLE SETTINGS THAT WORK
                audio.write_audiofile(
                    output_audio_path, 
                    verbose=False, 
                    logger=None,
                    fps=44100  # Standard audio sample rate
                )
            finally:
                video.close()
                
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

    def extract_audio_for_whisper(self, video_path: str) -> str:
        """
        Extract audio specifically optimized for Whisper transcription.
        Uses higher quality settings and ensures proper format.
        """
        if not MOVIEPY_AVAILABLE:
            raise ValueError("MoviePy not available. Install moviepy.")
        
        # Create temp directory for whisper audio
        whisper_temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whisper_audio")
        os.makedirs(whisper_temp_dir, exist_ok=True)
        
        # Create a more persistent temp file
        temp_filename = f"whisper_{uuid.uuid4().hex}.wav"
        output_audio_path = os.path.join(whisper_temp_dir, temp_filename)
        
        print(f"🔊 Extracting audio for Whisper: {video_path}")
        
        try:
            if VideoFileClip is None:
                raise ImportError("MoviePy's VideoFileClip is not available")
            with VideoFileClip(video_path) as video:
                audio = video.audio
                if audio is None:
                    raise ValueError("No audio track found in video file")
                
                print(f"💾 Writing high-quality audio for Whisper...")
                # Use higher quality settings for better transcription
                audio.write_audiofile(
                    output_audio_path, 
                    verbose=False, 
                    logger=None,
                    fps=16000,  # Whisper prefers 16kHz
                    ffmpeg_params=['-ac', '1']  # Mono audio for Whisper
                )
                
            # Verify the file was created properly
            if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0:
                print(f"✅ Whisper-ready audio created: {output_audio_path}")
                self.temp_files.append(output_audio_path)
                return output_audio_path
            else:
                raise Exception("Whisper audio file was not created properly")
                
        except Exception as e:
            # Clean up on error
            if os.path.exists(output_audio_path):
                try:
                    os.unlink(output_audio_path)
                except:
                    pass
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
        TARGETED FIX: Better beginning capture with segmented approach.
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
                
                # TARGETED FIX: Use shorter noise adjustment to preserve beginning
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # TARGETED FIX: Focus on capturing the beginning
                print("🎤 Capturing beginning audio (first 10 seconds)...")
                
                # Read first 10 seconds VERY carefully (where intros usually are)
                beginning_audio = self.recognizer.record(source, duration=10, offset=0)
                
                # Then read the rest
                rest_audio = self.recognizer.record(source)
                
                print("🎤 Transcribing beginning segment...")
                try:
                    beginning_text = self.recognizer.recognize_google(beginning_audio, language=language)
                    print(f"✅ Beginning transcribed: {len(beginning_text)} characters")
                except speech_module.UnknownValueError:
                    print("⚠️ Beginning segment unclear, trying full audio...")
                    # If beginning fails, try full audio as fallback
                    source.SAMPLE_WIDTH = None
                    source.DURATION = None
                    full_audio = self.recognizer.record(source)
                    full_text = self.recognizer.recognize_google(full_audio, language=language)
                    print(f"✅ Full audio transcribed: {len(full_text)} characters")
                    return full_text
                
                print("🎤 Transcribing remaining audio...")
                rest_text = self.recognizer.recognize_google(rest_audio, language=language)
                
                combined_text = f"{beginning_text} {rest_text}"
                print(f"✅ Transcription successful: {len(combined_text)} total characters")
                return combined_text
                
        except speech_module.UnknownValueError:
            raise Exception("Speech recognition could not understand audio")
        except speech_module.RequestError as e:
            raise Exception(f"Speech recognition service error: {e}")
        except Exception as e:
            raise Exception(f"Transcription error: {str(e)}")
    
    def transcribe_with_intro_focus(self, audio_path: str, language: str = "en") -> str:
        """
        SPECIALIZED METHOD: Focus specifically on capturing intro audio.
        Uses multiple attempts to get the beginning.
        """
        if self.recognizer is None:
            raise ValueError("Speech recognition not available.")
        
        print(f"🎤 SPECIALIZED: Transcribing with intro focus: {audio_path}")
        
        try:
            if sr is None:
                raise ValueError("SpeechRecognition module not available.")
            
            with sr.AudioFile(audio_path) as source:
                # ATTEMPT 1: Very short noise adjustment to preserve beginning
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                # Read first 15 seconds with high priority
                print("🎤 Attempt 1: Focused intro capture (first 15s)...")
                intro_audio = self.recognizer.record(source, duration=15)
                
                try:
                    intro_text = self.recognizer.recognize_google(intro_audio, language=language)
                    print(f"✅ Intro captured: '{intro_text[:100]}...'")
                    
                    # Get the rest
                    rest_audio = self.recognizer.record(source)
                    rest_text = self.recognizer.recognize_google(rest_audio, language=language)
                    
                    return f"{intro_text} {rest_text}"
                    
                except speech_module.UnknownValueError:
                    print("⚠️ Intro capture failed, trying alternative approach...")
                    
                    # ATTEMPT 2: Reset and try different segmentation
                    source.SAMPLE_WIDTH = None
                    source.DURATION = None
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    
                    # Try even smaller segments for the beginning
                    print("🎤 Attempt 2: Ultra-focused beginning (first 5s)...")
                    beginning_audio = self.recognizer.record(source, duration=5)
                    middle_audio = self.recognizer.record(source, duration=10)
                    end_audio = self.recognizer.record(source)
                    
                    try:
                        beginning_text = self.recognizer.recognize_google(beginning_audio, language=language)
                        middle_text = self.recognizer.recognize_google(middle_audio, language=language)
                        end_text = self.recognizer.recognize_google(end_audio, language=language)
                        
                        return f"{beginning_text} {middle_text} {end_text}"
                    except:
                        # Final fallback: full audio
                        source.SAMPLE_WIDTH = None
                        source.DURATION = None
                        full_audio = self.recognizer.record(source)
                        return self.recognizer.recognize_google(full_audio, language=language)
                        
        except Exception as e:
            print(f"⚠️ Specialized intro transcription failed: {e}")
            # Fall back to regular transcription
            return self.transcribe_audio(audio_path, language)
    
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


# Update your main_app.py to use the specialized method:
"""
In your main_app.py, replace the transcription line in process_media_file:

# Change this:
transcription = extractor.transcribe_audio(audio_path)

# To this:
try:
    transcription = extractor.transcribe_with_intro_focus(audio_path)
    print("🔊 Used specialized intro-focused transcription")
except Exception as e:
    print(f"⚠️ Intro focus failed, using regular: {e}")
    transcription = extractor.transcribe_audio(audio_path)
"""

# Example usage and testing
if __name__ == "__main__":
    print("🎬 Audio Extractor Test - Intro Focus Version")
    print("=" * 50)
    
    extractor = AudioExtractor()
    
    # Check if audio processing is available
    if not extractor.is_audio_available():
        print("❌ Audio processing dependencies not available.")
        print("💡 Please install: pip install moviepy SpeechRecognition")
        exit(1)
    
    # Look for test video files
    test_files = [
        "test_video.mp4",
        "Nehemiah's Wall.mp4",
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
        # Step 1: Extract audio (SIMPLE version)
        print("\n🔊 Step 1: Extracting audio...")
        audio_path = extractor.extract_audio_from_video(video_path)
        
        # Step 2: Get duration
        print("\n⏱️ Step 2: Getting audio duration...")
        duration = extractor.get_audio_duration(audio_path)
        print(f"✅ Audio duration: {duration:.2f} seconds")
        
        # Step 3: Transcribe with intro focus
        print("\n🎤 Step 3: Transcribing with intro focus...")
        transcription = extractor.transcribe_with_intro_focus(audio_path)
        print(f"📝 Transcription: {transcription}")
        
        # Save transcription to file
        transcript_file = "intro_focus_transcription.txt"
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