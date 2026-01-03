# UACE - Universal Auto-Caption Engine

> **Words are noisy. Meaning is not.**  
> **Captions should speak clearly — and move beautifully.**

UACE transforms raw speech transcription into clean, readable, beautifully animated captions with professional-grade motion typography.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ What Makes UACE Special

Most caption tools just transcribe. **UACE transforms.**

### 🎯 The UACE Difference

- **🧹 Intelligent Cleaning** - Removes "um", "uh", repetitions, sound effects automatically
- **🎨 30+ Style Presets** - From viral TikTok to cinematic film subtitles
- **🎬 High-Quality Burn-in** - Embed captions without quality loss (CRF 18)
- **⚡ CPU & GPU Support** - Works on Kaggle, Colab, local machines
- **🔧 Extremely Customizable** - 80+ parameters for fine control
- **📦 Offline First** - No cloud APIs, no internet required
- **🌍 Multi-Language** - Language-aware cleaning and processing

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install faster-whisper pydantic rich click

# Add to path (if using from folder)
import sys
sys.path.append('/path/to/uace-package/src')
```

### Simple Usage

```python
from uace import CaptionEngine

# One line to caption your video
engine = CaptionEngine()
caption = engine.process("video.mp4", output="captions.ass")
```

### With Configuration

```python
from uace import CaptionEngine, ProcessingConfig

config = ProcessingConfig()

# Transcription
config.transcription.gpu = False  # Use CPU (works on Kaggle!)
config.transcription.model = "base"  # tiny, base, small, medium, large

# Styling
config.styling.preset = "big_bold"  # Choose from 30+ styles
config.styling.font_size = 72  # Custom font size
config.styling.primary_color = "#FFD700"  # Gold text

# Cleaning
config.cleaning.mode = "aggressive"  # Remove all fillers

# Generate captions
engine = CaptionEngine(config, verbose=True)
caption = engine.process("video.mp4", "captions.ass")

print(f"✅ Generated {len(caption.segments)} caption segments")
```

### Burn Captions (High Quality, No Quality Loss!)

```python
from uace.utils import burn_captions

# Embed captions directly into video
output = burn_captions(
    video_path="video.mp4",
    caption_path="captions.ass",
    output_path="output.mp4",
    quality="high",  # Visually lossless (CRF 18)
    gpu=True,
    verbose=True
)

print(f"✅ Video with captions: {output}")
```

---

## 🎨 30+ Built-in Style Presets

### 🔥 Viral/Social Media Styles
Perfect for TikTok, Instagram Reels, YouTube Shorts

- **viral_pop** - Original word-by-word pop
- **big_bold** - HUGE text that zooms in (72px!)
- **zoom_punch** - Explosive word-by-word zoom
- **wave_motion** - Smooth flowing wave animation
- **elastic_bounce** - Playful rubber band bounce
- **earthquake** - Violent shake effect

### 🎵 Music/Rhythm Styles
Sync with audio beats

- **karaoke** - Classic karaoke fill effect
- **beat_pulse** - Pulse to the beat
- **sound_wave** - Visual audio waveform
- **rhythm_bounce** - Bounce to rhythm

### 🎨 Creative/Artistic Styles
Unique aesthetics

- **neon** - Cyberpunk neon glow
- **glitch** - Digital glitch effect
- **retro_vhs** - 80s VHS aesthetic
- **hologram** - Futuristic hologram
- **graffiti** - Street art style
- **handwritten** - Personal handwriting

### 🎬 Cinematic Styles
Professional film quality

- **minimal** - Clean and professional
- **subtitle_classic** - Traditional subtitles
- **cinematic_fade** - Elegant film fade
- **noir_typewriter** - Detective story style

### ✨ Animation Styles
Dynamic motion effects

- **bounce** - Energetic bounce
- **slide_up** - Rise from bottom
- **slide_down** - Drop from top
- **flip_in** - 3D flip animation
- **rotate_in** - Spinning entrance
- **blur_focus** - Camera focus effect
- **typewriter** - Character-by-character typing

### 🌐 3D/Perspective + Special Effects

- **perspective_3d** - Dramatic 3D tilt
- **depth_blur** - Depth of field effect
- **floating** - Gentle floating motion
- **fire** - Burning flame effect
- **lightning** - Electric flash
- **particles** - Magical explosion
- **spotlight** - Stage reveal effect

**See [STYLE_GUIDE.md](STYLE_GUIDE.md) for detailed descriptions and examples.**

---

## 🎯 Key Features

### 🎤 Multi-Engine Transcription
- **faster-whisper** (default) - Fastest, GPU/CPU
- **WhisperX** - Advanced alignment + speaker diarization
- **distil-whisper** - Ultra-fast CPU inference
- Automatic engine selection

### 🧹 Intelligent Cleaning
- Filler removal ("um", "uh", "like")
- Sound effects ([laughter], [music])
- Repetitions ("I I I think" → "I think")
- Language-aware cleaning
- 4 cleaning modes: none, light, balanced, aggressive

### ✂️ Semantic Chunking
- Respects phrase boundaries
- Optimizes reading speed
- Maintains natural flow
- 5 chunking strategies

### 🎨 Motion Typography
- Word-by-word timing
- 20+ animation styles
- Karaoke effects
- ASS format (universal)

### 💾 Export Formats
- ASS, SRT, VTT, JSON, TXT

---

## 🔧 Extreme Customization

UACE provides **80+ configuration parameters**:

### Font Control
```python
config.styling.font_size = 80
config.styling.font_family = "Impact"
config.styling.font_file = "/path/to/custom.ttf"
config.styling.font_weight = "black"
config.styling.font_italic = True
config.styling.letter_spacing = 5
config.styling.text_transform = "uppercase"
```

### Color Control
```python
config.styling.primary_color = "#FFFFFF"
config.styling.outline_color = "#000000"
config.styling.shadow_color = "#FF0000"
config.styling.emphasis_color = "#FFD700"
```

### Effects Control
```python
config.styling.outline_width = 5
config.styling.shadow_depth = 10
config.styling.glow = True
config.styling.glow_intensity = 15
config.styling.blur = 3
config.styling.opacity = 0.9
```

### Animation Control
```python
config.styling.animation_duration = 0.3
config.styling.stagger_delay = 0.08
config.styling.scale_overshoot = 1.5
config.styling.rotation_start = -45
config.styling.rotation_end = 0
```

### 3D Effects
```python
config.styling.perspective = True
config.styling.rotation_x = 10
config.styling.rotation_y = 20
```

### Gradients
```python
config.styling.gradient_enabled = True
config.styling.gradient_start = "#FF00FF"
config.styling.gradient_end = "#00FFFF"
```

**See [DOCS.md](DOCS.md) for complete API reference.**

---

## 🎬 High-Quality Video Burn-in

Embed captions **without quality loss**:

### Simple High-Quality
```python
from uace.utils import burn_captions

