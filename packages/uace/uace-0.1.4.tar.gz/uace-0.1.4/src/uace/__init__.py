"""
UACE - Universal Auto-Caption Engine

Words are noisy. Meaning is not.
Captions should speak clearly — and move beautifully.

UACE transforms raw speech transcription into clean, readable,
beautifully animated captions.
"""

__version__ = "1.1.0"
__author__ = "UACE Contributors"
__license__ = "MIT"

from uace.engine import CaptionEngine
from uace.config import ProcessingConfig, CleaningMode, EnginePreference
from uace.styling.presets import StylePreset
from uace.models import Caption, CaptionSegment, TranscriptionResult

__all__ = [
    "CaptionEngine",
    "ProcessingConfig",
    "CleaningMode",
    "EnginePreference",
    "StylePreset",
    "Caption",
    "CaptionSegment",
    "TranscriptionResult",
]
