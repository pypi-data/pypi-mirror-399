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
    
    # New advanced animations
    ZOOM_PUNCH = "zoom_punch"
    ELASTIC = "elastic"
    WAVE = "wave"
    EARTHQUAKE = "earthquake"
    FLIP = "flip"
    ROTATE = "rotate"
    BLUR_FOCUS = "blur_focus"
    PERSPECTIVE = "perspective"
    GLITCH = "glitch"
    PULSE = "pulse"
    FLOAT = "float"
    
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


# === NEW VIRAL/SOCIAL MEDIA STYLES ===

BIG_BOLD = StylePreset(
    name="BigBold",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#FFFFFF",
        outline="#000000",
        emphasis="#FF0000"  # Red emphasis
    ),
    font=FontStyle(
        family="Impact",
        size=72,  # HUGE
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=6,
        shadow_depth=4,
        animation=AnimationStyle.ZOOM_PUNCH,
        animation_duration=0.2,
        stagger_delay=0.08
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="HUGE bold text that zooms in one word at a time - viral style"
)


ZOOM_PUNCH = StylePreset(
    name="ZoomPunch",
    colors=ColorPalette(
        primary="#FFFF00",  # Yellow
        secondary="#FFFFFF",
        outline="#000000",
        emphasis="#FF0000"
    ),
    font=FontStyle(
        family="Arial Black",
        size=68,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=5,
        shadow_depth=3,
        animation=AnimationStyle.ZOOM_PUNCH,
        animation_duration=0.18,
        stagger_delay=0.06
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Each word ZOOMS in with punch - maximum impact"
)


WAVE_MOTION = StylePreset(
    name="WaveMotion",
    colors=ColorPalette(
        primary="#00D4FF",  # Bright cyan
        secondary="#FFFFFF",
        outline="#000066",
        emphasis="#FFD700"
    ),
    font=FontStyle(
        family="Montserrat",
        size=58,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=2,
        animation=AnimationStyle.WAVE,
        animation_duration=0.4,
        stagger_delay=0.04
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=120
    ),
    description="Smooth wave animation flowing through words"
)


ELASTIC_BOUNCE = StylePreset(
    name="ElasticBounce",
    colors=ColorPalette(
        primary="#FF1493",  # Hot pink
        secondary="#FFFFFF",
        outline="#000000",
        emphasis="#00FFFF"
    ),
    font=FontStyle(
        family="Poppins",
        size=64,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=5,
        shadow_depth=3,
        animation=AnimationStyle.ELASTIC,
        animation_duration=0.5,
        stagger_delay=0.05
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Elastic bounce with overshoot - playful and energetic"
)


EARTHQUAKE = StylePreset(
    name="Earthquake",
    colors=ColorPalette(
        primary="#FF4500",  # Orange red
        secondary="#FFD700",
        outline="#000000",
        emphasis="#FFFF00"
    ),
    font=FontStyle(
        family="Impact",
        size=66,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=5,
        shadow_depth=4,
        animation=AnimationStyle.EARTHQUAKE,
        animation_duration=0.3,
        stagger_delay=0.03
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Violent shake effect - words appear with earthquake"
)


# === MUSIC/RHYTHM STYLES ===

BEAT_PULSE = StylePreset(
    name="BeatPulse",
    colors=ColorPalette(
        primary="#FF00FF",  # Magenta
        secondary="#00FFFF",  # Cyan
        outline="#000000",
        emphasis="#FFFF00"
    ),
    font=FontStyle(
        family="Bebas Neue",
        size=60,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=2,
        animation=AnimationStyle.PULSE,
        animation_duration=0.12,
        stagger_delay=0.08
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Pulse to the beat - perfect for music videos"
)


SOUND_WAVE = StylePreset(
    name="SoundWave",
    colors=ColorPalette(
        primary="#00FF00",  # Lime green
        secondary="#00FFFF",
        outline="#001100",
        emphasis="#FFFF00"
    ),
    font=FontStyle(
        family="Orbitron",
        size=56,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=0,
        glow=True,
        glow_intensity=8,
        animation=AnimationStyle.WAVE,
        animation_duration=0.25
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=100
    ),
    description="Visual sound wave effect - sync with audio"
)


RHYTHM_BOUNCE = StylePreset(
    name="RhythmBounce",
    colors=ColorPalette(
        primary="#FF1493",
        secondary="#FFD700",
        outline="#000000",
        emphasis="#00FFFF"
    ),
    font=FontStyle(
        family="Righteous",
        size=62,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=3,
        animation=AnimationStyle.BOUNCE,
        animation_duration=0.2,
        stagger_delay=0.06
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=120
    ),
    description="Bounce to rhythm - music video style"
)


# === CREATIVE/ARTISTIC STYLES ===

GLITCH = StylePreset(
    name="Glitch",
    colors=ColorPalette(
        primary="#FF00FF",
        secondary="#00FFFF",
        outline="#FF0000",
        emphasis="#00FF00"
    ),
    font=FontStyle(
        family="Courier New",
        size=58,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=0,
        animation=AnimationStyle.GLITCH,
        animation_duration=0.15
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Digital glitch effect - cyberpunk aesthetic"
)


RETRO_VHS = StylePreset(
    name="RetroVHS",
    colors=ColorPalette(
        primary="#FF6B9D",  # Pink
        secondary="#C0A0FF",  # Purple
        outline="#000000",
        emphasis="#FFD700"
    ),
    font=FontStyle(
        family="VT323",
        size=64,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=2,
        animation=AnimationStyle.FADE,
        animation_duration=0.3
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=100
    ),
    description="80s VHS aesthetic - retro nostalgia"
)


HOLOGRAM = StylePreset(
    name="Hologram",
    colors=ColorPalette(
        primary="#00FFFF",
        secondary="#00FFFF",
        outline="#0088AA",
        emphasis="#FFFFFF"
    ),
    font=FontStyle(
        family="Orbitron",
        size=54,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=1,
        shadow_depth=0,
        glow=True,
        glow_intensity=10,
        animation=AnimationStyle.FLOAT,
        animation_duration=0.4
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Futuristic hologram projection effect"
)


GRAFFITI = StylePreset(
    name="Graffiti",
    colors=ColorPalette(
        primary="#FF4500",
        secondary="#FFD700",
        outline="#000000",
        emphasis="#00FF00"
    ),
    font=FontStyle(
        family="Permanent Marker",
        size=68,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=6,
        shadow_depth=4,
        animation=AnimationStyle.SLIDE_UP,
        animation_duration=0.25,
        stagger_delay=0.05
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Street art graffiti style - urban aesthetic"
)


HANDWRITTEN = StylePreset(
    name="Handwritten",
    colors=ColorPalette(
        primary="#2C3E50",  # Dark gray
        secondary="#34495E",
        outline="#ECF0F1",
        emphasis="#E74C3C"  # Red
    ),
    font=FontStyle(
        family="Caveat",
        size=62,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=1,
        animation=AnimationStyle.TYPEWRITER,
        animation_duration=0.08
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=100
    ),
    description="Handwritten note style - personal touch"
)


# === ANIMATION STYLES ===

SLIDE_DOWN = StylePreset(
    name="SlideDown",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#FFFFFF",
        outline="#000000",
        emphasis="#FFD700"
    ),
    font=FontStyle(
        family="Roboto",
        size=56,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=2,
        animation=AnimationStyle.SLIDE_DOWN,
        animation_duration=0.3,
        stagger_delay=0.05
    ),
    position=PositionConfig(
        alignment="center",
        vertical="top",
        margin_top=80
    ),
    description="Slides down from top - elegant entry"
)


FLIP_IN = StylePreset(
    name="FlipIn",
    colors=ColorPalette(
        primary="#9B59B6",  # Purple
        secondary="#E74C3C",  # Red
        outline="#000000",
        emphasis="#F1C40F"  # Yellow
    ),
    font=FontStyle(
        family="Montserrat",
        size=60,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=3,
        animation=AnimationStyle.FLIP,
        animation_duration=0.4,
        stagger_delay=0.06
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="3D flip animation - dynamic entrance"
)


ROTATE_IN = StylePreset(
    name="RotateIn",
    colors=ColorPalette(
        primary="#3498DB",  # Blue
        secondary="#2ECC71",  # Green
        outline="#000000",
        emphasis="#E67E22"  # Orange
    ),
    font=FontStyle(
        family="Raleway",
        size=58,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=2,
        animation=AnimationStyle.ROTATE,
        animation_duration=0.35,
        stagger_delay=0.05
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=110
    ),
    description="Rotate and zoom in - spinning entrance"
)


BLUR_FOCUS = StylePreset(
    name="BlurFocus",
    colors=ColorPalette(
        primary="#ECF0F1",  # Light gray
        secondary="#BDC3C7",
        outline="#2C3E50",  # Dark blue
        emphasis="#E74C3C"
    ),
    font=FontStyle(
        family="Lato",
        size=54,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=1,
        blur=8,
        animation=AnimationStyle.BLUR_FOCUS,
        animation_duration=0.5
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=100
    ),
    description="Blur to sharp focus - cinematic effect"
)


NOIR_TYPEWRITER = StylePreset(
    name="NoirTypewriter",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#CCCCCC",
        outline="#000000",
        emphasis="#FF0000"
    ),
    font=FontStyle(
        family="Courier Prime",
        size=52,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=3,
        animation=AnimationStyle.TYPEWRITER,
        animation_duration=0.06
    ),
    position=PositionConfig(
        alignment="left",
        vertical="top",
        margin_top=60,
        margin_left=60
    ),
    description="Film noir typewriter - classic detective style"
)


CINEMATIC_FADE = StylePreset(
    name="CinematicFade",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#E0E0E0",
        outline="#000000",
        background="#000000"
    ),
    font=FontStyle(
        family="Crimson Text",
        size=48,
        weight="normal",
        italic=True
    ),
    effects=EffectsConfig(
        outline_width=1,
        shadow_depth=0,
        animation=AnimationStyle.FADE,
        animation_duration=0.8
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=80
    ),
    description="Elegant cinematic fade - film subtitles"
)


# === 3D/PERSPECTIVE STYLES ===

PERSPECTIVE_3D = StylePreset(
    name="Perspective3D",
    colors=ColorPalette(
        primary="#FFD700",  # Gold
        secondary="#FFA500",  # Orange
        outline="#8B4513",  # Brown
        emphasis="#FF0000"
    ),
    font=FontStyle(
        family="Bebas Neue",
        size=70,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=5,
        perspective=True,
        animation=AnimationStyle.PERSPECTIVE,
        animation_duration=0.4,
        rotation_y=15.0
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="3D perspective tilt - dramatic depth"
)


DEPTH_BLUR = StylePreset(
    name="DepthBlur",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#CCCCCC",
        outline="#000000",
        emphasis="#4A90E2"  # Blue
    ),
    font=FontStyle(
        family="Roboto",
        size=58,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=0,
        blur=5,
        animation=AnimationStyle.BLUR_FOCUS,
        animation_duration=0.6,
        perspective=True
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Depth of field with blur - DSLR camera effect"
)


FLOATING = StylePreset(
    name="Floating",
    colors=ColorPalette(
        primary="#87CEEB",  # Sky blue
        secondary="#FFFFFF",
        outline="#4682B4",  # Steel blue
        emphasis="#FFD700"
    ),
    font=FontStyle(
        family="Quicksand",
        size=56,
        weight="normal"
    ),
    effects=EffectsConfig(
        outline_width=2,
        shadow_depth=4,
        animation=AnimationStyle.FLOAT,
        animation_duration=2.0
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Gentle floating motion - dreamy atmosphere"
)


# === SPECIAL EFFECTS ===

FIRE = StylePreset(
    name="Fire",
    colors=ColorPalette(
        primary="#FF4500",  # Orange red
        secondary="#FFD700",  # Gold
        outline="#8B0000",  # Dark red
        emphasis="#FFFF00"  # Yellow
    ),
    font=FontStyle(
        family="Impact",
        size=68,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=0,
        glow=True,
        glow_intensity=12,
        animation=AnimationStyle.PULSE,
        animation_duration=0.15
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Burning fire effect - intense and hot"
)


LIGHTNING = StylePreset(
    name="Lightning",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#00FFFF",
        outline="#0000FF",
        emphasis="#FFFF00"
    ),
    font=FontStyle(
        family="Teko",
        size=64,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=0,
        glow=True,
        glow_intensity=15,
        animation=AnimationStyle.GLITCH,
        animation_duration=0.1
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Electric lightning flash - powerful energy"
)


PARTICLES = StylePreset(
    name="Particles",
    colors=ColorPalette(
        primary="#FFD700",  # Gold
        secondary="#FFA500",  # Orange
        outline="#FF4500",  # Red orange
        emphasis="#FFFFFF"
    ),
    font=FontStyle(
        family="Righteous",
        size=60,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=4,
        shadow_depth=2,
        glow=True,
        glow_intensity=8,
        animation=AnimationStyle.SCALE,
        animation_duration=0.3
    ),
    position=PositionConfig(
        alignment="center",
        vertical="bottom",
        margin_bottom=100
    ),
    description="Particle explosion effect - magical appearance"
)


SPOTLIGHT = StylePreset(
    name="Spotlight",
    colors=ColorPalette(
        primary="#FFFFFF",
        secondary="#FFFFCC",  # Light yellow
        outline="#000000",
        emphasis="#FFD700"
    ),
    font=FontStyle(
        family="Oswald",
        size=62,
        weight="bold"
    ),
    effects=EffectsConfig(
        outline_width=3,
        shadow_depth=5,
        glow=True,
        glow_intensity=6,
        animation=AnimationStyle.FADE,
        animation_duration=0.4
    ),
    position=PositionConfig(
        alignment="center",
        vertical="middle",
        margin_bottom=0
    ),
    description="Dramatic spotlight reveal - stage performance"
)


# Preset registry
PRESET_REGISTRY: Dict[str, StylePreset] = {
    # Original presets
    "viral_pop": VIRAL_POP,
    "minimal": MINIMAL,
    "karaoke": KARAOKE,
    "subtitle_classic": SUBTITLE_CLASSIC,
    "bounce": BOUNCE,
    "neon": NEON,
    
    # Viral/Social Media
    "big_bold": BIG_BOLD,
    "zoom_punch": ZOOM_PUNCH,
    "wave_motion": WAVE_MOTION,
    "elastic_bounce": ELASTIC_BOUNCE,
    "earthquake": EARTHQUAKE,
    
    # Music/Rhythm
    "beat_pulse": BEAT_PULSE,
    "sound_wave": SOUND_WAVE,
    "rhythm_bounce": RHYTHM_BOUNCE,
    
    # Creative/Artistic
    "glitch": GLITCH,
    "retro_vhs": RETRO_VHS,
    "hologram": HOLOGRAM,
    "graffiti": GRAFFITI,
    "handwritten": HANDWRITTEN,
    
    # Animation Styles
    "slide_down": SLIDE_DOWN,
    "flip_in": FLIP_IN,
    "rotate_in": ROTATE_IN,
    "blur_focus": BLUR_FOCUS,
    "noir_typewriter": NOIR_TYPEWRITER,
    "cinematic_fade": CINEMATIC_FADE,
    
    # 3D/Perspective
    "perspective_3d": PERSPECTIVE_3D,
    "depth_blur": DEPTH_BLUR,
    "floating": FLOATING,
    
    # Special Effects
    "fire": FIRE,
    "lightning": LIGHTNING,
    "particles": PARTICLES,
    "spotlight": SPOTLIGHT,
}


def get_preset(name: str) -> Optional[StylePreset]:
    """Get a preset by name."""
    return PRESET_REGISTRY.get(name.lower())


def list_presets() -> List[str]:
    """List all available presets."""
    return list(PRESET_REGISTRY.keys())
