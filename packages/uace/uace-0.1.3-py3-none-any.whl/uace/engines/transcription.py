"""
Transcription Engine Abstraction

Provides a unified interface to multiple transcription backends:
- faster-whisper (default, fastest)
- OpenAI Whisper (maximum accuracy)
- WhisperX (advanced alignment + diarization)
- Distil-Whisper (ultra-fast CPU)
- Custom engines
"""

import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path

from uace.models import TranscriptionResult, CaptionSegment, Word
from uace.config import TranscriptionConfig, EnginePreference, SpecificEngine


class TranscriptionEngine(ABC):
    """
    Abstract base class for transcription engines.
    
    All transcription backends must implement this interface.
    """
    
    def __init__(self, config: TranscriptionConfig):
        self.config = config
        self.model_loaded = False
    
    @abstractmethod
    def load_model(self) -> None:
        """Load the transcription model."""
        pass
    
    @abstractmethod
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            TranscriptionResult with segments and metadata
        """
        pass
    
    @abstractmethod
    def supports_diarization(self) -> bool:
        """Check if this engine supports speaker diarization."""
        pass
    
    @abstractmethod
    def supports_word_timestamps(self) -> bool:
        """Check if this engine supports word-level timestamps."""
        pass
    
    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if this engine's dependencies are available."""
        pass
    
    @classmethod
    @abstractmethod
    def engine_name(cls) -> str:
        """Get the engine identifier."""
        pass


class FasterWhisperEngine(TranscriptionEngine):
    """
    faster-whisper engine implementation.
    
    This is the default engine - fastest and most efficient.
    """
    
    def __init__(self, config: TranscriptionConfig):
        super().__init__(config)
        self.model = None
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if faster-whisper is installed."""
        try:
            import faster_whisper
            return True
        except ImportError:
            return False
    
    @classmethod
    def engine_name(cls) -> str:
        return "faster-whisper"
    
    def load_model(self) -> None:
        """Load faster-whisper model."""
        if self.model_loaded:
            return
        
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError(
                "faster-whisper not installed. Install with: pip install faster-whisper"
            )
        
        device = "cuda" if self.config.gpu else "cpu"
        
        # Auto-detect compute type based on device
        compute_type = self.config.compute_type
        if compute_type == "auto":
            if device == "cuda":
                compute_type = "float16"  # GPU supports float16
            else:
                compute_type = "int8"  # CPU works best with int8
        
        # Validate compute type for device
        if device == "cpu" and compute_type == "float16":
            # CPU doesn't support efficient float16, fallback to int8
            compute_type = "int8"
            print("⚠️  float16 not supported on CPU, using int8")
        
        self.model = WhisperModel(
            self.config.model,
            device=device,
            compute_type=compute_type,
        )
        
        self.model_loaded = True
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using faster-whisper."""
        if not self.model_loaded:
            self.load_model()
        
        start_time = time.time()
        
        segments_iter, info = self.model.transcribe(
            audio_path,
            language=self.config.language,
            beam_size=self.config.beam_size,
            word_timestamps=self.config.word_timestamps,
            temperature=self.config.temperature,
        )
        
        segments = []
        
        for segment in segments_iter:
            words = []
            if self.config.word_timestamps and hasattr(segment, 'words'):
                words = [
                    Word(
                        text=word.word,
                        start=word.start,
                        end=word.end,
                        confidence=word.probability  # Validator will normalize
                    )
                    for word in segment.words
                ]
            
            # Get confidence (avg_logprob may be negative, validator will normalize)
            confidence = getattr(segment, 'avg_logprob', 0.0)
            
            cap_segment = CaptionSegment(
                text=segment.text.strip(),
                start=segment.start,
                end=segment.end,
                confidence=confidence,  # Validator will handle negative values
                words=words
            )
            segments.append(cap_segment)
        
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            segments=segments,
            language=info.language if hasattr(info, 'language') else self.config.language or "en",
            engine=self.engine_name(),
            model=self.config.model,
            processing_time=processing_time,
            audio_duration=info.duration if hasattr(info, 'duration') else None,
        )
    
    def supports_diarization(self) -> bool:
        return False
    
    def supports_word_timestamps(self) -> bool:
        return True


