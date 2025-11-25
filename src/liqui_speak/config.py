"""Configuration management for Liqui-Speak."""

import os
from pathlib import Path


def get_config() -> dict[str, str]:
    """
    Get configuration for transcription.
    
    Returns:
        Configuration dictionary with model paths and settings
    """
    setup_dir = Path.home() / ".liqui_speak"
    models_dir = setup_dir / "models"

    config = {
        "model_dir": str(models_dir),
        "model_path": str(models_dir / "LFM2-Audio-1.5B-Q8_0.gguf"),
        "mmproj_path": str(models_dir / "mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf"),
        "audiodecoder_path": str(models_dir / "audiodecoder-LFM2-Audio-1.5B-Q8_0.gguf"),
        "binary_path": str(models_dir / "runners"),
        "sample_rate": "48000",
        "channels": "1",
        "chunk_duration": "2.0",
        "overlap": "0.5",
    }

    # Override with environment variables if present
    for key in config:
        env_key = f"LIQUI_SPEAK_{key.upper()}"
        if env_key in os.environ:
            config[key] = os.environ[env_key]

    return config


def is_configured() -> bool:
    """Check if Liqui-Speak is properly configured."""
    config = get_config()

    # Check if model files exist
    required_files = [
        config["model_path"],
        config["mmproj_path"],
        config["audiodecoder_path"],
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
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
