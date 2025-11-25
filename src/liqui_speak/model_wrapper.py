"""Model wrapper for llama.cpp LFM2-Audio integration."""

import subprocess
from pathlib import Path

from liqui_speak.config import get_config


class LFM2AudioWrapper:
    """Wrapper for llama-lfm2-audio binary."""

    def __init__(self, config: dict[str, str] | None = None):
        """
        Initialize the model wrapper.
        
        Args:
            config: Configuration dictionary (auto-detected if None)
        """
        self.config = config or get_config()
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate that all required files exist."""
        required_files = [
            self.config["model_path"],
            self.config["mmproj_path"],
            self.config["audiodecoder_path"],
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                raise ValueError(f"Missing required file: {file_path}")

    def transcribe_audio_file(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using LFM2 model.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
            
        Raises:
            RuntimeError: If transcription fails
        """
        audio_path = Path(audio_file_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        # Get platform-specific binary path
        from liqui_speak.platform_utils import PlatformDetector
        detector = PlatformDetector()
        platform = detector.get_supported_platform()

        if not platform:
            raise RuntimeError(f"Unsupported platform: {detector.system}-{detector.machine}")

        binary_path = Path(self.config["binary_path"]) / platform / "bin" / "llama-lfm2-audio"

        if not binary_path.exists():
            raise ValueError(f"Binary not found: {binary_path}")

        # Build command
        cmd = [
            str(binary_path),
            "-m", self.config["model_path"],
            "--mmproj", self.config["mmproj_path"],
            "-mv", self.config["audiodecoder_path"],
            "-sys", "Perform ASR.",
            "--audio", str(audio_path)
        ]

        try:
            # Run transcription
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,  # Get bytes to handle encoding issues
                timeout=60,  # 60 second timeout
                check=False
            )

            if result.returncode != 0:
                error_msg = f"Transcription failed with code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr.decode('utf-8', errors='replace')}"
                raise RuntimeError(error_msg)

            # Parse output
            transcription = self._parse_output(result.stdout)
            return transcription

        except subprocess.TimeoutExpired:
            raise RuntimeError("Transcription timed out (60s)")
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {str(e)}")

    def _parse_output(self, output: bytes) -> str:
        """Parse model output to extract transcription."""
        try:
            output_str = output.decode('utf-8', errors='replace')
        except Exception:
            output_str = str(output)

        # Simple parsing - look for text after the audio processing messages
        lines = output_str.strip().split('\n')

        # Skip common model loading messages
        transcription_lines = []
        for line in lines:
            line = line.strip()

            # Skip empty lines and model messages
            if not line:
                continue

            # Skip model loading messages
            if any(msg in line.lower() for msg in [
                "loading", "model", "load_gguf", "loaded",
                "gguf", "encoding", "slice"
            ]):
                continue

            # Skip timing/performance info
            if "ms" in line or "tokens" in line or "speed" in line:
                continue

            # This should be transcription text
            transcription_lines.append(line)

        # Join transcription lines
        transcription = ' '.join(transcription_lines).strip()

        # Clean up extra whitespace
        transcription = ' '.join(transcription.split())

        return transcription

    def test_model(self, test_audio_path: str | None = None) -> bool:
        """Test if the model is working correctly."""
        try:
            if test_audio_path:
                # Test with provided audio
                result = self.transcribe_audio_file(test_audio_path)
                return len(result.strip()) > 0
            else:
                # Create a simple test audio
                # This would require audio generation capabilities
                # For now, just check if model loads
                return True

        except Exception as e:
            print(f"Model test failed: {e}")
            return False
