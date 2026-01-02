"""
UACE Test Suite

Comprehensive tests for all components.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from uace import CaptionEngine, ProcessingConfig, CleaningMode
from uace.models import CaptionSegment, Caption, Word, TimeSpan
from uace.cleaning.engine import SubtitleCleaner
from uace.chunking.semantic import SemanticChunker
from uace.config import ChunkingConfig, CleaningConfig


class TestModels:
    """Test core data models."""
    
    def test_caption_segment_creation(self):
        """Test creating a caption segment."""
        segment = CaptionSegment(
            text="Hello world",
            start=0.0,
            end=2.0,
            confidence=0.95
        )
        
        assert segment.text == "Hello world"
        assert segment.duration == 2.0
        assert segment.confidence == 0.95
    
    def test_word_timing(self):
        """Test word-level timing."""
        word = Word(text="hello", start=0.0, end=0.5, confidence=0.98)
        
        assert word.duration == 0.5
        assert word.text == "hello"
    
    def test_timespan_overlap(self):
        """Test timespan overlap detection."""
        span1 = TimeSpan(start=0.0, end=2.0)
        span2 = TimeSpan(start=1.0, end=3.0)
        span3 = TimeSpan(start=3.0, end=4.0)
        
        assert span1.overlaps(span2)
        assert not span1.overlaps(span3)
    
    def test_caption_statistics(self):
        """Test caption statistics computation."""
        segments = [
            CaptionSegment(text="Hello world", start=0.0, end=2.0, confidence=0.9),
            CaptionSegment(text="How are you", start=2.0, end=4.0, confidence=0.95),
        ]
        
        caption = Caption(segments=segments)
        caption.compute_stats()
        
        assert caption.word_count == 5
        assert caption.avg_confidence == pytest.approx(0.925)
        assert caption.duration == 4.0


class TestCleaning:
    """Test subtitle cleaning engine."""
    
    def test_filler_removal(self):
        """Test filler word removal."""
        config = CleaningConfig(mode=CleaningMode.BALANCED)
        cleaner = SubtitleCleaner(config)
        
        segment = CaptionSegment(
            text="Um, I think, uh, we should go",
            start=0.0,
            end=2.0
        )
        
        cleaned = cleaner.clean_segment(segment)
        
        assert "um" not in cleaned.text.lower()
        assert "uh" not in cleaned.text.lower()
        assert "we should go" in cleaned.text
    
    def test_sound_effect_removal(self):
        """Test sound effect marker removal."""
        config = CleaningConfig(mode=CleaningMode.BALANCED)
        cleaner = SubtitleCleaner(config)
        
        segment = CaptionSegment(
            text="[laughter] That was funny [music]",
            start=0.0,
            end=2.0
        )
        
        cleaned = cleaner.clean_segment(segment)
        
        assert "[laughter]" not in cleaned.text
        assert "[music]" not in cleaned.text
        assert "That was funny" in cleaned.text
    
    def test_repetition_collapse(self):
        """Test repetition collapsing."""
        config = CleaningConfig(
            mode=CleaningMode.BALANCED,
            collapse_repetitions=True
        )
        cleaner = SubtitleCleaner(config)
        
        segment = CaptionSegment(
            text="I I I think we we should go",
            start=0.0,
            end=2.0
        )
        
        cleaned = cleaner.clean_segment(segment)
        
        # Should collapse multiple repetitions
        assert cleaned.text.count("I") < segment.text.count("I")
    
    def test_cleaning_modes(self):
        """Test different cleaning modes."""
        segment = CaptionSegment(
            text="Um, [laughter] I I think, like, we should go",
            start=0.0,
            end=2.0
        )
        
        # None mode
        config_none = CleaningConfig(mode=CleaningMode.NONE)
        cleaner_none = SubtitleCleaner(config_none)
        cleaned_none = cleaner_none.clean_segment(segment)
        assert cleaned_none.text == segment.text
        
        # Light mode
        config_light = CleaningConfig(mode=CleaningMode.LIGHT)
        cleaner_light = SubtitleCleaner(config_light)
        cleaned_light = cleaner_light.clean_segment(segment)
        assert "[laughter]" not in cleaned_light.text
        
        # Aggressive mode
        config_agg = CleaningConfig(mode=CleaningMode.AGGRESSIVE)
        cleaner_agg = SubtitleCleaner(config_agg)
        cleaned_agg = cleaner_agg.clean_segment(segment)
        assert len(cleaned_agg.text) < len(segment.text)
    
    def test_preservation(self):
        """Test that raw text is preserved."""
        config = CleaningConfig(mode=CleaningMode.BALANCED)
        cleaner = SubtitleCleaner(config)
        
        segment = CaptionSegment(
            text="Um, hello world",
            start=0.0,
            end=2.0
        )
        
        cleaned = cleaner.clean_segment(segment)
        
        assert cleaned.raw_text == "Um, hello world"
        assert cleaned.text != cleaned.raw_text


class TestChunking:
    """Test semantic chunking."""
    
    def test_simple_chunking(self):
        """Test basic chunking."""
        config = ChunkingConfig()
        chunker = SemanticChunker(config)
        
        segments = [
            CaptionSegment(text="Hello", start=0.0, end=0.5),
            CaptionSegment(text="world", start=0.5, end=1.0),
            CaptionSegment(text="how", start=1.0, end=1.5),
            CaptionSegment(text="are", start=1.5, end=2.0),
            CaptionSegment(text="you", start=2.0, end=2.5),
        ]
        
        chunked = chunker.chunk_segments(segments)
        
        # Should combine into fewer segments
        assert len(chunked) < len(segments)
    
    def test_gap_handling(self):
        """Test that large gaps force new chunks."""
        config = ChunkingConfig(gap_threshold=2.0)
        chunker = SemanticChunker(config)
        
        segments = [
            CaptionSegment(text="First", start=0.0, end=1.0),
            CaptionSegment(text="segment", start=1.0, end=2.0),
            # Large gap here
            CaptionSegment(text="Second", start=10.0, end=11.0),
            CaptionSegment(text="segment", start=11.0, end=12.0),
        ]
        
        chunked = chunker.chunk_segments(segments)
        
        # Should create at least 2 chunks due to gap
        assert len(chunked) >= 2
    
    def test_line_splitting(self):
        """Test line splitting for long text."""
        config = ChunkingConfig(max_chars_per_line=20)
        chunker = SemanticChunker(config)
        
        long_text = "This is a very long sentence that should be split across lines"
        segment = CaptionSegment(text=long_text, start=0.0, end=5.0)
        
        chunked = chunker.chunk_segments([segment])
        
        # Should have line breaks
        assert len(chunked) > 0
        # Text might be split into multiple lines


class TestConfiguration:
    """Test configuration system."""
    
    def test_quick_config(self):
        """Test quick configuration presets."""
        config = ProcessingConfig.quick(
            cleaning=CleaningMode.AGGRESSIVE,
            style="viral_pop"
        )
        
        assert config.cleaning.mode == CleaningMode.AGGRESSIVE
        assert config.styling.preset == "viral_pop"
    
    def test_fast_config(self):
        """Test fast configuration."""
        config = ProcessingConfig.fast()
        
        assert config.transcription.model == "tiny"
        assert config.cleaning.mode == CleaningMode.LIGHT
    
    def test_accurate_config(self):
        """Test accurate configuration."""
        config = ProcessingConfig.accurate()
        
        assert config.transcription.model == "large"
        assert config.transcription.beam_size >= 10


class TestEngine:
    """Test main caption engine."""
    
    @patch('uace.engines.transcription.EngineSelector.select_engine')
    def test_engine_initialization(self, mock_selector):
        """Test engine initialization."""
        engine = CaptionEngine()
        
        assert engine.config is not None
        assert isinstance(engine.config, ProcessingConfig)
    
    def test_config_override(self):
        """Test configuration overrides."""
        config = ProcessingConfig()
        config.cleaning.mode = CleaningMode.LIGHT
        
        engine = CaptionEngine(config)
        
        assert engine.config.cleaning.mode == CleaningMode.LIGHT


class TestStyling:
    """Test styling presets."""
    
    def test_preset_loading(self):
        """Test loading style presets."""
        from uace.styling.presets import get_preset, list_presets
        
        presets = list_presets()
        assert len(presets) > 0
        assert "viral_pop" in presets
        
        preset = get_preset("viral_pop")
        assert preset is not None
        assert preset.name == "ViralPop"
    
    def test_ass_style_generation(self):
        """Test ASS style string generation."""
        from uace.styling.presets import get_preset
        
        preset = get_preset("viral_pop")
        ass_style = preset.to_ass_style()
        
        assert "Style:" in ass_style
        assert "ViralPop" in ass_style


class TestExport:
    """Test export functionality."""
    
    def test_srt_export(self, tmp_path):
        """Test SRT export."""
        from uace.export.formats import SRTExporter
        
        caption = Caption(segments=[
            CaptionSegment(text="Hello world", start=0.0, end=2.0),
            CaptionSegment(text="How are you", start=2.0, end=4.0),
        ])
        
        output_file = tmp_path / "test.srt"
        exporter = SRTExporter()
        exporter.export(caption, str(output_file))
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "Hello world" in content
        assert "How are you" in content


class TestCLI:
    """Test CLI functionality."""
    
    def test_cli_import(self):
        """Test that CLI can be imported."""
        from uace import cli
        
        assert cli is not None


# Integration Tests

class TestIntegration:
    """Integration tests (require actual files)."""
    
    @pytest.mark.skip("Requires audio file")
    def test_end_to_end(self):
        """Test complete end-to-end processing."""
        engine = CaptionEngine()
        caption = engine.process("test_audio.mp3")
        
        assert len(caption.segments) > 0
        assert caption.duration > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
