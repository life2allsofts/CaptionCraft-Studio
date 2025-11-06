"""
VTT Generator Engine for CaptionCraft Studio
Core functionality for WebVTT subtitle generation with advanced styling

Module: vtt_generator.py
Description: Generates WebVTT subtitle files with advanced features including
             word-by-word timing, CSS styling, and multiple export formats.
Author: Tetteh-Kofi (Isaac Tetteh-Apotey)
Version: 1.0.0

Key Features:
- Word-by-word timing for karaoke effect
- CSS-based styling with class support
- Multiple timestamp format handling
- Robust error handling and fallbacks
- Cross-platform file encoding support
"""

import webvtt
from datetime import timedelta
from typing import List, Dict, Any, Optional
import os
import sys

# =============================================================================
# PATH CONFIGURATION & IMPORTS
# =============================================================================

# Add project root to Python path to enable cross-module imports
# This allows importing utils.config_manager from deep directory structures
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from utils.config_manager import config_manager
    print("✅ Successfully imported config_manager from utils")
except ImportError as e:
    print(f"⚠️  Could not import config_manager: {e}")
    print("🔄 Using fallback configuration...")
    
    # Fallback configuration for when imports fail (e.g., during direct execution)
    # This ensures the class remains functional even without external dependencies
    class FallbackConfig:
        """
        Fallback configuration provider when main config manager is unavailable.
        Provides default values for styling and formatting.
        """
        
        def get(self, key: str, default: Any = None) -> Any:
            """
            Retrieve configuration value with fallback defaults.
            
            Args:
                key (str): Dot-notation key for configuration value
                default (Any): Default value if key not found
                
            Returns:
                Any: Configuration value or default
            """
            # Default styling values used when main config is unavailable
            defaults = {
                "default_styles.highlight_color": "#FFD700",  # Gold
                "default_styles.text_color": "#FFFFFF",       # White
                "default_styles.font_family": "Arial",        # Standard font
                "default_styles.font_size": "24px",           # Readable size
                "default_styles.background_color": "#000000"  # Black background
            }
            return defaults.get(key, default)
    
    config_manager = FallbackConfig()


