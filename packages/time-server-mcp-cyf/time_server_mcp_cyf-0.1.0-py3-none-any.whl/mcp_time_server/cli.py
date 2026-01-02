import argparse
import sys
from .time_server import TimeServerMCP

def main():
    parser = argparse.ArgumentParser(
        description="MCP Time Server - 提供时间服务的 MCP 服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 使用 stdio 传输
  %(prog)s --transport stdio  # 明确指定 stdio 传输
        """
    )

    parser.add_argument(
        "--transport",
        type=str,
        default="stdio",
        choices=["stdio"],
        help="MCP 传输方式 (默认: stdio)"
    )

    parser.add_argument(
        "--name",
        type=str,
        default="time-server",
        help="服务器名称 (默认: time-server)"
    )

    args = parser.parse_args()

    # 创建并运行服务器
    server = TimeServerMCP(name=args.name)
    server.run(transport=args.transport)


if __name__ == "__main__":
    main()