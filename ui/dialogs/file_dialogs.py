"""
File Dialog Utilities for CaptionCraft Studio
"""

import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
import os
from utils.config_manager import config_manager


class FileDialogs:
    """Handles all file operations and dialogs"""
    
    def __init__(self, app):
        self.app = app
    
    def open_file(self) -> str:
        """Open file dialog for opening subtitle files"""
        return filedialog.askopenfilename(
            title="Open Subtitle File",
            filetypes=[
                ("Subtitle files", "*.vtt *.srt *.sbv"),
                ("WebVTT files", "*.vtt"),
                ("SubRip files", "*.srt"),
                ("All files", "*.*")
            ]
        )
    
    def save_file_as(self) -> str:
        """Save file dialog for new files"""
        return filedialog.asksaveasfilename(
            title="Save Subtitle File",
            defaultextension=".vtt",
            filetypes=[
                ("WebVTT files", "*.vtt"),
                ("SubRip files", "*.srt"),
                ("All files", "*.*")
            ]
        )
    
    def export_file(self) -> str:
        """Export file dialog"""
        return filedialog.asksaveasfilename(
            title="Export Subtitle File",
            defaultextension=".vtt",
            filetypes=[
                ("WebVTT files", "*.vtt"),
                ("SubRip files", "*.srt"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
    
    def load_file_content(self, file_path: str) -> str:
        """Load content from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            config_manager.add_recent_file(file_path)
            return content
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")
            return ""
    
    def save_file(self, file_path: str, content: str) -> bool:
        """Save content to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            config_manager.add_recent_file(file_path)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")
            return False