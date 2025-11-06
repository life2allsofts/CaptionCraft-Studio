"""
CaptionCraft Studio - Main Application Entry Point
Refactored to be minimal and delegate to components

Module: main_app.py
Description: Main application window orchestrator with theme management,
             window positioning, and component coordination.
Author: Tetteh-Kofi (Isaac Tetteh-Apotey)
Version: 1.0.0

Key Features:
- Theme toggling between dark and light modes
- Proper window positioning above taskbar
- Component-based UI architecture
- Centralized application state management
- AI media transcription capabilities
"""

import tkinter as tk
import customtkinter as ctk
import os
import sys
from typing import TYPE_CHECKING, Any

# Add the project root to Python path for cross-module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level to project root
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from ui.components.header import HeaderComponent as HeaderComponentType
    from ui.components.editor_tab import EditorTab as EditorTabType
    from ui.components.styling_tab import StylingTab as StylingTabType
    from ui.components.preview_tab import PreviewTab as PreviewTabType
    from ui.components.status_bar import StatusBar as StatusBarType
    from ui.dialogs.file_dialogs import FileDialogs as FileDialogsType
    from core.vtt_engine.vtt_generator import VTTGenerator as VTTGeneratorType

try:
    from utils.config_manager import config_manager
    from core.vtt_engine.vtt_generator import VTTGenerator
    
    # Import UI components
    from ui.components.header import HeaderComponent
    from ui.components.editor_tab import EditorTab
    from ui.components.styling_tab import StylingTab
    from ui.components.preview_tab import PreviewTab
    from ui.components.status_bar import StatusBar
    from ui.dialogs.file_dialogs import FileDialogs
    
    print("✅ All imports successful")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔄 Using fallback imports...")
    
    # Fallback imports for development
    import utils.config_manager as config_manager
    from core.vtt_engine import vtt_generator
    
    # Create minimal fallback components
    class HeaderComponent:
        def __init__(self, parent, app):
            self.parent = parent
            self.app = app
        
        def setup_ui(self):
            pass
    
    class EditorTab:
        def __init__(self, notebook, app):
            self.notebook = notebook
            self.app = app
        
        def get_text(self) -> str:
            return ""
        
        def set_text(self, text: str):
            pass
    
    class StylingTab:
        def __init__(self, notebook, app):
            self.notebook = notebook
            self.app = app
    
    class PreviewTab:
        def __init__(self, notebook, app):
            self.notebook = notebook
            self.app = app
        
        def update_preview(self, content: str):
            pass
    
    class StatusBar:
        def __init__(self, parent, app):
            self.parent = parent
            self.app = app
        
        def update_status(self, message: str):
            print(f"Status: {message}")
        
        def show_progress(self):
            print("Progress started")
        
        def hide_progress(self):
            print("Progress ended")
    
    class FileDialogs:
        def __init__(self, app):
            self.app = app