class WhisperXEngine(TranscriptionEngine):
    """
    WhisperX engine implementation.
    
    Provides advanced features:
    - Forced phoneme alignment
    - Speaker diarization
    - Enhanced word-level timing
    """
    
    def __init__(self, config: TranscriptionConfig):
        super().__init__(config)
        self.model = None
        self.align_model = None
        self.diarize_pipeline = None
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if WhisperX is installed."""
        try:
            import whisperx
            return True
        except ImportError:
            return False
    
    @classmethod
    def engine_name(cls) -> str:
        return "whisperx"
    
    def load_model(self) -> None:
        """Load WhisperX models."""
        if self.model_loaded:
            return
        
        try:
            import whisperx
        except ImportError:
            raise ImportError(
                "WhisperX not installed. Install with: pip install whisperx"
            )
        
        device = "cuda" if self.config.gpu else "cpu"
        compute_type = self.config.compute_type
        
        # Load transcription model
        self.model = whisperx.load_model(
            self.config.model,
            device=device,
            compute_type=compute_type
        )
        
        self.model_loaded = True
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using WhisperX with alignment and optional diarization."""
        if not self.model_loaded:
            self.load_model()
        
        import whisperx
        
        start_time = time.time()
        device = "cuda" if self.config.gpu else "cpu"
        
        # Load audio
        audio = whisperx.load_audio(audio_path)
        
        # Transcribe
        result = self.model.transcribe(
            audio,
            batch_size=self.config.batch_size,
            language=self.config.language
        )
        
        language = result.get("language", self.config.language or "en")
        
        # Load alignment model
        if not self.align_model:
            self.align_model, metadata = whisperx.load_align_model(
                language_code=language,
                device=device
            )
        
        # Align
        result = whisperx.align(
            result["segments"],
            self.align_model,
            metadata,
            audio,
            device
        )
        
        # Diarization (if requested)
        speakers = None
        if self.config.diarization:
            if not self.diarize_pipeline:
                # This requires HuggingFace token
                self.diarize_pipeline = whisperx.DiarizationPipeline(
                    device=device
                )
            
            diarize_result = self.diarize_pipeline(audio)
            result = whisperx.assign_word_speakers(diarize_result, result)
            speakers = list(set(
                seg.get("speaker")
                for seg in result["segments"]
                if seg.get("speaker")
            ))
        
        # Convert to our format
        segments = []
        for segment in result["segments"]:
            words = []
            if "words" in segment:
                words = [
                    Word(
                        text=word["word"],
                        start=word["start"],
                        end=word["end"],
                        confidence=word.get("score", 1.0)  # Validator will normalize
                    )
                    for word in segment["words"]
                ]
            
            cap_segment = CaptionSegment(
                text=segment["text"].strip(),
                start=segment["start"],
                end=segment["end"],
                confidence=segment.get("score", 1.0),  # Validator will normalize
                speaker=segment.get("speaker"),
                words=words
            )
            segments.append(cap_segment)
        
        processing_time = time.time() - start_time
        
        return TranscriptionResult(
            segments=segments,
            language=language,
            engine=self.engine_name(),
            model=self.config.model,
            processing_time=processing_time,
            speakers=speakers,
        )
    
    def supports_diarization(self) -> bool:
        return True
    
    def supports_word_timestamps(self) -> bool:
        return True


