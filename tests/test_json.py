import json

buffer = '{"id":"019680d31034795677186adbd981a91d","object":"chat.completion.chunk","created":1745918038,"model":"deepseek-ai/DeepSeek-V3","choices":[{"index":0,"delta":{"content":"5.","reasoning_content":""},"finish_reason":""}],"system_fingerprint":"","usage":{"prompt_tokens":3996,"completion_tokens":204,"total_tokens":4200}}{"id":"019680d31034795677186adbd981a91d","object":"chat.completion.chunk","created":1745918038,"model":"deepseek-ai/DeepSeek-V3","choices":[{"index":0,"delta":{"content":"47元","reasoning_content":""},"finish_reason":""}],"system_fingerprint":"","usage":{"prompt_tokens":3996,"completion_tokens":206,"total_tokens":4202}}{"id":"019680d31034795677186adbd981a91d","object":"chat.completion.chunk","created":1745918038,"model":"deepseek-ai/DeepSeek-V3","choices":[{"index":0,"delta":{"content":"）才能","reasoning_content":""},"finish_reason":""}],"system_fingerprint":"","usage":{"prompt_tokens":3996,"completion_tokens":208,"total_tokens":4204}}{"id":"019680d31034795677186adbd981a91d","object":"chat.completion.chunk","created":1745918038,"model":"deepseek-ai/DeepSeek-V3","choices":[{"index":0,"delta":{"content":"确认上升","reasoning_content":""},"finish_reason":""}],"system_fingerprint":"","usage":{"prompt_tokens":3996,"completion_tokens":210,"total_tokens":4206}}'
decoder = json.JSONDecoder()

# buffer = buffer[6:]

# print(buffer)

while buffer.strip():
    obj, idx = decoder.raw_decode(buffer)
    # 格式化输出
    print(f"============================{idx}==========================")
    print(json.dumps(obj, indent=4, ensure_ascii=False))
    print("======================================================")
    buffer = buffer[idx:].lstrip()  # 移除已解析部分
