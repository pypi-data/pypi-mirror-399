"""
UACE Utilities

Helper functions for common tasks.
"""

import os
from pathlib import Path
from typing import Optional, Union


def is_video_file(filepath: Union[str, Path]) -> bool:
    """
    Check if a file is a video file based on extension.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if video file, False otherwise
    """
    video_extensions = {
        '.mp4', '.mov', '.avi', '.mkv', '.webm', 
        '.flv', '.wmv', '.m4v', '.mpg', '.mpeg'
    }
    
    path = Path(filepath)
    return path.suffix.lower() in video_extensions


def is_audio_file(filepath: Union[str, Path]) -> bool:
    """
    Check if a file is an audio file based on extension.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if audio file, False otherwise
    """
    audio_extensions = {
        '.mp3', '.wav', '.flac', '.m4a', '.ogg',
        '.aac', '.wma', '.opus', '.aiff'
    }
    
    path = Path(filepath)
    return path.suffix.lower() in audio_extensions


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {secs}s"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    return f"{hours}h {minutes}m {secs}s"


def format_filesize(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable string.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} PB"


def get_file_info(filepath: Union[str, Path]) -> dict:
    """
    Get information about a file.
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with file information
    """
    path = Path(filepath)
    
    if not path.exists():
        return {"exists": False}
    
    stat = path.stat()
    
    return {
        "exists": True,
        "name": path.name,
        "size": stat.st_size,
        "size_formatted": format_filesize(stat.st_size),
        "extension": path.suffix,
        "is_video": is_video_file(path),
        "is_audio": is_audio_file(path),
    }


def ensure_output_dir(output_path: Union[str, Path]) -> Path:
    """
    Ensure output directory exists.
    
    Args:
        output_path: Path to output file
        
    Returns:
        Path object to output directory
    """
    path = Path(output_path)
    output_dir = path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def auto_output_path(
    input_path: Union[str, Path],
    suffix: str = "_captions",
    extension: str = ".ass"
) -> str:
    """
    Generate output path based on input path.
    
    Args:
        input_path: Input file path
        suffix: Suffix to add to filename
        extension: Output file extension
        
    Returns:
        Output file path
    """
    path = Path(input_path)
    output_name = f"{path.stem}{suffix}{extension}"
    return str(path.parent / output_name)


def validate_language_code(code: str) -> bool:
    """
    Validate ISO 639-1 language code.
    
    Args:
        code: Language code
        
    Returns:
        True if valid, False otherwise
    """
    # Common language codes
    valid_codes = {
        'en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh',
        'ar', 'hi', 'tr', 'pl', 'nl', 'sv', 'da', 'no', 'fi', 'cs',
        'el', 'he', 'th', 'vi', 'id', 'ms', 'fa', 'uk', 'ro', 'hu'
    }
    
    return code.lower() in valid_codes


def seconds_to_timestamp(seconds: float, format: str = "srt") -> str:
    """
    Convert seconds to timestamp string.
    
    Args:
        seconds: Time in seconds
        format: Format type ('srt', 'ass', 'vtt')
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    if format == "srt":
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    elif format == "ass":
        centis = millis // 10
        return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"
    elif format == "vtt":
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def estimate_processing_time(
    duration_seconds: float,
    model_size: str = "base",
    gpu: bool = True
) -> float:
    """
    Estimate processing time for a video/audio file.
    
    Args:
        duration_seconds: Duration of media in seconds
        model_size: Whisper model size
        gpu: Whether GPU is available
        
    Returns:
        Estimated processing time in seconds
    """
    # Rough estimates based on testing
    multipliers = {
        "tiny": 0.05,
        "base": 0.08,
        "small": 0.12,
        "medium": 0.20,
        "large": 0.35,
    }
    
    multiplier = multipliers.get(model_size, 0.15)
    
    # CPU is roughly 3-5x slower
    if not gpu:
        multiplier *= 4
    
    return duration_seconds * multiplier


def get_gpu_info() -> dict:
    """
    Get GPU information if available.
    
    Returns:
        Dictionary with GPU info
    """
    try:
        import torch
        
        if not torch.cuda.is_available():
            return {
                "available": False,
                "reason": "CUDA not available"
            }
        
        return {
            "available": True,
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(0),
            "memory_total": torch.cuda.get_device_properties(0).total_memory,
            "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
        }
    
    except ImportError:
        return {
            "available": False,
            "reason": "PyTorch not installed"
        }


def check_ffmpeg() -> bool:
    """
    Check if ffmpeg is available.
    
    Returns:
        True if ffmpeg is available, False otherwise
    """
    import subprocess
    
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


__all__ = [
    "is_video_file",
    "is_audio_file",
    "format_duration",
    "format_filesize",
    "get_file_info",
    "ensure_output_dir",
    "auto_output_path",
    "validate_language_code",
    "seconds_to_timestamp",
    "estimate_processing_time",
    "get_gpu_info",
    "check_ffmpeg",
]