output = burn_captions(
    "video.mp4", 
    "captions.ass", 
    "output.mp4",
    quality="high"  # CRF 18 - visually lossless
)
```

### Lossless (Perfect Quality)
```python
from uace.utils.burnin import VideoBurnIn

VideoBurnIn.burn_captions_lossless(
    "video.mp4", 
    "captions.ass", 
    "output.mp4"
)
```

### Fast Processing
```python
VideoBurnIn.burn_captions_fast(
    "video.mp4",
    "captions.ass", 
    "output.mp4",
    gpu=True
)
```

### Custom Settings
```python
VideoBurnIn.burn_captions(
    video_path="video.mp4",
    caption_path="captions.ass",
    output_path="output.mp4",
    preset="slow",  # veryslow, slow, medium, fast
    crf=15,  # 0-51 (lower = better)
    font_size=80,
    custom_font="/path/to/font.ttf"
)
```

**See [BURNIN_GUIDE.md](BURNIN_GUIDE.md) for complete guide.**

---

## 💻 Platform Support

### ✅ Kaggle
```python
config = ProcessingConfig()
config.transcription.gpu = False  # Auto-detects CPU
engine = CaptionEngine(config)
```

**See [KAGGLE_SETUP.md](KAGGLE_SETUP.md)**

### ✅ Google Colab
```python
config.transcription.gpu = True  # Use GPU
```

### ✅ Local Machine
Works on CPU or GPU, your choice!

---

## 📊 Performance

### Processing Speed (base model)

| Video Length | CPU Time | GPU Time |
|--------------|----------|----------|
| 1 minute     | ~5s      | ~2s      |
| 10 minutes   | ~60s     | ~15s     |
| 30 minutes   | ~3min    | ~45s     |
| 1 hour       | ~6min    | ~90s     |

### Burn-in Speed (1080p, 10-min)

| Quality  | CPU Time | GPU Time |
|----------|----------|----------|
| High     | ~15 min  | ~3 min   |
| Lossless | ~30 min  | ~8 min   |
| Fast     | ~5 min   | ~1 min   |

---

## 🎓 Examples

### Viral TikTok Style
```python
config = ProcessingConfig()
config.styling.preset = "big_bold"
config.styling.font_size = 80
config.cleaning.mode = "aggressive"

