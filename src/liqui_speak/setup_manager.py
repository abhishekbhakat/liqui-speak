"""Automated setup manager for Liqui-Speak."""

import subprocess
import sys
from pathlib import Path

from liqui_speak.model_downloader import ModelDownloader
from liqui_speak.platform_utils import PlatformDetector


class SetupManager:
    """Handles automatic installation of system dependencies and models."""

    def __init__(self):
        self.platform = PlatformDetector()
        self.model_downloader = ModelDownloader()
        self.setup_dir = Path.home() / ".liqui_speak"
        self.setup_dir.mkdir(exist_ok=True)

    def run_full_setup(self, verbose: bool = True) -> bool:
        """
        Run complete setup process.
        
        Args:
            verbose: Show detailed progress
            
        Returns:
            True if setup successful
        """
        if verbose:
            print("🚀 Starting Liqui-Speak setup...")

        try:
            # Phase 1: System dependencies
            if verbose:
                print("\n📦 Installing system dependencies...")
            self._install_system_dependencies()

            # Phase 2: Python environment
            if verbose:
                print("\n🐍 Setting up Python environment...")
            self._setup_python_environment()

            # Phase 3: Download models
            if verbose:
                print("\n📥 Downloading models...")
            self._download_models()

            # Phase 4: Verify installation
            if verbose:
                print("\n✅ Verifying installation...")
            self._verify_installation()

            if verbose:
                print("\n🎉 Setup complete! You can now use: liqui-speak your_audio.m4a")

            return True

        except Exception as e:
            if verbose:
                print(f"\n❌ Setup failed: {e}")
                print("💡 Try running with --verbose for more details")
            return False

    def _install_system_dependencies(self) -> None:
        """Install PortAudio and FFmpeg system dependencies."""
        system = self.platform.system

        if system == "Darwin":  # macOS
            self._install_macos_dependencies()
        elif system == "Linux":
            self._install_linux_dependencies()
        elif system == "Windows":
            self._install_windows_dependencies()
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

    def _install_macos_dependencies(self) -> None:
        """Install dependencies on macOS."""
        if not self._command_exists("brew"):
            raise RuntimeError("Homebrew not found. Please install from https://brew.sh")

        packages = ["portaudio", "ffmpeg"]
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run(["brew", "install", package], check=True)

    def _install_linux_dependencies(self) -> None:
        """Install dependencies on Linux."""
        # Try apt first (Ubuntu/Debian)
        if self._command_exists("apt-get"):
            packages = ["portaudio19-dev", "ffmpeg"]
            subprocess.run(["sudo", "apt-get", "update"], check=False)
            subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=True)
        # Try yum (CentOS/RHEL)
        elif self._command_exists("yum"):
            packages = ["portaudio-devel", "ffmpeg"]
            subprocess.run(["sudo", "yum", "install", "-y"] + packages, check=True)
        # Try pacman (Arch)
        elif self._command_exists("pacman"):
            packages = ["portaudio", "ffmpeg"]
            subprocess.run(["sudo", "pacman", "-S", "--noconfirm"] + packages, check=True)
        else:
            raise RuntimeError("No supported package manager found (apt/yum/pacman)")

    def _install_windows_dependencies(self) -> None:
        """Install dependencies on Windows."""
        if self._command_exists("choco"):
            packages = ["portaudio", "ffmpeg"]
            for package in packages:
                subprocess.run(["choco", "install", package, "-y"], check=True)
        elif self._command_exists("scoop"):
            subprocess.run(["scoop", "install", "portaudio", "ffmpeg"], check=True)
        else:
            raise RuntimeError(
                "Chocolatey or Scoop not found. "
                "Please install Chocolatey from https://chocolatey.org"
            )

    def _setup_python_environment(self) -> None:
        """Verify Python version and install PyDub if needed."""
        if sys.version_info < (3, 12):
            raise RuntimeError(f"Python >= 3.12 required, found {sys.version}")

        print(f"✅ Python {sys.version.split()[0]} detected")

        # Check if pydub is available
        try:
            import pydub
            print("✅ PyDub already installed")
        except ImportError:
            print("Installing PyDub...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pydub"], check=True)

    def _download_models(self) -> None:
        """Download LFM2-Audio model and binaries."""
        model_dir = self.setup_dir / "models"
        model_dir.mkdir(exist_ok=True)

        # Check if models already exist
        model_files = [
            "LFM2-Audio-1.5B-Q8_0.gguf",
            "mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf",
            "audiodecoder-LFM2-Audio-1.5B-Q8_0.gguf"
        ]

        # Check if all model files exist
        all_models_exist = all((model_dir / filename).exists() for filename in model_files)

        if all_models_exist:
            print("✅ Model files already downloaded")
        else:
            print("📥 Downloading LFM2-Audio-1.5B model files...")
            # Download model files
            self.model_downloader.download_all_models(model_dir)

        # Check if binary exists
        from liqui_speak.platform_utils import PlatformDetector
        detector = PlatformDetector()
        platform = detector.get_supported_platform()

        if platform:
            binary_path = model_dir / "runners" / platform / "bin" / "llama-lfm2-audio"
            if binary_path.exists():
                print(f"✅ Binary already downloaded for {platform}")
            else:
                print(f"📥 Downloading {platform} binary...")
                binary_result = self.model_downloader.download_binary(model_dir, platform)
                if binary_result:
                    print(f"✅ Binary downloaded: {binary_result}")
        else:
            print(f"⚠️  Platform {detector.system}-{detector.machine} not supported for binaries")

    def _verify_installation(self) -> None:
        """Verify that everything is working correctly."""
        # Check system dependencies (ffmpeg is the main CLI tool we need)
        deps = {
            "ffmpeg": self._command_exists("ffmpeg"),
            "pydub": self._check_python_module("pydub"),
        }

        missing = [name for name, installed in deps.items() if not installed]
        if missing:
            raise RuntimeError(f"Missing dependencies: {', '.join(missing)}")

        # Check model files
        model_files = [
            "LFM2-Audio-1.5B-Q8_0.gguf",
            "mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf",
            "audiodecoder-LFM2-Audio-1.5B-Q8_0.gguf"
        ]

        for filename in model_files:
            filepath = self.setup_dir / "models" / filename
            if not filepath.exists():
                raise RuntimeError(f"Missing model file: {filename}")

        print("✅ All dependencies verified")

    def _command_exists(self, command: str) -> bool:
        """Check if a system command exists."""
        try:
            # Use different flags for different commands
            if command == "ffmpeg":
                subprocess.run([command, "-version"],
                             capture_output=True, check=True)
            else:
                subprocess.run([command, "--version"],
                             capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _check_python_module(self, module: str) -> bool:
        """Check if a Python module is installed."""
        try:
            __import__(module)
            return True
        except ImportError:
            return False

    def get_config(self) -> dict[str, str]:
        """Get configuration for transcription."""
        return {
            "model_dir": str(self.setup_dir / "models"),
            "binary_path": str(self.setup_dir / "models" / "llama-lfm2-audio"),
            "sample_rate": "48000",
            "channels": "1",
        }
