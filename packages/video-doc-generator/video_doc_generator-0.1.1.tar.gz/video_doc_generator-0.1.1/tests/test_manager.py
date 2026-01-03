"""测试视频管理器"""

import tempfile
from pathlib import Path

import pytest

from video_doc_generator.manager import VideoLink, VideoManager


def test_video_link_platform_detection():
    """测试视频平台检测"""
    # YouTube
    link = VideoLink(url="https://www.youtube.com/watch?v=test")
    assert link.platform == "youtube"

    # Bilibili
    link = VideoLink(url="https://www.bilibili.com/video/BV123456")
    assert link.platform == "bilibili"

    # Vimeo
    link = VideoLink(url="https://vimeo.com/123456")
    assert link.platform == "vimeo"

    # Unknown
    link = VideoLink(url="https://example.com/video")
    assert link.platform == "unknown"


def test_video_manager_add():
    """测试添加视频"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "videos.json"
        manager = VideoManager(storage_path=str(storage_path))

        video = manager.add("https://www.youtube.com/watch?v=test", title="Test Video")
        assert video.url == "https://www.youtube.com/watch?v=test"
        assert video.title == "Test Video"
        assert video.platform == "youtube"
        assert manager.count() == 1


def test_video_manager_remove():
    """测试删除视频"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "videos.json"
        manager = VideoManager(storage_path=str(storage_path))

        url = "https://www.youtube.com/watch?v=test"
        manager.add(url)
        assert manager.count() == 1

        assert manager.remove(url) is True
        assert manager.count() == 0

        assert manager.remove(url) is False


def test_video_manager_get():
    """测试获取视频"""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "videos.json"
        manager = VideoManager(storage_path=str(storage_path))

        url = "https://www.youtube.com/watch?v=test"
        manager.add(url, title="Test Video")

        video = manager.get(url)
        assert video is not None
        assert video.title == "Test Video"

        assert manager.get("https://example.com/not-exist") is None
