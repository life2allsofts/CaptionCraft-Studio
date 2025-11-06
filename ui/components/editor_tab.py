"""
Editor Tab Component for CaptionCraft Studio
"""

import customtkinter as ctk


class EditorTab:
    """Subtitle editor tab component"""
    
    def __init__(self, notebook, app):
        self.notebook = notebook
        self.app = app
        self.tab = self.notebook.add("Subtitle Editor")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the editor tab UI"""
        # Editor frame
        editor_frame = ctk.CTkFrame(self.tab)
        editor_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Text area for subtitle editing
        self.subtitle_text = ctk.CTkTextbox(
            editor_frame,
            font=ctk.CTkFont(family="Consolas", size=12)
        )
        self.subtitle_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add some example content
        self.set_example_content()
    
    def set_example_content(self):
        """Set example subtitle content"""
        example_content = """00:00:01.000 --> 00:00:04.000
Welcome to CaptionCraft Studio!

00:00:05.000 --> 00:00:08.000
Create advanced subtitles with word-by-word timing.

00:00:09.000 --> 00:00:12.000
Customize styles and export to multiple formats."""
        
        self.subtitle_text.insert("1.0", example_content)
    
    def get_text(self) -> str:
        """Get current text from editor"""
        return self.subtitle_text.get("1.0", "end-1c")
    
    def set_text(self, text: str):
        """Set text in editor"""
        self.subtitle_text.delete("1.0", "end")
        self.subtitle_text.insert("1.0", text)
    
    def clear_text(self):
        """Clear editor content"""
        self.subtitle_text.delete("1.0", "end")