class DistilWhisperEngine(TranscriptionEngine):
    """
    Distil-Whisper engine implementation.
    
    Ultra-fast CPU inference, good for real-time applications.
    """
    
    def __init__(self, config: TranscriptionConfig):
        super().__init__(config)
        self.model = None
        self.processor = None
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if transformers is installed."""
        try:
            import transformers
            return True
        except ImportError:
            return False
    
    @classmethod
    def engine_name(cls) -> str:
        return "distil-whisper"
    
    def load_model(self) -> None:
        """Load Distil-Whisper model."""
        if self.model_loaded:
            return
        
        try:
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor
            import torch
        except ImportError:
            raise ImportError(
                "transformers not installed. Install with: pip install transformers torch"
            )
        
        device = "cuda" if self.config.gpu and torch.cuda.is_available() else "cpu"
        
        model_id = f"distil-whisper/distil-{self.config.model}.en"
        
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id).to(device)
        
        self.model_loaded = True
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """Transcribe using Distil-Whisper."""
        # Simplified implementation
        # In practice, would use full pipeline with chunking
        
        raise NotImplementedError("Distil-Whisper engine implementation pending")
    
    def supports_diarization(self) -> bool:
        return False
    
    def supports_word_timestamps(self) -> bool:
        return False


class EngineSelector:
    """
    Intelligent engine selection based on requirements and availability.
    
    This is the core of UACE's engine-agnostic design.
    """
    
    @staticmethod
    def select_engine(config: TranscriptionConfig) -> TranscriptionEngine:
        """
        Select the best available engine based on config.
        
        Decision tree:
        1. If specific engine requested, use it (if available)
        2. If diarization needed, use WhisperX
        3. If GPU available, use faster-whisper
        4. If speed priority, use distil-whisper
        5. Fallback to faster-whisper CPU
        """
        # Explicit engine selection
        if config.specific_engine:
            return EngineSelector._get_specific_engine(config.specific_engine, config)
        
        # Automatic selection based on preference
        if config.preference == EnginePreference.DIARIZATION:
            if WhisperXEngine.is_available():
                return WhisperXEngine(config)
            raise RuntimeError("Diarization requested but WhisperX not available")
        
        if config.preference == EnginePreference.SPEED:
            # Try distil first for CPU speed
            if not config.gpu and DistilWhisperEngine.is_available():
                return DistilWhisperEngine(config)
            # Otherwise faster-whisper is fastest
            if FasterWhisperEngine.is_available():
                return FasterWhisperEngine(config)
        
        if config.preference == EnginePreference.ACCURACY:
            # WhisperX provides best alignment
            if WhisperXEngine.is_available():
                return WhisperXEngine(config)
            # Fallback to faster-whisper with large model
            if FasterWhisperEngine.is_available():
                config.model = "large"
                return FasterWhisperEngine(config)
        
        # Default/Balanced: faster-whisper
        if FasterWhisperEngine.is_available():
            return FasterWhisperEngine(config)
        
        # Try any available engine
        for engine_class in [WhisperXEngine, DistilWhisperEngine]:
            if engine_class.is_available():
                return engine_class(config)
        
        raise RuntimeError(
            "No transcription engine available. "
            "Install at least one: faster-whisper, whisperx, or transformers"
        )
    
    @staticmethod
    def _get_specific_engine(
        engine: SpecificEngine,
        config: TranscriptionConfig
    ) -> TranscriptionEngine:
        """Get a specific engine by name."""
        engine_map = {
            SpecificEngine.FASTER_WHISPER: FasterWhisperEngine,
            SpecificEngine.WHISPERX: WhisperXEngine,
            SpecificEngine.DISTIL_WHISPER: DistilWhisperEngine,
        }
        
        engine_class = engine_map.get(engine)
        if not engine_class:
            raise ValueError(f"Unknown engine: {engine}")
        
        if not engine_class.is_available():
            raise RuntimeError(
                f"{engine.value} not available. "
                f"Install dependencies for this engine."
            )
        
        return engine_class(config)
    
    @staticmethod
    def get_available_engines() -> List[str]:
        """Get list of available engines."""
        available = []
        
        for engine_class in [FasterWhisperEngine, WhisperXEngine, DistilWhisperEngine]:
            if engine_class.is_available():
                available.append(engine_class.engine_name())
        
        return available
