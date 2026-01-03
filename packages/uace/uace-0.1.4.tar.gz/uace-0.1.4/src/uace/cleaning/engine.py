"""
Subtitle Cleaning Engine

The core of UACE's speech refinement capability.
Transforms raw transcription into clean, readable captions.
"""

import re
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass

from uace.config import CleaningMode, CleaningConfig
from uace.models import CaptionSegment


# Language-specific filler word databases
FILLERS_DATABASE: Dict[str, Set[str]] = {
    "en": {
        # Common English fillers
        "um", "uh", "umm", "uhh", "erm", "err", "ah", "ahh",
        "hmm", "hm", "mm", "mmm", "mhm", "uh-huh", "mm-hmm",
        
        # Discourse markers (conversational)
        "like", "you know", "i mean", "kind of", "sort of",
        "basically", "actually", "literally", "honestly",
        "so yeah", "yeah so", "right", "okay",
        
        # Contractions and colloquialisms
        "kinda", "sorta", "gonna", "wanna", "gotta",
        "dunno", "lemme", "gimme", "lemme",
        "yunno", "y'know", "ya know",
    },
    "en-us": {
        # US-specific additions
        "anyways", "anyhow", "whatever", "whatnot",
        "and stuff", "or whatever", "and all that",
    },
    "en-gb": {
        # UK-specific additions
        "innit", "yeah", "right then", "you see",
        "as it were", "so to speak",
    },
    "en-ng": {
        # Nigerian English additions
        "abeg", "abi", "sha", "oya", "ehn",
        "shey", "nau", "sef",
    }
}


# Patterns for stage directions and sound effects
SOUND_EFFECT_PATTERNS = [
    r'\[.*?\]',           # [laughter], [music], [door opens]
    r'\(.*?\)',           # (background noise), (applause)
    r'\{.*?\}',           # {sound effect}
    r'<.*?>',             # <music>, <sfx>
]


# Patterns for music/sound markers
MUSIC_MARKERS = [
    r'♪.*?♪',
    r'♫.*?♫',
    r'\[music\]',
    r'\[Music\]',
    r'\(music\)',
    r'\(Music\)',
]


@dataclass
class CleaningStats:
    """Statistics from a cleaning operation."""
    
    original_length: int
    cleaned_length: int
    fillers_removed: int
    sound_effects_removed: int
    repetitions_collapsed: int
    operations_applied: List[str]
    
    @property
    def reduction_percent(self) -> float:
        """Percentage reduction in text length."""
        if self.original_length == 0:
            return 0.0
        reduction = self.original_length - self.cleaned_length
        return (reduction / self.original_length) * 100


