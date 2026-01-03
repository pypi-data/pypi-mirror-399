# nanmai-tts

Async Python library for Nanmai TTS (DeepSeek/Kimi voices).

This package provides an easy-to-use interface for the Nanmai AI text-to-speech service, featuring high-quality Chinese voices. It follows the same design pattern as [edge-tts](https://github.com/rany2/edge-tts) for consistency.

## Installation

```bash
pip install nanmai-tts
```

## Usage

### Basic Usage

```python
import asyncio
import nanmai_tts

async def main():
    # Create a Communicate instance
    communicate = nanmai_tts.Communicate("你好世界", "DeepSeek")

    # Get audio data
    audio_data = await communicate.get_audio_data()

    # Or save directly to file
    await communicate.save("output.mp3")

asyncio.run(main())
```

### Streaming

```python
async def stream_audio():
    communicate = nanmai_tts.Communicate("Hello world", "Kimi")

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            # Process audio chunk
            print(f"Received {len(chunk['data'])} bytes of audio")
```

### CLI Usage

```bash
nanmai-tts --text "你好世界" --voice DeepSeek --write-media output.mp3
```

## Available Voices

- **DeepSeek**: Male voice, optimized for Chinese text
- **Kimi**: Female voice, optimized for Chinese text

## API Reference

### Communicate Class

- `__init__(text: str, voice: str = "DeepSeek")`: Initialize with text and voice
- `stream()`: Async generator yielding audio chunks
- `save(filename: str)`: Save audio to file
- `get_audio_data() -> bytes`: Get complete audio data

## Requirements

- Python 3.8+
- aiohttp

## License

This project is for educational and research purposes. The underlying Nanmai TTS API is proprietary.

## Disclaimer

This package uses reverse-engineered authentication methods for the Nanmai TTS service. Use at your own risk and in accordance with applicable laws and terms of service.
