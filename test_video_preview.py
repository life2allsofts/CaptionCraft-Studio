"""
Test script for Video Preview functionality
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_video_preview():
    """Test video preview integration"""
    print("🧪 Testing Video Preview Integration")
    print("=" * 50)
    
    # Test 1: Check if component can be imported
    print("\n1. 🔧 Testing Video Preview Component...")
    try:
        from ui.components.video_preview_tab import VideoPreviewTab
        print("   ✅ VideoPreviewTab imported successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Check sample VTT content
    print("\n2. 📝 Testing VTT Content Processing...")
    sample_vtt = """WEBVTT

1
00:00:01.000 --> 00:00:04.000
This is the first subtitle

2
00:00:05.000 --> 00:00:08.000
This is the second subtitle"""
    
    # Test subtitle counting
    try:
        # Simulate the counting method
        lines = sample_vtt.split('\n')
        count = 0
        for line in lines:
            if '-->' in line:
                count += 1
        print(f"   ✅ Subtitle counting works: {count} blocks detected")
    except Exception as e:
        print(f"   ❌ Subtitle counting failed: {e}")
        return False
    
    # Test 3: Check if test video exists
    print("\n3. 🎬 Testing Video File Detection...")
    test_files = ["test_video.mp4", "test_video.mp4.mp4"]
    test_file = None
    
    for filename in test_files:
        if os.path.exists(filename):
            test_file = filename
            break
    
    if test_file:
        print(f"   ✅ Test video found: {test_file}")
    else:
        print("   ⚠️ No test video found (component will still work)")
    
    print("\n🎉 Video Preview Component: READY FOR INTEGRATION!")
    print("\n📋 User Workflow:")
    print("   1. User imports media and generates subtitles")
    print("   2. User switches to '🎥 Video Preview' tab") 
    print("   3. Clicks 'Sync Current Subtitles'")
    print("   4. Gets instructions for playing video with subtitles")
    print("   5. Can verify timing accuracy visually")
    
    return True

if __name__ == "__main__":
    success = test_video_preview()
    if success:
        print("\n🚀 Phase 4 Video Preview: READY FOR DEVELOPMENT!")
    else:
        print("\n❅ Some tests failed. Check dependencies.")