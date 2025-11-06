"""
Debug script to see file creation issues
"""

import os
import tempfile
import time

def debug_temp_files():
    """Debug temporary file creation."""
    print("🔍 Debugging Temporary File Creation")
    print("=" * 40)
    
    # Test 1: Regular temp file
    print("\n🧪 Test 1: Regular tempfile.NamedTemporaryFile")
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_path = temp_file.name
    print(f"Created: {temp_path}")
    print(f"Exists: {os.path.exists(temp_path)}")
    
    # Write some data
    temp_file.write(b"test data")
    temp_file.close()
    
    print(f"After close - Exists: {os.path.exists(temp_path)}")
    print(f"File size: {os.path.getsize(temp_path)} bytes")
    
    # Clean up
    os.unlink(temp_path)
    print(f"After unlink - Exists: {os.path.exists(temp_path)}")
    
    # Test 2: With our custom directory
    print("\n🧪 Test 2: Custom temp directory")
    custom_temp_dir = os.path.join(os.getcwd(), "debug_temp")
    os.makedirs(custom_temp_dir, exist_ok=True)
    
    temp_file2 = tempfile.NamedTemporaryFile(
        suffix='.wav', 
        delete=False,
        dir=custom_temp_dir
    )
    temp_path2 = temp_file2.name
    print(f"Created: {temp_path2}")
    
    # Write data and close
    temp_file2.write(b"more test data")
    temp_file2.close()
    
    print(f"After close - Exists: {os.path.exists(temp_path2)}")
    print(f"File size: {os.path.getsize(temp_path2)} bytes")
    
    # Keep it for inspection
    print(f"File kept for inspection at: {temp_path2}")
    
    print(f"\n📁 Files in {custom_temp_dir}:")
    for file in os.listdir(custom_temp_dir):
        full_path = os.path.join(custom_temp_dir, file)
        print(f"  - {file} ({os.path.getsize(full_path)} bytes)")

if __name__ == "__main__":
    debug_temp_files()