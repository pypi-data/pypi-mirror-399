"""
Intelligent Speaker Labeling & Diarization

Advanced speaker identification with creative labeling and visual styling.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import colorsys

from uace.models import CaptionSegment


@dataclass
class SpeakerProfile:
    """Profile for a detected speaker."""
    
    id: str                    # Original ID (e.g., "SPEAKER_00")
    label: str                 # Creative label (e.g., "Host", "Guest 1")
    color: str                 # Hex color for this speaker
    emoji: str                 # Emoji representing speaker
    segment_count: int         # Number of segments
    total_duration: float      # Total speaking time
    avg_confidence: float      # Average confidence
    voice_characteristics: Dict[str, float]  # Pitch, energy, etc.


class SpeakerLabeler:
    """
    Intelligent speaker labeling system.
    
    Features:
    - Automatic role detection (host, guest, narrator)
    - Creative naming (not just "Speaker 1")
    - Color assignment for visual distinction
    - Emoji representation
    - Speaking pattern analysis
    """
    
    # Creative label templates
    ROLE_TEMPLATES = {
        'host': ['Host', 'Main Speaker', 'Presenter', 'Narrator'],
        'guest': ['Guest', 'Expert', 'Interviewee', 'Contributor'],
        'moderator': ['Moderator', 'Facilitator', 'MC'],
        'participant': ['Speaker', 'Participant', 'Member']
    }
    
    # Emoji sets for different contexts
    EMOJI_SETS = {
        'professional': ['👔', '💼', '🎯', '📊', '🎤', '🎙️', '👨‍💼', '👩‍💼'],
        'casual': ['😊', '🙂', '😄', '🤗', '👋', '✨', '🎈', '🌟'],
        'educational': ['👨‍🏫', '👩‍🏫', '📚', '🎓', '✏️', '📖', '🧑‍🎓', '👨‍🔬'],
        'podcast': ['🎙️', '🎧', '🎤', '📻', '🔊', '🎵', '🎶', '🗣️'],
        'interview': ['💬', '🗨️', '💭', '🎤', '🎙️', '📝', '✍️', '🤝']
    }
    
    # Color palettes for speaker distinction
    COLOR_PALETTES = {
        'vibrant': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'],
        'professional': ['#2E86DE', '#EE5A6F', '#10AC84', '#F79F1F', '#5F27CD', '#00D2D3'],
        'pastel': ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFDFBA', '#E0BBE4'],
        'neon': ['#FF00FF', '#00FFFF', '#FFFF00', '#FF0080', '#00FF80', '#8000FF'],
        'warm': ['#FF6B6B', '#FFA07A', '#FFD93D', '#F8B500', '#FF8C42', '#FF4E50'],
        'cool': ['#4ECDC4', '#45B7D1', '#5F9EA0', '#6C5CE7', '#74B9FF', '#00B894']
    }
    
    def __init__(
        self,
        style: str = 'professional',
        context: str = 'podcast',
        auto_detect_roles: bool = True
    ):
        """
        Initialize speaker labeler.
        
        Args:
            style: Color palette style
            context: Content context for emoji selection
            auto_detect_roles: Automatically detect speaker roles
        """
        self.style = style
        self.context = context
        self.auto_detect_roles = auto_detect_roles
        self.speaker_profiles: Dict[str, SpeakerProfile] = {}
    
    def label_segments(
        self,
        segments: List[CaptionSegment],
        custom_labels: Optional[Dict[str, str]] = None
    ) -> List[CaptionSegment]:
        """
        Label all segments with intelligent speaker identification.
        
        Args:
            segments: Caption segments with speaker IDs
            custom_labels: Optional custom labels {speaker_id: label}
            
        Returns:
            Segments with enhanced speaker information
        """
        # Analyze speakers
        self._analyze_speakers(segments)
        
        # Assign creative labels
        if custom_labels:
            self._apply_custom_labels(custom_labels)
        elif self.auto_detect_roles:
            self._auto_assign_labels()
        else:
            self._assign_default_labels()
        
        # Apply labels to segments
        labeled_segments = []
        for segment in segments:
            if segment.speaker and segment.speaker in self.speaker_profiles:
                profile = self.speaker_profiles[segment.speaker]
                
                # Create enhanced segment
                enhanced_segment = CaptionSegment(
                    text=segment.text,
                    start=segment.start,
                    end=segment.end,
                    confidence=segment.confidence,
                    speaker=profile.label,  # Use creative label
                    raw_text=segment.raw_text,
                    words=segment.words,
                    metadata={
                        'speaker_id': segment.speaker,
                        'speaker_label': profile.label,
                        'speaker_color': profile.color,
                        'speaker_emoji': profile.emoji,
                        'speaker_role': self._get_speaker_role(segment.speaker)
                    }
                )
                labeled_segments.append(enhanced_segment)
            else:
                labeled_segments.append(segment)
        
        return labeled_segments
    
    def _analyze_speakers(self, segments: List[CaptionSegment]):
        """Analyze speaker patterns and characteristics."""
        speaker_stats = {}
        
        for segment in segments:
            if not segment.speaker:
                continue
            
            speaker_id = segment.speaker
            if speaker_id not in speaker_stats:
                speaker_stats[speaker_id] = {
                    'segments': [],
                    'total_duration': 0.0,
                    'confidences': []
                }
            
            speaker_stats[speaker_id]['segments'].append(segment)
            speaker_stats[speaker_id]['total_duration'] += segment.duration
            speaker_stats[speaker_id]['confidences'].append(segment.confidence)
        
        # Create profiles
        colors = self._get_color_palette()
        emojis = self._get_emoji_set()
        
        for i, (speaker_id, stats) in enumerate(speaker_stats.items()):
            self.speaker_profiles[speaker_id] = SpeakerProfile(
                id=speaker_id,
                label=speaker_id,  # Temporary, will be replaced
                color=colors[i % len(colors)],
                emoji=emojis[i % len(emojis)],
                segment_count=len(stats['segments']),
                total_duration=stats['total_duration'],
                avg_confidence=sum(stats['confidences']) / len(stats['confidences']),
                voice_characteristics={}
            )
    
    def _auto_assign_labels(self):
        """
        Automatically assign creative labels based on speaking patterns.
        
        Heuristics:
        - Most speaking time = Host/Main Speaker
        - Second most = Guest/Co-host
        - Others = Guests/Participants
        """
        if not self.speaker_profiles:
            return
        
        # Sort by speaking time
        sorted_speakers = sorted(
            self.speaker_profiles.items(),
            key=lambda x: x[1].total_duration,
            reverse=True
        )
        
        if len(sorted_speakers) == 1:
            # Solo speaker
            sorted_speakers[0][1].label = "Narrator"
        
        elif len(sorted_speakers) == 2:
            # Two speakers - likely interview or conversation
            primary_time = sorted_speakers[0][1].total_duration
            secondary_time = sorted_speakers[1][1].total_duration
            
            # Check if one dominates
            if primary_time > secondary_time * 1.5:
                sorted_speakers[0][1].label = "Host"
                sorted_speakers[1][1].label = "Guest"
            else:
                # Equal conversation
                sorted_speakers[0][1].label = "Speaker A"
                sorted_speakers[1][1].label = "Speaker B"
        
        else:
            # Multiple speakers
            sorted_speakers[0][1].label = "Host"
            sorted_speakers[1][1].label = "Co-host"
            
            for i in range(2, len(sorted_speakers)):
                sorted_speakers[i][1].label = f"Guest {i - 1}"
    
    def _assign_default_labels(self):
        """Assign simple numeric labels."""
        for i, (speaker_id, profile) in enumerate(self.speaker_profiles.items()):
            profile.label = f"Speaker {i + 1}"
    
    def _apply_custom_labels(self, custom_labels: Dict[str, str]):
        """Apply user-provided custom labels."""
        for speaker_id, label in custom_labels.items():
            if speaker_id in self.speaker_profiles:
                self.speaker_profiles[speaker_id].label = label
        
        # Default labels for unmapped speakers
        for speaker_id, profile in self.speaker_profiles.items():
            if profile.label == speaker_id:
                profile.label = f"Speaker {len([p for p in self.speaker_profiles.values() if p.label.startswith('Speaker')]) + 1}"
    
    def _get_speaker_role(self, speaker_id: str) -> str:
        """Get the role of a speaker."""
        if speaker_id not in self.speaker_profiles:
            return 'unknown'
        
        label = self.speaker_profiles[speaker_id].label.lower()
        
        if any(word in label for word in ['host', 'presenter', 'narrator']):
            return 'host'
        elif any(word in label for word in ['guest', 'expert', 'interviewee']):
            return 'guest'
        elif any(word in label for word in ['moderator', 'facilitator']):
            return 'moderator'
        else:
            return 'participant'
    
    def _get_color_palette(self) -> List[str]:
        """Get color palette for current style."""
        return self.COLOR_PALETTES.get(self.style, self.COLOR_PALETTES['professional'])
    
    def _get_emoji_set(self) -> List[str]:
        """Get emoji set for current context."""
        return self.EMOJI_SETS.get(self.context, self.EMOJI_SETS['professional'])
    
    def get_speaker_summary(self) -> str:
        """
        Get a formatted summary of all speakers.
        
        Returns:
            Formatted string with speaker statistics
        """
        if not self.speaker_profiles:
            return "No speakers detected"
        
        lines = ["=" * 60]
        lines.append("SPEAKER SUMMARY")
        lines.append("=" * 60)
        
        for profile in sorted(
            self.speaker_profiles.values(),
            key=lambda x: x.total_duration,
            reverse=True
        ):
            lines.append(f"{profile.emoji} {profile.label}")
            lines.append(f"   Segments: {profile.segment_count}")
            lines.append(f"   Duration: {profile.total_duration:.1f}s")
            lines.append(f"   Confidence: {profile.avg_confidence:.1%}")
            lines.append(f"   Color: {profile.color}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)


class SpeakerStyler:
    """
    Apply visual styling based on speaker.
    
    Creates speaker-specific caption styles for visual distinction.
    """
    
    @staticmethod
    def create_speaker_styles(
        speaker_profiles: Dict[str, SpeakerProfile],
        base_style: dict
    ) -> Dict[str, dict]:
        """
        Create style overrides for each speaker.
        
        Args:
            speaker_profiles: Speaker profile dictionary
            base_style: Base style to modify
            
        Returns:
            Dictionary of speaker_id -> style_dict
        """
        styles = {}
        
        for speaker_id, profile in speaker_profiles.items():
            # Clone base style
            speaker_style = base_style.copy()
            
            # Apply speaker-specific colors
            speaker_style['primary_color'] = profile.color
            speaker_style['outline_color'] = SpeakerStyler._get_contrast_color(profile.color)
            
            # Position based on speaker role
            role = profile.label.lower()
            if 'host' in role or 'narrator' in role:
                speaker_style['vertical_position'] = 'bottom'
                speaker_style['alignment'] = 'center'
            elif 'guest' in role:
                speaker_style['vertical_position'] = 'top'
                speaker_style['alignment'] = 'center'
            
            styles[speaker_id] = speaker_style
        
        return styles
    
    @staticmethod
    def _get_contrast_color(hex_color: str) -> str:
        """Get high-contrast color (black or white) for given color."""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        # Return black or white based on luminance
        return '#000000' if luminance > 0.5 else '#FFFFFF'


def generate_speaker_colors(num_speakers: int, palette: str = 'vibrant') -> List[str]:
    """
    Generate visually distinct colors for speakers.
    
    Uses HSV color space to ensure maximum distinction.
    
    Args:
        num_speakers: Number of speakers
        palette: Color palette style
        
    Returns:
        List of hex colors
    """
    if num_speakers <= len(SpeakerLabeler.COLOR_PALETTES.get(palette, [])):
        return SpeakerLabeler.COLOR_PALETTES[palette][:num_speakers]
    
    # Generate colors with even spacing in hue
    colors = []
    for i in range(num_speakers):
        hue = i / num_speakers
        saturation = 0.7 + (i % 2) * 0.2  # Alternate saturation
        value = 0.8 + (i % 3) * 0.1       # Alternate brightness
        
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        hex_color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
        colors.append(hex_color)
    
    return colors


__all__ = [
    'SpeakerLabeler',
    'SpeakerProfile',
    'SpeakerStyler',
    'generate_speaker_colors',
]
