"""Configuration management for Liqui-Speak."""

import logging
import os
from pathlib import Path

MODEL_FILES = {
    "model": "LFM2-Audio-1.5B-Q8_0.gguf",
    "mmproj": "mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf",
    "audiodecoder": "audiodecoder-LFM2-Audio-1.5B-Q8_0.gguf",
}

TRANSCRIPTION_TIMEOUT = 60


LOG_LEVEL = os.getenv("LIQUI_SPEAK_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def setup_logging() -> logging.Logger:
    """Set up logging configuration for Liqui-Speak."""
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
    return logging.getLogger("liqui_speak")


def get_config() -> dict[str, str | int | float]:
    """
    Get configuration for transcription.

    Returns:
        Configuration dictionary with model paths and settings
    """
    setup_dir = Path.home() / ".liqui_speak"
    models_dir = setup_dir / "models"

    config = {
        "model_dir": str(models_dir),
        "model_path": str(models_dir / MODEL_FILES["model"]),
        "mmproj_path": str(models_dir / MODEL_FILES["mmproj"]),
        "audiodecoder_path": str(models_dir / MODEL_FILES["audiodecoder"]),
        "binary_path": str(models_dir / "runners"),
        "sample_rate": 48000,
        "channels": 1,
        "chunk_duration": 2.0,
        "overlap": 0.5,
        "transcription_timeout": TRANSCRIPTION_TIMEOUT,
    }


    for key in config:
        env_key = f"LIQUI_SPEAK_{key.upper()}"
        if env_key in os.environ:
            if key in ["sample_rate", "channels", "transcription_timeout"]:
                try:
                    config[key] = int(os.environ[env_key])
                except ValueError:
                    config[key] = float(os.environ[env_key])
            elif key in ["chunk_duration", "overlap"]:
                config[key] = float(os.environ[env_key])
            else:
                config[key] = os.environ[env_key]

    return config


def is_configured() -> bool:
    """Check if Liqui-Speak is properly configured."""
    config = get_config()


    required_files = [
        config["model_path"],
        config["mmproj_path"],
        config["audiodecoder_path"],
    ]

    for file_path in required_files:
        if not Path(str(file_path)).exists():
            return False

    return True


def get_setup_dir() -> Path:
    """Get the setup directory path."""
    return Path.home() / ".liqui_speak"


def ensure_setup_dir() -> Path:
    """Ensure setup directory exists and return path."""
    setup_dir = get_setup_dir()
    setup_dir.mkdir(exist_ok=True)
    return setup_dir
