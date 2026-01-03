"""
Semantic Chunking Engine

Intelligently chunks captions for optimal readability:
- Respects semantic boundaries
- Maintains reading speed
- Preserves phrase structure
- Adapts to context
"""

import re
from typing import List, Tuple, Optional
from dataclasses import dataclass

from uace.config import ChunkingConfig, ChunkingStrategy
from uace.models import CaptionSegment


@dataclass
class ChunkConstraints:
    """Constraints for a valid chunk."""
    
    max_chars: int
    max_lines: int
    max_duration: float
    min_duration: float
    chars_per_second: float


class SemanticChunker:
    """
    Semantic text chunker.
    
    Converts time-aligned transcript segments into
    readable caption chunks that respect meaning boundaries.
    """
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
        self.constraints = ChunkConstraints(
            max_chars=config.max_chars_per_line * config.max_lines,
            max_lines=config.max_lines,
            max_duration=config.max_duration,
            min_duration=config.min_duration,
            chars_per_second=config.chars_per_second,
        )
    
    def chunk_segments(self, segments: List[CaptionSegment]) -> List[CaptionSegment]:
        """
        Chunk segments according to strategy.
        
        This is the main entry point.
        """
        if self.config.strategy == ChunkingStrategy.SEMANTIC:
            return self._semantic_chunk(segments)
        elif self.config.strategy == ChunkingStrategy.SENTENCE:
            return self._sentence_chunk(segments)
        elif self.config.strategy == ChunkingStrategy.FIXED_TIME:
            return self._fixed_time_chunk(segments)
        elif self.config.strategy == ChunkingStrategy.WORD_COUNT:
            return self._word_count_chunk(segments)
        elif self.config.strategy == ChunkingStrategy.PUNCTUATION:
            return self._punctuation_chunk(segments)
        else:
            return segments
    
    def _semantic_chunk(self, segments: List[CaptionSegment]) -> List[CaptionSegment]:
        """
        Semantic chunking - the smart default.
        
        Combines multiple strategies:
        1. Respect semantic boundaries (phrases, clauses)
        2. Maintain readability constraints
        3. Optimize for reading speed
        4. Handle timing gaps
        """
        if not segments:
            return []
        
        chunks = []
        current_chunk = []
        current_text = []
        current_start = segments[0].start
        
        for i, segment in enumerate(segments):
            # Check for large gap (forces new chunk)
            if current_chunk and segment.start - current_chunk[-1].end > self.config.gap_threshold:
                if current_text:
                    chunks.append(self._create_chunk(current_chunk, current_text, current_start))
                    current_chunk = []
                    current_text = []
                    current_start = segment.start
            
            # Add segment to current chunk
            current_chunk.append(segment)
            current_text.append(segment.text)
            
            combined_text = ' '.join(current_text)
            duration = segment.end - current_start
            
            # Check if we should finalize this chunk
            should_break = False
            
            # Constraint checks
            if len(combined_text) > self.constraints.max_chars:
                should_break = True
            elif duration > self.constraints.max_duration:
                should_break = True
            elif self._should_break_at_boundary(combined_text):
                should_break = True
            
            # Look ahead for natural break
            if should_break or i == len(segments) - 1:
                chunks.append(self._create_chunk(current_chunk, current_text, current_start))
                current_chunk = []
                current_text = []
                if i < len(segments) - 1:
                    current_start = segments[i + 1].start
        
        # Finalize any remaining chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, current_text, current_start))
        
        # Post-process: split lines if needed
        return self._split_long_lines(chunks)
    
    def _should_break_at_boundary(self, text: str) -> bool:
        """
        Determine if text ends at a natural semantic boundary.
        """
        if not self.config.respect_punctuation:
            return False
        
        # Strong boundaries (always break)
        if re.search(r'[.!?]\s*$', text):
            return True
        
        # Medium boundaries (break if approaching constraints)
        if re.search(r'[,;:]\s*$', text) and len(text) > self.constraints.max_chars * 0.7:
            return True
        
        # Conjunction boundaries (natural pause points)
        conjunctions = ['and', 'but', 'or', 'so', 'yet', 'for', 'nor']
        words = text.split()
        if words and words[-1].lower() in conjunctions and len(text) > self.constraints.max_chars * 0.6:
            return True
        
        return False
    
    def _create_chunk(
        self,
        segments: List[CaptionSegment],
        texts: List[str],
        start: float
    ) -> CaptionSegment:
        """Create a single chunk from multiple segments."""
        if not segments:
            raise ValueError("Cannot create chunk from empty segments")
        
        combined_text = ' '.join(texts)
        end = segments[-1].end
        
        # Compute average confidence
        avg_confidence = sum(seg.confidence for seg in segments) / len(segments)
        
        # Collect all words
        all_words = []
        for seg in segments:
            all_words.extend(seg.words)
        
        # Get speaker (if consistent)
        speakers = {seg.speaker for seg in segments if seg.speaker}
        speaker = speakers.pop() if len(speakers) == 1 else None
        
        return CaptionSegment(
            text=combined_text,
            start=start,
            end=end,
            confidence=avg_confidence,
            speaker=speaker,
            words=all_words,
            raw_text=' '.join(seg.raw_text or seg.text for seg in segments)
        )
    
    def _split_long_lines(self, chunks: List[CaptionSegment]) -> List[CaptionSegment]:
        """
        Split chunks that are too long into multiple lines.
        
        This ensures captions fit on screen properly.
        """
        result = []
        
        for chunk in chunks:
            if len(chunk.text) <= self.config.max_chars_per_line:
                result.append(chunk)
                continue
            
            # Split into multiple lines
            lines = self._split_into_lines(chunk.text)
            
            if len(lines) <= self.config.max_lines:
                # Just format as multi-line
                chunk.text = '\n'.join(lines)
                result.append(chunk)
            else:
                # Need to split into multiple chunks
                # For now, keep as single chunk but truncate
                # (In production, would split with timing)
                chunk.text = '\n'.join(lines[:self.config.max_lines])
                result.append(chunk)
        
        return result
    
    def _split_into_lines(self, text: str) -> List[str]:
        """
        Split text into lines respecting word boundaries.
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + (1 if current_line else 0)  # +1 for space
            
            if current_length + word_length > self.config.max_chars_per_line and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _sentence_chunk(self, segments: List[CaptionSegment]) -> List[CaptionSegment]:
        """Chunk by sentence boundaries."""
        # Simplified - in production would use proper sentence tokenization
        return self._semantic_chunk(segments)
    
    def _fixed_time_chunk(self, segments: List[CaptionSegment]) -> List[CaptionSegment]:
        """Chunk into fixed time intervals."""
        if not segments:
            return []
        
        chunks = []
        chunk_duration = self.config.max_duration
        
        current_chunk = []
        current_start = segments[0].start
        
        for segment in segments:
            if segment.end - current_start > chunk_duration and current_chunk:
                chunks.append(self._create_chunk(
                    current_chunk,
                    [seg.text for seg in current_chunk],
                    current_start
                ))
                current_chunk = []
                current_start = segment.start
            
            current_chunk.append(segment)
        
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk,
                [seg.text for seg in current_chunk],
                current_start
            ))
        
        return chunks
    
    def _word_count_chunk(self, segments: List[CaptionSegment]) -> List[CaptionSegment]:
        """Chunk by fixed word count."""
        target_words = 8  # Optimal for reading
        
        chunks = []
        current_chunk = []
        word_count = 0
        
        for segment in segments:
            current_chunk.append(segment)
            word_count += len(segment.text.split())
            
            if word_count >= target_words:
                chunks.append(self._create_chunk(
                    current_chunk,
                    [seg.text for seg in current_chunk],
                    current_chunk[0].start
                ))
                current_chunk = []
                word_count = 0
        
        if current_chunk:
            chunks.append(self._create_chunk(
                current_chunk,
                [seg.text for seg in current_chunk],
                current_chunk[0].start
            ))
        
        return chunks
    
    def _punctuation_chunk(self, segments: List[CaptionSegment]) -> List[CaptionSegment]:
        """Chunk strictly on punctuation boundaries."""
        # Combine all text first
        all_text = ' '.join(seg.text for seg in segments)
        
        # Split on sentence-ending punctuation
        sentences = re.split(r'([.!?]+)', all_text)
        
        # Reconstruct with punctuation
        combined = []
        for i in range(0, len(sentences), 2):
            if i < len(sentences):
                text = sentences[i]
                if i + 1 < len(sentences):
                    text += sentences[i + 1]
                combined.append(text.strip())
        
        # Map back to segments (simplified)
        # In production would preserve exact timing
        return self._semantic_chunk(segments)


class ReadabilityOptimizer:
    """
    Optimizes caption chunks for maximum readability.
    
    Applies research-backed rules for caption display.
    """
    
    @staticmethod
    def optimize_chunk(chunk: CaptionSegment, constraints: ChunkConstraints) -> CaptionSegment:
        """
        Optimize a single chunk for readability.
        
        Rules:
        - 42 chars per line maximum (research-backed)
        - 2 lines maximum
        - 20 chars/second reading speed
        - Natural phrase breaks
        """
        text = chunk.text
        
        # Check if timing allows reading
        chars = len(text)
        duration = chunk.duration
        reading_speed = chars / duration if duration > 0 else 0
        
        # If too fast, split chunk (user can't read it)
        if reading_speed > constraints.chars_per_second * 1.5:
            # Mark for split
            pass
        
        return chunk
