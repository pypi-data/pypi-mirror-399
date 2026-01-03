"""
视频解析 API 提供商接口

定义视频解析 API 提供商的抽象接口，支持多种 API 提供商。
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional

from video_doc_generator.parser import VideoParseResult


class VideoParserProvider(ABC):
    """视频解析 API 提供商抽象基类"""

    @abstractmethod
    def parse(self, video_url: str, **kwargs) -> VideoParseResult:
        """
        解析视频

        Args:
            video_url: 视频 URL
            **kwargs: 其他参数

        Returns:
            VideoParseResult 对象
        """
        pass

    @abstractmethod
    async def parse_async(self, video_url: str, **kwargs) -> VideoParseResult:
        """
        异步解析视频

        Args:
            video_url: 视频 URL
            **kwargs: 其他参数

        Returns:
            VideoParseResult 对象
        """
        pass

    @staticmethod
    @abstractmethod
    def get_provider_name() -> str:
        """获取提供商名称"""
        pass

