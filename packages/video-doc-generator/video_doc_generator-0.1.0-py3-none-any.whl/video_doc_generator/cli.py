"""
命令行接口模块

提供 CLI 工具来使用视频转文档生成器。
"""

import os
from pathlib import Path

import click

from video_doc_generator.generator import DocumentGenerator
from video_doc_generator.manager import VideoManager
from video_doc_generator.parser import VideoParser


@click.group()
@click.version_option()
def cli():
    """Video Doc Generator - 视频转文档生成器"""
    pass


@cli.command()
@click.argument("url")
@click.option("--title", help="视频标题")
def add(url: str, title: str):
    """添加视频链接"""
    manager = VideoManager()
    video = manager.add(url, title=title)
    click.echo(f"✓ 已添加视频: {video.title or url}")
    click.echo(f"  平台: {video.platform}")


@cli.command()
@click.argument("url")
def remove(url: str):
    """删除视频链接"""
    manager = VideoManager()
    if manager.remove(url):
        click.echo(f"✓ 已删除视频: {url}")
    else:
        click.echo(f"✗ 未找到视频: {url}")


@cli.command()
def list():
    """列出所有视频链接"""
    manager = VideoManager()
    videos = manager.list_all()

    if not videos:
        click.echo("暂无视频链接")
        return

    click.echo(f"共 {len(videos)} 个视频:\n")
    for i, video in enumerate(videos, 1):
        click.echo(f"{i}. {video.title or str(video.url)}")
        click.echo(f"   URL: {video.url}")
        click.echo(f"   平台: {video.platform}")
        click.echo()


@cli.command()
@click.argument("url")
@click.option("--output-dir", default="docs", help="输出目录")
@click.option("--api-key", envvar="VIDEO_PARSER_API_KEY", help="视频解析 API 密钥")
@click.option("--api-url", envvar="VIDEO_PARSER_API_URL", help="视频解析 API 地址")
@click.option("--use-get", is_flag=True, default=True, help="使用 GET 方法（BigGPT 推荐，默认启用）")
def parse(url: str, output_dir: str, api_key: str, api_url: str, use_get: bool):
    """解析视频并生成文档"""
    click.echo(f"正在解析视频: {url}")

    # 初始化解析器（默认使用 BigGPT，推荐 GET 方法）
    parser = VideoParser(api_key=api_key, api_url=api_url, use_get_method=use_get)

    try:
        # 解析视频
        result = parser.parse(url)
        click.echo("✓ 视频解析成功")

        # 生成文档
        generator = DocumentGenerator(output_dir=output_dir)
        filepath = generator.generate_markdown(result)
        click.echo(f"✓ 文档已生成: {filepath}")

    except Exception as e:
        click.echo(f"✗ 错误: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--output-dir", default="docs", help="输出目录")
@click.option("--api-key", envvar="VIDEO_PARSER_API_KEY", help="视频解析 API 密钥")
@click.option("--api-url", envvar="VIDEO_PARSER_API_URL", help="视频解析 API 地址")
@click.option("--use-get", is_flag=True, default=True, help="使用 GET 方法（BigGPT 推荐，默认启用）")
def process_all(output_dir: str, api_key: str, api_url: str, use_get: bool):
    """处理所有已添加的视频"""
    manager = VideoManager()
    videos = manager.list_all()

    if not videos:
        click.echo("暂无视频链接")
        return

    parser = VideoParser(api_key=api_key, api_url=api_url, use_get_method=use_get)
    generator = DocumentGenerator(output_dir=output_dir)

    click.echo(f"开始处理 {len(videos)} 个视频...\n")

    for i, video in enumerate(videos, 1):
        click.echo(f"[{i}/{len(videos)}] 处理: {video.title or str(video.url)}")
        try:
            result = parser.parse(str(video.url))
            filepath = generator.generate_markdown(result)
            click.echo(f"  ✓ 完成: {filepath}\n")
        except Exception as e:
            click.echo(f"  ✗ 失败: {e}\n", err=True)

    click.echo("全部处理完成！")


if __name__ == "__main__":
    cli()
