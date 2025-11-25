# Liqui-Speak 🎤

**One-command setup for real-time audio transcription using LFM2-Audio-1.5B**

Liqui-Speak automates the entire setup process for audio transcription, handling system dependencies, model downloads, and format conversions automatically.

## 🚀 Quick Start

```bash
# Install the package
pip install liqui-speak

# Run one-time setup (installs everything)
liqui-speak config

# Transcribe any audio file
liqui-speak audio.m4a
```

## ✨ Features

- **🔄 Auto-setup**: Single command installs all dependencies
- **📁 Format support**: M4A, AAC, WAV, MP3, FLAC, and more
- **⚡ Fast conversion**: PyDub-based in-memory processing
- **🎯 Cross-platform**: macOS, Linux, Windows support
- **📦 Complete automation**: Downloads models, binaries, libraries
- **🔧 Zero configuration**: Works out of the box

## 📋 Installation

### Prerequisites

- Python >= 3.12
- libmagic (for audio format detection)
- Package manager: Homebrew (macOS/Linux), apt/yum/pacman (Linux), or Chocolatey (Windows)

**Installing libmagic:**
```bash
# macOS
brew install libmagic

# Ubuntu/Debian
sudo apt-get install libmagic1

# Fedora/RHEL/CentOS
sudo dnf install file-libs

# Arch Linux
sudo pacman -S file

# Windows
pip install python-magic-bin
```

### Install Package

```bash
pip install liqui-speak
```

### First-time Setup

```bash
liqui-speak config
```

This will:

- Install PortAudio and FFmpeg system dependencies
- Download LFM2-Audio-1.5B model files (~1.5GB)
- Download platform-specific llama.cpp binary
- Verify installation

## 🎤 Usage

### Basic Transcription

```bash
# Transcribe any audio file (both formats work)
liqui-speak audio.m4a                    # Simple format
liqui-speak transcribe audio.m4a         # Explicit format

# Or with different file types
liqui-speak recording.wav
liqui-speak podcast.mp3
```

### Advanced Options

```bash
# Play audio during transcription
liqui-speak audio.m4a --play-audio

# Enable text cleaning
liqui-speak audio.wav --clean-text

# Verbose output
liqui-speak audio.mp3 --verbose
```

### Python API

```python
from liqui_speak import transcribe

# Transcribe audio file
text = transcribe("audio.m4a")
print(text)
```

## 🔧 Configuration

### Environment Variables

```bash
export LIQUI_SPEAK_MODEL_DIR="/custom/path"
export LIQUI_SPEAK_SAMPLE_RATE="44100"
```

### Setup Directory

Configuration and models are stored in `~/.liqui_speak/`

## 📊 Supported Formats

**✅ Native support**: WAV, FLAC, OGG, AIFF, MP3
**✅ Auto-converted**: M4A, AAC, ALAC (Apple), WMA
**❌ Not supported**: DRM-protected files

## 🏗️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/abhishekbhakat/liqui-speak.git
cd liqui-speak

# Install with dev dependencies
make install-dev

# Run quality checks
make lint
make type-check
make test
```



## 🔍 Troubleshooting

### "Format not recognized" error

Your file might be M4A with wrong extension. Use:

```bash
liqui-speak config  # Will detect and convert automatically
```

### Missing system dependencies

Run setup again:

```bash
liqui-speak config --verbose
```

### Model download fails

Check internet connection and available disk space (~2GB needed).

### Permission errors

Make sure you have admin/sudo access for system dependency installation.

## 🚀 Performance

- **Setup time**: < 5 minutes (first run)
- **Conversion speed**: < 10% of audio duration
- **Memory usage**: ~2GB during transcription
- **Model size**: ~1.5GB

## 🔗 Dependencies

### Python Packages

- `pydub` - Audio conversion
- `soundfile` - Audio I/O
- `huggingface-hub` - Model downloads
- `click` - CLI framework
- `python-magic` - Format detection

### System Dependencies

- `portaudio` - Audio I/O library
- `ffmpeg` - Audio format support

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test: `make quality`
4. Commit changes: `git commit -am 'Add feature'`
5. Push to branch: `git push origin feature-name`
6. Submit pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/abhishekbhakat/liqui-speak/issues)
- **Discussions**: [GitHub Discussions](https://github.com/abhishekbhakat/liqui-speak/discussions)
- **Discord**: [Join our server](https://discord.gg/your-invite)

## 🙏 Acknowledgments

- **LFM2-Audio-1.5B model**: LiquidAI team
- **llama.cpp**: Georgi Gerganov
- **PyDub**: James Robert
- **Hugging Face**: Model hosting platform
