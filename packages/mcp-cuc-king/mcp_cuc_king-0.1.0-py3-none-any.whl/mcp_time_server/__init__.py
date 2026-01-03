"""MCP Time Server - 提供获取当前时间的功能"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
import pytz


mcp = FastMCP("time_server")


@mcp.tool()
def get_current_time(timezone: str = "UTC") -> str:
    """获取当前时间,支持指定时区。"""
    try:
        if timezone.upper() == "UTC":
            current_time = datetime.now(pytz.UTC)
        else:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
        
        return f"当前时间 ({timezone}): {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    
    except pytz.UnknownTimeZoneError:
        return f"错误: 无效的时区 '{timezone}'"


def main():
    """CLI 入口点"""
    mcp.run()
