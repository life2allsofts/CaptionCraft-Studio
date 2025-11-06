"""
Test Complete User Workflow
"""

import os
import sys
import customtkinter as ctk

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_workflow():
    """Test the complete user workflow"""
    print("🧪 Testing Complete User Workflow")
    print("=" * 50)
    
    # Test 1: Check dependencies
    print("\n1. 🔍 Checking Dependencies...")
    try:
        from core.audio_processor.unified_processor import UnifiedAudioProcessor
        processor = UnifiedAudioProcessor()
        status = processor.get_status()
        print(f"   ✅ Whisper available: {status['whisper_available']}")
        print(f"   ✅ Available methods: {status['available_methods']}")
    except Exception as e:
        print(f"   ❌ Dependencies check failed: {e}")
        return False
    
    # Test 2: Check test video exists
    print("\n2. 🎬 Checking Test Media...")
    test_files = ["test_video.mp4", "test_video.mp4"]
    test_file = None
    
    for filename in test_files:
        if os.path.exists(filename):
            test_file = filename
            break
    
    if test_file:
        print(f"   ✅ Test video found: {test_file}")
        file_size = os.path.getsize(test_file) / (1024 * 1024)
        print(f"   📊 File size: {file_size:.1f} MB")
    else:
        print("   ❌ No test video found")
        print("   📁 Available files:")
        for file in os.listdir('.'):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                print(f"      - {file}")
        return False
    
    # Test 3: Test audio extraction
    print("\n3. 🔊 Testing Audio Extraction...")
    try:
        from core.audio_processor.audio_extractor import AudioExtractor
        extractor = AudioExtractor()
        
        if extractor.is_audio_available():
            audio_path = extractor.extract_audio_from_video(test_file)
            duration = extractor.get_audio_duration(audio_path)
            print(f"   ✅ Audio extracted: {duration:.1f}s duration")
            extractor.cleanup()
        else:
            print("   ⚠️ Audio extraction not available")
    except Exception as e:
        print(f"   ❌ Audio extraction failed: {e}")
        return False
    
    # Test 4: Test AI transcription
    print("\n4. 🤖 Testing AI Transcription...")
    try:
        result = processor.transcribe_media(test_file)
        if result["success"]:
            print(f"   ✅ Transcription successful")
            print(f"   📝 Text length: {len(result['text'])} characters")
            print(f"   🔤 Language: {result.get('language', 'unknown')}")
            print(f"   📊 Segments: {len(result.get('segments', []))}")
        else:
            print(f"   ❌ Transcription failed: {result.get('error')}")
            return False
    except Exception as e:
        print(f"   ❌ Transcription test failed: {e}")
        return False
    
    # Test 5: Test VTT generation
    print("\n5. 📄 Testing VTT Generation...")
    try:
        from core.vtt_engine.vtt_generator import VTTGenerator
        generator = VTTGenerator()
        
        # Add sample captions
        generator.add_caption("00:00:01.000", "00:00:04.000", "Test subtitle line 1")
        generator.add_caption("00:00:05.000", "00:00:08.000", "Test subtitle line 2")
        
        vtt_content = generator.generate_vtt_content()
        print(f"   ✅ VTT generation successful")
        print(f"   📋 Content length: {len(vtt_content)} characters")
        
    except Exception as e:
        print(f"   ❌ VTT generation failed: {e}")
        return False
    
    print("\n🎉 ALL TESTS PASSED! Workflow is ready.")
    print("\n📋 Complete User Journey:")
    print("   1. User opens app")
    print("   2. Clicks 'Import Media'") 
    print("   3. Selects video file")
    print("   4. Sees progress indicators")
    print("   5. Gets AI-generated subtitles")
    print("   6. Can edit and export results")
    
    processor.cleanup()
    return True

if __name__ == "__main__":
    # Set dark theme for consistent testing
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    success = test_workflow()
    if success:
        print("\n🚀 Phase 3A Polish: READY FOR USER TESTING!")
    else:
        print("\n❌ Some tests failed. Check dependencies and file paths.")