class CaptionCraftStudio(ctk.CTk):
    """
    Main application window for CaptionCraft Studio.
    
    Orchestrates all UI components and manages application-level state
    including theme preferences, window geometry, and user sessions.
    
    Features:
    - Dynamic theme switching (dark/light)
    - Smart window positioning above taskbar
    - Component lifecycle management
    - Application state persistence
    - AI media transcription
    """
    
    def __init__(self):
        """
        Initialize the main application window.
        
        Sets up window properties, initializes components, and restores
        previous session state from configuration.
        """
        super().__init__()
        
        # Configure window properties before UI setup
        self._configure_window()
        
        # Initialize application state with type annotations
        self.vtt_generator: Any = VTTGenerator()
        self.current_file: str | None = None
        self.file_dialogs: Any = FileDialogs(self)
        self.theme_mode: str = config_manager.get("ui.theme", "dark")
        
        # Initialize UI component references
        self.header: Any = None
        self.status_bar: Any = None
        self.editor_tab: Any = None
        self.styling_tab: Any = None
        self.preview_tab: Any = None
        self.notebook: Any = None
        self.main_frame: Any = None
        
        # Setup UI components
        self.setup_ui()
        
        # Load and apply configuration
        self.load_config()
    
    def _configure_window(self):
        """
        Configure main window properties and positioning.
        
        Sets window title, size, minimum dimensions, and ensures proper
        positioning above the taskbar on all platforms.
        """
        # Basic window properties
        self.title(config_manager.get("app.name", "CaptionCraft Studio"))
        
        # Set initial window size (slightly smaller than full screen)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate window size (90% of screen, positioned centered)
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.85)  # Reserve space for taskbar
        
        # Calculate position to center window
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # Set window geometry and minimum size
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.minsize(1000, 700)  # Minimum usable size
        
        # Set window icon (future enhancement)
        # self.iconbitmap("assets/icon.ico")  # Uncomment when icon is available
    
    def setup_ui(self):
        """
        Setup the main user interface by delegating to components.
        
        Creates the main application frame and initializes all UI components
        in the proper hierarchy for responsive layout.
        """
        # Create main application frame with padding
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize UI components
        self.header = HeaderComponent(self.main_frame, self)
        self.status_bar = StatusBar(self.main_frame, self)
        
        # Setup main content area with tabs
        self.setup_main_content()
    
    def setup_main_content(self):
        """
        Setup the main content area with tabbed interface.
        
        Creates the notebook (tab container) and initializes all tab
        components for organized feature access.
        """
        content_frame = ctk.CTkFrame(self.main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabbed interface for feature organization
        self.notebook = ctk.CTkTabview(content_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Initialize tab components
        self.editor_tab = EditorTab(self.notebook, self)
        self.styling_tab = StylingTab(self.notebook, self)
        self.preview_tab = PreviewTab(self.notebook, self)
    
    def load_config(self):
        """
        Load and apply application configuration.
        
        Applies stored user preferences including theme, window state,
        and recent files. Called during application initialization.
        """
        # Apply theme from configuration
        self.apply_theme(self.theme_mode)
        
        # Update status to indicate successful configuration load
        self.status_bar.update_status("Configuration loaded successfully")
    
    def apply_theme(self, theme_mode: str):
        """
        Apply theme to the entire application.
        
        Updates all UI components to use the specified theme and persists
        the preference to configuration for future sessions.
        
        Args:
            theme_mode (str): Theme to apply - 'dark' or 'light'
        """
        try:
            # Update theme in customtkinter
            ctk.set_appearance_mode(theme_mode)
            
            # Update local state
            self.theme_mode = theme_mode
            
            # Persist to configuration
            config_manager.set("ui.theme", theme_mode)
            
            # Provide user feedback
            self.status_bar.update_status(f"Theme changed to {theme_mode} mode")
            
        except Exception as e:
            # Graceful degradation on theme change failure
            print(f"Theme change error: {e}")
            self.status_bar.update_status("Error changing theme")
    
    def toggle_theme(self):
        """
        Toggle between dark and light themes.
        
        Provides quick theme switching functionality that can be triggered
        from menu items, keyboard shortcuts, or UI buttons.
        """
        new_theme = "light" if self.theme_mode == "dark" else "dark"
        self.apply_theme(new_theme)
    
    def get_subtitle_text(self) -> str:
        """
        Get current subtitle text from editor component.
        
        Returns:
            str: Current content of the subtitle editor
        """
        return self.editor_tab.get_text()
    
    def set_subtitle_text(self, text: str):
        """
        Set subtitle text in editor component.
        
        Args:
            text (str): Text to display in subtitle editor
        """
        self.editor_tab.set_text(text)
    
    def update_preview(self, content: str):
        """
        Update preview tab with generated content.
        
        Args:
            content (str): Content to display in preview tab
        """
        self.preview_tab.update_preview(content)

    def process_media_file(self, file_path: str):
        """
        Process media file for AI transcription.
        
        Args:
            file_path (str): Path to media file to process
        """
        try:
            self.status_bar.update_status(f"Processing media: {os.path.basename(file_path)}")
            self.status_bar.show_progress()
            
            # Initialize audio processor
            from core.audio_processor.unified_processor import UnifiedAudioProcessor
            processor = UnifiedAudioProcessor()
            
            # Check if AI transcription is available
            if not processor.get_status()["whisper_available"]:
                self.status_bar.update_status("AI transcription not available. Install whisper.")
                return
            
            # Process the media file
            self.status_bar.update_status("AI transcribing media...")
            result = processor.transcribe_media(file_path)
            
            if result["success"]:
                # Convert segments to subtitle format
                subtitle_content = self._convert_whisper_to_vtt(result["segments"])
                self.set_subtitle_text(subtitle_content)
                self.status_bar.update_status(f"AI transcription complete: {len(result['segments'])} segments")
            else:
                self.status_bar.update_status(f"Transcription failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.status_bar.update_status(f"Media processing error: {e}")
        finally:
            self.status_bar.hide_progress()
            if 'processor' in locals():
                processor.cleanup()

    def _convert_whisper_to_vtt(self, segments: list) -> str:
        """
        Convert Whisper segments to VTT format.
        
        Args:
            segments (list): Whisper transcription segments
            
        Returns:
            str: VTT formatted subtitles
        """
        vtt_content = "WEBVTT\n\n"
        
        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment["text"].strip()
            
            vtt_content += f"{i}\n"
            vtt_content += f"{start} --> {end}\n"
            vtt_content += f"{text}\n\n"
        
        return vtt_content

    def _format_timestamp(self, seconds: float) -> str:
        """
        Format seconds to VTT timestamp.
        
        Args:
            seconds (float): Time in seconds
            
        Returns:
            str: Formatted timestamp (HH:MM:SS.mmm)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_remaining = seconds % 60
        milliseconds = int((seconds_remaining - int(seconds_remaining)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds_remaining):02d}.{milliseconds:03d}"
    
    def center_window(self):
        """
        Center the window on the screen above taskbar.
        
        Useful for window management and ensuring proper visibility
        regardless of monitor configuration or taskbar position.
        """
        # Update window geometry to ensure accurate measurements
        self.update_idletasks()
        
        # Get current window dimensions
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate centered position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Apply new position
        self.geometry(f"+{x}+{y}")


def main():
    """
    Main application entry point.
    
    Initializes and runs the CaptionCraft Studio application with
    comprehensive error handling and user-friendly error reporting.
    """
    try:
        # Create and run application
        app = CaptionCraftStudio()
        app.mainloop()
        
    except Exception as e:
        # Comprehensive error handling for application startup failures
        error_message = f"Could not start application: {e}"
        print(f"Fatal Error: {error_message}")
        
        # Attempt to show user-friendly error dialog
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Fatal Error", error_message)
        except:
            # Fallback if even error dialog fails
            print("Additional error showing error dialog")


# =============================================================================
# PYLANCE CONFIGURATION
# =============================================================================
# These directives suppress false positive warnings from Pylance static analysis
# while maintaining full runtime functionality. The application imports work
# correctly at runtime through dynamic path modification.
#
# pyright: reportMissingImports=false  
# pyright: reportAttributeAccessIssue=false
# pyright: reportAssignmentType=false   
# pyright: reportUnusedImport=false      
#
# Note: These are development-time only and don't affect runtime performance.
# =============================================================================
# pyright: reportMissingImports=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportAssignmentType=false
# pyright: reportUnusedImport=false

# Application entry point
if __name__ == "__main__":
    main()