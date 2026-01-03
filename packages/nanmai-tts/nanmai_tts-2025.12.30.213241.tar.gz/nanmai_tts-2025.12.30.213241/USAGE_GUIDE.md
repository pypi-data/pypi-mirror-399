# Nanmai-TTS 使用指南

安裝 nanmai-tts 後，有多種方式可以使用它來合成語音：

## 📦 安裝

```bash
# 如果是本地安裝
pip install /path/to/nanmai-tts

# 或者如果已發佈到 PyPI
pip install nanmai-tts
```

## 🎵 使用方式

### 1. Python API (程式設計)

#### 基本使用

```python
import asyncio
import nanmai_tts

async def main():
    # 建立 Communicate 實例
    communicate = nanmai_tts.Communicate("你好世界", "DeepSeek")

    # 儲存到檔案
    await communicate.save("hello.mp3")

    # 或者取得音頻數據
    audio_data = await communicate.get_audio_data()
    print(f"取得 {len(audio_data)} bytes 音頻數據")

asyncio.run(main())
```

#### 串流處理

```python
async def stream_example():
    communicate = nanmai_tts.Communicate("測試串流", "Kimi")

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            print(f"收到 {len(chunk['data'])} bytes 音頻數據")
            # 可以即時處理或播放

asyncio.run(stream_example())
```

#### 語音管理

```python
import nanmai_tts

async def voices_example():
    # 取得所有可用語音
    voices = await nanmai_tts.list_voices()
    print(f"可用語音: {len(voices)} 個")

    # 使用 VoicesManager 查找特定語音
    vm = await nanmai_tts.VoicesManager.create()
    female_voices = vm.find(gender="Female")
    print(f"女性語音: {len(female_voices)} 個")

asyncio.run(voices_example())
```

### 2. 命令列工具

#### 基本語音合成

```bash
# 合成並儲存到檔案
nanmai-tts -t "你好，這是語音合成測試" -v DeepSeek -f output.mp3
```

#### 參數說明

- `-t, --text`: 要合成的文字 (必需)
- `-v, --voice`: 語音類型 (DeepSeek 或 Kimi, 預設: DeepSeek)
- `-f, --write-media`: 輸出檔案名稱 (必需)

#### 支援的語音

- `DeepSeek`: 高品質中文語音
- `Kimi`: 高品質中文語音

**注意**: 兩個語音都是女性音色，提供不同的語音特色。

### 3. 進階用法：即時播放

nanmai-tts 支援與媒體播放器（如 mpv）配合，實現邊下載邊播放：

```bash
# 與 mpv 配合即時播放
nanmai-tts -t "你好，這是即時播放測試" -v DeepSeek -f - | mpv -

# 或者使用其他播放器
nanmai-tts -t "測試文字" -v Kimi -f - | vlc -
```

**說明**: `-f -` 表示輸出到標準輸出，透過管道傳給播放器。

### 4. 批次處理

```python
import asyncio
import nanmai_tts

async def batch_synthesis():
    texts = [
        "第一段文字",
        "第二段文字",
        "第三段文字"
    ]

    for i, text in enumerate(texts, 1):
        communicate = nanmai_tts.Communicate(text, "DeepSeek")
        await communicate.save(f"output_{i}.mp3")
        print(f"已生成 output_{i}.mp3")

asyncio.run(batch_synthesis())
```

## 🔧 錯誤處理

```python
import nanmai_tts

async def safe_synthesis():
    try:
        communicate = nanmai_tts.Communicate("測試文字", "DeepSeek")
        await communicate.save("output.mp3")
    except nanmai_tts.NanmaiAPIError as e:
        print(f"API 錯誤: {e}")
    except nanmai_tts.NetworkError as e:
        print(f"網路錯誤: {e}")
    except Exception as e:
        print(f"其他錯誤: {e}")

asyncio.run(safe_synthesis())
```

## 📋 API 參考

### Communicate 類別

- `__init__(text: str, voice: str)`: 初始化
- `stream()`: 非同步串流音頻數據
- `save(filename: str)`: 儲存到檔案
- `get_audio_data()`: 取得完整音頻數據

### 工具函數

- `list_voices()`: 取得可用語音列表
- `VoicesManager`: 語音管理類別

## ⚡ 效能特點

- **真實串流**: 支援邊下載邊播放，降低延遲
- **低記憶體使用**: 不會預載整個音頻檔案
- **非同步設計**: 完全支援 async/await
- **管道友好**: 支援標準輸出，可與其他工具配合

## 🎯 整合到 SpeakUB

安裝 nanmai-tts 後，SpeakUB 的 NanmaiTTSProvider 可以大幅簡化：

```python
# 新的 speakub/tts/engines/nanmai_tts_provider.py
import nanmai_tts
from speakub.tts.engine import TTSEngine

class NanmaiTTSProvider(TTSEngine):
    async def synthesize(self, text: str, voice: str, **kwargs) -> bytes:
        communicate = nanmai_tts.Communicate(text, voice)
        return await communicate.get_audio_data()
```

這樣 SpeakUB 就可以專注於播放控制和使用者介面，而將底層的 TTS 邏輯委派給專門的 nanmai-tts 套件。