class VTTGenerator:
    """
    Main engine for generating WebVTT subtitle files with advanced features.
    
    This class handles the complete subtitle generation workflow including:
    - Caption management with precise timing
    - CSS styling application
    - Word-by-word timing calculations
    - File export in WebVTT format
    
    Attributes:
        captions (List[Dict]): List of subtitle captions with timing and text
        styles (Dict[str, str]): CSS style definitions for subtitle formatting
    """
    
    def __init__(self):
        """
        Initialize a new VTTGenerator instance.
        
        Sets up empty collections for captions and styles, ready for population
        through method calls.
        """
        self.captions: List[Dict[str, Any]] = []  # Stores all subtitle entries
        self.styles: Dict[str, str] = {}          # CSS style definitions
    
    def add_caption(self, start_time: str, end_time: str, text: str, 
                   style: Optional[str] = None) -> None:
        """
        Add a new subtitle caption with specified timing and optional styling.
        
        Args:
            start_time (str): Start timestamp in format "HH:MM:SS.mmm"
            end_time (str): End timestamp in format "HH:MM:SS.mmm"
            text (str): Subtitle text content
            style (Optional[str]): CSS class name for styling. Defaults to None.
            
        Example:
            >>> generator.add_caption("00:00:01.000", "00:00:04.000", "Hello World", "highlight")
        """
        caption = {
            'start': start_time,  # Start timestamp
            'end': end_time,      # End timestamp  
            'text': text,         # Subtitle text
            'style': style        # Optional CSS class
        }
        self.captions.append(caption)
    
    def set_style(self, style_name: str, css_properties: Dict[str, str]) -> None:
        """
        Define a CSS style for subtitle formatting.
        
        Creates CSS class definitions that can be applied to individual captions
        for consistent styling across the subtitle file.
        
        Args:
            style_name (str): Name of the CSS class (e.g., "highlight", "normal")
            css_properties (Dict[str, str]): CSS property-value pairs
            
        Example:
            >>> generator.set_style("highlight", {"color": "#FFD700", "font-weight": "bold"})
        """
        # Build CSS string from property dictionary
        css_string = "{\n"
        for prop, value in css_properties.items():
            css_string += f"  {prop}: {value};\n"  # Format as valid CSS
        css_string += "}"
        self.styles[style_name] = css_string
    
    def generate_word_by_word_caption(self, start_time: str, end_time: str, 
                                    text: str, words_per_chunk: int = 1) -> List[Dict[str, str]]:
        """
        Generate word-by-word timing for karaoke-style subtitle effects.
        
        Splits text into individual words or chunks and calculates precise timing
        for each segment, creating a smooth karaoke reading experience.
        
        Args:
            start_time (str): Overall start timestamp
            end_time (str): Overall end timestamp  
            text (str): Text to split into timed segments
            words_per_chunk (int): Number of words per timing chunk. Defaults to 1.
            
        Returns:
            List[Dict[str, str]]: List of caption dictionaries with calculated timing
            
        Example:
            >>> captions = generator.generate_word_by_word_caption(
            ...     "00:00:10.000", "00:00:15.000", "Hello world", 1
            ... )
        """
        words = text.split()  # Split text into individual words
        total_words = len(words)
        
        # Calculate total duration and time per word/chunk
        duration = self._time_difference(end_time, start_time)
        word_duration = duration / total_words
        
        chunks = []
        current_time = self._parse_timestamp(start_time)
        
        # Create timing chunks for words or word groups
        for i in range(0, total_words, words_per_chunk):
            # Calculate end time for this chunk
            chunk_end = current_time + (word_duration * words_per_chunk)
            # Extract words for this chunk
            chunk_text = ' '.join(words[i:i + words_per_chunk])
            
            # Create caption entry for this timing chunk
            chunks.append({
                'start': self._format_timestamp(current_time),
                'end': self._format_timestamp(chunk_end),
                'text': chunk_text
            })
            
            # Move to next time segment
            current_time = chunk_end
        
        return chunks
    
    def generate_vtt_content(self) -> str:
        """
        Generate complete WebVTT file content as a string.
        
        Constructs the full VTT file including:
        - WEBVTT header
        - CSS style definitions (if any)
        - Numbered captions with timing and text
        
        Returns:
            str: Complete VTT file content ready for saving
            
        Example:
            >>> vtt_content = generator.generate_vtt_content()
            >>> print(vtt_content)
        """
        content = "WEBVTT\n\n"  # VTT file header
        
        # Add CSS style section if styles are defined
        if self.styles:
            content += "STYLE\n"
            for style_name, style_css in self.styles.items():
                # Format as ::style_name { css-properties }
                content += f"::{style_name} {style_css}\n"
            content += "\n"  # Extra newline after styles
        
        # Add all captions with numbering and timing
        for i, caption in enumerate(self.captions, 1):
            content += f"{i}\n"  # Caption number
            content += f"{caption['start']} --> {caption['end']}\n"  # Timing line
            
            # Add text with optional CSS class styling
            if caption.get('style'):
                # Apply CSS class if specified: <c.classname>text</c>
                content += f"<c.{caption['style']}>{caption['text']}</c>\n"
            else:
                # Plain text without styling
                content += f"{caption['text']}\n"
            
            content += "\n"  # Blank line between captions
        
        return content
    
    def save_to_file(self, filename: str) -> None:
        """
        Save generated VTT content to a file.
        
        Writes the complete VTT content to specified file with UTF-8 encoding
        to ensure compatibility across different platforms and media players.
        
        Args:
            filename (str): Path to output file
            
        Raises:
            IOError: If file cannot be written (permissions, disk space, etc.)
        """
        content = self.generate_vtt_content()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _parse_timestamp(self, timestamp: str) -> timedelta:
        """
        Parse VTT timestamp string into timedelta object for calculations.
        
        Handles multiple timestamp formats including:
        - 00:00:01.000 (standard VTT format with dots)
        - 00:00:01,000 (SRT format with commas)
        
        Args:
            timestamp (str): Timestamp string to parse
            
        Returns:
            timedelta: Python timedelta object for time calculations
            
        Raises:
            ValueError: If timestamp format is invalid
        """
        try:
            # Handle both dot and comma decimal separators
            timestamp = timestamp.replace(',', '.')
            parts = timestamp.split(':')
            
            if len(parts) == 3:  # Standard HH:MM:SS.mmm format
                hours, minutes, seconds_millis = parts
                seconds_parts = seconds_millis.split('.')
                seconds = int(seconds_parts[0])
                milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            else:
                # Fallback for malformed timestamps
                hours, minutes, seconds, milliseconds = 0, 0, 1, 0
                
            return timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
                milliseconds=int(milliseconds)
            )
        except (ValueError, IndexError) as e:
            # Graceful degradation for invalid timestamps
            print(f"⚠️  Error parsing timestamp '{timestamp}': {e}")
            return timedelta(seconds=1)  # Default 1-second duration
    
    def _format_timestamp(self, td: timedelta) -> str:
        """
        Format timedelta object back to VTT timestamp string.
        
        Converts Python timedelta to standard WebVTT timestamp format
        HH:MM:SS.mmm for inclusion in VTT files.
        
        Args:
            td (timedelta): Python timedelta object
            
        Returns:
            str: Formatted timestamp string "HH:MM:SS.mmm"
        """
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = td.microseconds // 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    def _time_difference(self, end: str, start: str) -> timedelta:
        """
        Calculate time difference between two timestamp strings.
        
        Utility method for duration calculations used in word-by-word timing
        and other time-based operations.
        
        Args:
            end (str): End timestamp string
            start (str): Start timestamp string
            
        Returns:
            timedelta: Difference between end and start times
        """
        return self._parse_timestamp(end) - self._parse_timestamp(start)


