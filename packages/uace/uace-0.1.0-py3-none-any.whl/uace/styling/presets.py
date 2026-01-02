"""
Style Presets

Declarative styling for captions - CapCut-like effects without rendering.
Exports to ASS format for universal compatibility.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum


class AnimationStyle(str, Enum):
    """Animation types."""
    
    WORD_POP = "word_pop"
    BOUNCE = "bounce"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    TYPEWRITER = "typewriter"
    FADE = "fade"
    SCALE = "scale"
    KARAOKE = "karaoke"
    NONE = "none"


@dataclass
class ColorPalette:
    """Color scheme for captions."""
    
    primary: str
    secondary: str
    outline: str
    background: Optional[str] = None
    shadow: Optional[str] = None
    emphasis: Optional[str] = None


@dataclass
class FontStyle:
    """Font styling parameters."""
    
    family: str
    size: int
    weight: str = "bold"
    italic: bool = False
    file_path: Optional[str] = None


@dataclass
class EffectsConfig:
    """Visual effects configuration."""
    
    outline_width: int = 3
    shadow_depth: int = 2
    glow: bool = False
    glow_intensity: int = 0
    blur: int = 0
    
    # Animation
    animation: AnimationStyle = AnimationStyle.WORD_POP
    animation_duration: float = 0.15  # seconds
    stagger_delay: float = 0.05  # delay between words
    
    # 3D transforms
    perspective: bool = False
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0


@dataclass
class PositionConfig:
    """Caption positioning."""
    
    alignment: str = "center"  # left, center, right
    vertical: str = "bottom"   # top, middle, bottom
    margin_left: int = 0
    margin_right: int = 0
    margin_top: int = 0
    margin_bottom: int = 100
    

class StylePreset:
    """
    A complete style preset for captions.
    
    This is what users interact with - simple, declarative styling.
    """
    
    def __init__(
        self,
        name: str,
        colors: ColorPalette,
        font: FontStyle,
        effects: EffectsConfig,
        position: PositionConfig,
        description: str = ""
    ):
        self.name = name
        self.colors = colors
        self.font = font
        self.effects = effects
        self.position = position
        self.description = description
    
    def to_ass_style(self) -> str:
        """
        Convert to ASS style string.
        
        ASS format is the most powerful caption format,
        supporting all the effects we need.
        """
        # ASS style format:
        # Style: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, 
        #        OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut,
        #        ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow,
        #        Alignment, MarginL, MarginR, MarginV, Encoding
        
        alignment = self._get_ass_alignment()
        bold = -1 if self.font.weight == "bold" else 0
        italic = -1 if self.font.italic else 0
        
        primary = self._color_to_ass(self.colors.primary)
        secondary = self._color_to_ass(self.colors.secondary)
        outline = self._color_to_ass(self.colors.outline)
        back = self._color_to_ass(self.colors.background) if self.colors.background else "&H00000000"
        
        style = (
            f"Style: {self.name},"
            f"{self.font.family},"
            f"{self.font.size},"
            f"{primary},{secondary},{outline},{back},"
            f"{bold},{italic},0,0,"
            f"100,100,0,0,"
            f"1,{self.effects.outline_width},{self.effects.shadow_depth},"
            f"{alignment},"
            f"{self.position.margin_left},{self.position.margin_right},"
            f"{self.position.margin_bottom},1"
        )
        
        return style
    
    def _get_ass_alignment(self) -> int:
        """
        Get ASS alignment number.
        
        ASS uses numpad layout:
        7 8 9
        4 5 6
        1 2 3
        """
        alignment_map = {
            ("bottom", "left"): 1,
            ("bottom", "center"): 2,
            ("bottom", "right"): 3,
            ("middle", "left"): 4,
            ("middle", "center"): 5,
            ("middle", "right"): 6,
            ("top", "left"): 7,
            ("top", "center"): 8,
            ("top", "right"): 9,
        }
        
        key = (self.position.vertical, self.position.alignment)
        return alignment_map.get(key, 2)
    
    def _color_to_ass(self, hex_color: str) -> str:
        """
        Convert hex color to ASS format.
        
        ASS uses &HAABBGGRR (alpha, blue, green, red)
        """
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 6:
            r, g, b = hex_color[0:2], hex_color[2:4], hex_color[4:6]
            return f"&H00{b.upper()}{g.upper()}{r.upper()}"
        
        return "&H00FFFFFF"


# Built-in Presets

VIRAL_POP = StylePreset(
    name="ViralPop",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#FFFFFF",
        outline="#000000",
        emphasis="#FFD700"  # Gold for emphasis
    ),
    font=FontStyle(
        family="Inter",
        size=56,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=2,
        animation=AnimationStyle.WORD_POP,
        animation_duration=0.12,
        stagger_delay=0.05
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=120
    ),
    description="High-energy TikTok/Shorts style with word-by-word pop animation"
)


MINIMAL = StylePreset(
    name="Minimal",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#CCCCCC",
        outline="#000000"
    ),
    font=FontStyle(
        family="SF Pro Display",
        size=48,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=0,
        animation=AnimationStyle.FADE,
        animation_duration=0.3
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=80
    ),
    description="Clean, minimal style for professional content"
)


KARAOKE = StylePreset(
    name="Karaoke",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#FFD700",  # Unsung words
        outline="#000000",
        emphasis="#FF6B9D"    # Currently sung word
    ),
    font=FontStyle(
        family="Arial",
        size=52,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=2,
        animation=AnimationStyle.KARAOKE,
        animation_duration=0.0  # Instant color change
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=100
    ),
    description="Karaoke-style with word-level timing color change"
)


SUBTITLE_CLASSIC = StylePreset(
    name="SubtitleClassic",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#FFFFFF",
        outline="#000000",
        background="#000000"  # Semi-transparent black background
    ),
    font=FontStyle(
        family="Arial",
        size=44,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=0,
        animation=AnimationStyle.NONE
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=60
    ),
    description="Traditional subtitle style for movies/TV"
)


BOUNCE = StylePreset(
    name="Bounce",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#FFFFFF",
        outline="#FF1493",  # Deep pink outline
        emphasis="#00FFFF"  # Cyan emphasis
    ),
    font=FontStyle(
        family="Montserrat",
        size=60,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=5,
        shadow_depth=3,
        animation=AnimationStyle.BOUNCE,
        animation_duration=0.3,
        stagger_delay=0.04
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Energetic bounce animation with colorful outline"
)


NEON = StylePreset(
    name="Neon",
    colors=ColorPalette(
        primary="#00FFFF",  # Cyan
        secondary="#FF1493",  # Deep pink
        outline="#000000",
        emphasis="#FFD700",  # Gold
        shadow="#00FFFF"  # Cyan glow
    ),
    font=FontStyle(
        family="Rajdhani",
        size=54,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=0,
        glow=True,
        glow_intensity=5,
        animation=AnimationStyle.SCALE,
        animation_duration=0.15
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=100
    ),
    description="Cyberpunk neon glow effect"
)


# Preset registry
PRESET_REGISTRY: Dict[str, StylePreset] = {
    "viral_pop": VIRAL_POP,
    "minimal": MINIMAL,
    "karaoke": KARAOKE,
    "subtitle_classic": SUBTITLE_CLASSIC,
    "bounce": BOUNCE,
    "neon": NEON,
}


def get_preset(name: str) -> Optional[StylePreset]:
    """Get a preset by name."""
    return PRESET_REGISTRY.get(name.lower())


def list_presets() -> List[str]:
    """List all available presets."""
    return list(PRESET_REGISTRY.keys())
