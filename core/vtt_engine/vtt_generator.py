"""
VTT Generator Engine for CaptionCraft Studio
Core functionality for WebVTT subtitle generation with advanced styling
"""

import webvtt
from datetime import timedelta
from typing import List, Dict, Any, Optional
import os
import sys

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from utils.config_manager import config_manager
    print("✅ Successfully imported config_manager from utils")
except ImportError as e:
    print(f"⚠️  Could not import config_manager: {e}")
    print("🔄 Using fallback configuration...")
    
    # Fallback configuration
    class FallbackConfig:
        def get(self, key, default=None):
            defaults = {
                "default_styles.highlight_color": "#FFD700",
                "default_styles.text_color": "#FFFFFF", 
                "default_styles.font_family": "Arial",
                "default_styles.font_size": "24px",
                "default_styles.background_color": "#000000"
            }
            return defaults.get(key, default)
    
    config_manager = FallbackConfig()


class VTTGenerator:
    """Generates WebVTT subtitles with advanced styling and timing"""
    
    def __init__(self):
        self.captions: List[Dict[str, Any]] = []
        self.styles: Dict[str, str] = {}
    
    def add_caption(self, start_time: str, end_time: str, text: str, 
                   style: Optional[str] = None) -> None:
        """Add a caption with timing and optional styling"""
        caption = {
            'start': start_time,
            'end': end_time,
            'text': text,
            'style': style
        }
        self.captions.append(caption)
    
    def set_style(self, style_name: str, css_properties: Dict[str, str]) -> None:
        """Define a CSS style for subtitles"""
        css_string = "{\n"
        for prop, value in css_properties.items():
            css_string += f"  {prop}: {value};\n"
        css_string += "}"
        self.styles[style_name] = css_string
    
    def generate_word_by_word_caption(self, start_time: str, end_time: str, 
                                    text: str, words_per_chunk: int = 1) -> List[Dict[str, str]]:
        """Generate word-by-word timing for karaoke effect"""
        words = text.split()
        total_words = len(words)
        duration = self._time_difference(end_time, start_time)
        word_duration = duration / total_words
        
        chunks = []
        current_time = self._parse_timestamp(start_time)
        
        for i in range(0, total_words, words_per_chunk):
            chunk_end = current_time + (word_duration * words_per_chunk)
            chunk_text = ' '.join(words[i:i + words_per_chunk])
            
            chunks.append({
                'start': self._format_timestamp(current_time),
                'end': self._format_timestamp(chunk_end),
                'text': chunk_text
            })
            
            current_time = chunk_end
        
        return chunks
    
    def generate_vtt_content(self) -> str:
        """Generate complete VTT file content"""
        content = "WEBVTT\n\n"
        
        # Add styles
        if self.styles:
            content += "STYLE\n"
            for style_name, style_css in self.styles.items():
                content += f"::{style_name} {style_css}\n"
            content += "\n"
        
        # Add captions
        for i, caption in enumerate(self.captions, 1):
            content += f"{i}\n"
            content += f"{caption['start']} --> {caption['end']}\n"
            
            if caption.get('style'):
                content += f"<c.{caption['style']}>{caption['text']}</c>\n"
            else:
                content += f"{caption['text']}\n"
            
            content += "\n"
        
        return content
    
    def save_to_file(self, filename: str) -> None:
        """Save generated VTT to file"""
        content = self.generate_vtt_content()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _parse_timestamp(self, timestamp: str) -> timedelta:
        """Parse VTT timestamp string to timedelta"""
        try:
            # Handle both 00:00:01.000 and 00:00:01,000 formats
            timestamp = timestamp.replace(',', '.')
            parts = timestamp.split(':')
            
            if len(parts) == 3:  # HH:MM:SS.mmm
                hours, minutes, seconds_millis = parts
                seconds_parts = seconds_millis.split('.')
                seconds = int(seconds_parts[0])
                milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
            else:
                # Fallback
                hours, minutes, seconds, milliseconds = 0, 0, 1, 0
                
            return timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
                milliseconds=int(milliseconds)
            )
        except (ValueError, IndexError) as e:
            print(f"⚠️  Error parsing timestamp '{timestamp}': {e}")
            return timedelta(seconds=1)
    
    def _format_timestamp(self, td: timedelta) -> str:
        """Format timedelta to VTT timestamp"""
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        milliseconds = td.microseconds // 1000
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
    
    def _time_difference(self, end: str, start: str) -> timedelta:
        """Calculate time difference between two timestamps"""
        return self._parse_timestamp(end) - self._parse_timestamp(start)


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing VTT Generator...")
    
    # Test the VTT generator
    generator = VTTGenerator()
    
    # Define some styles
    generator.set_style("highlight", {
        "color": str(config_manager.get("default_styles.highlight_color", "#FFD700") or "#FFD700"),
        "font-weight": "bold"
    })
    
    generator.set_style("normal", {
        "color": str(config_manager.get("default_styles.text_color", "#FFFFFF") or "#FFFFFF"),
        "font-family": str(config_manager.get("default_styles.font_family", "Arial") or "Arial"),
        "font-size": str(config_manager.get("default_styles.font_size", "24px") or "24px")
    })
    
    # Add captions
    generator.add_caption("00:00:01.000", "00:00:04.000", 
                         "Welcome to CaptionCraft Studio", "normal")
    
    generator.add_caption("00:00:05.000", "00:00:08.000", 
                         "Advanced subtitle generation", "highlight")
    
    # Test word-by-word generation
    print("🔤 Testing word-by-word timing...")
    word_captions = generator.generate_word_by_word_caption(
        "00:00:10.000", "00:00:15.000", 
        "This is word by word timing", 
        words_per_chunk=1
    )
    
    for caption in word_captions:
        generator.add_caption(caption['start'], caption['end'], caption['text'])
    
    # Generate and print VTT content
    vtt_content = generator.generate_vtt_content()
    print("📄 Generated VTT Content:")
    print("=" * 50)
    print(vtt_content)
    print("=" * 50)
    
    # Save to file
    output_file = "test_output.vtt"
    generator.save_to_file(output_file)
    print(f"💾 Test VTT file saved as '{output_file}'")
    
    print("✅ VTT Generator test completed successfully!")