"""
UACE Command Line Interface

Beautiful, intuitive CLI for caption generation.
"""

import click
from pathlib import Path
from typing import Optional

from uace import CaptionEngine, ProcessingConfig, CleaningMode, StylePreset
from uace.config import EnginePreference
from uace.styling.presets import list_presets
from uace.engines.transcription import EngineSelector


@click.group()
@click.version_option(version="1.1.0", prog_name="uace")
def cli():
    """
    UACE - Universal Auto-Caption Engine
    
    Words are noisy. Meaning is not.
    Captions should speak clearly — and move beautifully.
    
    Transform raw speech into clean, animated captions.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option(
    '-o', '--output',
    type=click.Path(),
    help='Output file path'
)
@click.option(
    '--style',
    type=click.Choice(list_presets(), case_sensitive=False),
    default='viral_pop',
    help='Caption style preset'
)
@click.option(
    '--cleaning',
    type=click.Choice(['none', 'light', 'balanced', 'aggressive'], case_sensitive=False),
    default='balanced',
    help='Text cleaning mode'
)
@click.option(
    '--language',
    default='en',
    help='Language code (ISO 639-1)'
)
@click.option(
    '--model',
    type=click.Choice(['tiny', 'base', 'small', 'medium', 'large']),
    default='base',
    help='Whisper model size'
)
@click.option(
    '--diarization/--no-diarization',
    default=False,
    help='Enable speaker diarization'
)
@click.option(
    '--gpu/--no-gpu',
    default=True,
    help='Use GPU acceleration'
)
@click.option(
    '-v', '--verbose',
    is_flag=True,
    help='Verbose output'
)
@click.option(
    '--format',
    type=click.Choice(['ass', 'srt', 'vtt', 'json']),
    default='ass',
    help='Output format'
)
def process(
    input_file: str,
    output: Optional[str],
    style: str,
    cleaning: str,
    language: str,
    model: str,
    diarization: bool,
    gpu: bool,
    verbose: bool,
    format: str
):
    """
    Process a video or audio file to generate captions.
    
    Examples:
    
        # Basic usage
        uace process video.mp4
        
        # Custom style and cleaning
        uace process video.mp4 --style minimal --cleaning aggressive
        
        # With speaker diarization
        uace process podcast.mp3 --diarization --model large
        
        # Export as SRT
        uace process video.mp4 --format srt -o captions.srt
    """
    # Build configuration
    config = ProcessingConfig()
    
    # Transcription
    config.transcription.language = language if language != 'en' else None
    config.transcription.model = model
    config.transcription.diarization = diarization
    config.transcription.gpu = gpu
    
    # Cleaning
    config.cleaning.mode = CleaningMode(cleaning)
    
    # Styling
    config.styling.preset = style
    
    # Export
    config.export.format = format
    
    # Verbose
    config.verbose = verbose
    
    # Auto-generate output if not provided
    if not output:
        input_path = Path(input_file)
        output = str(input_path.with_suffix(f'.{format}'))
    
    # Process
    engine = CaptionEngine(config, verbose=verbose)
    
    try:
        caption = engine.process(input_file, output)
        
        if not verbose:
            click.echo(f"✓ Captions saved to: {output}")
            click.echo(f"  {len(caption.segments)} segments")
            click.echo(f"  {caption.word_count} words")
            click.echo(f"  {caption.duration:.1f}s duration")
    
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def styles():
    """
    List available style presets.
    """
    from uace.styling.presets import PRESET_REGISTRY
    
    click.echo("\nAvailable Style Presets:\n")
    
    for name, preset in PRESET_REGISTRY.items():
        click.echo(f"  {name:20} - {preset.description}")
    
    click.echo("\nUse with: uace process video.mp4 --style <name>\n")


@cli.command()
def engines():
    """
    Show available transcription engines.
    """
    available = EngineSelector.get_available_engines()
    
    click.echo("\nAvailable Transcription Engines:\n")
    
    if not available:
        click.echo("  No engines available!")
        click.echo("  Install at least one: pip install faster-whisper")
        return
    
    for engine in available:
        click.echo(f"  ✓ {engine}")
    
    click.echo("\nRecommended: faster-whisper (fastest)")
    click.echo("Advanced: whisperx (diarization support)\n")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['json', 'txt']), default='txt')
def info(input_file: str, format: str):
    """
    Show information about a caption file.
    """
    # This would parse an existing caption file
    # For now, just process and show info
    
    config = ProcessingConfig.fast()
    config.verbose = False
    
    engine = CaptionEngine(config)
    caption = engine.process(input_file)
    
    if format == 'json':
        import json
        click.echo(json.dumps(caption.model_dump(), indent=2))
    else:
        click.echo(f"\nCaption Information:")
        click.echo(f"  Duration:     {caption.duration:.2f}s")
        click.echo(f"  Segments:     {len(caption.segments)}")
        click.echo(f"  Words:        {caption.word_count}")
        click.echo(f"  Language:     {caption.language}")
        click.echo(f"  Engine:       {caption.engine_used}")
        click.echo(f"  Confidence:   {(caption.avg_confidence or 0) * 100:.1f}%")


@cli.command()
def demo():
    """
    Show example usage and workflows.
    """
    examples = """
    UACE Examples
    =============
    
    1. Quick Start
       Generate captions with defaults:
       
       $ uace process video.mp4
    
    2. TikTok/Shorts Style
       Viral pop style with aggressive cleaning:
       
       $ uace process video.mp4 --style viral_pop --cleaning aggressive
    
    3. Podcast with Speakers
       Multi-speaker diarization:
       
       $ uace process podcast.mp3 --diarization --model large
    
    4. Professional Subtitles
       Classic style with light cleaning:
       
       $ uace process movie.mp4 --style subtitle_classic --cleaning light --format srt
    
    5. Maximum Accuracy
       Large model, balanced cleaning:
       
       $ uace process important.mp4 --model large --gpu
    
    6. Fast Processing
       Tiny model for quick results:
       
       $ uace process video.mp4 --model tiny --cleaning light
    
    7. Custom Output
       Specify output location:
       
       $ uace process video.mp4 -o my_captions.ass
    
    See all styles:
    $ uace styles
    
    Check available engines:
    $ uace engines
    """
    
    click.echo(examples)


@cli.command()
@click.option('--check-gpu', is_flag=True, help='Check GPU availability')
def doctor(check_gpu: bool):
    """
    Diagnose installation and show system info.
    """
    import sys
    
    click.echo("\nUACE System Check\n")
    click.echo(f"Python:  {sys.version.split()[0]}")
    click.echo(f"UACE:    1.1.0")
    
    # Check engines
    click.echo("\nTranscription Engines:")
    engines = EngineSelector.get_available_engines()
    
    if engines:
        for engine in engines:
            click.echo(f"  ✓ {engine}")
    else:
        click.echo("  ✗ No engines available")
        click.echo("    Install: pip install faster-whisper")
    
    # Check GPU
    if check_gpu:
        click.echo("\nGPU Check:")
        try:
            import torch
            if torch.cuda.is_available():
                click.echo(f"  ✓ CUDA available")
                click.echo(f"    Device: {torch.cuda.get_device_name(0)}")
            else:
                click.echo(f"  ✗ CUDA not available")
        except ImportError:
            click.echo("  ✗ PyTorch not installed")
    
    click.echo()


def main():
    """Entry point for CLI."""
    cli()


if __name__ == '__main__':
    main()
