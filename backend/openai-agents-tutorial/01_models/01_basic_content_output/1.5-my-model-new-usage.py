# -*- coding: utf-8 -*-
"""
1.5-my-model-new-usage.py
Created on 2026/9/13 11:33
@author: Allan Lyu
@version: 1.0
@Description: 
"""

import os
from openai import OpenAI
from  dotenv import load_dotenv

# 加载环境变量
load_dotenv()

client = OpenAI(
    api_key=os.getenv("AL_BAILIAN_API_KEY"),
    base_url="https://llm-s3a6zdh6l7xj9614.cn-beijing.maas.aliyuncs.com/api/v2/apps/protocols/compatible-mode/v1",
)

response = client.responses.create(
    model="qwen3.8-27b",
    input="9.9和9.11哪个大？",
    extra_body={
        "enable_thinking": True  # 启用思考模式
    }
)

# 遍历输出项
for item in response.output:
    if item.type == "reasoning":
        # 打印推理过程摘要
        print("【推理过程】")
        for summary in item.summary:
            print(summary.text[:500])  # 截取前500字符
        print()
    elif item.type == "message":
        # 打印最终答案
        print("【最终答案】")
        print(item.content[0].text)