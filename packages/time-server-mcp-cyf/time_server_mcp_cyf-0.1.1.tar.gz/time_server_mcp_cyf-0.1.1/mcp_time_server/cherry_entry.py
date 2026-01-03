#!/usr/bin/env python3
"""
Cherry Studio 专用入口点
这个脚本专门用于在 Cherry Studio 中运行 MCP 服务器
"""

import sys
import os

# 确保当前目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Cherry Studio 入口点"""
    print("Cherry Studio MCP 服务器启动", file=sys.stderr)

    try:
        # 直接导入模块，避免包结构问题
        from time_server import TimeServerMCP

        print("创建服务器实例...", file=sys.stderr)
        server = TimeServerMCP(name="time-server")

        print("启动 stdio 传输模式...", file=sys.stderr)
        server.run(transport="stdio")

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()