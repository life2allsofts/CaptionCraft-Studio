"""
Status Bar Component for CaptionCraft Studio
"""

import customtkinter as ctk


class StatusBar:
    """Status bar component for displaying messages"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the status bar UI"""
        self.status_frame = ctk.CTkFrame(self.parent)
        self.status_frame.pack(fill="x", padx=10, pady=5)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to create amazing subtitles!",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10, pady=2)
        
        # Progress bar (for future use)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame, width=200)
        self.progress_bar.pack(side="right", padx=10, pady=2)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hide by default
    
    def update_status(self, message: str, duration: int = 5000):
        """Update the status bar message"""
        self.status_label.configure(text=message)
        # Clear message after duration
        self.app.after(duration, self.clear_status)
    
    def clear_status(self):
        """Clear status message to default"""
        self.status_label.configure(text="Ready")
    
    def show_progress(self):
        """Show progress bar"""
        self.progress_bar.pack(side="right", padx=10, pady=2)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.pack_forget()
    
    def set_progress(self, value: float):
        """Set progress bar value (0.0 to 1.0)"""
        self.progress_bar.set(value)