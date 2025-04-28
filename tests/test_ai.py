import asyncio
import os
from dotenv import load_dotenv
import httpx
import json

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
API_MODEL = os.getenv("API_MODEL", "gpt-3.5-turbo")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", 60))

API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

print(API_URL, API_KEY, API_MODEL, API_TIMEOUT)


async def stream_openai():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": API_MODEL,
        "messages": [{"role": "user", "content": "解释一下Python中的装饰器是什么？"}],
        "stream": True,
    }

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", API_URL, headers=headers, json=data
        ) as response:
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    with open("output.txt", "w+") as f:
                        f.write(line.strip())
                    if line:
                        decoded_line = line.strip()
                        if decoded_line.startswith("data:"):
                            content = decoded_line[5:].strip()
                            if content != "[DONE]":
                                try:
                                    data = json.loads(content)
                                    delta = data["choices"][0]["delta"]
                                    if "content" in delta:
                                        print(delta["content"], end="", flush=True)
                                except json.JSONDecodeError:
                                    continue
            else:
                # 修复：使用aiter_text()读取错误信息
                error_text = ""
                async for chunk in response.aiter_text():
                    error_text += chunk
                print(f"Error: {response.status_code}, {error_text}")


# 运行异步函数
asyncio.run(stream_openai())
