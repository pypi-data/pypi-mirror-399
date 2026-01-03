"""CLI utilities for nanmai-tts."""

import argparse
import asyncio
import sys

from .communicate import Communicate
from .exceptions import NanmaiTTSException


async def _main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="Nanmai TTS CLI")
    parser.add_argument("-t", "--text", help="Text to speak")
    parser.add_argument("-v", "--voice", default="DeepSeek",
                       choices=["DeepSeek", "Kimi"], help="Voice (default: DeepSeek)")
    parser.add_argument("-f", "--write-media", help="Output MP3 file (use '-' for stdout)")
    parser.add_argument("-l", "--list-voices", action="store_true",
                       help="List available voices and exit")

    args = parser.parse_args()

    # Handle list voices request
    if args.list_voices:
        from .voices import list_voices
        voices = await list_voices()
        print("Available voices:")
        for voice in voices:
            print(f"  {voice['name']} ({voice['gender']}, {voice['locale']})")
        return

    # Validate required arguments for synthesis
    if not args.text:
        parser.error("--text is required for synthesis")
    if not args.write_media:
        parser.error("--write-media is required for synthesis")

    try:
        comm = Communicate(args.text, args.voice)

        if args.write_media == "-":
            # Output to stdout for piping (e.g., to mpv)
            # Use stderr for progress messages to avoid corrupting binary output
            print(f"Synthesizing text with voice '{args.voice}' to stdout...",
                  file=sys.stderr)

            # Write binary data directly to stdout buffer
            stream = sys.stdout.buffer
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    stream.write(chunk["data"])
                    stream.flush()  # Ensure data is sent immediately for streaming

            print("✓ Audio data sent to stdout", file=sys.stderr)
        else:
            # Normal file output
            print(f"Synthesizing text with voice '{args.voice}'...")
            await comm.save(args.write_media)
            print(f"✓ Saved to {args.write_media}")

    except NanmaiTTSException as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user", file=sys.stderr)
        sys.exit(1)
