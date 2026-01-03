"""
MCP Time Server - 提供时间服务的 MCP 服务器

这个包提供了一个通过 MCP (Model Context Protocol) 协议
提供时间服务的服务器，支持获取不同时区的当前时间。
"""

__version__ = "0.1.1"
__author__ = "Your Name"
__email__ = "your.email@example.com"

def run_cli():
    """运行命令行接口"""
    from .cli import main
    main()

# 延迟导入，避免在包初始化时加载所有模块
def __getattr__(name):
    if name == "TimeServerMCP":
        from .time_server import TimeServerMCP
        return TimeServerMCP
    elif name == "create_server":
        from .time_server import create_server
        return create_server
    elif name == "server_main":
        from .time_server import main as server_main
        return server_main
    elif name == "cli_main":
        from .cli import main as cli_main
        return cli_main
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")