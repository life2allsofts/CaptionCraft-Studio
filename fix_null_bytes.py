import os
import glob

def remove_null_bytes_from_file(filepath):
    """Remove null bytes from a single file"""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        if b'\x00' in content:
            clean_content = content.replace(b'\x00', b'')
            with open(filepath, 'wb') as f:
                f.write(clean_content)
            print(f"✅ Cleaned: {filepath}")
            return True
        else:
            print(f"✓ Clean: {filepath}")
            return False
    except Exception as e:
        print(f"❌ Error cleaning {filepath}: {e}")
        return False

def clean_all_python_files(directory):
    """Clean all Python files in directory and subdirectories"""
    python_files = glob.glob(os.path.join(directory, "**", "*.py"), recursive=True)
    cleaned_count = 0
    
    print(f"🔍 Scanning {len(python_files)} Python files...")
    
    for filepath in python_files:
        if remove_null_bytes_from_file(filepath):
            cleaned_count += 1
    
    print(f"🎯 Cleaned {cleaned_count} files with null bytes")
    return cleaned_count

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    clean_all_python_files(project_root)