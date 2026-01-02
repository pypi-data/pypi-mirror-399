"""
北京化工大学课程平台PDF下载工具

一个用于登录北化课程平台并下载PPT和PDF文件的Python库。
"""

from .core import GetsPdf, LoginError, NetworkError

__version__ = "0.1.0"
__all__ = ["GetsPdf", "LoginError", "NetworkError"]