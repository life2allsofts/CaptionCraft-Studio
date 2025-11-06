"""
Header Component for CaptionCraft Studio

Module: header.py
Description: Application header with title, menu buttons, and theme controls.
Author: Tetteh-Kofi (Isaac Tetteh-Apotey)
Version: 1.0.0
"""

import customtkinter as ctk
from utils.config_manager import config_manager


class HeaderComponent:
    """Header component with app title and menu buttons"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the header UI"""
        header_frame = ctk.CTkFrame(self.parent)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        # App title and version
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{config_manager.get('app.name')} v{config_manager.get('app.version')}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=10, pady=5)
        
        # Author credit
        author_label = ctk.CTkLabel(
            header_frame,
            text=f"by {config_manager.get('app.author')}",
            font=ctk.CTkFont(size=12)
        )
        author_label.pack(side="left", padx=(0, 20), pady=5)
        
        # Menu buttons
        self.setup_menu_buttons(header_frame)
    
    def setup_menu_buttons(self, parent):
        """Setup menu buttons in header"""
        menu_frame = ctk.CTkFrame(parent)
        menu_frame.pack(side="right", padx=10, pady=5)
        
        # Import Media button
        import_btn = ctk.CTkButton(
            menu_frame, 
            text="🎬 Import Media", 
            command=self.import_media,
            width=100
        )
        import_btn.pack(side="left", padx=2)
        
        # Theme toggle button
        theme_btn = ctk.CTkButton(
            menu_frame, 
            text="🌓 Theme", 
            command=self.toggle_theme,
            width=80
        )
        theme_btn.pack(side="left", padx=2)
        
        new_btn = ctk.CTkButton(menu_frame, text="New", command=self.new_project, width=60)
        new_btn.pack(side="left", padx=2)
        
        open_btn = ctk.CTkButton(menu_frame, text="Open", command=self.open_file, width=60)
        open_btn.pack(side="left", padx=2)
        
        save_btn = ctk.CTkButton(menu_frame, text="Save", command=self.save_file, width=60)
        save_btn.pack(side="left", padx=2)
        
        # Add more buttons as needed
        settings_btn = ctk.CTkButton(menu_frame, text="Settings", command=self.open_settings, width=70)
        settings_btn.pack(side="left", padx=2)
    
    def import_media(self):
        """Handle media file import for AI transcription"""
        file_path = self.app.file_dialogs.import_media_file()
        if file_path:
            self.app.process_media_file(file_path)
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.app.toggle_theme()
    
    def new_project(self):
        """Handle new project creation"""
        self.app.set_subtitle_text("")
        self.app.current_file = None
        self.app.status_bar.update_status("New project created")
    
    def open_file(self):
        """Handle file opening"""
        file_path = self.app.file_dialogs.open_file()
        if file_path:
            content = self.app.file_dialogs.load_file_content(file_path)
            if content is not None:
                self.app.set_subtitle_text(content)
                self.app.current_file = file_path
                self.app.status_bar.update_status(f"Opened: {file_path}")
    
    def save_file(self):
        """Handle file saving"""
        if not self.app.current_file:
            self.save_file_as()
            return
        
        content = self.app.get_subtitle_text()
        success = self.app.file_dialogs.save_file(self.app.current_file, content)
        if success:
            self.app.status_bar.update_status(f"Saved: {self.app.current_file}")
    
    def save_file_as(self):
        """Handle save as operation"""
        file_path = self.app.file_dialogs.save_file_as()
        if file_path:
            self.app.current_file = file_path
            self.save_file()
    
    def open_settings(self):
        """Open settings dialog (to be implemented)"""
        self.app.status_bar.update_status("Settings dialog will be implemented soon")