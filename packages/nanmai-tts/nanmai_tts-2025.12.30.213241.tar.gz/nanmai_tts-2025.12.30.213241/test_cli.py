#!/usr/bin/env python3
"""Test CLI functionality."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nanmai_tts import Communicate


async def test_cli_functionality():
    """Test what CLI does."""
    print("🧪 Testing CLI-like functionality...")

    try:
        # Simulate CLI arguments
        text = "CLI測試"
        voice = "Kimi"
        output_file = "cli_test.mp3"

        print(f"Synthesizing text with voice '{voice}'...")
        comm = Communicate(text, voice)
        await comm.save(output_file)
        print(f"✓ Saved to {output_file}")

        # Check file exists
        if os.path.exists(output_file):
            size = os.path.getsize(output_file)
            print(f"✓ File created successfully: {size} bytes")
            return True
        else:
            print("❌ File was not created")
            return False

    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Testing CLI functionality...\n")

    success = await test_cli_functionality()

    if success:
        print("\n✅ CLI functionality works!")
        return 0
    else:
        print("\n❌ CLI test failed.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
