# Python API 使用範例

import asyncio
import nanmai_tts

async def basic_usage():
    print('=== 基本使用方式 ===')
    # 建立 Communicate 實例
    communicate = nanmai_tts.Communicate('你好世界', 'DeepSeek')
    
    # 方法1: 儲存到檔案
    await communicate.save('hello.mp3')
    print('✓ 已儲存到 hello.mp3')
    
    # 方法2: 取得音頻數據
    audio_data = await communicate.get_audio_data()
    print(f'✓ 取得音頻數據: {len(audio_data)} bytes')
    
    # 方法3: 串流處理
    print('串流處理:')
    async for chunk in communicate.stream():
        if chunk['type'] == 'audio':
            print(f'  收到音頻塊: {len(chunk["data"])} bytes')

asyncio.run(basic_usage())

