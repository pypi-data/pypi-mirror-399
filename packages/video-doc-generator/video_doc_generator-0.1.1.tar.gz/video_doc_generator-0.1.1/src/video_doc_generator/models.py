"""
视频解析数据模型
"""

from typing import Dict, Optional

from pydantic import BaseModel, HttpUrl


class VideoMetadata(BaseModel):
    """视频元数据模型"""

    url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None  # 秒
    thumbnail: Optional[str] = None
    author: Optional[str] = None
    platform: Optional[str] = None


class VideoTranscript(BaseModel):
    """视频转录文本模型"""

    text: str
    segments: Optional[list] = None  # 分段信息
    language: Optional[str] = None


class VideoParseResult(BaseModel):
    """视频解析结果模型"""

    metadata: VideoMetadata
    transcript: Optional[VideoTranscript] = None
    raw_data: Optional[Dict] = None
