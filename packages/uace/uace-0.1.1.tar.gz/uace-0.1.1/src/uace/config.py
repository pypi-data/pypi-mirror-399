"""
Configuration models for UACE.

Provides declarative configuration for the caption processing pipeline.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class EnginePreference(str, Enum):
    """Transcription engine preference."""
    
    SPEED = "speed"
    ACCURACY = "accuracy"
    BALANCED = "balanced"
    DIARIZATION = "diarization"
    AUTO = "auto"


class SpecificEngine(str, Enum):
    """Specific transcription engines."""
    
    FASTER_WHISPER = "faster-whisper"
    OPENAI_WHISPER = "openai-whisper"
    WHISPERX = "whisperx"
    DISTIL_WHISPER = "distil-whisper"
    CUSTOM = "custom"


class CleaningMode(str, Enum):
    """Caption cleaning modes."""
    
    NONE = "none"           # No cleaning, raw transcript
    LIGHT = "light"         # Remove fillers and events only
    BALANCED = "balanced"   # Default: fillers, events, repetitions
    AGGRESSIVE = "aggressive"  # Maximum cleaning for creator content
    CUSTOM = "custom"       # User-defined cleaning rules


class ChunkingStrategy(str, Enum):
    """Text chunking strategies."""
    
    SEMANTIC = "semantic"       # Chunk by semantic meaning
    SENTENCE = "sentence"       # Chunk by sentence boundaries
    FIXED_TIME = "fixed_time"   # Fixed time-based chunks
    WORD_COUNT = "word_count"   # Fixed word count
    PUNCTUATION = "punctuation" # Chunk on punctuation


class StylePresetName(str, Enum):
    """Built-in style presets."""
    
    # Viral/Social Media Styles
    VIRAL_POP = "viral_pop"
    BIG_BOLD = "big_bold"
    ZOOM_PUNCH = "zoom_punch"
    WAVE_MOTION = "wave_motion"
    ELASTIC_BOUNCE = "elastic_bounce"
    EARTHQUAKE = "earthquake"
    
    # Cinematic Styles
    MINIMAL = "minimal"
    SUBTITLE_CLASSIC = "subtitle_classic"
    CINEMATIC_FADE = "cinematic_fade"
    NOIR_TYPEWRITER = "noir_typewriter"
    
    # Music/Rhythm Styles
    KARAOKE = "karaoke"
    BEAT_PULSE = "beat_pulse"
    SOUND_WAVE = "sound_wave"
    RHYTHM_BOUNCE = "rhythm_bounce"
    
    # Creative/Artistic Styles
    NEON = "neon"
    GLITCH = "glitch"
    RETRO_VHS = "retro_vhs"
    HOLOGRAM = "hologram"
    GRAFFITI = "graffiti"
    HANDWRITTEN = "handwritten"
    
    # Animation Styles
    BOUNCE = "bounce"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    FLIP_IN = "flip_in"
    ROTATE_IN = "rotate_in"
    TYPEWRITER = "typewriter"
    BLUR_FOCUS = "blur_focus"
    
    # 3D/Perspective
    PERSPECTIVE_3D = "perspective_3d"
    DEPTH_BLUR = "depth_blur"
    FLOATING = "floating"
    
    # Special Effects
    FIRE = "fire"
    LIGHTNING = "lightning"
    PARTICLES = "particles"
    SPOTLIGHT = "spotlight"
    
    CUSTOM = "custom"


class ExportFormat(str, Enum):
    """Supported export formats."""
    
    ASS = "ass"         # Advanced SubStation Alpha (styled)
    SRT = "srt"         # SubRip (basic)
    VTT = "vtt"         # WebVTT
    JSON = "json"       # JSON export
    TXT = "txt"         # Plain text
    FCPXML = "fcpxml"   # Final Cut Pro XML


class TranscriptionConfig(BaseModel):
    """Configuration for transcription engines."""
    
    # Engine selection
    preference: EnginePreference = Field(
        default=EnginePreference.AUTO,
        description="Engine selection strategy"
    )
    specific_engine: Optional[SpecificEngine] = Field(
        default=None,
        description="Override with specific engine"
    )
    
    # Model parameters
    model: str = Field(default="base", description="Model size (tiny, base, small, medium, large)")
    language: Optional[str] = Field(default=None, description="Language code (auto-detect if None)")
    
    # Performance
    gpu: bool = Field(default=True, description="Use GPU if available")
    compute_type: str = Field(default="auto", description="Compute type (auto, float16, int8, float32)")
    batch_size: int = Field(default=16, description="Batch size for processing")
    
    # Advanced features
    diarization: bool = Field(default=False, description="Enable speaker diarization")
    word_timestamps: bool = Field(default=True, description="Generate word-level timestamps")
    
    # Quality settings
    beam_size: int = Field(default=5, description="Beam search size")
    best_of: int = Field(default=5, description="Number of candidates")
    temperature: float = Field(default=0.0, description="Sampling temperature")


class CleaningConfig(BaseModel):
    """Configuration for caption cleaning."""
    
    mode: CleaningMode = Field(default=CleaningMode.BALANCED, description="Cleaning mode")
    
    # Filler removal
    remove_fillers: bool = Field(default=True, description="Remove filler words")
    custom_fillers: List[str] = Field(
        default_factory=list,
        description="Additional filler words to remove"
    )
    
    # Sound effects and stage directions
    remove_sound_effects: bool = Field(default=True, description="Remove [sound] markers")
    remove_stage_directions: bool = Field(default=True, description="Remove (actions)")
    
    # Repetition handling
    collapse_repetitions: bool = Field(default=True, description="Collapse stutters/repeats")
    repetition_threshold: int = Field(default=2, description="Min repetitions to collapse")
    
    # Conversational normalization
    normalize_contractions: bool = Field(default=False, description="gonna -> going to")
    fix_grammar: bool = Field(default=False, description="Apply light grammar fixes")
    
    # Language-specific
    language: str = Field(default="en", description="Language for cleaning rules")
    dialect: Optional[str] = Field(default=None, description="Dialect-specific rules")
    
    # Preservation
    preserve_emphasis: bool = Field(default=True, description="Keep intentional repetition")
    preserve_punctuation: bool = Field(default=True, description="Keep sentence structure")


class ChunkingConfig(BaseModel):
    """Configuration for text chunking."""
    
    strategy: ChunkingStrategy = Field(
        default=ChunkingStrategy.SEMANTIC,
        description="Chunking strategy"
    )
    
    # Constraints
    max_chars_per_line: int = Field(default=42, description="Max characters per line")
    max_lines: int = Field(default=2, description="Max lines per segment")
    max_duration: float = Field(default=7.0, description="Max duration per segment (seconds)")
    min_duration: float = Field(default=0.5, description="Min duration per segment (seconds)")
    
    # Reading speed
    chars_per_second: float = Field(default=20.0, description="Target reading speed")
    
    # Timing
    gap_threshold: float = Field(
        default=2.0,
        description="Min gap to force new segment (seconds)"
    )
    
    # Semantic chunking
    preserve_phrases: bool = Field(default=True, description="Keep phrases intact")
    respect_punctuation: bool = Field(default=True, description="Break on punctuation")


class StylingConfig(BaseModel):
    """Configuration for caption styling."""
    
    preset: StylePresetName = Field(
        default=StylePresetName.VIRAL_POP,
        description="Style preset to use"
    )
    
    # Font settings (highly customizable)
    font_family: str = Field(default="Inter", description="Font family")
    font_file: Optional[str] = Field(default=None, description="Path to custom font file")
    font_size: int = Field(default=52, description="Font size (pixels)")
    font_weight: str = Field(default="bold", description="Font weight (normal, bold, black)")
    font_italic: bool = Field(default=False, description="Italic text")
    
    # Colors (fully customizable)
    primary_color: str = Field(default="#FFFFFF", description="Primary text color (hex)")
    secondary_color: Optional[str] = Field(default=None, description="Secondary color (hex)")
    outline_color: str = Field(default="#000000", description="Outline color (hex)")
    background_color: Optional[str] = Field(default=None, description="Background color (hex)")
    shadow_color: Optional[str] = Field(default=None, description="Shadow color (hex)")
    emphasis_color: str = Field(default="#FFD700", description="Emphasis color (hex)")
    
    # Effects (fine-tune everything)
    outline_width: int = Field(default=3, description="Outline width (pixels)")
    shadow: bool = Field(default=True, description="Enable shadow")
    shadow_depth: int = Field(default=2, description="Shadow depth (pixels)")
    shadow_offset_x: int = Field(default=0, description="Shadow X offset")
    shadow_offset_y: int = Field(default=0, description="Shadow Y offset")
    glow: bool = Field(default=False, description="Enable glow effect")
    glow_intensity: int = Field(default=0, description="Glow intensity (0-20)")
    blur: int = Field(default=0, description="Blur amount (0-10)")
    
    # Animation (extensive control)
    animation_style: str = Field(default="word_pop", description="Animation style")
    animation_duration: float = Field(default=0.15, description="Animation duration (seconds)")
    stagger_delay: float = Field(default=0.05, description="Delay between words (seconds)")
    
    # Advanced animation
    ease_function: str = Field(default="ease_out", description="Easing function")
    scale_start: float = Field(default=0.0, description="Starting scale for zoom animations")
    scale_end: float = Field(default=1.0, description="Ending scale")
    scale_overshoot: float = Field(default=1.2, description="Overshoot scale (for elastic)")
    rotation_start: float = Field(default=0.0, description="Starting rotation (degrees)")
    rotation_end: float = Field(default=0.0, description="Ending rotation (degrees)")
    
    # Position (precise control)
    position: str = Field(default="bottom_center", description="Caption position")
    alignment: str = Field(default="center", description="Text alignment (left, center, right)")
    vertical_position: str = Field(default="bottom", description="Vertical position (top, middle, bottom)")
    margin_left: int = Field(default=0, description="Left margin (pixels)")
    margin_right: int = Field(default=0, description="Right margin (pixels)")
    margin_top: int = Field(default=0, description="Top margin (pixels)")
    margin_bottom: int = Field(default=100, description="Bottom margin (pixels)")
    
    # Layout
    max_width_percent: int = Field(default=90, description="Max width as % of screen")
    line_spacing: float = Field(default=1.0, description="Line spacing multiplier")
    letter_spacing: int = Field(default=0, description="Letter spacing (pixels)")
    
    # Emphasis
    auto_emphasis: bool = Field(default=True, description="Auto-detect words to emphasize")
    emphasis_words: List[str] = Field(default_factory=list, description="Specific words to emphasize")
    emphasis_scale: float = Field(default=1.1, description="Scale multiplier for emphasized words")
    emphasis_animation: Optional[str] = Field(default=None, description="Special animation for emphasized words")
    
    # Karaoke mode
    karaoke_mode: bool = Field(default=False, description="Enable karaoke-style timing")
    karaoke_fill_color: str = Field(default="#FFD700", description="Karaoke fill color")
    
    # 3D Effects
    perspective: bool = Field(default=False, description="Enable 3D perspective")
    perspective_depth: int = Field(default=1000, description="Perspective depth (pixels)")
    rotation_x: float = Field(default=0.0, description="3D rotation X axis (degrees)")
    rotation_y: float = Field(default=0.0, description="3D rotation Y axis (degrees)")
    rotation_z: float = Field(default=0.0, description="3D rotation Z axis (degrees)")
    
    # Advanced effects
    text_transform: str = Field(default="none", description="Text transform (none, uppercase, lowercase, capitalize)")
    opacity: float = Field(default=1.0, description="Text opacity (0.0-1.0)")
    background_opacity: float = Field(default=0.8, description="Background opacity if enabled")
    background_padding: int = Field(default=10, description="Background padding (pixels)")
    background_radius: int = Field(default=0, description="Background border radius (pixels)")
    
    # Special effects
    stroke_style: str = Field(default="solid", description="Stroke style (solid, dashed, dotted)")
    gradient_enabled: bool = Field(default=False, description="Enable gradient fill")
    gradient_start: Optional[str] = Field(default=None, description="Gradient start color")
    gradient_end: Optional[str] = Field(default=None, description="Gradient end color")
    gradient_angle: int = Field(default=0, description="Gradient angle (degrees)")


class ExportConfig(BaseModel):
    """Configuration for caption export."""
    
    format: ExportFormat = Field(default=ExportFormat.ASS, description="Export format")
    output_path: Optional[str] = Field(default=None, description="Output file path")
    
    # Format-specific options
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    include_styles: bool = Field(default=True, description="Include style information")
    
    # Video integration
    embed_in_video: bool = Field(default=False, description="Burn captions into video")
    video_resolution: Optional[tuple[int, int]] = Field(
        default=None,
        description="Video resolution (width, height)"
    )
    
    # Quality
    preserve_timing: bool = Field(default=True, description="Preserve exact timing")
    optimize_filesize: bool = Field(default=False, description="Optimize output size")


class ProcessingConfig(BaseModel):
    """
    Complete configuration for the UACE processing pipeline.
    
    This is the main configuration object used by CaptionEngine.
    """
    
    # Sub-configs
    transcription: TranscriptionConfig = Field(default_factory=TranscriptionConfig)
    cleaning: CleaningConfig = Field(default_factory=CleaningConfig)
    chunking: ChunkingConfig = Field(default_factory=ChunkingConfig)
    styling: StylingConfig = Field(default_factory=StylingConfig)
    export: ExportConfig = Field(default_factory=ExportConfig)
    
    # Global settings
    audio_file: Optional[str] = Field(default=None, description="Input audio file")
    video_file: Optional[str] = Field(default=None, description="Input video file")
    
    # Performance
    num_workers: int = Field(default=1, description="Number of worker threads")
    cache_enabled: bool = Field(default=True, description="Enable result caching")
    
    # Debugging
    verbose: bool = Field(default=False, description="Verbose output")
    save_intermediate: bool = Field(default=False, description="Save intermediate results")
    
    @classmethod
    def quick(
        cls,
        cleaning: CleaningMode = CleaningMode.BALANCED,
        style: StylePresetName = StylePresetName.VIRAL_POP,
        **kwargs: Any
    ) -> "ProcessingConfig":
        """
        Create a quick configuration with sensible defaults.
        
        Args:
            cleaning: Cleaning mode to use
            style: Style preset to use
            **kwargs: Additional overrides
            
        Returns:
            ProcessingConfig instance
        """
        config = cls(**kwargs)
        config.cleaning.mode = cleaning
        config.styling.preset = style
        return config
    
    @classmethod
    def fast(cls, **kwargs: Any) -> "ProcessingConfig":
        """Fast processing configuration (speed over quality)."""
        config = cls(**kwargs)
        config.transcription.preference = EnginePreference.SPEED
        config.transcription.model = "tiny"
        config.transcription.word_timestamps = False
        config.cleaning.mode = CleaningMode.LIGHT
        return config
    
    @classmethod
    def accurate(cls, **kwargs: Any) -> "ProcessingConfig":
        """Accurate processing configuration (quality over speed)."""
        config = cls(**kwargs)
        config.transcription.preference = EnginePreference.ACCURACY
        config.transcription.model = "large"
        config.transcription.beam_size = 10
        config.cleaning.mode = CleaningMode.BALANCED
        return config
