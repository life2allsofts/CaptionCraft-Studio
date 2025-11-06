"""
Styling Tab Component for CaptionCraft Studio
"""

import customtkinter as ctk
from utils.config_manager import config_manager


class StylingTab:
    """Styling controls tab component"""
    
    def __init__(self, notebook, app):
        self.notebook = notebook
        self.app = app
        self.tab = self.notebook.add("Styling")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the styling tab UI"""
        styling_frame = ctk.CTkFrame(self.tab)
        styling_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        styling_label = ctk.CTkLabel(
            styling_frame,
            text="Advanced Styling Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        styling_label.pack(pady=20)
        
        # Create scrollable frame for styling controls
        self.scrollable_frame = ctk.CTkScrollableFrame(styling_frame)
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Setup styling controls
        self.setup_font_controls()
        self.setup_color_controls()
        self.setup_timing_controls()
    
    def setup_font_controls(self):
        """Setup font styling controls"""
        font_frame = ctk.CTkFrame(self.scrollable_frame)
        font_frame.pack(fill="x", pady=10)
        
        font_label = ctk.CTkLabel(
            font_frame,
            text="Font Settings",
            font=ctk.CTkFont(weight="bold")
        )
        font_label.pack(anchor="w", padx=10, pady=5)
        
        # Font family
        font_family_frame = ctk.CTkFrame(font_frame)
        font_family_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(font_family_frame, text="Font Family:").pack(side="left")
        self.font_family_var = ctk.StringVar(value=config_manager.get("default_styles.font_family"))
        font_combo = ctk.CTkComboBox(
            font_family_frame,
            values=["Arial", "Helvetica", "Verdana", "Georgia", "Times New Roman"],
            variable=self.font_family_var
        )
        font_combo.pack(side="left", padx=10)
        
        # Font size
        font_size_frame = ctk.CTkFrame(font_frame)
        font_size_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(font_size_frame, text="Font Size:").pack(side="left")
        self.font_size_var = ctk.StringVar(value=config_manager.get("default_styles.font_size"))
        font_size_entry = ctk.CTkEntry(font_size_frame, textvariable=self.font_size_var, width=80)
        font_size_entry.pack(side="left", padx=10)
        ctk.CTkLabel(font_size_frame, text="px").pack(side="left")
    
    def setup_color_controls(self):
        """Setup color styling controls"""
        color_frame = ctk.CTkFrame(self.scrollable_frame)
        color_frame.pack(fill="x", pady=10)
        
        color_label = ctk.CTkLabel(
            color_frame,
            text="Color Settings",
            font=ctk.CTkFont(weight="bold")
        )
        color_label.pack(anchor="w", padx=10, pady=5)
        
        # Text color
        text_color_frame = ctk.CTkFrame(color_frame)
        text_color_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(text_color_frame, text="Text Color:").pack(side="left")
        self.text_color_var = ctk.StringVar(value=config_manager.get("default_styles.text_color"))
        text_color_entry = ctk.CTkEntry(text_color_frame, textvariable=self.text_color_var, width=100)
        text_color_entry.pack(side="left", padx=10)
        
        # Background color
        bg_color_frame = ctk.CTkFrame(color_frame)
        bg_color_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(bg_color_frame, text="Background:").pack(side="left")
        self.bg_color_var = ctk.StringVar(value=config_manager.get("default_styles.background_color"))
        bg_color_entry = ctk.CTkEntry(bg_color_frame, textvariable=self.bg_color_var, width=100)
        bg_color_entry.pack(side="left", padx=10)
    
    def setup_timing_controls(self):
        """Setup timing controls"""
        timing_frame = ctk.CTkFrame(self.scrollable_frame)
        timing_frame.pack(fill="x", pady=10)
        
        timing_label = ctk.CTkLabel(
            timing_frame,
            text="Timing Settings",
            font=ctk.CTkFont(weight="bold")
        )
        timing_label.pack(anchor="w", padx=10, pady=5)
        
        # Subtitle mode
        mode_frame = ctk.CTkFrame(timing_frame)
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(mode_frame, text="Subtitle Mode:").pack(side="left")
        self.mode_var = ctk.StringVar(value="block")
        
        block_radio = ctk.CTkRadioButton(mode_frame, text="Block Text", variable=self.mode_var, value="block")
        block_radio.pack(side="left", padx=10)
        
        word_radio = ctk.CTkRadioButton(mode_frame, text="Word-by-Word", variable=self.mode_var, value="word_by_word")
        word_radio.pack(side="left", padx=10)
    
    def get_styles(self) -> dict:
        """Get current styling settings"""
        return {
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "text_color": self.text_color_var.get(),
            "background_color": self.bg_color_var.get(),
            "mode": self.mode_var.get()
        }