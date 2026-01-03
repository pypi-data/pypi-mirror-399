"""
NexFramework - AI 对话框架
支持多模型切换、工具调用、流式输出、多会话管理、MCP服务器
"""
from .framework import NexFramework
from .database import Database
from .mcp_client import MCPClient, MCPManager
from ._version import __version__


def get_webserver_app():
    """延迟获取 webserver app，避免在导入时初始化"""
    from .webserver import app
    return app


__author__ = "3w4e"
__all__ = ['NexFramework', 'Database', 'get_webserver_app', 'MCPClient', 'MCPManager', '__version__']
