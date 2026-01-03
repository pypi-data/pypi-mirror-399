"""
文档生成模块

将视频内容转换为专业文档和分析说明。
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from video_doc_generator.models import VideoParseResult


class DocumentGenerator:
    """文档生成器"""

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化文档生成器

        Args:
            output_dir: 输出目录，默认为当前目录下的 docs 文件夹
        """
        if output_dir is None:
            output_dir = "docs"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_markdown(
        self,
        parse_result: VideoParseResult,
        filename: Optional[str] = None,
    ) -> Path:
        """
        生成 Markdown 格式文档

        Args:
            parse_result: 视频解析结果
            filename: 输出文件名，默认为视频标题或时间戳

        Returns:
            生成的文件路径
        """
        metadata = parse_result.metadata
        transcript = parse_result.transcript

        # 生成文件名
        if filename is None:
            if metadata.title:
                # 清理标题作为文件名
                filename = "".join(c for c in metadata.title if c.isalnum() or c in (" ", "-", "_"))
                filename = filename.strip().replace(" ", "_")
            else:
                filename = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}.md"

        filepath = self.output_dir / filename

        # 生成 Markdown 内容
        content = self._build_markdown_content(parse_result)

        # 写入文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def _build_markdown_content(self, parse_result: VideoParseResult) -> str:
        """构建 Markdown 内容"""
        metadata = parse_result.metadata
        transcript = parse_result.transcript

        lines = []

        # 标题
        title = metadata.title or "未命名视频"
        lines.append(f"# {title}\n")

        # 元数据
        lines.append("## 视频信息\n")
        lines.append(f"- **URL**: {metadata.url}\n")
        if metadata.platform:
            lines.append(f"- **平台**: {metadata.platform}\n")
        if metadata.author:
            lines.append(f"- **作者**: {metadata.author}\n")
        if metadata.duration:
            minutes = metadata.duration // 60
            seconds = metadata.duration % 60
            lines.append(f"- **时长**: {minutes}分{seconds}秒\n")
        if metadata.thumbnail:
            lines.append(f"- **缩略图**: ![Thumbnail]({metadata.thumbnail})\n")
        lines.append(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("\n")

        # 描述
        if metadata.description:
            lines.append("## 视频描述\n")
            lines.append(f"{metadata.description}\n")
            lines.append("\n")

        # 转录文本
        if transcript and transcript.text:
            lines.append("## 视频内容\n")
            lines.append("### 完整转录\n")
            lines.append(f"{transcript.text}\n")
            lines.append("\n")

            # 如果有分段信息
            if transcript.segments:
                lines.append("### 分段内容\n")
                for i, segment in enumerate(transcript.segments, 1):
                    start_time = segment.get("start", 0)
                    end_time = segment.get("end", 0)
                    text = segment.get("text", "")
                    lines.append(f"#### 片段 {i} ({self._format_time(start_time)} - {self._format_time(end_time)})\n")
                    lines.append(f"{text}\n")
                    lines.append("\n")

        # 分析说明
        lines.append("## 内容分析\n")
        analysis = self._generate_analysis(parse_result)
        lines.append(analysis)
        lines.append("\n")

        # 关键点
        lines.append("## 关键要点\n")
        key_points = self._extract_key_points(parse_result)
        for point in key_points:
            lines.append(f"- {point}\n")
        lines.append("\n")

        return "".join(lines)

    def _format_time(self, seconds: float) -> str:
        """格式化时间为 MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _generate_analysis(self, parse_result: VideoParseResult) -> str:
        """生成内容分析"""
        metadata = parse_result.metadata
        transcript = parse_result.transcript

        analysis = []

        if transcript and transcript.text:
            word_count = len(transcript.text.split())
            analysis.append(f"本视频转录文本共包含约 {word_count} 个词。")

            if metadata.duration:
                words_per_minute = word_count / (metadata.duration / 60) if metadata.duration > 0 else 0
                analysis.append(f"语速约为每分钟 {int(words_per_minute)} 个词。")

        if not analysis:
            analysis.append("暂无详细分析数据。")

        return " ".join(analysis)

    def _extract_key_points(self, parse_result: VideoParseResult) -> list:
        """提取关键要点"""
        transcript = parse_result.transcript

        if not transcript or not transcript.text:
            return ["暂无转录内容"]

        # 简单的关键点提取（可以根据需要改进）
        text = transcript.text
        sentences = text.split("。")
        key_points = []

        # 提取前几个较长的句子作为关键点
        long_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        key_points = long_sentences[:5]  # 取前5个

        if not key_points:
            key_points = ["视频内容已转录，请查看完整转录部分"]

        return key_points
