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
    
    VIRAL_POP = "viral_pop"
    MINIMAL = "minimal"
    KARAOKE = "karaoke"
    SUBTITLE_CLASSIC = "subtitle_classic"
    BOUNCE = "bounce"
    SLIDE_UP = "slide_up"
    TYPEWRITER = "typewriter"
    NEON = "neon"
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
    compute_type: str = Field(default="float16", description="Compute type (float16, int8, float32)")
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
    
    # Font settings
    font_family: str = Field(default="Inter", description="Font family")
    font_file: Optional[str] = Field(default=None, description="Path to font file")
    font_size: int = Field(default=52, description="Font size")
    font_weight: str = Field(default="bold", description="Font weight")
    
    # Colors
    primary_color: str = Field(default="#FFFFFF", description="Primary text color")
    outline_color: str = Field(default="#000000", description="Outline color")
    background_color: Optional[str] = Field(default=None, description="Background color")
    
    # Effects
    outline_width: int = Field(default=3, description="Outline width")
    shadow: bool = Field(default=True, description="Enable shadow")
    glow: bool = Field(default=False, description="Enable glow effect")
    
    # Animation
    animation_style: str = Field(default="word_pop", description="Animation style")
    animation_duration: float = Field(default=0.15, description="Animation duration (seconds)")
    
    # Position
    position: str = Field(default="bottom_center", description="Caption position")
    margin_bottom: int = Field(default=100, description="Bottom margin (pixels)")
    
    # Emphasis
    auto_emphasis: bool = Field(default=True, description="Auto-detect words to emphasize")
    emphasis_color: str = Field(default="#FFD700", description="Emphasis color")
    
    # Karaoke mode
    karaoke_mode: bool = Field(default=False, description="Enable karaoke-style timing")


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
