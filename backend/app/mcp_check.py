# -*- coding: utf-8 -*-
"""
MCP 连通性验证脚本

用途：一条命令判定百炼 WebSearch MCP / 百度地图 MCP 是否打通（连接→列工具→调用 三步）。

使用方式（在 backend/app 目录下）：
    python mcp_check.py              # 检查全部
    python mcp_check.py search       # 只查百炼 WebSearch
    python mcp_check.py baidu        # 只查百度地图

结果解读（失败时按 hint 修复）：
    401 Unauthorized        -> key 无效（不是对应平台的 key / key 已删除）
    403 / Arrearage         -> key 有效但账户欠费，去阿里云费用中心充值
    list_tools 失败         -> URL 错或服务端异常，检查 DASHSCOPE_BASE_URL
    call_tool quota 类错误  -> 欠费或调用额度用尽
    三步全 OK               -> 完全打通 ✅
"""

import asyncio
import sys

from agents.mcp import MCPServerSse, MCPServerStreamableHttp
from config.settings import settings


def build_search_client() -> MCPServerStreamableHttp:
    """百炼通用联网搜索 MCP（/mcp 为 streamable-HTTP 传输，/sse 已被阿里云下线）"""
    return MCPServerStreamableHttp(
        name="百炼WebSearch",
        params={
            "url": settings.DASHSCOPE_BASE_URL,
            "headers": {"Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}"},
            "timeout": 30,
            "sse_read_timeout": 60,
        },
        cache_tools_list=False,
    )


def build_baidu_client() -> MCPServerSse:
    """百度地图 MCP"""
    return MCPServerSse(
        name="百度地图",
        params={
            "url": f"https://mcp.map.baidu.com/sse?ak={settings.BAIDUMAP_AK}",
            "timeout": 30,
            "sse_read_timeout": 60,
        },
        cache_tools_list=False,
    )


async def check(client: MCPServerSse, call_args: dict) -> bool:
    """对单个 MCP 执行 连接→列工具→调用 三步检查，返回是否全通"""
    print(f"\n{'=' * 60}\n[检查] {client.name}  ->  {client.params['url']}")
    ok = False
    try:
        # ① 建立连接（key 鉴权在这一步）
        await client.connect()
        print("① 建立连接: OK")

        # ② 获取工具列表
        tools = await client.list_tools()
        print(f"② 工具列表: {[t.name for t in tools]}")

        # ③ 真实调用一次（消耗极少量额度）
        tool_name = tools[0].name
        result = await client.call_tool(tool_name, call_args)
        print(f"③ 调用 {tool_name}: OK -> {str(result.content[0])[:80]}")
        print(f"✅ {client.name} 完全打通")
        ok = True

    except Exception as e:
        msg = str(e)
        hint = "服务端/网络异常，检查 URL 与网络代理"
        if "401" in msg or "Unauthorized" in msg:
            hint = "key 无效：确认使用的是对应平台的有效 key"
        elif "403" in msg or "Arrearage" in msg or "good standing" in msg:
            hint = "账户欠费：去阿里云费用中心充值后重试"
        elif "quota" in msg.lower() or "限流" in msg:
            hint = "额度/限流问题：检查平台调用量与余额"
        print(f"❌ 失败: {type(e).__name__} | {msg[:160]}\n   ↳ 修复建议: {hint}")
    finally:
        try:
            await client.cleanup()
        except Exception:
            pass
    return ok


async def main():
    targets = sys.argv[1:] or ["search", "baidu"]
    results = {}

    if "search" in targets:
        results["百炼WebSearch"] = await check(
            build_search_client(), {"query": "今天广州天气"})

    if "baidu" in targets:
        results["百度地图"] = await check(
            build_baidu_client(), {"address": "北京市昌平区"})

    print(f"\n{'=' * 60}\n汇总:")
    for name, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {name}")
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    asyncio.run(main())
