"""
Enhanced Video Preview Tab with Multi-Player Support and Fallbacks
"""

import customtkinter as ctk
import os
import tempfile
import subprocess
import threading
import webbrowser
from typing import Optional, List

class VideoPreviewTab:
    """Video preview tab with multiple player options and fallbacks"""
    
    def __init__(self, notebook, app):
        self.notebook = notebook
        self.app = app
        self.video_path: Optional[str] = None
        self.vtt_content: Optional[str] = None
        self.temp_vtt_file: Optional[str] = None
        self.is_playing = False
        self.available_players = self._detect_media_players()
        
        # Create tab
        self.tab = self.notebook.add("🎥 Video Preview")
        self.setup_ui()
    
    def _detect_media_players(self) -> List[dict]:
        """Detect available media players on the system"""
        players = []
        
        # Check VLC
        vlc_paths = [
            "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
            "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe",
            "vlc"  # If in PATH
        ]
        for path in vlc_paths:
            if os.path.exists(path) or path == "vlc":
                players.append({
                    'name': 'VLC Media Player',
                    'command': [path, '--sub-file', '{subtitle}', '{video}', '--play-and-exit'],
                    'type': 'desktop'
                })
                break
        
        # Check Windows Media Player
        wmp_path = "C:\\Program Files\\Windows Media Player\\wmplayer.exe"
        if os.path.exists(wmp_path):
            players.append({
                'name': 'Windows Media Player', 
                'command': [wmp_path, '{video}'],
                'type': 'desktop',
                'note': 'Subtitles may need manual loading'
            })
        
        # Check MPV
        mpv_paths = [
            "C:\\Program Files\\mpv\\mpv.exe",
            "mpv"  # If in PATH
        ]
        for path in mpv_paths:
            if os.path.exists(path) or path == "mpv":
                players.append({
                    'name': 'MPV Player',
                    'command': [path, '--sub-file={subtitle}', '{video}'],
                    'type': 'desktop'
                })
                break
        
        # Check PotPlayer
        potplayer_paths = [
            "C:\\Program Files\\DAUM\\PotPlayer\\PotPlayerMini64.exe",
            "C:\\Program Files (x86)\\DAUM\\PotPlayer\\PotPlayerMini.exe"
        ]
        for path in potplayer_paths:
            if os.path.exists(path):
                players.append({
                    'name': 'PotPlayer',
                    'command': [path, '{video}'],
                    'type': 'desktop', 
                    'note': 'Subtitles may need manual loading'
                })
                break
        
        # Always include system default as fallback
        players.append({
            'name': 'System Default Player',
            'command': ['{video}'],  # os.startfile equivalent
            'type': 'system',
            'note': 'Basic playback - subtitles need manual loading'
        })
        
        return players
    
    def setup_ui(self):
        """Setup the video preview UI with multiple player options"""
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
        
        # Player detection info
        player_count = len(self.available_players)
        self.player_info_label = ctk.CTkLabel(
            info_frame,
            text=f"🎯 {player_count} players detected",
            font=ctk.CTkFont(size=10),
            text_color="#888888"
        )
        self.player_info_label.pack(side="right", padx=10, pady=5)
        
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
            text="🔄 Sync Subtitles",
            command=self.sync_current_subtitles,
            width=140,
            state="disabled"
        )
        self.sync_btn.pack(side="left", padx=5, pady=5)
        
        # Player selection dropdown
        self.player_var = ctk.StringVar(value="auto")
        self.player_dropdown = ctk.CTkOptionMenu(
            controls_frame,
            values=self._get_player_options(),
            variable=self.player_var,
            width=180,
            state="disabled"
        )
        self.player_dropdown.pack(side="left", padx=5, pady=5)
        
        # Play button
        self.play_btn = ctk.CTkButton(
            controls_frame,
            text="▶️ Play Video",
            command=self.play_video,
            width=120,
            state="disabled",
            fg_color="#2AA876",
            hover_color="#228B69"
        )
        self.play_btn.pack(side="left", padx=5, pady=5)
        
        # Open folder button
        self.folder_btn = ctk.CTkButton(
            controls_frame,
            text="📂 Show Files",
            command=self.show_files,
            width=120,
            state="disabled"
        )
        self.folder_btn.pack(side="left", padx=5, pady=5)
        
        # Preview area
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status display
        self.status_label = ctk.CTkLabel(
            preview_frame,
            text=self._get_welcome_message(),
            font=ctk.CTkFont(size=13),
            justify="left"
        )
        self.status_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Player recommendations frame
        self.recommendation_frame = ctk.CTkFrame(main_frame)
        self.recommendation_frame.pack(fill="x", padx=5, pady=5)
        
        self.recommendation_label = ctk.CTkLabel(
            self.recommendation_frame,
            text="",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.recommendation_label.pack(padx=10, pady=5)
        
        # Progress frame
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", padx=5, pady=5)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to load video and subtitles",
            font=ctk.CTkFont(size=11)
        )
        self.progress_label.pack(padx=10, pady=5)
    
    def _get_welcome_message(self) -> str:
        """Get welcome message based on detected players"""
        vlc_available = any('VLC' in player['name'] for player in self.available_players)
        
        if vlc_available:
            return ("🎬 Video Preview\n\n"
                   "✅ VLC detected - best subtitle support\n\n"
                   "1. Load a video file\n"
                   "2. Generate subtitles in Editor tab\n" 
                   "3. Sync subtitles here\n"
                   "4. Play with automatic subtitle loading")
        else:
            return ("🎬 Video Preview\n\n"
                   "⚠️ No advanced players detected\n\n"
                   "1. Load a video file\n"
                   "2. Generate subtitles in Editor tab\n"
                   "3. Sync subtitles here\n" 
                   "4. Use system player (subtitles need manual loading)\n\n"
                   "💡 For best experience, install VLC Media Player")
    
    def _get_player_options(self) -> List[str]:
        """Get player options for dropdown"""
        options = ["Auto-select best player"]
        for player in self.available_players:
            options.append(player['name'])
        return options
    
    def load_video(self):
        """Load a video file for preview"""
        file_path = self.app.file_dialogs.import_media_file()
        if file_path:
            self.video_path = file_path
            filename = os.path.basename(file_path)
            self.video_info_label.configure(text=f"Video: {filename}")
            self.sync_btn.configure(state="normal")
            self.play_btn.configure(state="normal")
            self.folder_btn.configure(state="normal")
            self.player_dropdown.configure(state="normal")
            
            # Update recommendations
            self._update_player_recommendations()
            
            self.status_label.configure(
                text=f"🎬 {filename}\n\n"
                     f"✅ Video loaded successfully!\n\n"
                     f"📊 Detected {len(self.available_players)} media players\n\n"
                     f"🎯 Next: Generate subtitles in Editor tab, then sync here"
            )
            
            self.progress_label.configure(text=f"Video loaded: {filename}")
            self.app.status_bar.update_status(f"Video loaded: {filename}")
    
    def _update_player_recommendations(self):
        """Update player recommendations based on available players"""
        recommendations = []
        
        for player in self.available_players:
            if 'VLC' in player['name']:
                recommendations.append("✅ VLC: Best subtitle support")
            elif 'MPV' in player['name']:
                recommendations.append("✅ MPV: Great subtitle support") 
            elif 'PotPlayer' in player['name']:
                recommendations.append("⚠️ PotPlayer: Good, subtitles may need manual load")
            elif 'Windows Media Player' in player['name']:
                recommendations.append("⚠️ WMP: Basic, subtitles need manual load")
            elif 'System Default' in player['name']:
                recommendations.append("❌ System: Limited, no auto-subtitles")
        
        if recommendations:
            self.recommendation_label.configure(text=" | ".join(recommendations))
    
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
            video_name = os.path.splitext(os.path.basename(self.video_path))[0]
            temp_dir = tempfile.gettempdir()
            self.temp_vtt_file = os.path.join(temp_dir, f"{video_name}_subtitles.vtt")
            
            with open(self.temp_vtt_file, 'w', encoding='utf-8') as f:
                f.write(vtt_content)
            
            # Analyze subtitle timing
            block_count = self._count_subtitle_blocks(vtt_content)
            
            # Update status
            filename = os.path.basename(self.video_path)
            
            self.status_label.configure(
                text=f"🎬 {filename}\n\n"
                     f"✅ Subtitles synchronized!\n\n"
                     f"📊 {block_count} subtitle blocks ready\n\n"
                     f"🎯 Select a player and click 'Play Video'\n\n"
                     f"💡 For automatic subtitles, use VLC or MPV"
            )
            
            self.progress_label.configure(text=f"Subtitles ready: {block_count} blocks")
            self.app.status_bar.show_success(f"Subtitles synchronized: {block_count} blocks")
            
        except Exception as e:
            self.app.status_bar.show_error(f"Failed to sync subtitles: {e}")
    
    def play_video(self):
        """Play video with subtitles using selected player"""
        if not self.video_path:
            self.app.status_bar.show_error("Please load a video first")
            return
        
        if not self.temp_vtt_file or not os.path.exists(self.temp_vtt_file):
            self.app.status_bar.show_error("Please sync subtitles first")
            return
        
        try:
            self.is_playing = True
            self.play_btn.configure(state="disabled")
            
            # Get selected player
            selected_player = self._get_selected_player()
            
            # Update status
            self.status_label.configure(
                text=f"🎬 Launching {selected_player['name']}...\n\n"
                     f"Loading video with subtitles...\n\n"
                     f"{selected_player.get('note', '')}"
            )
            
            self.progress_label.configure(text=f"🎬 Launching {selected_player['name']}...")
            self.app.status_bar.update_status(f"Launching {selected_player['name']}...")
            
            # Launch player in separate thread
            threading.Thread(
                target=self._launch_player, 
                args=(selected_player,), 
                daemon=True
            ).start()
            
        except Exception as e:
            self.app.status_bar.show_error(f"Failed to play video: {e}")
            self._reset_playback_state()
    
    def _get_selected_player(self) -> dict:
        """Get the selected player based on dropdown choice"""
        selected = self.player_var.get()
        
        if selected == "Auto-select best player":
            # Prefer VLC, then MPV, then others
            for player in self.available_players:
                if 'VLC' in player['name']:
                    return player
            for player in self.available_players:
                if 'MPV' in player['name']:
                    return player
            return self.available_players[0]  # First available
        
        # Find by name
        for player in self.available_players:
            if player['name'] == selected:
                return player
        
        # Fallback to first available
        return self.available_players[0]
    
    def _launch_player(self, player: dict):
        """Launch the selected media player (runs in separate thread)"""
        try:
            if player['type'] == 'system':
                # Use system default player
                if not self.video_path:
                    self.app.status_bar.show_error("No video path to open")
                    self._reset_playback_state()
                    return
                os.startfile(self.video_path)
                self.app.status_bar.update_status(
                    "Video opened in default player - subtitles may need manual loading"
                )
            else:
                # Build command with proper file paths
                command = []
                for part in player['command']:
                    if part == '{video}':
                        command.append(self.video_path)
                    elif part == '{subtitle}':
                        command.append(self.temp_vtt_file)
                    else:
                        command.append(part)
                
                # Launch the player
                subprocess.run(command, check=True)
            
            # Reset UI state when playback finishes
            self._reset_playback_state()
            
        except subprocess.CalledProcessError:
            self.app.status_bar.show_error(f"Failed to launch {player['name']}")
            self._show_installation_help(player)
        except Exception as e:
            self.app.status_bar.show_error(f"Player error: {e}")
            self._reset_playback_state()
    
    def _show_installation_help(self, player: dict):
        """Show help for installing media players"""
        help_text = ""
        
        if 'VLC' in player['name']:
            help_text = ("❌ VLC not found or failed to launch\n\n"
                        "💡 Please install VLC Media Player:\n"
                        "1. Download from https://www.videolan.org/\n"
                        "2. Run the installer\n"
                        "3. Restart CaptionCraft Studio")
        elif 'MPV' in player['name']:
            help_text = ("❌ MPV not found\n\n"
                        "💡 Download MPV Player from:\n"
                        "https://mpv.io/installation/")
        
        if help_text:
            self.status_label.configure(text=help_text)
    
    def show_files(self):
        """Show the video and subtitle files in file explorer"""
        try:
            files_to_show = []
            
            if self.video_path:
                files_to_show.append(self.video_path)
            
            if self.temp_vtt_file and os.path.exists(self.temp_vtt_file):
                files_to_show.append(self.temp_vtt_file)
            
            if files_to_show:
                # Show the folder containing the first file
                first_file_dir = os.path.dirname(files_to_show[0])
                subprocess.run(['explorer', first_file_dir], shell=True)
                
                if len(files_to_show) > 1:
                    self.app.status_bar.update_status("Folder opened - video and subtitle files shown")
                else:
                    self.app.status_bar.update_status("Video folder opened")
        except Exception as e:
            self.app.status_bar.show_error(f"Failed to open folder: {e}")
    
    def _reset_playback_state(self):
        """Reset playback UI state"""
        self.is_playing = False
        self.play_btn.configure(state="normal")
        self.progress_label.configure(text="Ready for playback")
    
    def _count_subtitle_blocks(self, vtt_content: str) -> int:
        """Count the number of subtitle blocks in VTT content"""
        lines = vtt_content.split('\n')
        count = 0
        for line in lines:
            if '-->' in line:  # Timing line indicates a subtitle block
                count += 1
        return count
    
    def update_preview(self, video_path: Optional[str] = None, vtt_content: Optional[str] = None):
        """Update preview with new video or subtitle content"""
        if video_path:
            self.video_path = video_path
            filename = os.path.basename(video_path)
            self.video_info_label.configure(text=f"Video: {filename}")
            self.sync_btn.configure(state="normal")
            self.play_btn.configure(state="normal")
            self.folder_btn.configure(state="normal")
            self.player_dropdown.configure(state="normal")
            self._update_player_recommendations()
        
        if vtt_content:
            self.vtt_content = vtt_content
            # Auto-sync if video is already loaded
            if self.video_path:
                self.sync_current_subtitles()
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_vtt_file and os.path.exists(self.temp_vtt_file):
                os.unlink(self.temp_vtt_file)
        except Exception:
            pass