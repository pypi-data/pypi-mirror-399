#!/usr/bin/env python3
"""简单测试：直接调用工具方法"""
import asyncio
import sys
sys.path.insert(0, '/Users/liuzhi/Desktop/notest-l1/data/gongrzhe-audio-mcp-server')

from audio_server import mcp

async def test_tools():
    """测试工具列表"""
    print("Testing tools...")
    
    # 获取工具列表
    tools = mcp._tool_manager._tools
    print(f"Found {len(tools)} tools:")
    for name, tool in tools.items():
        print(f"  - {name}: {tool.description}")
    
    return len(tools)

if __name__ == "__main__":
    count = asyncio.run(test_tools())
    print(f"\nTotal tools: {count}")