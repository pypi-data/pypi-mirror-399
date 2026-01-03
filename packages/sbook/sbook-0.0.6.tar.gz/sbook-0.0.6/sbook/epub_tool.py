import json
import logging
import mimetypes
import warnings
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from ebooklib import epub
from bs4 import BeautifulSoup, NavigableString

# 配置日志和警告
# 过滤 ebooklib 的未来警告和用户警告，保持输出清爽
warnings.filterwarnings("ignore", category=UserWarning, module="ebooklib")
warnings.filterwarnings("ignore", category=FutureWarning, module="ebooklib")

# 配置 logger，仅用于调试模式
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger("EpubTool")

app = typer.Typer(help="EPUB 电子书处理工具：元数据管理、封面提取、内容导出", add_completion=False)

# 常量定义
DC_NS = "http://purl.org/dc/elements/1.1/"
OPF_NS = "http://www.idpf.org/2007/opf"
DOCUMENT_TYPES = {9, "application/xhtml+xml", "text/html"}  # 使用集合加快查找


class FileUtils:
    """文件操作工具类"""

    @staticmethod
    def get_safe_path(base_path: Path, suffix_modifier: str = None, extension: str = None) -> Path:
        """
        生成不冲突的文件路径。
        :param base_path: 基础路径
        :param suffix_modifier: 文件名后缀修饰符 (如 "_modified")
        :param extension: 强制修改扩展名 (如 ".json")，若为 None 则保持原样
        :return: 唯一的文件路径
        """
        target_dir = base_path.parent
        target_stem = base_path.stem
        target_ext = extension if extension else base_path.suffix

        if suffix_modifier:
            target_stem = f"{target_stem}_{suffix_modifier}"

        candidate = target_dir / f"{target_stem}{target_ext}"

        if not candidate.exists():
            return candidate

        # 冲突处理：追加数字计数器
        counter = 1
        while True:
            candidate = target_dir / f"{target_stem}_{counter}{target_ext}"
            if not candidate.exists():
                return candidate
            counter += 1