engine = CaptionEngine(config)
caption = engine.process("video.mp4")
```

### Music Video Karaoke
```python
config.styling.preset = "karaoke"
config.transcription.word_timestamps = True
```

### Professional Documentary
```python
config.styling.preset = "subtitle_classic"
config.cleaning.mode = "light"
config.transcription.model = "large"
```

### Podcast with Speakers
```python
config.transcription.diarization = True
config.styling.preset = "minimal"
```

### Custom Cyberpunk
```python
config.styling.preset = "neon"
config.styling.glow_intensity = 20
config.styling.perspective = True
```

**See [examples.py](examples.py) for 10+ examples.**

---

## 🔥 Complete Workflow

```python
from uace import CaptionEngine, ProcessingConfig
from uace.utils import burn_captions

# Configure
config = ProcessingConfig()
config.transcription.gpu = False
config.styling.preset = "big_bold"
config.styling.font_size = 72
config.cleaning.mode = "aggressive"

# Generate captions
engine = CaptionEngine(config, verbose=True)
caption = engine.process("video.mp4", "captions.ass")

print(f"✅ Generated {len(caption.segments)} segments")

# Burn into video (high quality)
output = burn_captions(
    "video.mp4",
    "captions.ass",
    "final.mp4",
    quality="high",
    gpu=True
)

print(f"🎉 Final video: {output}")
```

---

## 📚 Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick start with fixes
- **[DOCS.md](DOCS.md)** - Complete API reference
- **[STYLE_GUIDE.md](STYLE_GUIDE.md)** - All 30+ styles
- **[BURNIN_GUIDE.md](BURNIN_GUIDE.md)** - Video burn-in guide
- **[KAGGLE_SETUP.md](KAGGLE_SETUP.md)** - Kaggle setup
- **[FIXES_v1.2.1.md](FIXES_v1.2.1.md)** - Recent bug fixes
- **[STRUCTURE.md](STRUCTURE.md)** - Architecture
- **[IMPORTS.md](IMPORTS.md)** - Import guide

---

## ❓ FAQ

**Q: Does it work without GPU?**  
A: Yes! Set `config.transcription.gpu = False`.

**Q: Can I use it on Kaggle?**  
A: Absolutely! See [KAGGLE_SETUP.md](KAGGLE_SETUP.md).

**Q: Will burning reduce video quality?**  
A: Not with UACE! Use `quality="high"` (CRF 18).

**Q: Can I customize everything?**  
A: Yes! 80+ configuration parameters.

**Q: What languages are supported?**  
A: 30+ languages with language-aware cleaning.

**Q: Can I add custom fonts?**  
A: Yes! Use `config.styling.font_file`.

---

## 🐛 Recent Fixes (v1.2.1)

✅ **Fixed:** String preset handling  
✅ **Fixed:** Auto CPU detection  
✅ **Fixed:** Video quality loss  
✅ **Added:** Font size customization  
✅ **Added:** Custom font support  
✅ **Added:** High-quality burn-in

---

## 🎯 Comparison

| Feature | UACE | Whisper | CapCut |
|---------|------|---------|--------|
| Intelligent Cleaning | ✅ | ❌ | ✅ |
| 30+ Presets | ✅ | ❌ | ✅ |
| Offline | ✅ | ✅ | ❌ |
| CPU Support | ✅ | ✅ | ❌ |
| Quality Burn-in | ✅ | ❌ | ✅ |
| Open Source | ✅ | ✅ | ❌ |
| Customizable | ✅ | ❌ | ⚠️ |

---

## 🌟 Why Choose UACE?

1. **Complete Pipeline** - Transcribe → Clean → Style → Export → Burn
2. **Professional Quality** - Visually lossless output
3. **Extreme Flexibility** - 80+ parameters, 30+ presets
4. **Platform Agnostic** - Kaggle, Colab, local
5. **Offline Capable** - No cloud dependencies
6. **Open Source** - MIT license, extensible
7. **Well Documented** - 8 comprehensive guides

---

## 📦 What's Included

- Core Engine with multi-stage pipeline
- 3 Transcription Engines
- Intelligent Cleaner
- Semantic Chunker
- 30+ Style Presets
- Video Burn-in Utility
- 5 Export Formats
- Complete Documentation
- Test Suite

---

## 🚀 Get Started

```bash
# Install dependencies
pip install faster-whisper pydantic rich click

# Run demo
python demo.py

# Try examples
python examples.py
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🎉 Version History

- **v0.1.2** - Small Bug Fix
- **v0.1.1** - Bug fixes, burn-in, font customization
- **v0.1.0** - Initial release

---

**UACE - Transform speech into clarity.** 🎬✨

Made with ❤️ for content creators, video editors, and developers.
