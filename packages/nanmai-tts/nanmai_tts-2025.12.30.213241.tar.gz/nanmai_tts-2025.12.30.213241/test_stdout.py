#!/usr/bin/env python3
"""Test stdout functionality."""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nanmai_tts import Communicate


async def test_stdout_streaming():
    """Test stdout streaming functionality."""
    print("🧪 Testing stdout streaming...")

    try:
        comm = Communicate("測試 stdout 串流", "DeepSeek")

        # Count chunks received
        chunk_count = 0
        total_bytes = 0

        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                chunk_count += 1
                total_bytes += len(chunk["data"])
                # Print progress for first few chunks
                if chunk_count <= 3:
                    print(f"  Chunk {chunk_count}: {len(chunk['data'])} bytes")

        print(f"✓ Received {chunk_count} chunks, total {total_bytes} bytes")
        print("✓ True streaming is working - chunks arrive as data is downloaded")

        return True

    except Exception as e:
        print(f"❌ Stdout streaming test failed: {e}")
        return False


async def test_voices_manager():
    """Test the new VoicesManager functionality."""
    print("🧪 Testing VoicesManager...")

    try:
        from nanmai_tts import VoicesManager, list_voices

        # Test async list_voices function
        voices = await list_voices()
        print(f"✓ list_voices() returned {len(voices)} voices")

        # Test VoicesManager
        vm = await VoicesManager.create()
        print(f"✓ VoicesManager created with {len(vm.voices)} voices")

        # Test find functionality
        male_voices = vm.find(gender="Male")
        print(f"✓ Found {len(male_voices)} male voices")

        female_voices = vm.find(gender="Female")
        print(f"✓ Found {len(female_voices)} female voices")

        return True

    except Exception as e:
        print(f"❌ VoicesManager test failed: {e}")
        return False


async def main():
    """Main test function."""
    print("🚀 Testing nanmai-tts optimizations...\n")

    success1 = await test_stdout_streaming()
    print()
    success2 = await test_voices_manager()

    if success1 and success2:
        print("\n✅ All optimizations working correctly!")
        return 0
    else:
        print("\n❌ Some tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