class EpubProcessor:
    """EPUB 核心处理逻辑"""

    def __init__(self, epub_path: Path):
        if not epub_path.exists():
            raise FileNotFoundError(f"文件不存在: {epub_path}")
        if not epub_path.is_file():
            raise IsADirectoryError(f"路径不是文件: {epub_path}")

        self.epub_path = epub_path
        self.book = None
        self.toc_map = {}
        self._load()

    def _load(self) -> None:
        """加载 EPUB 文件并构建目录映射"""
        try:
            self.book = epub.read_epub(str(self.epub_path))
            self._build_toc_map()
        except Exception as e:
            raise RuntimeError(f"EPUB 文件解析失败: {e}")

    def get_metadata(self) -> Dict[str, Any]:
        """获取标准化的元数据"""
        title = self.book.get_metadata("DC", "title")
        creators = self.book.get_metadata("DC", "creator")
        language = self.book.get_metadata("DC", "language")

        return {
            "title": title[0][0] if title else "未知标题",
            "authors": [c[0] for c in creators] if creators else ["未知作者"],
            "language": language[0][0] if language else None,
            "file_name": self.epub_path.name,
            "file_size_mb": round(self.epub_path.stat().st_size / (1024 * 1024), 2),
        }

    def update_metadata(self, title: Optional[str] = None, author: Optional[str] = None) -> bool:
        """
        更新元数据。
        注意：为了防止元数据重复（如两个标题），会先清除对应项。
        """
        changed = False

        if title:
            # 清除旧标题
            if DC_NS in self.book.metadata:
                self.book.metadata[DC_NS].pop("title", None)
            self.book.set_title(title)
            changed = True

        if author:
            # 清除旧作者
            if DC_NS in self.book.metadata:
                self.book.metadata[DC_NS].pop("creator", None)
            self.book.add_author(author)
            changed = True

        return changed

    def update_cover(self, cover_path: Path) -> None:
        """更新封面图片"""
        if not cover_path.exists():
            raise FileNotFoundError(f"封面图片不存在: {cover_path}")

        try:
            with open(cover_path, "rb") as f:
                content = f.read()

            # 设置封面 (ebooklib 会自动处理 manifest 和 item)
            self.book.set_cover(cover_path.name, content)
        except Exception as e:
            raise RuntimeError(f"设置封面失败: {e}")

    def extract_cover(self, output_dir: Path) -> Path:
        """提取封面到指定目录"""
        cover_item = None

        # 策略 1: 通过 Metadata 查找
        cover_meta = self.book.get_metadata("OPF", "cover")
        if cover_meta:
            cover_id = cover_meta[0][0]
            cover_item = self.book.get_item_with_id(cover_id)

        # 策略 2: 遍历查找 ID 包含 'cover' 且是图片的项
        if not cover_item:
            for item in self.book.get_items():
                if item.media_type and item.media_type.startswith("image/") and "cover" in item.get_id().lower():
                    cover_item = item
                    break

        if not cover_item:
            raise RuntimeError("未在 EPUB 中找到封面图片资源")

        # 确定后缀名
        ext = mimetypes.guess_extension(cover_item.media_type) or Path(cover_item.get_name()).suffix or ".jpg"
        if ext == ".jpe":
            ext = ".jpg"

        output_path = FileUtils.get_safe_path(output_dir / "cover", extension=ext)
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(cover_item.get_content())

        return output_path

    def get_structured_content(self) -> List[Dict]:
        """解析所有章节内容，返回结构化列表"""
        chapters = []
        chapter_index = 0

        # 按 Spine 顺序遍历（阅读顺序）
        for item_id, _ in self.book.spine:
            item = self.book.get_item_with_id(item_id)
            if not item:
                continue

            # 过滤非文档类型
            if item.get_type() not in DOCUMENT_TYPES:
                continue

            # 尝试提取内容
            try:
                raw_html = item.get_content().decode("utf-8", errors="ignore")
                clean_content = self._clean_html(raw_html)

                # 跳过字数过少的内容（通常是版权页或空白页）
                if len(clean_content) < 50:
                    continue

                chapter_index += 1
                # 尝试从 TOC 获取标题，否则使用默认标题
                title = self.toc_map.get(item.get_name(), f"第 {chapter_index} 章")

                chapters.append(
                    {
                        "index": chapter_index,
                        "title": title,
                        "content_length": len(clean_content),
                        "content": clean_content,
                    }
                )
            except Exception as e:
                logger.warning(f"跳过损坏的章节 {item_id}: {e}")
                continue

        return chapters

    def save_epub(self, output_path: Path) -> None:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            epub.write_epub(str(output_path), self.book, {})
        except Exception as e:
            raise RuntimeError(f"保存 EPUB 文件失败: {e}")

    def save_json(self, output_path: Path) -> None:
        meta = self.get_metadata()
        chapters = self.get_structured_content()

        data = {"meta": meta, "chapter_count": len(chapters), "chapters": chapters}

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise RuntimeError(f"保存 JSON 文件失败: {e}")

    # --- 内部辅助方法 ---

    def _build_toc_map(self) -> None:
        """
        递归解析 TOC (Table of Contents)，建立 href -> title 的映射。
        解决嵌套目录问题。
        """

        def _recurse_toc(items):
            for item in items:
                if isinstance(item, tuple):
                    # Section 类型: (SectionObj, [Children...])
                    section, children = item
                    if hasattr(section, "href") and hasattr(section, "title"):
                        # 去除锚点 (#anchor) 只要文件名
                        href = section.href.split("#")[0]
                        self.toc_map[href] = section.title
                    _recurse_toc(children)
                elif isinstance(item, epub.Link):
                    href = item.href.split("#")[0]
                    self.toc_map[href] = item.title

        _recurse_toc(self.book.toc)

    @staticmethod
    def _clean_html(html_content: str) -> str:
        """
        深度清洗 HTML。
        1. 移除脚本、样式、头部。
        2. 保留段落结构。
        3. 去除多余空行。
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. 移除干扰元素
        for tag in soup(["script", "style", "meta", "link", "head", "title", "iframe", "svg"]):
            tag.decompose()

        # 2. 提取主体
        body = soup.find("body")
        if not body:
            return ""

        # 3. 智能提取文本（保留分段）
        # 这里不直接用 get_text()，因为会丢失段落间的换行
        # 我们遍历 body 的子元素，只保留块级元素的文本

        lines = []
        for element in body.descendants:
            if isinstance(element, NavigableString):
                text = element.strip()
                if text:
                    # 检查父级是否是不可见元素
                    parent_tags = [p.name for p in element.parents]
                    if not any(x in parent_tags for x in ["script", "style"]):
                        lines.append(text)

        # 简单拼接，或者使用更复杂的逻辑保留 <p> 标签。
        # 为了通用性（JSON阅读），这里选择用换行符拼接纯文本。
        return "\n\n".join(lines)


# --- Typer CLI 命令 ---


def _handle_error(e: Exception):
    """统一错误处理输出"""
    typer.secho(f"❌ 发生错误: {e}", fg=typer.colors.RED, err=True)
    raise typer.Exit(1)


@app.command()
def info(epub_file: Path = typer.Argument(..., exists=True, dir_okay=False, help="EPUB 文件路径")):
    """显示 EPUB 的详细元数据"""
    try:
        processor = EpubProcessor(epub_file)
        meta = processor.get_metadata()

        typer.secho("📘 书籍信息", fg=typer.colors.CYAN, bold=True)
        typer.echo(f"   标题: {meta['title']}")
        typer.echo(f"   作者: {', '.join(meta['authors'])}")
        typer.echo(f"   语言: {meta['language']}")
        typer.echo(f"   大小: {meta['file_size_mb']} MB")
    except Exception as e:
        _handle_error(e)


@app.command()
def modify(
    epub_file: Path = typer.Argument(..., exists=True, dir_okay=False),
    title: str = typer.Option(None, "--title", "-t", help="新标题"),
    author: str = typer.Option(None, "--author", "-a", help="新作者"),
    cover: Path = typer.Option(None, "--cover", "-c", exists=True, dir_okay=False, help="新封面图片"),
    output: Path = typer.Option(None, "--output", "-o", help="输出路径（可选）"),
):
    """修改元数据或封面"""
    if not any([title, author, cover]):
        typer.secho("⚠️  请至少指定一个修改项", fg=typer.colors.YELLOW)
        raise typer.Exit(0)

    try:
        processor = EpubProcessor(epub_file)
        msgs = []

        if processor.update_metadata(title, author):
            if title:
                msgs.append(f"标题 -> {title}")
            if author:
                msgs.append(f"作者 -> {author}")

        if cover:
            processor.update_cover(cover)
            msgs.append(f"封面 -> {cover.name}")

        out_path = output or FileUtils.get_safe_path(epub_file, suffix_modifier="modified")
        processor.save_epub(out_path)

        typer.secho("✅ 修改成功!", fg=typer.colors.GREEN)
        for msg in msgs:
            typer.echo(f"   - {msg}")
        typer.secho(f"   -> {out_path}", fg=typer.colors.BRIGHT_BLACK)

    except Exception as e:
        _handle_error(e)


@app.command(name="extract-cover")
def extract_cover_cmd(
    epub_file: Path = typer.Argument(..., exists=True, dir_okay=False),
    output_dir: Path = typer.Option(None, "--output-dir", "-d", file_okay=False, help="输出目录"),
):
    """提取封面图片"""
    try:
        processor = EpubProcessor(epub_file)
        target_dir = output_dir or epub_file.parent
        saved_path = processor.extract_cover(target_dir)
        typer.secho(f"✅ 封面已保存至: {saved_path}", fg=typer.colors.GREEN)
    except Exception as e:
        _handle_error(e)


@app.command(name="to-json")
def to_json_cmd(
    epub_file: Path = typer.Argument(..., exists=True, dir_okay=False),
    output: Path = typer.Option(None, "--output", "-o", help="JSON 输出路径"),
    preview: bool = typer.Option(False, "--preview", "-p", help="仅预览前3章信息，不写入文件"),
):
    """将书籍内容转为 JSON"""
    try:
        processor = EpubProcessor(epub_file)

        typer.echo("🔄 正在解析内容...", nl=False)
        chapters = processor.get_structured_content()
        typer.echo(f"\r✅ 解析完成: 共 {len(chapters)} 章")

        if preview:
            typer.secho("--- 预览模式 ---", fg=typer.colors.YELLOW)
            for ch in chapters[:3]:
                typer.echo(f"[{ch['index']}] {ch['title']} (字数: {ch['content_length']})")
                typer.echo(f"摘要: {ch['content'][:50]}...")
            return

        out_path = output or FileUtils.get_safe_path(epub_file, extension=".json")
        processor.save_json(out_path)
        typer.secho(f"✅ JSON 已导出: {out_path}", fg=typer.colors.GREEN)

    except Exception as e:
        _handle_error(e)


if __name__ == "__main__":
    app()
