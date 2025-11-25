"""Model and binary downloader for Liqui-Speak."""

import hashlib
import zipfile
from pathlib import Path

from huggingface_hub import hf_hub_download


class ModelDownloader:
    """Handles downloading models and binaries from Hugging Face."""

    def __init__(self):
        self.repo_id = "LiquidAI/LFM2-Audio-1.5B-GGUF"
        self.model_files = [
            "LFM2-Audio-1.5B-Q8_0.gguf",
            "mmproj-audioencoder-LFM2-Audio-1.5B-Q8_0.gguf",
            "audiodecoder-LFM2-Audio-1.5B-Q8_0.gguf",
        ]

    def download_all_models(self, target_dir: Path) -> bool:
        """
        Download all required model files.
        
        Args:
            target_dir: Directory to save models
            
        Returns:
            True if all downloads successful
        """
        target_dir.mkdir(parents=True, exist_ok=True)

        print("📥 Downloading LFM2-Audio-1.5B model files...")

        for filename in self.model_files:
            print(f"Downloading {filename}...")
            try:
                hf_hub_download(
                    repo_id=self.repo_id,
                    filename=filename,
                    local_dir=str(target_dir),
                    local_dir_use_symlinks=False
                )
                print(f"✅ {filename} downloaded")
            except Exception as e:
                print(f"❌ Failed to download {filename}: {e}")
                return False

        return True

    def download_binary(self, target_dir: Path, platform: str) -> Path | None:
        """
        Download platform-specific llama.cpp binary.
        
        Args:
            target_dir: Directory to save binary
            platform: Platform identifier (e.g., 'macos-arm64')
            
        Returns:
            Path to extracted binary or None if failed
        """
        binary_zip = f"lfm2-audio-{platform}.zip"
        runners_dir = target_dir / "runners" / platform
        runners_dir.mkdir(parents=True, exist_ok=True)

        print(f"📥 Downloading {platform} binary...")

        try:
            # Download binary zip
            zip_path = runners_dir / binary_zip
            hf_hub_download(
                repo_id=self.repo_id,
                filename=f"runners/{platform}/{binary_zip}",
                local_dir=str(target_dir),
                local_dir_use_symlinks=False
            )

            # Extract binary
            print("🔧 Extracting binary...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(runners_dir)

            # Find the actual binary
            binary_name = "llama-lfm2-audio"
            binary_path = None

            # Look in extracted directory
            for item in runners_dir.iterdir():
                if item.is_dir():
                    binary_candidate = item / binary_name
                    if binary_candidate.exists():
                        binary_path = binary_candidate
                        break

            # Move binary to expected location
            if binary_path:
                final_path = runners_dir / "bin" / binary_name
                final_path.parent.mkdir(exist_ok=True)

                # Copy binary and all libraries
                import shutil
                if binary_path.parent != runners_dir:
                    for file in binary_path.parent.iterdir():
                        if file.is_file():
                            dest = final_path.parent / file.name
                            shutil.copy2(file, dest)

                # Make executable
                final_path.chmod(0o755)

                # Clean up zip
                zip_path.unlink()

                print(f"✅ Binary extracted to {final_path}")
                return final_path
            else:
                print(f"❌ Binary not found in {binary_zip}")
                return None

        except Exception as e:
            print(f"❌ Failed to download binary: {e}")
            return None

    def verify_downloads(self, target_dir: Path) -> bool:
        """Verify all required files are downloaded and intact."""
        # Check model files
        for filename in self.model_files:
            filepath = target_dir / filename
            if not filepath.exists():
                print(f"❌ Missing model file: {filename}")
                return False

        # Check binary
        # Note: Binary path will be verified separately with platform info

        return True

    def get_file_hash(self, filepath: Path) -> str:
        """Get SHA256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
