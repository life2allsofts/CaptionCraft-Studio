"""
CaptionCraft Studio - Main Application Entry Point
Refactored to be minimal and delegate to components
"""

import tkinter as tk
import customtkinter as ctk
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.config_manager import config_manager
from core.vtt_engine.vtt_generator import VTTGenerator
from ui.components.header import HeaderComponent
from ui.components.editor_tab import EditorTab
from ui.components.styling_tab import StylingTab
from ui.components.preview_tab import PreviewTab
from ui.components.status_bar import StatusBar
from ui.dialogs.file_dialogs import FileDialogs


class CaptionCraftStudio(ctk.CTk):
    """Main application window - refactored to be minimal"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(config_manager.get("app.name", "CaptionCraft Studio"))
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Configure theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.vtt_generator = VTTGenerator()
        self.current_file = None
        self.file_dialogs = FileDialogs(self)
        
        # Setup UI
        self.setup_ui()
        
        # Load configuration
        self.load_config()
    
    def setup_ui(self):
        """Setup the main user interface by delegating to components"""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize components
        self.header = HeaderComponent(self.main_frame, self)
        self.status_bar = StatusBar(self.main_frame, self)
        
        # Setup main content area
        self.setup_main_content()
    
    def setup_main_content(self):
        """Setup the main content area with tabs"""
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(content_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Initialize tab components
        self.editor_tab = EditorTab(self.notebook, self)
        self.styling_tab = StylingTab(self.notebook, self)
        self.preview_tab = PreviewTab(self.notebook, self)
    
    def load_config(self):
        """Load application configuration"""
        theme = config_manager.get("ui.theme", "dark")
        ctk.set_appearance_mode(theme)
        
        self.status_bar.update_status("Configuration loaded successfully")
    
    def get_subtitle_text(self) -> str:
        """Get current subtitle text from editor"""
        return self.editor_tab.get_text()
    
    def set_subtitle_text(self, text: str):
        """Set subtitle text in editor"""
        self.editor_tab.set_text(text)
    
    def update_preview(self, content: str):
        """Update preview tab with content"""
        self.preview_tab.update_preview(content)


def main():
    """Main application entry point"""
    try:
        app = CaptionCraftStudio()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import tkinter.messagebox as messagebox
        messagebox.showerror("Fatal Error", f"Could not start application: {e}")


if __name__ == "__main__":
    main()