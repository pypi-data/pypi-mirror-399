#!/usr/bin/env python3
"""简单的测试脚本，验证服务器能否正常启动并响应"""
import subprocess
import json
import time
import sys

# 启动服务器
proc = subprocess.Popen(
    ["/Users/liuzhi/Desktop/notest-l1/.venv/bin/python3", "/Users/liuzhi/Desktop/notest-l1/data/gongrzhe-audio-mcp-server/audio_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

try:
    # 发送初始化请求
    init_req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()

    # 等待响应
    time.sleep(2)

    # 发送initialized通知
    initialized = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }

    proc.stdin.write(json.dumps(initialized) + "\n")
    proc.stdin.flush()

    # 等待响应
    time.sleep(2)

    # 获取工具列表
    tools_req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }

    proc.stdin.write(json.dumps(tools_req) + "\n")
    proc.stdin.flush()

    # 等待响应
    time.sleep(5)

    # 读取输出
    proc.stdin.close()
    stdout, stderr = proc.communicate(timeout=5)

    print("STDOUT:", stdout)
    print("STDERR:", stderr)

except Exception as e:
    print(f"Error: {e}")
finally:
    proc.terminate()
    proc.wait()
