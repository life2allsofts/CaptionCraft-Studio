"""
Enhanced Status Bar with Progress Indicators
"""

import customtkinter as ctk
from typing import Optional

class StatusBar:
    """Status bar with progress indicators and better messaging"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the status bar UI"""
        self.status_frame = ctk.CTkFrame(self.parent, height=30)
        self.status_frame.pack(fill="x", side="bottom", padx=10, pady=5)
        self.status_frame.pack_propagate(False)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_frame, 
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Progress bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(
            self.status_frame,
            width=200,
            height=16
        )
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.pack_forget()  # Hide initially
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=10)
        )
        self.progress_label.pack(side="right", padx=(0, 5), pady=5)
        self.progress_label.pack_forget()
    
    def update_status(self, message: str, duration: Optional[int] = None):
        """Update status message with optional auto-clear"""
        self.status_label.configure(text=message)
        self.parent.update()
        
        if duration:
            self.parent.after(duration, lambda: self.update_status("Ready"))
    
    def show_progress(self, message: str = "Processing..."):
        """Show progress bar with message"""
        self.progress_label.configure(text=message)
        self.progress_label.pack(side="right", padx=(0, 5), pady=5)
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.set(0)
        self.parent.update()
    
    def update_progress(self, value: float, message: Optional[str] = None):
        """Update progress bar value (0.0 to 1.0)"""
        self.progress_bar.set(value)
        if message:
            self.progress_label.configure(text=message)
        self.parent.update()
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_label.pack_forget()
        self.progress_bar.pack_forget()
        self.parent.update()
    
    def show_error(self, message: str):
        """Show error message with red styling"""
        self.status_label.configure(text=f"❌ {message}", text_color="#FF4444")
        self.parent.update()
    
    def show_success(self, message: str):
        """Show success message with green styling"""
        self.status_label.configure(text=f"✅ {message}", text_color="#44FF44")
        self.parent.update()