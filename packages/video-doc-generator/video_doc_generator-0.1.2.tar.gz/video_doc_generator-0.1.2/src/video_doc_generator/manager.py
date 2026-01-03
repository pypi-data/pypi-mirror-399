"""
视频链接管理模块

提供视频链接的添加、删除、查询和批量管理功能。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, HttpUrl, model_validator


class VideoLink(BaseModel):
    """视频链接数据模型"""

    url: HttpUrl
    title: Optional[str] = None
    platform: Optional[str] = None
    added_at: Optional[str] = None
    metadata: Optional[Dict] = None

    @model_validator(mode="after")
    def set_platform(self):
        """如果 platform 未设置，从 URL 中提取"""
        if not self.platform:
            self.platform = self._detect_platform(str(self.url))
        return self

    @staticmethod
    def _detect_platform(url: str) -> str:
        """检测视频平台"""
        domain = urlparse(url).netloc.lower()
        if "youtube.com" in domain or "youtu.be" in domain:
            return "youtube"
        elif "bilibili.com" in domain:
            return "bilibili"
        elif "vimeo.com" in domain:
            return "vimeo"
        else:
            return "unknown"


class VideoManager:
    """视频链接管理器"""

    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化视频管理器

        Args:
            storage_path: 存储文件路径，默认为 ~/.video_doc_generator/videos.json
        """
        if storage_path is None:
            home = Path.home()
            storage_dir = home / ".video_doc_generator"
            storage_dir.mkdir(exist_ok=True)
            storage_path = str(storage_dir / "videos.json")

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._videos: List[VideoLink] = []
        self._load()

    def _load(self) -> None:
        """从文件加载视频链接"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._videos = [VideoLink(**item) for item in data]
            except (json.JSONDecodeError, Exception) as e:
                print(f"加载视频数据失败: {e}")
                self._videos = []

    def _save(self) -> None:
        """保存视频链接到文件"""
        try:
            # 使用 model_dump 的 mode='json' 来确保 URL 正确序列化
            data = [video.model_dump(mode='json') for video in self._videos]
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存视频数据失败: {e}")

    def add(self, url: str, title: Optional[str] = None, metadata: Optional[Dict] = None) -> VideoLink:
        """
        添加视频链接

        Args:
            url: 视频 URL
            title: 视频标题（可选）
            metadata: 额外元数据（可选）

        Returns:
            创建的 VideoLink 对象
        """
        from datetime import datetime

        video = VideoLink(
            url=url,
            title=title,
            added_at=datetime.now().isoformat(),
            metadata=metadata or {},
        )

        # 检测平台
        if not video.platform:
            video.platform = VideoLink._detect_platform(str(url))

        self._videos.append(video)
        self._save()
        return video

    def remove(self, url: str) -> bool:
        """
        删除视频链接

        Args:
            url: 要删除的视频 URL

        Returns:
            是否成功删除
        """
        initial_count = len(self._videos)
        self._videos = [v for v in self._videos if str(v.url) != url]
        removed = len(self._videos) < initial_count
        if removed:
            self._save()
        return removed

    def get(self, url: str) -> Optional[VideoLink]:
        """
        获取指定 URL 的视频链接

        Args:
            url: 视频 URL

        Returns:
            VideoLink 对象，如果不存在则返回 None
        """
        for video in self._videos:
            if str(video.url) == url:
                return video
        return None

    def list_all(self) -> List[VideoLink]:
        """
        获取所有视频链接

        Returns:
            所有视频链接的列表
        """
        return self._videos.copy()

    def count(self) -> int:
        """
        获取视频链接数量

        Returns:
            视频链接总数
        """
        return len(self._videos)

    def clear(self) -> None:
        """清空所有视频链接"""
        self._videos = []
        self._save()
