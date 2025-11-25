"""Fast audio format converter using PyDub for M4A/AAC support."""

import tempfile
from pathlib import Path

import magic


def convert_audio_for_transcription(input_file: str, output_format: str = "wav") -> str:
    """
    Convert audio file to format supported by the transcription tool.
    
    Uses PyDub for fast in-memory conversion without external ffmpeg calls.
    
    Args:
        input_file: Path to input audio file (M4A, AAC, etc.)
        output_format: Target format ("wav", "mp3", "flac")
        
    Returns:
        Path to converted audio file (temporary file)
        
    Raises:
        ImportError: If PyDub is not installed
        ValueError: If conversion fails
    """
    try:
        from pydub import AudioSegment
    except ImportError:
        raise ImportError(
            "PyDub is required for audio conversion. "
            "Install with: pip install pydub"
        )

    input_path = Path(input_file)

    try:
        # Load audio file (PyDub will handle format detection)
        audio = AudioSegment.from_file(str(input_path))

        # Convert to mono and standard sample rate for transcription
        audio = audio.set_channels(1)  # Mono
        audio = audio.set_frame_rate(48000)  # 48kHz (standard for transcription)

        # Create temporary output file
        temp_file = tempfile.NamedTemporaryFile(
            suffix=f".{output_format}",
            delete=False,
            prefix="liqui_speak_"
        )
        temp_file.close()

        # Export to desired format
        audio.export(temp_file.name, format=output_format,
                    codec="pcm_s16le" if output_format == "wav" else None)

        return temp_file.name

    except Exception as e:
        raise ValueError(f"Audio conversion failed: {e}")


def is_format_supported(filename: str) -> bool:
    """
    Check if audio file format is supported by transcription tool.
    
    Uses python-magic for accurate format detection.
    
    Args:
        filename: Path to audio file
        
    Returns:
        True if format is supported, False otherwise
    """
    supported_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.aiff', '.au'}

    try:
        # Use python-magic for accurate format detection
        mime = magic.from_file(filename, mime=True)

        # Map MIME types to supported formats
        supported_mimes = {
            'audio/wav', 'audio/x-wav', 'audio/wave',
            'audio/mpeg', 'audio/mp3',
            'audio/flac', 'audio/x-flac',
            'audio/ogg', 'audio/vorbis',
            'audio/aiff', 'audio/x-aiff',
            'audio/basic', 'audio/x-au'
        }

        # Quick check for common Apple formats that aren't supported
        if mime in {'audio/mp4', 'audio/x-m4a', 'audio/aac'}:
            return False

        return mime in supported_mimes

    except Exception:
        # Fallback to extension check if magic fails
        ext = Path(filename).suffix.lower()
        return ext in supported_extensions


def quick_convert_m4a_to_wav(m4a_file: str) -> str:
    """
    Quick conversion specifically for M4A files to WAV format.
    
    Args:
        m4a_file: Path to M4A file
        
    Returns:
        Path to converted WAV file
    """
    return convert_audio_for_transcription(m4a_file, "wav")


def detect_audio_format(filename: str) -> str:
    """
    Detect the actual format of an audio file.
    
    Args:
        filename: Path to audio file
        
    Returns:
        Format name (wav, m4a, mp3, etc.)
    """
    try:
        mime = magic.from_file(filename, mime=True)

        # Map MIME types to format names
        mime_to_format = {
            'audio/wav': 'wav',
            'audio/x-wav': 'wav',
            'audio/wave': 'wav',
            'audio/mpeg': 'mp3',
            'audio/mp3': 'mp3',
            'audio/mp4': 'm4a',
            'audio/x-m4a': 'm4a',
            'audio/aac': 'aac',
            'audio/flac': 'flac',
            'audio/ogg': 'ogg',
            'audio/aiff': 'aiff',
            'audio/x-aiff': 'aiff',
        }

        return mime_to_format.get(mime, 'unknown')

    except Exception:
        # Fallback to extension
        return Path(filename).suffix.lower().lstrip('.')
