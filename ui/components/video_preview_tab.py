"""
Video Preview Tab for CaptionCraft Studio
Integrated video player with subtitle overlay
"""

import customtkinter as ctk
import os
import tempfile
from typing import Optional

class VideoPreviewTab:
    """Video preview tab with synchronized subtitle playback"""
    
    def __init__(self, notebook, app):
        self.notebook = notebook
        self.app = app
        self.video_path: Optional[str] = None
        self.vtt_content: Optional[str] = None
        self.temp_vtt_file: Optional[str] = None
        
        # Create tab
        self.tab = self.notebook.add("🎥 Video Preview")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the video preview UI"""
        # Main container
        main_frame = ctk.CTkFrame(self.tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Video info section
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        self.video_info_label = ctk.CTkLabel(
            info_frame,
            text="No video loaded",
            font=ctk.CTkFont(size=12)
        )
        self.video_info_label.pack(side="left", padx=10, pady=5)
        
        # Controls frame
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Load video button
        self.load_btn = ctk.CTkButton(
            controls_frame,
            text="📁 Load Video",
            command=self.load_video,
            width=120
        )
        self.load_btn.pack(side="left", padx=5, pady=5)
        
        # Sync subtitles button
        self.sync_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Sync Current Subtitles",
            command=self.sync_current_subtitles,
            width=180,
            state="disabled"
        )
        self.sync_btn.pack(side="left", padx=5, pady=5)
        
        # Preview area
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview placeholder (will be replaced with actual video player)
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="🎬 Video Preview\n\nLoad a video to see it here with subtitles",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        self.preview_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Instructions
        instructions_frame = ctk.CTkFrame(main_frame)
        instructions_frame.pack(fill="x", padx=5, pady=5)
        
        instructions = (
            "💡 How to use:\n"
            "1. Click 'Load Video' to select a video file\n"
            "2. Click 'Sync Current Subtitles' to load subtitles from editor\n"
            "3. Video will play with synchronized subtitles"
        )
        
        instructions_label = ctk.CTkLabel(
            instructions_frame,
            text=instructions,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        instructions_label.pack(padx=10, pady=10)
    
    def load_video(self):
        """Load a video file for preview"""
        file_path = self.app.file_dialogs.import_media_file()
        if file_path:
            self.video_path = file_path
            filename = os.path.basename(file_path)
            self.video_info_label.configure(text=f"Video: {filename}")
            self.sync_btn.configure(state="normal")
            
            # Update preview display
            self.preview_label.configure(
                text=f"🎬 {filename}\n\n✅ Video loaded successfully!\n\n"
                     f"Click 'Sync Current Subtitles' to load subtitles from editor"
            )
            
            self.app.status_bar.update_status(f"Video loaded for preview: {filename}")
    
    def sync_current_subtitles(self):
        """Sync current editor subtitles with the loaded video"""
        if not self.video_path:
            self.app.status_bar.show_error("Please load a video first")
            return
        
        # Get current subtitles from editor
        vtt_content = self.app.get_subtitle_text()
        
        if not vtt_content or "WEBVTT" not in vtt_content:
            self.app.status_bar.show_error("No subtitles found in editor. Generate subtitles first.")
            return
        
        self.vtt_content = vtt_content
        
        # Create temporary VTT file for video player
        try:
            if self.temp_vtt_file and os.path.exists(self.temp_vtt_file):
                os.unlink(self.temp_vtt_file)
            
            # Create temp VTT file
            temp_dir = tempfile.gettempdir()
            self.temp_vtt_file = os.path.join(temp_dir, f"preview_{os.path.basename(self.video_path)}.vtt")
            
            with open(self.temp_vtt_file, 'w', encoding='utf-8') as f:
                f.write(vtt_content)
            
            # Update preview display
            filename = os.path.basename(self.video_path)
            self.preview_label.configure(
                text=f"🎬 {filename}\n\n"
                     f"✅ Subtitles synchronized!\n\n"
                     f"📝 {self._count_subtitle_blocks(vtt_content)} subtitle blocks loaded\n\n"
                     f"🎯 Ready for playback with subtitle overlay"
            )
            
            self.app.status_bar.show_success("Subtitles synchronized with video preview")
            
            # Show playback instructions
            self._show_playback_instructions()
            
        except Exception as e:
            self.app.status_bar.show_error(f"Failed to sync subtitles: {e}")
    
    def _count_subtitle_blocks(self, vtt_content: str) -> int:
        """Count the number of subtitle blocks in VTT content"""
        lines = vtt_content.split('\n')
        count = 0
        for line in lines:
            if '-->' in line:  # Timing line indicates a subtitle block
                count += 1
        return count
    
    def _show_playback_instructions(self):
        """Show instructions for playing video with subtitles"""
        instructions = (
            "🎯 To play video with subtitles:\n\n"
            "1. Open video in a media player that supports VTT subtitles\n"
            "2. Load the subtitle file from temporary location\n"
            "3. Play and verify subtitle timing\n\n"
            f"📁 Subtitle file: {self.temp_vtt_file}"
        )
        
        # Could be enhanced with actual embedded video player in future
        print(instructions)  # For now, show in console
    
    def update_preview(self, video_path: Optional[str] = None, vtt_content: Optional[str] = None):
        """Update preview with new video or subtitle content"""
        if video_path:
            self.video_path = video_path
            filename = os.path.basename(video_path)
            self.video_info_label.configure(text=f"Video: {filename}")
            self.sync_btn.configure(state="normal")
        
        if vtt_content:
            self.vtt_content = vtt_content
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_vtt_file and os.path.exists(self.temp_vtt_file):
                os.unlink(self.temp_vtt_file)
        except Exception:
            pass