class SubtitleCleaner:
    """
    The Subtitle Cleaning Engine.
    
    Implements UACE's speech refinement pipeline:
    1. Filler removal
    2. Sound effect removal
    3. Repetition collapsing
    4. Conversational normalization
    5. Readability optimization
    """
    
    def __init__(self, config: CleaningConfig):
        self.config = config
        self.fillers = self._build_filler_set()
        self.stats = CleaningStats(
            original_length=0,
            cleaned_length=0,
            fillers_removed=0,
            sound_effects_removed=0,
            repetitions_collapsed=0,
            operations_applied=[]
        )
    
    def _build_filler_set(self) -> Set[str]:
        """Build the complete set of fillers for this language/dialect."""
        fillers = set()
        
        # Base language fillers
        if self.config.language in FILLERS_DATABASE:
            fillers.update(FILLERS_DATABASE[self.config.language])
        else:
            fillers.update(FILLERS_DATABASE["en"])
        
        # Dialect-specific additions
        if self.config.dialect:
            dialect_key = f"{self.config.language}-{self.config.dialect}"
            if dialect_key in FILLERS_DATABASE:
                fillers.update(FILLERS_DATABASE[dialect_key])
        
        # Custom user fillers
        fillers.update(f.lower() for f in self.config.custom_fillers)
        
        return fillers
    
    def clean_segment(self, segment: CaptionSegment) -> CaptionSegment:
        """
        Clean a single caption segment.
        
        This is the main entry point for the cleaning pipeline.
        """
        # Store original
        if segment.raw_text is None:
            segment.raw_text = segment.text
        
        text = segment.text
        self.stats.original_length = len(text)
        
        # Apply cleaning based on mode
        if self.config.mode == CleaningMode.NONE:
            return segment
        
        # Pipeline stages
        operations = []
        
        if self.config.mode in [CleaningMode.LIGHT, CleaningMode.BALANCED, CleaningMode.AGGRESSIVE]:
            if self.config.remove_sound_effects:
                text = self._remove_sound_effects(text)
                operations.append("sound_effects")
            
            if self.config.remove_stage_directions:
                text = self._remove_stage_directions(text)
                operations.append("stage_directions")
            
            if self.config.remove_fillers:
                text = self._remove_fillers(text)
                operations.append("fillers")
        
        if self.config.mode in [CleaningMode.BALANCED, CleaningMode.AGGRESSIVE]:
            if self.config.collapse_repetitions:
                text = self._collapse_repetitions(text)
                operations.append("repetitions")
        
        if self.config.mode == CleaningMode.AGGRESSIVE:
            if self.config.normalize_contractions:
                text = self._normalize_contractions(text)
                operations.append("contractions")
            
            text = self._aggressive_cleanup(text)
            operations.append("aggressive")
        
        # Final polish
        text = self._polish_text(text)
        
        # Update segment
        segment.text = text
        segment.cleaning_applied = operations
        
        self.stats.cleaned_length = len(text)
        self.stats.operations_applied = operations
        
        return segment
    
    def _remove_sound_effects(self, text: str) -> str:
        """Remove sound effect markers like [music], (applause), etc."""
        original = text
        
        for pattern in SOUND_EFFECT_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        for pattern in MUSIC_MARKERS:
            text = re.sub(pattern, '', text)
        
        if len(text) < len(original):
            self.stats.sound_effects_removed += 1
        
        return text
    
    def _remove_stage_directions(self, text: str) -> str:
        """Remove stage directions and non-speech annotations."""
        # Common stage direction patterns
        patterns = [
            r'\*[^*]+\*',      # *laughs*, *sighs*
            r'_[^_]+_',        # _whispers_, _shouts_
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        
        return text
    
    def _remove_fillers(self, text: str) -> str:
        """
        Remove filler words intelligently.
        
        This is phrase-aware and position-aware to maintain
        conversational rhythm.
        """
        words = text.split()
        cleaned_words = []
        filler_count = 0
        
        # Multi-word filler patterns (must check first)
        multi_word_fillers = [f for f in self.fillers if ' ' in f]
        multi_word_fillers.sort(key=len, reverse=True)  # Check longest first
        
        i = 0
        while i < len(words):
            # Check for multi-word fillers
            matched = False
            for filler in multi_word_fillers:
                filler_words = filler.split()
                if i + len(filler_words) <= len(words):
                    window = ' '.join(words[i:i+len(filler_words)]).lower()
                    if window == filler:
                        filler_count += 1
                        i += len(filler_words)
                        matched = True
                        break
            
            if matched:
                continue
            
            # Check single word
            word = words[i]
            word_clean = word.lower().strip('.,!?;:')
            
            if word_clean in self.fillers:
                filler_count += 1
            else:
                cleaned_words.append(word)
            
            i += 1
        
        self.stats.fillers_removed += filler_count
        return ' '.join(cleaned_words)
    
    def _collapse_repetitions(self, text: str) -> str:
        """
        Collapse stutters and repetitions.
        
        Example: "I I I think" -> "I think"
        Example: "we we should" -> "we should"
        """
        words = text.split()
        if len(words) < 2:
            return text
        
        collapsed = [words[0]]
        repetition_count = 0
        
        for i in range(1, len(words)):
            current = words[i].lower().strip('.,!?;:')
            previous = words[i-1].lower().strip('.,!?;:')
            
            # Count consecutive identical words
            if current == previous and i + 1 < len(words):
                next_word = words[i+1].lower().strip('.,!?;:')
                # Only collapse if it repeats multiple times
                if next_word == current:
                    repetition_count += 1
                    continue
            
            collapsed.append(words[i])
        
        self.stats.repetitions_collapsed += repetition_count
        return ' '.join(collapsed)
    
    def _normalize_contractions(self, text: str) -> str:
        """
        Normalize informal contractions to formal forms.
        
        gonna -> going to
        wanna -> want to
        gotta -> got to
        """
        contractions = {
            "gonna": "going to",
            "wanna": "want to",
            "gotta": "got to",
            "hafta": "have to",
            "oughta": "ought to",
            "shoulda": "should have",
            "coulda": "could have",
            "woulda": "would have",
            "musta": "must have",
            "dunno": "don't know",
            "lemme": "let me",
            "gimme": "give me",
            "kinda": "kind of",
            "sorta": "sort of",
        }
        
        words = text.split()
        normalized = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in contractions:
                normalized.append(contractions[word_lower])
            else:
                normalized.append(word)
        
        return ' '.join(normalized)
    
    def _aggressive_cleanup(self, text: str) -> str:
        """
        Aggressive cleanup for creator-style content.
        
        Removes even more conversational elements for
        maximum readability in short-form content.
        """
        # Remove trailing discourse markers
        text = re.sub(r'\s+(right|okay|yeah)\s*$', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(so|well|now)\s+', '', text, flags=re.IGNORECASE)
        
        # Remove excessive punctuation
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)
        
        return text
    
    def _polish_text(self, text: str) -> str:
        """
        Final polish pass.
        
        - Fix spacing
        - Fix capitalization
        - Fix punctuation
        """
        # Fix multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*([.,!?;:])', r'\1', text)
        
        # Trim
        text = text.strip()
        
        # Capitalize first letter
        if text and self.config.preserve_punctuation:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        return text
    
    def clean_batch(self, segments: List[CaptionSegment]) -> List[CaptionSegment]:
        """Clean a batch of segments."""
        return [self.clean_segment(seg) for seg in segments]
    
    def get_stats(self) -> CleaningStats:
        """Get cleaning statistics."""
        return self.stats


class LanguageSpecificCleaner:
    """
    Extended cleaner with language-specific rules.
    
    Can be subclassed for specific languages/dialects.
    """
    
    def __init__(self, language: str, dialect: Optional[str] = None):
        self.language = language
        self.dialect = dialect
    
    def apply_language_rules(self, text: str) -> str:
        """Apply language-specific cleaning rules."""
        # Override in subclasses
        return text


class NigerianEnglishCleaner(LanguageSpecificCleaner):
    """Cleaner for Nigerian English."""
    
    def __init__(self):
        super().__init__("en", "ng")
    
    def apply_language_rules(self, text: str) -> str:
        """Apply Nigerian English specific rules."""
        # Preserve intentional Pidgin but clean fillers
        # This is where cultural sensitivity matters
        
        # Common Nigerian discourse markers to optionally keep
        cultural_markers = {"abeg", "abi", "sha"}
        
        # Example: could selectively preserve these in LIGHT mode
        # but remove in AGGRESSIVE mode
        
        return text
