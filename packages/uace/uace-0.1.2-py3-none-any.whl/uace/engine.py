"""
UACE Caption Engine

The main entry point for the UACE pipeline.
This is what users interact with.
"""

import time
from pathlib import Path
from typing import Optional, Union
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from uace.config import ProcessingConfig, CleaningMode, ExportFormat
from uace.models import Caption, ProcessingPipeline, TranscriptionResult
from uace.engines.transcription import EngineSelector
from uace.cleaning.engine import SubtitleCleaner
from uace.chunking.semantic import SemanticChunker
from uace.styling.presets import get_preset, VIRAL_POP
from uace.export.formats import ASSExporter, SRTExporter, VTTExporter


class CaptionEngine:
    """
    Universal Auto-Caption Engine
    
    The complete pipeline: Transcribe → Clean → Chunk → Style → Export
    
    Examples:
        # Simple usage
        >>> engine = CaptionEngine()
        >>> engine.process("video.mp4", output="captions.ass")
        
        # Custom configuration
        >>> config = ProcessingConfig.quick(
        ...     cleaning=CleaningMode.AGGRESSIVE,
        ...     style="viral_pop"
        ... )
        >>> engine = CaptionEngine(config)
        >>> engine.process("video.mp4")
        
        # Advanced control
        >>> config = ProcessingConfig()
        >>> config.transcription.diarization = True
        >>> config.cleaning.mode = CleaningMode.BALANCED
        >>> engine = CaptionEngine(config)
        >>> caption = engine.process_audio("podcast.mp3")
    """
    
    def __init__(
        self,
        config: Optional[ProcessingConfig] = None,
        verbose: bool = False
    ):
        """
        Initialize Caption Engine.
        
        Args:
            config: Processing configuration (uses defaults if None)
            verbose: Enable verbose output
        """
        self.config = config or ProcessingConfig()
        self.verbose = verbose or self.config.verbose
        self.console = Console() if self.verbose else None
        self.pipeline = ProcessingPipeline()
        
        # Components (lazy-loaded)
        self._transcription_engine = None
        self._cleaner = None
        self._chunker = None
    
    def process(
        self,
        input_file: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
        **overrides
    ) -> Caption:
        """
        Process a video or audio file end-to-end.
        
        This is the main entry point for most users.
        
        Args:
            input_file: Path to video or audio file
            output: Output file path (auto-generated if None)
            **overrides: Override config parameters
            
        Returns:
            Caption object with all segments
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Apply overrides
        self._apply_overrides(**overrides)
        
        # Determine if video or audio
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
        video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        
        suffix = input_path.suffix.lower()
        
        if suffix in audio_extensions:
            return self.process_audio(str(input_path), output)
        elif suffix in video_extensions:
            return self.process_video(str(input_path), output)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def process_video(
        self,
        video_file: str,
        output: Optional[str] = None
    ) -> Caption:
        """
        Process a video file.
        
        Extracts audio, then processes as audio.
        """
        if self.verbose:
            self.console.print("[bold blue]Processing video...[/bold blue]")
        
        # Extract audio (would use ffmpeg in production)
        audio_file = self._extract_audio(video_file)
        
        # Process audio
        caption = self.process_audio(audio_file, output)
        
        # Clean up temp audio if created
        # (implementation detail)
        
        return caption
    
    def process_audio(
        self,
        audio_file: str,
        output: Optional[str] = None
    ) -> Caption:
        """
        Process an audio file through the complete pipeline.
        
        Pipeline stages:
        1. Transcription
        2. Cleaning
        3. Chunking
        4. Styling (metadata only)
        5. Export
        """
        if self.verbose:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                TimeElapsedColumn(),
                console=self.console
            )
            progress.start()
            task = progress.add_task("Processing", total=5)
        
        # Stage 1: Transcription
        if self.verbose:
            progress.update(task, description="Transcribing audio...", completed=1)
        
        transcription = self._transcribe(audio_file)
        
        # Stage 2: Cleaning
        if self.verbose:
            progress.update(task, description="Cleaning transcript...", completed=2)
        
        caption = self._clean(transcription)
        
        # Stage 3: Chunking
        if self.verbose:
            progress.update(task, description="Optimizing chunks...", completed=3)
        
        caption = self._chunk(caption)
        
        # Stage 4: Styling (metadata)
        if self.verbose:
            progress.update(task, description="Applying styling...", completed=4)
        
        caption = self._style(caption)
        
        # Stage 5: Export
        if output:
            if self.verbose:
                progress.update(task, description="Exporting...", completed=5)
            
            self.export(caption, output)
        
        if self.verbose:
            progress.stop()
            self._print_summary(caption)
        
        return caption
    
    def _transcribe(self, audio_file: str) -> TranscriptionResult:
        """Transcription stage."""
        start_time = time.time()
        
        # Get or create engine
        if not self._transcription_engine:
            self._transcription_engine = EngineSelector.select_engine(
                self.config.transcription
            )
        
        # Transcribe
        result = self._transcription_engine.transcribe(audio_file)
        
        # Track in pipeline
        self.pipeline.add_stage(
            "transcription",
            duration=time.time() - start_time,
            metadata={
                "engine": result.engine,
                "model": result.model,
                "language": result.language,
                "segments": len(result.segments)
            }
        )
        
        return result
    
    def _clean(self, transcription: TranscriptionResult) -> Caption:
        """Cleaning stage."""
        start_time = time.time()
        
        # Get or create cleaner
        if not self._cleaner:
            self._cleaner = SubtitleCleaner(self.config.cleaning)
        
        # Convert to caption
        caption = transcription.to_caption()
        
        # Clean segments
        caption.segments = self._cleaner.clean_batch(caption.segments)
        caption.cleaning_mode = self.config.cleaning.mode.value
        
        # Compute stats
        caption.compute_stats()
        
        # Track in pipeline
        stats = self._cleaner.get_stats()
        self.pipeline.add_stage(
            "cleaning",
            duration=time.time() - start_time,
            metadata={
                "mode": self.config.cleaning.mode.value,
                "reduction": f"{stats.reduction_percent:.1f}%",
                "fillers_removed": stats.fillers_removed,
                "operations": stats.operations_applied
            }
        )
        
        return caption
    
    def _chunk(self, caption: Caption) -> Caption:
        """Chunking stage."""
        start_time = time.time()
        
        # Get or create chunker
        if not self._chunker:
            self._chunker = SemanticChunker(self.config.chunking)
        
        # Chunk segments
        caption.segments = self._chunker.chunk_segments(caption.segments)
        
        # Track in pipeline
        self.pipeline.add_stage(
            "chunking",
            duration=time.time() - start_time,
            metadata={
                "strategy": self.config.chunking.strategy.value,
                "final_segments": len(caption.segments)
            }
        )
        
        return caption
    
    def _style(self, caption: Caption) -> Caption:
        """Styling stage (metadata only, actual rendering happens at export)."""
        start_time = time.time()
        
        # Get preset - handle both enum and string
        preset_name = self.config.styling.preset
        if hasattr(preset_name, 'value'):
            preset_name = preset_name.value
        
        preset = get_preset(preset_name)
        if not preset:
            preset = VIRAL_POP
        
        # Store style info in caption
        caption.style_preset = preset.name
        
        # Auto-emphasis detection (if enabled)
        if self.config.styling.auto_emphasis:
            for segment in caption.segments:
                segment.emphasis_words = self._detect_emphasis_words(segment.text)
        
        # Track in pipeline
        self.pipeline.add_stage(
            "styling",
            duration=time.time() - start_time,
            metadata={
                "preset": preset.name,
                "animation": self.config.styling.animation_style
            }
        )
        
        return caption
    
    def export(self, caption: Caption, output_path: str) -> None:
        """
        Export caption to file.
        
        Supports: ASS, SRT, VTT, JSON
        """
        output = Path(output_path)
        format_str = output.suffix.lower().lstrip('.')
        
        # Determine format
        try:
            export_format = ExportFormat(format_str)
        except ValueError:
            export_format = ExportFormat.ASS
            output = output.with_suffix('.ass')
        
        # Get preset for styling
        preset = get_preset(self.config.styling.preset.value) or VIRAL_POP
        
        # Export based on format
        if export_format == ExportFormat.ASS:
            exporter = ASSExporter(preset, self.config.export)
            exporter.export(caption, str(output))
        
        elif export_format == ExportFormat.SRT:
            exporter = SRTExporter()
            exporter.export(caption, str(output))
        
        elif export_format == ExportFormat.VTT:
            exporter = VTTExporter()
            exporter.export(caption, str(output))
        
        elif export_format == ExportFormat.JSON:
            self._export_json(caption, str(output))
        
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        if self.verbose:
            self.console.print(f"[green]✓ Exported to: {output}[/green]")
    
    def _export_json(self, caption: Caption, output_path: str) -> None:
        """Export caption as JSON."""
        import json
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(caption.model_dump(), f, indent=2, ensure_ascii=False)
    
    def _extract_audio(self, video_file: str) -> str:
        """Extract audio from video (stub - would use ffmpeg)."""
        # In production: use ffmpeg-python
        # For now, assume video_file is actually audio or has audio stream
        return video_file
    
    def _detect_emphasis_words(self, text: str) -> list[str]:
        """
        Detect words that should be emphasized.
        
        Uses simple heuristics:
        - ALL CAPS words
        - Exclamations
        - Question words
        """
        words = text.split()
        emphasis = []
        
        for word in words:
            clean_word = word.strip('.,!?;:')
            
            # All caps (but not single letter)
            if clean_word.isupper() and len(clean_word) > 1:
                emphasis.append(word)
            
            # Words with exclamation
            if '!' in word:
                emphasis.append(word)
        
        return emphasis
    
    def _apply_overrides(self, **overrides) -> None:
        """Apply configuration overrides."""
        for key, value in overrides.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def _print_summary(self, caption: Caption) -> None:
        """Print processing summary."""
        from rich.table import Table
        
        table = Table(title="Processing Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Segments", str(len(caption.segments)))
        table.add_row("Duration", f"{caption.duration:.2f}s")
        table.add_row("Word Count", str(caption.word_count or 0))
        table.add_row("Avg Confidence", f"{(caption.avg_confidence or 0) * 100:.1f}%")
        table.add_row("Processing Time", f"{self.pipeline.total_time:.2f}s")
        table.add_row("Engine", caption.engine_used or "unknown")
        
        self.console.print(table)


# Convenience functions

def quick_caption(
    input_file: str,
    output: Optional[str] = None,
    style: str = "viral_pop",
    cleaning: str = "balanced"
) -> Caption:
    """
    Quick caption generation with sensible defaults.
    
    Args:
        input_file: Video or audio file
        output: Output path (auto-generated if None)
        style: Style preset name
        cleaning: Cleaning mode
        
    Returns:
        Caption object
    """
    config = ProcessingConfig.quick()
    config.styling.preset = style
    config.cleaning.mode = CleaningMode(cleaning)
    
    engine = CaptionEngine(config)
    return engine.process(input_file, output)
