"""
Test complete audio-to-subtitle pipeline
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.audio_processor.unified_processor import UnifiedAudioProcessor
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

def test_complete_pipeline():
    """Test the complete pipeline from video to subtitles."""
    print("🎬 Testing Complete Audio-to-Subtitle Pipeline")
    print("=" * 50)
    
    # Initialize the processor
    processor = UnifiedAudioProcessor()
    
    # Check status
    status = processor.get_status()
    print(f"🔧 MoviePy Available: {status.get('moviepy_available', False)}")
    print(f"🔧 Whisper Available: {status.get('whisper_available', False)}")
    
    if not status["available_methods"]:
        print("❌ No audio processing methods available")
        print("💡 Install: pip install moviepy openai-whisper")
        return
    
    # Test with the actual video file
    video_file = "test_video.mp4"  # Use the actual filename
    
    if not os.path.exists(video_file):
        print(f"❌ Video file not found: {video_file}")
        # Show available files
        print("📁 Available files:")
        for file in os.listdir('.'):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                print(f"   - {file}")
        return
    
    print(f"📹 Processing: {video_file}")
    print(f"🎯 Using methods: {', '.join(status['available_methods'])}")
    
    try:
        # Step 1: Transcribe with MoviePy extraction + Whisper
        print("\n🎤 Step 1: AI Transcription...")
        result = processor.transcribe_media(video_file)
        
        if result["success"]:
            print(f"✅ Transcription successful!")
            print(f"📝 Method: {result['method']}")
            print(f"📝 Text length: {len(result['text'])} characters")
            print(f"🔤 Detected language: {result.get('language', 'unknown')}")
            print(f"⏱️ Number of segments: {len(result.get('segments', []))}")
            
            # Show sample of transcribed text
            sample_text = result['text'][:150] + "..." if len(result['text']) > 150 else result['text']
            print(f"📄 Sample: {sample_text}")
            
            # Show first few segments
            print(f"\n⏱️ First 3 segments:")
            for i, segment in enumerate(result.get('segments', [])[:3]):
                print(f"  {i+1}. [{segment['start']:.1f}s - {segment['end']:.1f}s]: {segment['text']}")
            
            # Step 2: Generate VTT subtitles
            print("\n📄 Step 2: Generating VTT subtitles...")
            vtt_output = "ai_generated_subtitles.vtt"
            subtitle_result = processor.generate_subtitles(video_file, vtt_output, "vtt")
            
            if subtitle_result["success"]:
                print(f"✅ VTT file created: {vtt_output}")
                
                # Show preview of generated subtitles
                try:
                    with open(vtt_output, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"📋 Preview of first 10 lines:")
                    lines = content.split('\n')[:10]
                    for i, line in enumerate(lines, 1):
                        print(f"   {i:2d}: {line}")
                except Exception as e:
                    print(f"⚠️ Could not read VTT file: {e}")
            else:
                print(f"❌ Failed to generate VTT: {subtitle_result.get('error')}")
                
        else:
            print(f"❌ Transcription failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
    
    finally:
        processor.cleanup()
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    test_complete_pipeline()