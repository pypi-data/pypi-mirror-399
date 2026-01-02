import inspector
from typing import Optional
from datetime import datetime
import pytz
from mcp.server.fastmcp import FastMCP
import sys


class TimeServerMCP:
    """MCP 时间服务器类"""

    def __init__(self, name: str = "time-server"):
        self.mcp = FastMCP(name)
        self._register_tools()

    def _register_tools(self):
        """注册所有工具函数"""

        @self.mcp.tool()
        def get_current_time(timezone: Optional[str] = None) -> str:
            """获取当前时间的工具函数

            Args:
                timezone: 可选参数，时区字符串，例如 "Asia/Shanghai"、"America/New_York"
                          如果不提供，将使用系统默认时区

            Returns:
                格式化的当前时间字符串
            """
            try:
                if timezone:
                    # 如果提供了时区参数，使用指定的时区
                    tz = pytz.timezone(timezone)
                    current_time = datetime.now(tz)
                else:
                    # 如果没有提供时区参数，使用系统默认时区
                    current_time = datetime.now()

                # 格式化时间字符串
                # 格式：YYYY-MM-DD HH:MM:SS.SSSSSS 时区名称
                return current_time.strftime("%Y-%m-%d %H:%M:%S.%f %Z")
            except pytz.exceptions.UnknownTimeZoneError:
                # 处理无效的时区参数
                return f"错误：未知的时区 '{timezone}'"

    def run(self, transport: str = "stdio"):
        """运行 MCP 服务器"""
        self.mcp.run(transport=transport)


def create_server() -> TimeServerMCP:
    """创建并返回时间服务器实例"""
    return TimeServerMCP()


def main():
    """主函数，启动 MCP 服务器"""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()