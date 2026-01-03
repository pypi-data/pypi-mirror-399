"""
视频解析模块

调用视频解析 API 读取和解析视频内容。
支持多个 API 提供商（BigGPT 等）。
"""

from typing import Optional

# 导入模型（避免循环导入）
from video_doc_generator.models import VideoMetadata, VideoParseResult, VideoTranscript

# 向后兼容：导入默认提供商（延迟导入避免循环）
from video_doc_generator.parser_provider import VideoParserProvider

# 重新导出模型以保持向后兼容
__all__ = ["VideoParser", "VideoMetadata", "VideoTranscript", "VideoParseResult"]


class VideoParser:
    """视频解析器 - 支持多个 API 提供商"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        use_get_method: bool = False,
        provider: Optional[VideoParserProvider] = None,
        provider_name: Optional[str] = None,
    ):
        """
        初始化视频解析器

        Args:
            api_key: 视频解析 API 密钥
            api_url: 视频解析 API 地址（可选，如果不提供则使用默认地址）
            use_get_method: 是否使用 GET 方法（仅对 BigGPT 有效，默认 False，但 BigGPT 推荐使用 True）
            provider: 自定义 API 提供商实例（可选）
            provider_name: 提供商名称（可选，当前支持 'bigpt'，默认使用 BigGPT）
        """
        if provider:
            # 使用自定义提供商
            self.provider = provider
        else:
            # 延迟导入避免循环
            from video_doc_generator.providers.bigpt import BigGPTProvider
            
            # 默认使用 BigGPT 提供商
            provider_name = provider_name or "bigpt"
            if provider_name.lower() == "bigpt":
                self.provider = BigGPTProvider(
                    api_key=api_key,
                    api_url=api_url,
                    use_get_method=use_get_method,
                )
            else:
                raise ValueError(f"不支持的提供商: {provider_name}. 当前支持: 'bigpt'")

    def parse(self, video_url: str, **kwargs) -> VideoParseResult:
        """
        解析视频（同步方法）

        Args:
            video_url: 视频 URL
            **kwargs: 其他参数（如 include_detail 等，根据提供商而定）

        Returns:
            VideoParseResult 对象
        """
        return self.provider.parse(video_url, **kwargs)

    async def parse_async(self, video_url: str, **kwargs) -> VideoParseResult:
        """
        解析视频（异步方法）

        Args:
            video_url: 视频 URL
            **kwargs: 其他参数（如 include_detail 等，根据提供商而定）

        Returns:
            VideoParseResult 对象
        """
        return await self.provider.parse_async(video_url, **kwargs)
