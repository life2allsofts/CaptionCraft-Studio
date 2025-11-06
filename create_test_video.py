"""
Create a simple test video for audio processing testing
"""

import os

def create_test_video_info():
    """Provide instructions for creating a test video"""
    test_info = """
🎬 TEST VIDEO SETUP INSTRUCTIONS
    
To test the audio processing features, you need a video file with audio.

Option 1: Use your own video
- Place any video file (MP4, AVI, MOV) in the project root
- Rename it to 'test_video.mp4'

Option 2: Download a test video
- Download a short video from: https://sample-videos.com/
- Choose a small MP4 file with audio

Option 3: Record a quick test (5-10 seconds)
- Use your phone or computer to record a short video
- Transfer it to the project root as 'test_video.mp4'

Once you have a test video, run:
python core/audio_processor/audio_extractor.py
"""
    print(test_info)

if __name__ == "__main__":
    create_test_video_info()