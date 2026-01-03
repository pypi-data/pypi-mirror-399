"""
Core data models for UACE.

These models represent the data structures used throughout the caption
processing pipeline, ensuring type safety and validation.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
from datetime import timedelta


class TimeSpan(BaseModel):
    """Represents a time span with start and end times."""
    
    start: float = Field(ge=0, description="Start time in seconds")
    end: float = Field(ge=0, description="End time in seconds")
    
    @field_validator('end')
    @classmethod
    def end_after_start(cls, v: float, info) -> float:
        if 'start' in info.data and v < info.data['start']:
            raise ValueError('end must be >= start')
        return v
    
    @property
    def duration(self) -> float:
        """Duration in seconds."""
        return self.end - self.start
    
    def overlaps(self, other: "TimeSpan") -> bool:
        """Check if this timespan overlaps with another."""
        return self.start < other.end and other.start < self.end


class Word(BaseModel):
    """A single word with timing information."""
    
    text: str
    start: float
    end: float
    confidence: float = Field(default=1.0)
    
    @field_validator('confidence', mode='before')
    @classmethod
    def normalize_confidence(cls, v: float) -> float:
        """Normalize confidence scores (handle log probabilities from Whisper)."""
        if v < 0:
            # Whisper returns log probabilities, convert to probability
            import math
            v = math.exp(max(v, -10.0))  # Clamp to avoid underflow
        return max(0.0, min(1.0, v))
    
    @property
    def duration(self) -> float:
        return self.end - self.start


class CaptionSegment(BaseModel):
    """
    A single caption segment.
    
    This represents the atomic unit of a caption - a piece of text
    that appears on screen with specific timing.
    """
    
    text: str = Field(description="The caption text")
    start: float = Field(ge=0, description="Start time in seconds")
    end: float = Field(ge=0, description="End time in seconds")
    confidence: float = Field(default=1.0, description="Confidence score (normalized to 0-1)")
    speaker: Optional[str] = Field(default=None, description="Speaker identifier")
    
    @field_validator('confidence', mode='before')
    @classmethod
    def normalize_confidence(cls, v: float) -> float:
        """Normalize confidence scores (handle log probabilities from Whisper)."""
        if v < 0:
            # Whisper returns log probabilities, convert to probability
            import math
            v = math.exp(max(v, -10.0))  # Clamp to avoid underflow
        return max(0.0, min(1.0, v))
    
    # Cleaning tracking
    raw_text: Optional[str] = Field(default=None, description="Original unprocessed text")
    cleaning_applied: List[str] = Field(default_factory=list, description="Cleaning operations applied")
    
    # Word-level timing (for advanced animations)
    words: List[Word] = Field(default_factory=list, description="Word-level timing data")
    
    # Styling metadata
    style_class: Optional[str] = Field(default=None, description="Style preset identifier")
    emphasis_words: List[str] = Field(default_factory=list, description="Words to emphasize")
    
    @property
    def duration(self) -> float:
        """Duration of this segment in seconds."""
        return self.end - self.start
    
    @property
    def timespan(self) -> TimeSpan:
        """TimeSpan representation."""
        return TimeSpan(start=self.start, end=self.end)
    
    def has_words(self) -> bool:
        """Check if word-level timing is available."""
        return len(self.words) > 0


class Caption(BaseModel):
    """
    Complete caption data for a video.
    
    This is the main data structure that flows through the UACE pipeline.
    """
    
    segments: List[CaptionSegment] = Field(description="All caption segments")
    
    # Metadata
    language: str = Field(default="en", description="Language code (ISO 639-1)")
    total_duration: Optional[float] = Field(default=None, description="Total video duration")
    
    # Processing metadata
    engine_used: Optional[str] = Field(default=None, description="Transcription engine used")
    cleaning_mode: Optional[str] = Field(default=None, description="Cleaning mode applied")
    style_preset: Optional[str] = Field(default=None, description="Style preset applied")
    
    # Statistics
    word_count: Optional[int] = Field(default=None, description="Total word count")
    avg_confidence: Optional[float] = Field(default=None, description="Average confidence score")
    
    @property
    def duration(self) -> float:
        """Total duration based on segments."""
        if not self.segments:
            return 0.0
        return max(seg.end for seg in self.segments)
    
    def segment_at(self, time: float) -> Optional[CaptionSegment]:
        """Get the segment active at a specific time."""
        for seg in self.segments:
            if seg.start <= time < seg.end:
                return seg
        return None
    
    def compute_stats(self) -> None:
        """Compute and update statistics."""
        if not self.segments:
            self.word_count = 0
            self.avg_confidence = 0.0
            return
        
        total_words = sum(len(seg.text.split()) for seg in self.segments)
        self.word_count = total_words
        
        confidences = [seg.confidence for seg in self.segments]
        self.avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0


class TranscriptionResult(BaseModel):
    """
    Raw result from a transcription engine.
    
    This is the intermediate format before cleaning and styling.
    """
    
    segments: List[CaptionSegment]
    language: str = "en"
    
    # Engine-specific metadata
    engine: str = Field(description="Engine that produced this result")
    model: str = Field(description="Model identifier")
    
    # Processing info
    processing_time: Optional[float] = Field(default=None, description="Time taken to process")
    audio_duration: Optional[float] = Field(default=None, description="Duration of audio processed")
    
    # Diarization info (if available)
    speakers: Optional[List[str]] = Field(default=None, description="Detected speakers")
    speaker_timeline: Optional[Dict[str, List[TimeSpan]]] = Field(
        default=None, 
        description="Timeline of speaker segments"
    )
    
    def to_caption(self) -> Caption:
        """Convert to Caption object."""
        return Caption(
            segments=self.segments,
            language=self.language,
            engine_used=self.engine,
            total_duration=max((seg.end for seg in self.segments), default=0.0)
        )


class ProcessingPipeline(BaseModel):
    """
    Tracks the complete processing pipeline for a caption.
    
    This provides full transparency into what happened to the caption.
    """
    
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_stage(
        self, 
        name: str, 
        duration: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a processing stage."""
        stage = {
            "name": name,
            "duration": duration,
            "metadata": metadata or {}
        }
        self.stages.append(stage)
    
    @property
    def total_time(self) -> float:
        """Total processing time across all stages."""
        return sum(
            stage.get("duration", 0.0) or 0.0 
            for stage in self.stages
        )
    
    def get_stage(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific processing stage."""
        for stage in self.stages:
            if stage.get("name") == name:
                return stage
        return None
