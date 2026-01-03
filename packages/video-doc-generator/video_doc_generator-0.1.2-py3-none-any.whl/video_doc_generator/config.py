"""
配置管理模块

提供配置加载和管理功能。
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """配置类"""

    def __init__(self):
        """加载配置"""
        # 加载 .env 文件
        load_dotenv()

        # 视频解析 API 配置
        self.video_parser_api_key: Optional[str] = os.getenv("VIDEO_PARSER_API_KEY")
        self.video_parser_api_url: Optional[str] = os.getenv(
            "VIDEO_PARSER_API_URL", "https://api.example.com/video/parse"
        )

        # 存储路径
        home = Path.home()
        self.storage_dir = home / ".video_doc_generator"
        self.storage_dir.mkdir(exist_ok=True)
        self.videos_storage_path = self.storage_dir / "videos.json"

        # 默认输出目录
        self.default_output_dir = Path("docs")
