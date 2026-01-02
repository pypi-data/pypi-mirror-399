# UACE - Universal Auto-Caption Engine

> **Words are noisy. Meaning is not.**  
> **Captions should speak clearly — and move beautifully.**

UACE transforms raw speech transcription into clean, readable, beautifully animated captions.

[![PyPI version](https://badge.fury.io/py/uace.svg)](https://badge.fury.io/py/uace)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## Why UACE?

Most caption systems treat transcription as the end goal. **UACE treats transcription as raw material.**

Speech is messy:
- Fillers ("um", "uh", "like")
- Repetitions ("I I I think")
- Non-speech artifacts ("[laughter]", "[music]")
- Stage directions
- Background events

**UACE cleans, sculpts, and animates speech into readable motion.**

## Features

### 🎯 Core Philosophy

✅ **Offline first** - No cloud dependencies  
✅ **Software agnostic** - Works with any video editor  
✅ **Linear-time processing** - Fast, even on CPU  
✅ **Declarative styling** - Simple configuration, powerful results  
✅ **Graceful degradation** - Falls back intelligently  

### 🚀 What Makes UACE Different

1. **Multi-Engine Support**
   - `faster-whisper` (default, fastest)
   - `openai-whisper` (maximum accuracy)
   - `whisperx` (advanced alignment + diarization)
   - `distil-whisper` (ultra-fast CPU)
   - Custom engine plugins

2. **Intelligent Cleaning**
   - Language-aware filler removal
   - Sound effect stripping
   - Repetition collapsing
   - Conversational normalization
   - Cultural sensitivity (dialect-aware)

3. **Semantic Chunking**
   - Respects phrase boundaries
   - Optimizes reading speed
   - Maintains meaning
   - Adapts to context

4. **Motion Typography**
   - CapCut-style animations
   - Word-by-word timing
   - Karaoke effects
   - Bounce, pop, slide animations
   - ASS format export (universal compatibility)

## Installation

### Basic Installation

```bash
pip install uace
```

### With Transcription Engine

```bash
# faster-whisper (recommended)
pip install "uace[whisper]"

# WhisperX (for diarization)
pip install "uace[whisperx]"

# All features
pip install "uace[all]"
```

### Development

```bash
git clone https://github.com/chigozie-coder/uace
cd uace
pip install -e ".[dev]"
```

## Quick Start

### CLI Usage

```bash
# Simple processing
uace process video.mp4

# Custom style and cleaning
uace process video.mp4 --style viral_pop --cleaning aggressive

# Speaker diarization
uace process podcast.mp3 --diarization --model large

# Export as SRT
uace process video.mp4 --format srt -o captions.srt
```

### Python API

```python
from uace import CaptionEngine

# Simplest usage
engine = CaptionEngine()
caption = engine.process("video.mp4", output="captions.ass")

# Custom configuration
from uace import ProcessingConfig, CleaningMode

config = ProcessingConfig.quick(
    cleaning=CleaningMode.AGGRESSIVE,
    style="viral_pop"
)

engine = CaptionEngine(config)
caption = engine.process("video.mp4")

# Advanced control
config = ProcessingConfig()
config.transcription.diarization = True
config.cleaning.mode = CleaningMode.BALANCED
config.styling.preset = "neon"

engine = CaptionEngine(config)
caption = engine.process_audio("podcast.mp3")
```

## Style Presets

UACE includes professional style presets:

| Preset | Description | Use Case |
|--------|-------------|----------|
| `viral_pop` | High-energy word pop | TikTok, Shorts |
| `minimal` | Clean, professional | Corporate, vlogs |
| `karaoke` | Color-fill timing | Music videos, lyrics |
| `subtitle_classic` | Traditional subtitles | Movies, TV |
| `bounce` | Energetic bounce | Gaming, reactions |
| `neon` | Cyberpunk glow | Tech content |

List all styles:
```bash
uace styles
```

## Cleaning Modes

| Mode | What It Removes | Use Case |
|------|----------------|----------|
| `none` | Nothing | Legal, compliance |
| `light` | Fillers + sound effects | Interviews |
| `balanced` | Fillers + repetitions + effects | YouTube (default) |
| `aggressive` | Maximum cleaning | Shorts, TikTok |

## Pipeline

```
TRANSCRIBE → CLEAN → CHUNK → STYLE → EXPORT
```

Each stage is:
- **Configurable** - Full control over behavior
- **Non-destructive** - Original text preserved
- **Transparent** - Full processing metadata
- **Fast** - Linear time complexity

## Performance

### Without GPU

| Video Length | Processing Time |
|--------------|----------------|
| 30 minutes   | ~45 seconds    |
| 1 hour       | ~90 seconds    |

### With GPU

| Video Length | Processing Time |
|--------------|----------------|
| 1 hour       | ~15 seconds    |

## Advanced Features

### Speaker Diarization

```python
config = ProcessingConfig()
config.transcription.diarization = True
config.transcription.preference = EnginePreference.DIARIZATION

engine = CaptionEngine(config)
caption = engine.process("podcast.mp3")

# Access speaker info
for segment in caption.segments:
    print(f"[{segment.speaker}]: {segment.text}")
```

### Language Support

```python
config = ProcessingConfig()
config.transcription.language = "es"  # Spanish
config.cleaning.language = "es"
config.cleaning.dialect = "mx"  # Mexican Spanish

engine = CaptionEngine(config)
```

### Custom Fillers

```python
config = ProcessingConfig()
config.cleaning.custom_fillers = ["basically", "literally", "actually"]

engine = CaptionEngine(config)
```

### Word-Level Timing

```python
caption = engine.process("video.mp4")

for segment in caption.segments:
    if segment.has_words():
        for word in segment.words:
            print(f"{word.text}: {word.start:.2f}s - {word.end:.2f}s")
```

## Export Formats

- **ASS** - Advanced SubStation Alpha (with animations) ✨
- **SRT** - SubRip (basic compatibility)
- **VTT** - WebVTT (web)
- **JSON** - Full data export

## API Reference

### CaptionEngine

```python
engine = CaptionEngine(
    config: Optional[ProcessingConfig] = None,
    verbose: bool = False
)

# Process video/audio
caption = engine.process(
    input_file: str,
    output: Optional[str] = None,
    **overrides
) -> Caption

# Export caption
engine.export(
    caption: Caption,
    output_path: str
)
```

### ProcessingConfig

```python
# Quick configs
config = ProcessingConfig.quick(cleaning="balanced", style="viral_pop")
config = ProcessingConfig.fast()  # Speed priority
config = ProcessingConfig.accurate()  # Quality priority

# Full customization
config = ProcessingConfig()
config.transcription.model = "large"
config.transcription.diarization = True
config.cleaning.mode = CleaningMode.AGGRESSIVE
config.chunking.max_chars_per_line = 42
config.styling.preset = "neon"
```

## CLI Reference

```bash
# Main command
uace process INPUT [OPTIONS]

# Options
--style TEXT           Caption style preset
--cleaning TEXT        Text cleaning mode
--language TEXT        Language code (ISO 639-1)
--model TEXT          Whisper model size
--diarization         Enable speaker detection
--gpu/--no-gpu        Use GPU acceleration
--format TEXT         Output format (ass/srt/vtt/json)
-o, --output PATH     Output file path
-v, --verbose         Verbose output

# Utilities
uace styles           List available styles
uace engines          Show available engines
uace doctor          System diagnostics
uace demo            Show examples
```

## Architecture

```
uace/
├── engines/          # Transcription backends
│   └── transcription.py
├── cleaning/         # Text cleaning
│   └── engine.py
├── chunking/         # Semantic chunking
│   └── semantic.py
├── styling/          # Style presets
│   └── presets.py
├── export/          # Format exporters
│   └── formats.py
├── models.py        # Data models
├── config.py        # Configuration
├── engine.py        # Main pipeline
└── cli.py          # Command line interface
```

## Contributing

Contributions welcome! Areas of interest:

- Additional transcription engines
- Language-specific cleaning rules
- New style presets
- Performance optimizations
- Documentation improvements

## Roadmap

- [ ] Real-time processing
- [ ] More animation presets
- [ ] Video embedding (burn-in)
- [ ] Cloud API (optional)
- [ ] GUI application
- [ ] Plugin system

## License

MIT License - see LICENSE file for details.

## Credits

Built with:
- [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- [Pydantic](https://docs.pydantic.dev/)
- [Rich](https://rich.readthedocs.io/)
- [Click](https://click.palletsprojects.com/)

## Support

- 📚 [Documentation](https://docs.uace.dev)
- 🐛 [Issue Tracker](https://github.com/uace/uace/issues)
- 💬 [Discussions](https://github.com/uace/uace/discussions)

---

**UACE is not a subtitle generator. It is a speech refinement engine with motion typography.**

We don't transcribe speech. We transform it into clarity.
