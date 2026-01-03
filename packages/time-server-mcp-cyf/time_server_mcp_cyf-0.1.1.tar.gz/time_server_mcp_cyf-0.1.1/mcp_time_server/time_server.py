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
                    tz = pytz.timezone(timezone)
                    current_time = datetime.now(tz)
                else:
                    current_time = datetime.now()

                return current_time.strftime("%Y-%m-%d %H:%M:%S.%f %Z")
            except pytz.exceptions.UnknownTimeZoneError:
                return f"错误：未知的时区 '{timezone}'"

    def run(self, transport: str = "stdio"):
        """运行 MCP 服务器"""
        # 所有日志输出到 stderr
        print(f"MCP 服务器 '{self.mcp.name}' 启动，传输模式: {transport}", file=sys.stderr)
        print(f"Python 路径: {sys.path}", file=sys.stderr)

        try:
            if transport == "stdio":
                print("进入 stdio 模式，等待 MCP 客户端连接...", file=sys.stderr)
                # 这个调用会阻塞直到连接关闭
                self.mcp.run(transport="stdio")
                print("MCP 连接已关闭", file=sys.stderr)
            else:
                print(f"不支持的传输模式: {transport}", file=sys.stderr)
                sys.exit(1)

        except KeyboardInterrupt:
            print("\n服务器被用户中断", file=sys.stderr)
            sys.exit(0)
        except Exception as e:
            print(f"服务器运行时错误: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)


def create_server() -> TimeServerMCP:
    """创建并返回时间服务器实例"""
    return TimeServerMCP()


def main():
    """主函数，启动 MCP 服务器"""
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()