# YZ-OpenAI

有赞 LLM 统一调用库 - 支持 Chat 对话、Podcast TTS、ASR 语音识别

## 安装

```bash
pip install yz-openai
```

## 使用示例

### 1. Chat 对话

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    async with YzOpenAI(provider="volcengine", api_key="your-api-key") as client:
        # 非流式调用
        result = await client.chat.completion(
            model="doubao-pro-32k",
            messages=[{"role": "user", "content": "你好"}]
        )
        print(result.message.content)

        # 流式调用
        async for chunk in client.chat.completion(
            model="doubao-pro-32k",
            messages=[{"role": "user", "content": "写一篇文章"}],
            stream=True
        ):
            print(chunk["message"]["content"], end="", flush=True)

asyncio.run(main())
```

### 2. Podcast TTS - 生成播客

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    client = YzOpenAI(
        provider="volcengine",
        app_id="your-app-id",
        access_key="your-access-key"
    )

    # 根据文档URL生成
    result = await client.podcast.generate({
        "action": 0,
        "input_url": "https://example.com/document.pdf",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ],
        "audio_format": "mp3"
    })

    # 根据文本生成
    result = await client.podcast.generate({
        "action": 0,
        "input_text": "人工智能正在改变我们的生活...",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ]
    })

    # 根据对话文本生成
    result = await client.podcast.generate({
        "action": 3,
        "nlp_texts": [
            {"speaker": "zh_male_dayixiansheng_v2_saturn_bigtts", "text": "你好"},
            {"speaker": "zh_female_mizaitongxue_v2_saturn_bigtts", "text": "你好"}
        ]
    })

    # 保存音频
    with open("podcast.mp3", "wb") as f:
        f.write(result.audio_data)

    await client.close()

asyncio.run(main())
```

### 3. ASR 语音识别

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    client = YzOpenAI(
        provider="volcengine",
        app_id="your-app-id",
        access_key="your-access-key"
    )

    # 使用URL
    result = await client.asr.transcribe({
        "file_url": "https://example.com/audio.mp3"
    })

    # 使用本地文件
    result = await client.asr.transcribe({
        "file_path": "/path/to/audio.mp3",
        "enable_itn": True,
        "enable_punc": True
    })

    print(f"识别文本: {result.text}")
    await client.close()

asyncio.run(main())
```

## 异常处理

```python
from yz_openai.base.exceptions import YzOpenAIException, YzOpenAIErrorCode

try:
    result = await client.chat.completion(...)
except YzOpenAIException as e:
    print(f"错误码: {e.code}")
    print(f"错误信息: {e.message}")
```

---

**YZ-OpenAI - 让 LLM 调用更简单** 🚀
