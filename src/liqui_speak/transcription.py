"""Audio transcription functionality for Liqui-Speak."""

from pathlib import Path

from liqui_speak.audio_converter import (
    convert_audio_for_transcription,
    is_format_supported,
)
from liqui_speak.config import get_config
from liqui_speak.model_wrapper import LFM2AudioWrapper


def transcribe_audio(
    audio_file: str,
    play_audio: bool = False,
    clean_text: bool = False,
    verbose: bool = False
) -> str | None:
    """
    Transcribe an audio file to text.
    
    Args:
        audio_file: Path to audio file
        play_audio: Whether to play audio during transcription
        clean_text: Whether to clean the transcription
        verbose: Whether to show detailed progress
        
    Returns:
        Transcribed text or None if failed
    """
    audio_path = Path(audio_file)

    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Check if format is supported
    if not is_format_supported(audio_file):
        if verbose:
            print(f"🔄 Converting {audio_path.suffix} to WAV format...")

        try:
            # Convert unsupported format to WAV
            converted_file = convert_audio_for_transcription(audio_file, "wav")

            try:
                return _transcribe_wav_file(converted_file, play_audio, clean_text, verbose)
            finally:
                # Clean up temporary file
                try:
                    Path(converted_file).unlink()
                except OSError:
                    pass
        except Exception as e:
            if verbose:
                raise RuntimeError(f"Audio conversion failed: {e}")
            else:
                return None
    else:
        # Direct transcription for supported formats
        return _transcribe_wav_file(audio_file, play_audio, clean_text, verbose)


def _transcribe_wav_file(
    audio_file: str,
    play_audio: bool = False,
    clean_text: bool = False,
    verbose: bool = False
) -> str:
    """
    Transcribe a WAV file using the LFM2 model.
    
    Args:
        audio_file: Path to WAV file
        play_audio: Whether to play audio during transcription
        clean_text: Whether to clean the transcription
        verbose: Whether to show detailed progress
        
    Returns:
        Transcribed text
    """
    # Get configuration
    config = get_config()

    if verbose:
        print(f"🎵 Starting transcription of {Path(audio_file).name}")
        print(f"📊 Duration: {config.get('duration', 'unknown')}")

    try:
        # Initialize model wrapper
        model = LFM2AudioWrapper(config)

        # Transcribe the audio
        transcription = model.transcribe_audio_file(audio_file)

        if verbose:
            print("✅ Transcription complete")

        # Clean text if requested
        if clean_text:
            if verbose:
                print("🧹 Cleaning transcription...")
            # TODO: Implement text cleaning
            pass

        return transcription

    except Exception as e:
        if verbose:
            raise RuntimeError(f"Transcription failed: {e}")
        else:
            return None


def transcribe_with_chunks(
    audio_file: str,
    chunk_duration: float = 2.0,
    overlap: float = 0.5,
    play_audio: bool = False,
    verbose: bool = False
) -> str:
    """
    Transcribe audio with real-time chunk processing.
    
    Args:
        audio_file: Path to audio file
        chunk_duration: Duration of each chunk in seconds
        overlap: Overlap between chunks
        play_audio: Whether to play audio during transcription
        verbose: Whether to show progress
        
    Returns:
        Complete transcription
    """
    # TODO: Implement chunked transcription for real-time processing
    return transcribe_audio(audio_file, play_audio, False, verbose)
