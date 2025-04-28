import json

buffer = 'data: {"choices":[{"delta":{"content":"后轻仓追多。\n*   **止损位：** 建议将止损位设置在 5.40 元附近，一旦跌破此位置，应果断止损。\n\n**A股市场特点补充说明**\n\n*   A股市场受政策影响较大，注意","role":"assistant"},"index":0}],"created":1745835935,"model":"gemini-2.0-flash","object":"chat.completion.chunk"}'
decoder = json.JSONDecoder()

buffer = buffer[6:]

print(buffer)

while buffer.strip():
    # obj, idx = decoder.raw_decode(buffer)
    # print("Parsed object:", obj)
    # buffer = buffer[idx:].lstrip()  # 移除已解析部分
    _j = json.loads(buffer)
    print(_j)
