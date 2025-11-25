#!/usr/bin/env python3
"""Command-line interface for Liqui-Speak."""

import argparse
import sys
from pathlib import Path

from liqui_speak.setup_manager import SetupManager
from liqui_speak.transcription import transcribe_audio


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Liqui-Speak: Automated audio transcription with LFM2-Audio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  liqui-speak config                    # Setup everything
  liqui-speak transcribe audio.m4a      # Transcribe audio file
  liqui-speak transcribe audio.wav --verbose  # Transcribe with details
  liqui-speak transcribe audio.mp3 --play-audio  # Play audio during transcription
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Install dependencies and download models"
    )
    config_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed setup progress"
    )
    config_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstallation of dependencies"
    )

    # Transcribe command
    transcribe_parser = subparsers.add_parser(
        "transcribe",
        help="Transcribe audio file"
    )
    transcribe_parser.add_argument(
        "audio_file",
        help="Path to audio file (M4A, AAC, WAV, MP3, etc.)"
    )
    transcribe_parser.add_argument(
        "--play-audio",
        action="store_true",
        help="Play audio in background during transcription"
    )
    transcribe_parser.add_argument(
        "--clean-text",
        action="store_true",
        help="Clean transcription with language model"
    )
    transcribe_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed transcription progress"
    )

    # Handle case where no command is specified
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    # Handle case where first argument is not a command (assume transcribe)
    if len(sys.argv) > 1 and sys.argv[1] not in ['config', 'transcribe', '-h', '--help']:
        # Assume it's an audio file, add 'transcribe' command
        sys.argv.insert(1, 'transcribe')

    args = parser.parse_args()

    try:
        if args.command == "config":
            return handle_config(args)
        elif args.command == "transcribe":
            return handle_transcribe(args)
        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\n❌ Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def handle_config(args) -> int:
    """Handle config command."""
    print("🚀 Starting Liqui-Speak configuration...")

    setup_manager = SetupManager()

    if args.force:
        print("🔄 Force mode enabled - reinstalling everything")

    success = setup_manager.run_full_setup(verbose=args.verbose)

    if success:
        print("\n🎉 Configuration complete!")
        print("💡 You can now transcribe audio files:")
        print("   liqui-speak transcribe audio.m4a")
        print("   liqui-speak audio.m4a")
        return 0
    else:
        print("\n❌ Configuration failed. Check the logs above.")
        return 1


def handle_transcribe(args) -> int:
    """Handle transcribe command."""
    audio_file = Path(args.audio_file)

    if not audio_file.exists():
        if args.verbose:
            print(f"❌ Audio file not found: {audio_file}")
        return 1

    if args.verbose:
        print(f"🎵 Transcribing: {audio_file.name}")

    try:
        result = transcribe_audio(
            str(audio_file),
            play_audio=args.play_audio,
            clean_text=args.clean_text,
            verbose=args.verbose
        )

        if result:
            # Only print transcription result, no labels or formatting
            print(result)
            return 0
        else:
            if args.verbose:
                print("❌ Transcription failed")
            return 1

    except Exception as e:
        if args.verbose:
            print(f"❌ Transcription error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
