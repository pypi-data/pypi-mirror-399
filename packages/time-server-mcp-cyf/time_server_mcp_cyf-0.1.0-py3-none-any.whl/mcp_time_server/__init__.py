"""
MCP Time Server - 提供时间服务的 MCP 服务器

这个包提供了一个通过 MCP (Model Context Protocol) 协议
提供时间服务的服务器，支持获取不同时区的当前时间。
"""

from .time_server import TimeServerMCP, create_server, main as server_main
from .cli import main as cli_main

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "TimeServerMCP",
    "create_server",
    "server_main",
    "cli_main",
]