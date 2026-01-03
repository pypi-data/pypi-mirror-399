"""
BigGPT API 提供商实现
"""

import os
from typing import Dict, Optional

import aiohttp
import requests

from video_doc_generator.models import VideoMetadata, VideoParseResult, VideoTranscript
from video_doc_generator.parser_provider import VideoParserProvider


class BigGPTProvider(VideoParserProvider):
    """BigGPT API 提供商"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        use_get_method: bool = True,
    ):
        """
        初始化 BigGPT API 提供商

        Args:
            api_key: API 密钥
            api_url: API 地址（可选，如果不提供则使用默认地址）
            use_get_method: 是否使用 GET 方法（默认 True，推荐使用 GET）
        """
        self.api_key = api_key or os.getenv("VIDEO_PARSER_API_KEY") or os.getenv("BIGGPT_API_KEY")
        self.use_get_method = use_get_method

        if api_url:
            self.api_url = api_url
        elif self.api_key and use_get_method:
            # GET 方式：https://api.bibigpt.co/api/open/{token}?url={video_url}
            self.api_url = f"https://api.bibigpt.co/api/open/{self.api_key}"
            self.use_get_method = True
        else:
            # POST 方式
            self.api_url = api_url or os.getenv(
                "VIDEO_PARSER_API_URL", "https://api.bibigpt.co/api/v1/summarizeWithConfig"
            )
            self.use_get_method = False

    def parse(self, video_url: str, **kwargs) -> VideoParseResult:
        """同步解析视频"""
        include_detail = kwargs.get("include_detail", True)

        try:
            if self.use_get_method:
                response = requests.get(
                    self.api_url,
                    params={"url": video_url},
                    timeout=120,
                )
            else:
                headers = {
                    "Content-Type": "application/json",
                }
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                response = requests.post(
                    self.api_url,
                    json={
                        "url": video_url,
                        "includeDetail": include_detail,
                    },
                    headers=headers,
                    timeout=120,
                )

            response.raise_for_status()

            try:
                data = response.json()
            except ValueError:
                data = {"content": response.text}

            if not isinstance(data, dict):
                data = {"content": str(data)}

            return self._parse_response(data, video_url)

        except requests.exceptions.RequestException as e:
            raise Exception(f"BigGPT API 调用失败: {e}")

    async def parse_async(self, video_url: str, **kwargs) -> VideoParseResult:
        """异步解析视频"""
        include_detail = kwargs.get("include_detail", True)

        try:
            async with aiohttp.ClientSession() as session:
                if self.use_get_method:
                    async with session.get(
                        self.api_url,
                        params={"url": video_url},
                        timeout=aiohttp.ClientTimeout(total=120),
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()
                else:
                    headers = {
                        "Content-Type": "application/json",
                    }
                    if self.api_key:
                        headers["Authorization"] = f"Bearer {self.api_key}"

                    async with session.post(
                        self.api_url,
                        json={
                            "url": video_url,
                            "includeDetail": include_detail,
                        },
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=120),
                    ) as response:
                        response.raise_for_status()
                        try:
                            data = await response.json()
                        except Exception:
                            data = {"content": await response.text()}

                if not isinstance(data, dict):
                    data = {"content": str(data)}

                return self._parse_response(data, video_url)

        except aiohttp.ClientError as e:
            raise Exception(f"BigGPT API 调用失败: {e}")

    def _parse_response(self, data: Dict, video_url: str) -> VideoParseResult:
        """解析 API 响应数据"""
        # 提取标题
        title = None
        if isinstance(data, dict):
            if "summary" in data and isinstance(data["summary"], str):
                summary_lines = data["summary"].split("\n")
                found_abstract = False
                for line in summary_lines:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        if "摘要" in line:
                            found_abstract = True
                        continue
                    if line.startswith("-") or line.startswith("*"):
                        continue
                    if found_abstract and len(line) > 10 and len(line) < 200:
                        title = line
                        break

            title = title or data.get("title") or data.get("videoTitle") or data.get("id")

        description = None
        if isinstance(data, dict) and "summary" in data and isinstance(data["summary"], str):
            description = data["summary"][:500]

        metadata = VideoMetadata(
            url=video_url,
            title=title or (f"Video {data.get('id', 'Unknown')}" if isinstance(data, dict) else None),
            description=description,
            duration=None,
            thumbnail=None,
            author=None,
            platform=(
                data.get("service") or self._extract_platform_from_url(video_url)
                if isinstance(data, dict)
                else self._extract_platform_from_url(video_url)
            ),
        )

        # 提取转录文本
        transcript = None
        transcript_text = None

        if isinstance(data, dict):
            if "summary" in data and isinstance(data["summary"], str):
                transcript_text = data["summary"]
            elif "transcript" in data:
                transcript_data = data["transcript"]
                if isinstance(transcript_data, str):
                    transcript_text = transcript_data
                elif isinstance(transcript_data, dict):
                    transcript_text = transcript_data.get("text", "")
            elif "subtitle" in data:
                transcript_text = data["subtitle"] if isinstance(data["subtitle"], str) else ""
            elif "content" in data:
                content = data["content"]
                transcript_text = content if isinstance(content, str) else str(content)

        if transcript_text:
            language = data.get("language") if isinstance(data, dict) else None
            transcript = VideoTranscript(
                text=transcript_text,
                segments=None,
                language=language,
            )

        return VideoParseResult(
            metadata=metadata,
            transcript=transcript,
            raw_data=data,
        )

    @staticmethod
    def _extract_platform_from_url(url: str) -> str:
        """从 URL 中提取平台名称"""
        url_lower = url.lower()
        if "youtube.com" in url_lower or "youtu.be" in url_lower:
            return "youtube"
        elif "bilibili.com" in url_lower:
            return "bilibili"
        elif "tiktok.com" in url_lower:
            return "tiktok"
        elif "vimeo.com" in url_lower:
            return "vimeo"
        else:
            return "unknown"

    @staticmethod
    def get_provider_name() -> str:
        """获取提供商名称"""
        return "bigpt"

