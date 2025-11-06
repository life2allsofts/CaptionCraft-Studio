"""
Preview Tab Component for CaptionCraft Studio
"""

import customtkinter as ctk


class PreviewTab:
    """Preview tab component for generated subtitles"""
    
    def __init__(self, notebook, app):
        self.notebook = notebook
        self.app = app
        self.tab = self.notebook.add("Preview")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the preview tab UI"""
        preview_frame = ctk.CTkFrame(self.tab)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Preview area title
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="Subtitle Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        preview_label.pack(pady=10)
        
        # Preview text area
        self.preview_text = ctk.CTkTextbox(
            preview_frame,
            height=300,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.preview_text.pack(fill="both", expand=True, padx=20, pady=10)
        self.preview_text.insert("1.0", "Generated VTT content will appear here...")
        self.preview_text.configure(state="disabled")
        
        # Control buttons frame
        button_frame = ctk.CTkFrame(preview_frame)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        # Generate button
        generate_btn = ctk.CTkButton(
            button_frame,
            text="Generate Preview",
            command=self.generate_preview
        )
        generate_btn.pack(side="left", padx=5)
        
        # Export button
        export_btn = ctk.CTkButton(
            button_frame,
            text="Export VTT",
            command=self.export_vtt
        )
        export_btn.pack(side="left", padx=5)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear Preview",
            command=self.clear_preview
        )
        clear_btn.pack(side="left", padx=5)
    
    def generate_preview(self):
        """Generate a preview of the current subtitles"""
        try:
            content = self.app.get_subtitle_text()
            
            # For now, just show the content in preview
            self.update_preview(content)
            self.app.status_bar.update_status("Preview generated successfully")
        except Exception as e:
            self.app.status_bar.update_status(f"Error generating preview: {e}")
    
    def export_vtt(self):
        """Export the preview as VTT file"""
        content = self.preview_text.get("1.0", "end-1c")
        if content and content != "Generated VTT content will appear here...":
            file_path = self.app.file_dialogs.export_file()
            if file_path:
                success = self.app.file_dialogs.save_file(file_path, content)
                if success:
                    self.app.status_bar.update_status(f"Exported: {file_path}")
    
    def update_preview(self, content: str):
        """Update preview with content"""
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", content)
        self.preview_text.configure(state="disabled")
    
    def clear_preview(self):
        """Clear the preview area"""
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "Generated VTT content will appear here...")
        self.preview_text.configure(state="disabled")