# =============================================================================
# TESTING & DEMONSTRATION
# =============================================================================

if __name__ == "__main__":
    """
    Standalone test execution for VTT Generator functionality.
    
    This section runs when the file is executed directly (not imported).
    It demonstrates the core features and verifies the generator is working.
    """
    print("🧪 Testing VTT Generator...")
    
    # Create generator instance
    generator = VTTGenerator()
    
    # Define CSS styles for subtitle formatting
    generator.set_style("highlight", {
        "color": config_manager.get("default_styles.highlight_color", "#FFD700"),
        "font-weight": "bold"
    })
    
    generator.set_style("normal", {
        "color": config_manager.get("default_styles.text_color", "#FFFFFF"),
        "font-family": config_manager.get("default_styles.font_family", "Arial"),
        "font-size": config_manager.get("default_styles.font_size", "24px")
    })
    
    # Add regular captions with styling
    generator.add_caption("00:00:01.000", "00:00:04.000", 
                         "Welcome to CaptionCraft Studio", "normal")
    
    generator.add_caption("00:00:05.000", "00:00:08.000", 
                         "Advanced subtitle generation", "highlight")
    
    # Test word-by-word timing feature
    print("🔤 Testing word-by-word timing...")
    word_captions = generator.generate_word_by_word_caption(
        "00:00:10.000", "00:00:15.000", 
        "This is word by word timing", 
        words_per_chunk=1
    )
    
    # Add word-by-word captions to main collection
    for caption in word_captions:
        generator.add_caption(caption['start'], caption['end'], caption['text'])
    
    # Generate and display complete VTT content
    vtt_content = generator.generate_vtt_content()
    print("📄 Generated VTT Content:")
    print("=" * 50)
    print(vtt_content)
    print("=" * 50)
    
    # Save to file for verification
    output_file = "test_output.vtt"
    generator.save_to_file(output_file)
    print(f"💾 Test VTT file saved as '{output_file}'")
    
    print("✅ VTT Generator test completed successfully!")