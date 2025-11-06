"""
Debug MoviePy import issues
"""

import sys
import os

print("🔍 Debugging MoviePy Import Issues")
print("=" * 40)

# Check Python path
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Check if moviepy is installed
try:
    import moviepy
    print("✅ moviepy package found")
    print(f"📦 moviepy version: {moviepy.__version__}")
except ImportError as e:
    print(f"❌ moviepy package not found: {e}")

# Check moviepy.editor specifically
try:
    from moviepy.editor import VideoFileClip
    print("✅ moviepy.editor.VideoFileClip imported successfully")
    
    # Test basic functionality
    print("🧪 Testing MoviePy basic functionality...")
    if os.path.exists("test_video.mp4"):
        with VideoFileClip("test_video.mp4") as video:
            print(f"✅ Video loaded: {video.duration:.2f}s duration")
            if video.audio:
                print("✅ Audio track available")
            else:
                print("❌ No audio track")
    else:
        print("⚠️ test_video.mp4 not found for testing")
        
except ImportError as e:
    print(f"❌ moviepy.editor import failed: {e}")
except Exception as e:
    print(f"❌ MoviePy test failed: {e}")

# Check what's actually in site-packages
print("\n📁 Checking installed packages:")
try:
    import pkg_resources
    installed_packages = [dist.key for dist in pkg_resources.Environment()]
    moviepy_related = [pkg for pkg in installed_packages if 'movie' in pkg.lower() or 'py' in pkg.lower()]
    print("MoviePy related packages:", moviepy_related)
except:
    print("Could not list packages")

print("\n💡 If MoviePy shows as installed but not importing, try:")
print("   pip uninstall moviepy -y")
print("   pip install moviepy==1.0.3")