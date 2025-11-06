"""
Enhanced File Dialogs with Media Support
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from typing import Optional

class FileDialogs:
    """Enhanced file dialogs with better media support"""
    
    def __init__(self, app):
        self.app = app
    
    def import_media_file(self) -> Optional[str]:
        """Open dialog for importing media files"""
        file_types = [
            ("Video Files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
            ("Audio Files", "*.mp3 *.wav *.m4a *.aac *.flac"),
            ("All Media Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Import Media File",
            filetypes=file_types
        )
        
        if file_path:
            # Validate file exists and is readable
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return None
            
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            if file_size > 500:  # 500MB limit
                response = messagebox.askyesno(
                    "Large File", 
                    f"This file is {file_size:.1f}MB. Processing may take a while. Continue?"
                )
                if not response:
                    return None
            
            return file_path
        return None
    
    def open_file(self) -> Optional[str]:
        """Open subtitle file"""
        file_types = [
            ("Subtitle Files", "*.vtt *.srt *.txt"),
            ("WebVTT Files", "*.vtt"),
            ("SubRip Files", "*.srt"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Open Subtitle File",
            filetypes=file_types
        )
        return file_path if file_path else None
    
    def save_file_as(self) -> Optional[str]:
        """Save subtitle file as"""
        file_types = [
            ("WebVTT Files", "*.vtt"),
            ("SubRip Files", "*.srt"), 
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
        
        file_path = filedialog.asksaveasfilename(
            title="Save Subtitle File As",
            defaultextension=".vtt",
            filetypes=file_types
        )
        return file_path if file_path else None
    
    def save_file(self, file_path: str, content: str) -> bool:
        """Save content to file with error handling"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save file: {e}")
            return False
    
    def load_file_content(self, file_path: str) -> Optional[str]:
        """Load file content with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load file: {e}")
            return None