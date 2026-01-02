import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Union, Any, Callable

from ebooklib import epub

try:
    import requests
except ImportError:
    requests = None


@dataclass
class Chapter:
    """章节实体"""

    id: int
    title: str
    content: str


@dataclass
class Volume:
    """
    卷实体
    包含卷名和该卷下的章节列表
    """

    title: str
    chapters: List[Chapter] = field(default_factory=list)


class EpubCreator:
    """EPUB 格式导出器"""

    CSS_FILE_PATH: str = "style/style.css"
    DEFAULT_CSS: str = """
        body { margin: 10px; font-size: 1em; word-wrap: break-word; }
        ul, li { list-style-type: none; margin: 0; padding: 0; }
        p { text-indent: 2em; line-height: 1.8em; margin-top: 0; margin-bottom: 0.5em; }
        .catalog { line-height: 3.5em; height: 3.5em; font-size: 0.8em; border-bottom: 1px solid #d5d5d5; }
        /* 卷名样式：仅在有卷模式下显示 */
        .volume-header { font-size: 1.2em; font-weight: bold; margin-top: 20px;
        border-bottom: 2px solid #333; padding-bottom: 5px; color: #333; list-style: none; }
        h1 { font-size: 1.6em; font-weight: bold; }
        h2 { display: block; font-size: 1.2em; font-weight: bold; margin: 1em 0 0.83em 0; }
        a { color: inherit; text-decoration: none; }
        a[href] { color: blue; cursor: pointer; }
        .italic { font-style: italic; }
    """
    IMAGE_EXT_MAP: dict[str, str] = {".jpg": "jpg", ".jpeg": "jpg", ".png": "png", ".webp": "webp"}
    IMAGE_TIMEOUT: int = 15
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def __init__(
        self,
        title: str,
        author: str,
        description: str,
        cover_url: str,
        genre: str,
        novel_id: Optional[str] = None,
        output_dir: Union[str, Path] = ".",
        extension: str = "epub",
        logger: Optional[Callable[[str], None]] = None,
        content_processor: Optional[Callable[[str], str]] = None,
        custom_nav: bool = False,
    ) -> None:
        self.title: str = title
        self.author: str = author
        self.description: str = description
        self.cover_url: str = cover_url
        self.genre: str = genre
        self.novel_id: str = novel_id if novel_id else str(int(time.time()))
        self.extension: str = extension
        self.output_dir: Path = Path(output_dir).resolve()
        self.output_file: Path = self.prepare_output_path()

        self.logger = logger if logger else print
        self.content_processor = content_processor if content_processor else (lambda x: x)
        self.custom_nav: bool = custom_nav

    def export(self, content_items: Union[Iterable[Chapter], Iterable[Volume]]) -> str:
        """
        导出 EPUB
        兼容性接口：
        1. 传入 List[Chapter] -> 视为无卷模式（默认卷），生成扁平目录。
        2. 传入 List[Volume]  -> 视为分卷模式，生成树状目录。
        """
        # 0. 预处理数据：将输入归一化为 List[Volume]
        # 为了避免多次遍历迭代器，先转为 list
        items = list(content_items)
        if not items:
            self.echo("⚠ 没有内容可导出")
            return ""

        volumes: List[Volume] = []
        is_flat_mode = False

        # 判断第一个元素的类型来决定模式
        first_item = items[0]
        if isinstance(first_item, Chapter):
            # 兼容模式：传入的是章节列表，封装进一个默认卷
            # 默认卷 title 为空字符串，作为标记
            volumes = [Volume(title="", chapters=items)]  # type: ignore
            is_flat_mode = True
            self.echo("检测到章节列表，使用扁平模式导出。")
        elif isinstance(first_item, Volume):
            # 分卷模式
            volumes = items  # type: ignore
            is_flat_mode = False
            self.echo("检测到分卷列表，使用分卷模式导出。")
        else:
            self.echo(f"⚠ 未知的数据类型: {type(first_item)}，无法导出")
            return ""

        # --- 开始构建书籍 ---
        book = self._create_book()
        self._add_style(book)
        self._add_cover(book)
        intro_page = self._add_intro(book)

        spine_items: List[epub.EpubHtml] = []  # 阅读顺序
        nav_html_lines: List[str] = []  # HTML 目录源码
        toc_structure = []  # NCX/Sidebar 树状目录

        if intro_page:
            toc_structure.append(intro_page)

        # 遍历归一化后的卷列表
        for vol in volumes:
            vol_chapters_epub_objs = []

            # 1. 处理 HTML 目录显示（仅当不是扁平模式且卷名不为空时显示卷名）
            if not is_flat_mode and vol.title:
                nav_html_lines.append(f'<li class="volume-header">{vol.title}</li>')

            # 2. 处理卷内章节
            for chapter in vol.chapters:
                epub_chapter = self._create_epub_chapter(chapter)
                book.add_item(epub_chapter)

                # 加入阅读流
                spine_items.append(epub_chapter)
                # 收集当前卷的章节对象（用于 TOC 分组）
                vol_chapters_epub_objs.append(epub_chapter)
                # 加入 HTML 目录
                nav_html_lines.append(
                    f'<li class="catalog"><a href="{epub_chapter.file_name}">{chapter.title}</a></li>'
                )

            # 3. 构建 TOC 结构
            if is_flat_mode or not vol.title:
                # 扁平模式 或 卷名为空 -> 章节直接放根目录
                toc_structure.extend(vol_chapters_epub_objs)
            else:
                # 分卷模式 -> 创建 Section 节点
                if vol_chapters_epub_objs:  # 只有当卷里有章节时才添加
                    toc_section = (epub.Section(vol.title), vol_chapters_epub_objs)
                    toc_structure.append(toc_section)

        # 创建自定义目录页
        custom_nav_page = self._add_custom_nav(book, nav_html_lines) if self.custom_nav else None

        # 组装
        self._finalize_book(book, spine_items, toc_structure, intro_page, custom_nav_page)

        try:
            epub.write_epub(str(self.output_file), book)
            self.echo(f"成功导出: {self.output_file}")
            return str(self.output_file)
        except Exception as e:
            self.echo(f"导出失败: {e}")
            return ""

    # --- 下面的辅助方法基本保持不变 ---

    def echo(self, message: str) -> None:
        try:
            self.logger(message)
        except Exception:
            print(f"[Logger Error] {message}")

    def _create_epub_chapter(self, chapter: Chapter) -> epub.EpubHtml:
        raw_content = chapter.content
        try:
            processed_content = self.content_processor(raw_content)
        except Exception as e:
            self.echo(f"⚠ 章节 '{chapter.title}' 内容处理失败: {e}，将使用原始内容")
            processed_content = raw_content

        final_content = (processed_content or "").strip()

        epub_chapter = epub.EpubHtml(
            title=chapter.title,
            file_name=f"chapter_{chapter.id}.xhtml",
            lang="zh",
            uid=f"chapter_{chapter.id}",
            content=f"<h2>{chapter.title}</h2>{final_content}",
        )
        self._add_css_link(epub_chapter)
        return epub_chapter

    def _add_css_link(self, item: epub.EpubHtml) -> None:
        item.add_link(href=self.CSS_FILE_PATH, rel="stylesheet", type="text/css")

    def _create_book(self) -> epub.EpubBook:
        book = epub.EpubBook()
        book.set_identifier(f"novel_{self.novel_id}")
        book.set_title(self.title)
        book.set_language("zh")
        if self.author:
            book.add_author(self.author)
        if self.description:
            book.add_metadata("DC", "description", self.description)
        if self.genre:
            book.add_metadata("DC", "subject", self.genre)
        return book

    def _add_style(self, book: epub.EpubBook) -> None:
        style_item = epub.EpubItem(
            uid="style_nav", file_name=self.CSS_FILE_PATH, media_type="text/css", content=self.DEFAULT_CSS
        )
        book.add_item(style_item)

    def _add_cover(self, book: epub.EpubBook) -> None:
        if not self.cover_url:
            return
        target = self.cover_url.strip()
        local_path = Path(target)
        if local_path.exists() and local_path.is_file():
            self._process_local_cover(book, local_path)
        elif target.lower().startswith(("http://", "https://")):
            if requests:
                self._process_remote_cover(book, target)
            else:
                self.echo("⚠ 未安装 requests 库")
        else:
            self.echo(f"⚠ 封面无效: {target}")

    def _process_local_cover(self, book: epub.EpubBook, path: Path) -> None:
        try:
            ext = path.suffix.lower()
            with open(path, "rb") as f:
                content = f.read()
            final_ext = self.IMAGE_EXT_MAP.get(ext, "jpg")
            book.set_cover(f"cover.{final_ext}", content)
            self.echo(f"✓ 本地封面: {path.name}")
        except Exception as e:
            self.echo(f"⚠ 本地封面错误: {e}")

    def _process_remote_cover(self, book: epub.EpubBook, url: str) -> None:
        try:
            self.echo(f"下载封面: {url}")
            resp = requests.get(url, timeout=self.IMAGE_TIMEOUT, headers={"User-Agent": self.USER_AGENT})
            if resp.status_code == 200:
                ext = self._detect_web_image_extension(resp, url)
                book.set_cover(f"cover.{ext}", resp.content)
                self.echo("✓ 网络封面成功")
            else:
                self.echo(f"⚠ 封面下载失败: {resp.status_code}")
        except Exception as e:
            self.echo(f"⚠ 封面下载异常: {e}")

    def _detect_web_image_extension(self, response: Any, url: str) -> str:
        ctype = response.headers.get("Content-Type", "").lower()
        if "png" in ctype:
            return "png"
        if "webp" in ctype:
            return "webp"
        if "jpeg" in ctype or "jpg" in ctype:
            return "jpg"
        return self.IMAGE_EXT_MAP.get("." + url.split(".")[-1].lower(), "jpg")

    def _add_intro(self, book: epub.EpubBook) -> Optional[epub.EpubHtml]:
        if not self.description:
            return None
        intro = epub.EpubHtml(
            title="简介", file_name="intro.xhtml", lang="zh", content=f"<h2>简介</h2><p>{self.description}</p>"
        )
        self._add_css_link(intro)
        book.add_item(intro)
        return intro

    def _add_custom_nav(self, book: epub.EpubBook, nav_links_html: List[str]) -> epub.EpubHtml:
        custom_nav = epub.EpubHtml(
            title="目录",
            file_name="cusnav.xhtml",
            lang="zh",
            uid="cusnav",
            content=f"<h1>目录</h1><ul>{''.join(nav_links_html)}</ul>",
        )
        self._add_css_link(custom_nav)
        book.add_item(custom_nav)
        return custom_nav

    def _finalize_book(
        self,
        book: epub.EpubBook,
        spine_items: List[epub.EpubHtml],
        toc_structure: List[Union[epub.EpubHtml, tuple]],
        intro: Optional[epub.EpubHtml],
        nav: Optional[epub.EpubHtml],
    ) -> None:
        # TOC 侧边栏
        book.toc = toc_structure

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Spine 阅读顺序 (Nav -> Intro -> Chapters)
        book.spine = ([nav] if nav else []) + ([intro] if intro else []) + spine_items

    def prepare_output_path(self) -> Path:
        safe_title = self.sanitize_filename(self.title)
        safe_author = self.sanitize_filename(self.author) if self.author else "佚名"
        base = f"{safe_title}-{safe_author}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_dir / f"{base}.{self.extension}"
        idx = 1
        while out.exists():
            out = self.output_dir / f"{base}_{idx}.{self.extension}"
            idx += 1
        return out

    @staticmethod
    def sanitize_filename(name: str, max_length: int = 100) -> str:
        if not name:
            return "untitled"
        return "".join(c for c in name if c.isalnum() or c in " -_，。")[:max_length].strip()
