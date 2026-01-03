"""
Video Doc Generator - 视频转文档生成器

一个能够管理视频链接，调用视频解析 API，并将视频内容转换为专业文档的 Python 包。
"""

__version__ = "0.1.2"

from video_doc_generator.config import Config
from video_doc_generator.generator import DocumentGenerator
from video_doc_generator.manager import VideoManager
from video_doc_generator.models import VideoMetadata, VideoParseResult, VideoTranscript
from video_doc_generator.parser import VideoParser

__all__ = [
    "Config",
    "VideoManager",
    "VideoParser",
    "DocumentGenerator",
    "VideoMetadata",
    "VideoTranscript",
    "VideoParseResult",
]
