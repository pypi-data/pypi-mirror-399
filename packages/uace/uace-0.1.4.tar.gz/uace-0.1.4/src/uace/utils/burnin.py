"""
Video Burn-in Utility

High-quality caption burn-in that preserves video quality.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple


class VideoBurnIn:
    """
    Burn captions into video with quality preservation.
    
    Uses FFmpeg with optimized settings to maintain video quality.
    """
    
    @staticmethod
    def check_ffmpeg() -> bool:
        """Check if ffmpeg is available."""
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
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Get video information using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            import json
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Warning: Could not get video info: {e}")
            return {}
    
    @staticmethod
    def burn_captions(
        video_path: str,
        caption_path: str,
        output_path: str,
        quality: str = "high",
        gpu: bool = False,
        custom_font: Optional[str] = None,
        font_size: Optional[int] = None,
        preset: str = "slow",
        crf: int = 18,
        verbose: bool = False
    ) -> bool:
        """
        Burn captions into video with quality preservation.
        
        Args:
            video_path: Input video file
            caption_path: ASS subtitle file
            output_path: Output video file
            quality: Quality preset (high, medium, fast)
            gpu: Use GPU acceleration (NVENC)
            custom_font: Path to custom font file
            font_size: Override font size
            preset: FFmpeg preset (veryslow, slow, medium, fast, ultrafast)
            crf: Constant Rate Factor (0-51, lower = better quality, 18 = visually lossless)
            verbose: Show FFmpeg output
            
        Returns:
            True if successful, False otherwise
        """
        
        if not VideoBurnIn.check_ffmpeg():
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
        
        # Quality presets
        quality_settings = {
            "high": {
                "preset": "slow",
                "crf": 18,
                "profile": "high",
                "level": "4.1"
            },
            "medium": {
                "preset": "medium", 
                "crf": 23,
                "profile": "high",
                "level": "4.0"
            },
            "fast": {
                "preset": "fast",
                "crf": 23,
                "profile": "main",
                "level": "4.0"
            }
        }
        
        settings = quality_settings.get(quality, quality_settings["high"])
        
        # Override with custom settings
        if preset:
            settings["preset"] = preset
        if crf is not None:
            settings["crf"] = crf
        
        # Build subtitle filter
        subtitle_filter = f"ass='{caption_path}'"
        
        # Add font override if specified
        if font_size:
            subtitle_filter += f":force_style='Fontsize={font_size}'"
        
        if custom_font:
            subtitle_filter += f":fontsdir='{os.path.dirname(custom_font)}'"
        
        # Build FFmpeg command
        if gpu:
            # GPU-accelerated encoding (NVIDIA)
            cmd = [
                "ffmpeg",
                "-hwaccel", "cuda",
                "-hwaccel_output_format", "cuda",
                "-i", video_path,
                "-vf", subtitle_filter,
                "-c:v", "h264_nvenc",
                "-preset", "p7",  # Highest quality NVENC preset
                "-rc", "vbr",
                "-cq", str(settings["crf"]),
                "-b:v", "0",  # VBR mode
                "-profile:v", "high",
                "-c:a", "copy",  # Copy audio (no re-encoding)
                "-movflags", "+faststart",  # Web optimization
                "-y",  # Overwrite output
                output_path
            ]
        else:
            # CPU encoding with x264
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-vf", subtitle_filter,
                "-c:v", "libx264",
                "-preset", settings["preset"],
                "-crf", str(settings["crf"]),
                "-profile:v", settings["profile"],
                "-level", settings["level"],
                "-pix_fmt", "yuv420p",  # Maximum compatibility
                "-c:a", "copy",  # Copy audio (no re-encoding)
                "-movflags", "+faststart",
                "-y",
                output_path
            ]
        
        # Execute FFmpeg
        try:
            if verbose:
                print(f"🎬 Burning captions into video...")
                print(f"   Quality: {quality}")
                print(f"   CRF: {settings['crf']}")
                print(f"   Preset: {settings.get('preset', 'p7')}")
                print(f"   GPU: {'Yes' if gpu else 'No'}")
                
                result = subprocess.run(cmd, check=True)
            else:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True
                )
            
            if verbose:
                print(f"✅ Video saved to: {output_path}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error burning captions: {e}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"FFmpeg error: {e.stderr.decode()}")
            return False
    
    @staticmethod
    def burn_captions_lossless(
        video_path: str,
        caption_path: str,
        output_path: str,
        gpu: bool = False,
        verbose: bool = False
    ) -> bool:
        """
        Burn captions with truly lossless quality.
        
        Uses CRF 0 for mathematically lossless encoding (large file size).
        """
        return VideoBurnIn.burn_captions(
            video_path=video_path,
            caption_path=caption_path,
            output_path=output_path,
            quality="high",
            gpu=gpu,
            preset="veryslow",
            crf=0,  # Lossless
            verbose=verbose
        )
    
    @staticmethod
    def burn_captions_fast(
        video_path: str,
        caption_path: str,
        output_path: str,
        gpu: bool = True,
        verbose: bool = False
    ) -> bool:
        """
        Burn captions quickly (use GPU if available).
        
        Good quality but prioritizes speed.
        """
        return VideoBurnIn.burn_captions(
            video_path=video_path,
            caption_path=caption_path,
            output_path=output_path,
            quality="medium",
            gpu=gpu,
            preset="fast" if not gpu else None,
            crf=23,
            verbose=verbose
        )


# Convenience functions

def burn_captions(
    video_path: str,
    caption_path: str,
    output_path: Optional[str] = None,
    quality: str = "high",
    gpu: bool = False,
    verbose: bool = True
) -> str:
    """
    Burn captions into video (simple interface).
    
    Args:
        video_path: Input video
        caption_path: Caption file (.ass)
        output_path: Output video (auto-generated if None)
        quality: "high", "medium", or "fast"
        gpu: Use GPU acceleration
        verbose: Show progress
        
    Returns:
        Path to output video
        
    Example:
        >>> from uace.utils.burnin import burn_captions
        >>> output = burn_captions("video.mp4", "captions.ass")
        >>> print(f"Saved to: {output}")
    """
    
    if output_path is None:
        # Auto-generate output path
        video_path_obj = Path(video_path)
        output_path = str(video_path_obj.parent / f"{video_path_obj.stem}_captioned{video_path_obj.suffix}")
    
    success = VideoBurnIn.burn_captions(
        video_path=video_path,
        caption_path=caption_path,
        output_path=output_path,
        quality=quality,
        gpu=gpu,
        verbose=verbose
    )
    
    if success:
        return output_path
    else:
        raise RuntimeError("Failed to burn captions")


__all__ = [
    "VideoBurnIn",
    "burn_captions",
]
