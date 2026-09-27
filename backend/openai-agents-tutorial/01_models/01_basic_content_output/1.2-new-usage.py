from openai import OpenAI
from  dotenv import load_dotenv
import os


# 加载环境变量
load_dotenv()


# 创建客户端 - 需要传入api_key和base_url
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


# API调用（创建响应）
# ⚠️ Responses API（client.responses.create）是 OpenAI 官方独有端点，
#    智谱/硅基流动/百炼等 OpenAI 兼容服务商只实现了 Chat Completions API，
#    用 responses 会 404（如 /v4/responses Not Found）。
#    想练 Responses API 需要 OpenAI 官方 key + 官方 base_url。
# 原写法（仅 OpenAI 官方可用）：
# response = client.responses.create(
#     model=os.getenv("OPENAI_MODEL_NAME"),
#     input="写一个关于独角兽的睡前小故事"
# )
# print(response.output_text)

# # 兼容写法：Chat Completions API（所有 OpenAI 兼容服务商通用）
response = client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL_NAME"),
    messages=[
        {"role": "user", "content": "写一个关于独角兽的睡前小故事"}
    ]
)

print(response.choices[0].message.content)