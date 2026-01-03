#!/usr/bin/env python3
"""
MCP Time Server 主入口点
"""

import sys
import os
import logging
from datetime import datetime
import pytz

# 设置日志级别为INFO，只显示关键信息
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-time-server")

from mcp.server.fastmcp import FastMCP


def run_server(mode: str = "studio"):
    """
    运行MCP时间服务器
    
    Args:
        mode: 运行模式，可以是 "studio", "sse", 或 "streamable-http"
    """
    try:
        # 创建MCP服务器实例
        mcp = FastMCP("time-server")
        
        # 定义工具函数
        @mcp.tool()
        def get_current_time(timezone: str = None) -> str:
            """
            获取当前时间的工具函数
            
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
                    # 获取系统本地时区并将时间转换为带时区的时间
                    local_tz = pytz.timezone(pytz.country_timezones['CN'][0])  # 默认使用中国时区
                    current_time = local_tz.localize(current_time)
                
                return current_time.strftime("%Y-%m-%d %H:%M:%S.%f %Z")
            except pytz.exceptions.UnknownTimeZoneError:
                return f"错误：未知的时区 '{timezone}'"
        
        # 根据模式启动服务器
        if mode == "studio":
            print("启动 STUDIO 模式 (stdio)...")
            from mcp.server.stdio import stdio_server
            import anyio
            
            async def run_stdio():
                async with stdio_server() as (read_stream, write_stream):
                    await mcp._mcp_server.run(
                        read_stream,
                        write_stream,
                        mcp._mcp_server.create_initialization_options()
                    )
            
            anyio.run(run_stdio)
        else:
            print(f"启动 {mode} 模式...")
            mcp.run(transport=mode)
            
    except ImportError as e:
        print(f"错误: 无法导入MCP模块: {e}")
        print("请确保已安装mcp库: pip install mcp")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"服务器启动失败: {e}")
        sys.exit(1)


def main():
    """
    命令行入口点
    """
    print("=" * 60)
    print("          MCP Time Server")
    print("=" * 60)
    print()
    
    # 支持的模式
    modes = ["studio", "sse", "streamable-http"]
    
    print("支持的模式:")
    for i, mode in enumerate(modes):
        print(f"  {i+1}. {mode}")
    print()
    
    # 获取运行模式
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode not in modes:
            print(f"错误: 未知的模式 '{mode}'")
            print(f"可用模式: {', '.join(modes)}")
            sys.exit(1)
    else:
        mode = "studio"
        print("未指定模式，使用默认的 STUDIO 模式")
    
    print()
    print(f"正在启动服务器，模式: {mode}")
    print()
    print("按 Ctrl+C 停止服务器")
    print()
    
    try:
        run_server(mode)
    except KeyboardInterrupt:
        print()
        print("服务器已停止")
    except Exception as e:
        logger.exception(f"服务器运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()