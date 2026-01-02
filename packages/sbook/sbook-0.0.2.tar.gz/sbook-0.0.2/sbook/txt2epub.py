import re
import html
import hashlib
import typer
from pathlib import Path
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 尝试导入 book.py 中的类
try:
    from sbook.core.book import EpubCreator, Volume, Chapter
except ImportError:
    try:
        import sys

        sys.path.append(str(Path(__file__).parent))
        from sbook.core.book import EpubCreator, Volume, Chapter
    except ImportError:
        print("错误: 未找到 'book.py'，请确保该文件存在。")
        exit(1)

app = typer.Typer(help="小说工具：支持 TXT 转 EPUB、文本质量校验及编码转换")
console = Console()

# --- 1. 正则定义 (已包含防止误判的修复) ---
REGEX_VOLUME = re.compile(
    r"^\s*(第[0-9零一二三四五六七八九十百千]+卷|卷[0-9零一二三四五六七八九十百千]+|[Vv]ol(ume)?\.?\s*\d+)(?:\s+|[:：、]|$).*",
    re.IGNORECASE,
)
REGEX_CHAPTER = re.compile(
    r"^\s*(第[0-9零一二三四五六七八九十百千]+[章回节]|Chapter\s*\d+)(?:\s+|[:：、]|$).*", re.IGNORECASE
)

# --- 2. 辅助工具函数 ---


def get_unique_output_path(base_path: Path) -> Path:
    """获取不冲突的输出路径"""
    if not base_path.exists():
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent
    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


# --- 2.1 数字处理工具 ---
CN_NUM = {
    "零": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
}


def _cn2an_simple(text: str) -> int:
    """简易中文数字转阿拉伯数字"""
    val = 0
    tmp = 0
    for c in text:
        if c in CN_NUM:
            tmp = CN_NUM[c]
        elif c == "十":
            val += (tmp if tmp > 0 else 1) * 10
            tmp = 0
        elif c == "百":
            val += tmp * 100
            tmp = 0
        elif c == "千":
            val += tmp * 1000
            tmp = 0
        elif c == "万":
            val += tmp
            val *= 10000
            tmp = 0
    val += tmp
    return val


def extract_chapter_num(title: str) -> Optional[int]:
    """从标题提取章节数字"""
    match = re.search(r"第([0-9零一二三四五六七八九十百千]+)[章回节]", title)
    if match:
        num_str = match.group(1)
        if num_str.isdigit():
            return int(num_str)
        return _cn2an_simple(num_str)

    match_en = re.search(r"Chapter\s*(\d+)", title, re.IGNORECASE)
    if match_en:
        return int(match_en.group(1))

    return None


# --- 3. 解析逻辑 ---


def parse_txt_to_volumes(file_path: Path, encoding: str = "utf-8") -> List[Volume]:
    volumes: List[Volume] = []
    current_vol = Volume(title="", chapters=[])
    volumes.append(current_vol)
    current_chapter: Optional[Chapter] = None
    chapter_id_counter = 1

    def process_file_stream(f):
        nonlocal current_vol, current_chapter, chapter_id_counter
        for line in f:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            if len(line_stripped) < 100:
                if REGEX_VOLUME.match(line_stripped):
                    current_vol = Volume(title=line_stripped, chapters=[])
                    volumes.append(current_vol)
                    current_chapter = None
                    continue

                if REGEX_CHAPTER.match(line_stripped):
                    new_chapter = Chapter(id=chapter_id_counter, title=line_stripped, content="")
                    current_vol.chapters.append(new_chapter)
                    current_chapter = new_chapter
                    chapter_id_counter += 1
                    continue

            safe_content = html.escape(line_stripped)
            paragraph = f"<p>{safe_content}</p>\n"

            if current_chapter:
                current_chapter.content += paragraph
            else:
                if not current_vol.chapters:
                    if current_vol.title == "":
                        preface_title = "书籍相关/序章"
                    else:
                        preface_title = f"【{current_vol.title}】卷首语"
                    preface = Chapter(id=chapter_id_counter, title=preface_title, content="")
                    current_vol.chapters.append(preface)
                    current_chapter = preface
                    chapter_id_counter += 1
                if current_chapter:
                    current_chapter.content += paragraph

    try:
        with open(file_path, "r", encoding=encoding) as f:
            f.read(10)
            f.seek(0)
            with Progress(
                SpinnerColumn(), TextColumn("[progress.description]正在解析文本..."), transient=True
            ) as progress:
                progress.add_task("parse", total=None)
                process_file_stream(f)
    except UnicodeDecodeError:
        if encoding == "utf-8":
            console.print("[yellow]⚠ UTF-8 解析失败，尝试 GB18030...[/yellow]")
            return parse_txt_to_volumes(file_path, encoding="gb18030")
        else:
            console.print(f"[red]❌ 无法解析文件编码。[/red]")
            return []
    except Exception as e:
        console.print(f"[red]❌ 读取失败: {e}[/red]")
        return []

    return [v for v in volumes if v.chapters]


# --- 4. 分析器逻辑 ---


class TxtNovelAnalyzer:
    def __init__(self, volumes: List[Volume]):
        self.chapters: List[Chapter] = []
        for vol in volumes:
            self.chapters.extend(vol.chapters)
        self.issues: List[Dict[str, Any]] = []

    def _get_pure_text(self, html_content: str) -> str:
        if not html_content:
            return ""
        text = re.sub(r"<[^>]+>", "", html_content)
        return text.replace("\n", "").strip()

    def analyze_empty_content(self) -> Dict[str, Any]:
        """检测空章节"""
        empty_chapters = []
        short_chapters = []
        for chapter in self.chapters:
            content = self._get_pure_text(chapter.content)
            if not content:
                empty_chapters.append({"index": chapter.id, "title": chapter.title})
            elif len(content) < 50:
                short_chapters.append({"index": chapter.id, "title": chapter.title, "length": len(content)})

        if empty_chapters:
            self.issues.append({"level": "error", "type": "empty", "message": f"{len(empty_chapters)} 章内容为空"})
        if short_chapters:
            self.issues.append({"level": "warning", "type": "short", "message": f"{len(short_chapters)} 章内容过短"})

        return {"empty_chapters": empty_chapters, "short_chapters": short_chapters}

    def analyze_garbled_text(self) -> Dict[str, Any]:
        """检测乱码 (修改版：记录具体章节)"""
        critical_patterns = {"unicode_replacement": r"[\ufffd]{3,}", "classic_utf8": r"(锟斤拷|烫烫烫)"}
        garbled_chapters = []  # 记录具体信息
        count = 0

        for chapter in self.chapters:
            content = self._get_pure_text(chapter.content)
            matched = False
            for name, p in critical_patterns.items():
                if re.search(p, content):
                    count += 1
                    garbled_chapters.append({"index": chapter.id, "title": chapter.title, "type": name})  # 记录乱码类型
                    matched = True
                    break

            # 如果没匹配到严重乱码，可以尝试检测一下 ？？？ 这种
            if not matched:
                if "????" in content and len(content) > 100:
                    # 简单的问号检测，作为警告
                    pass

        if count > 0:
            self.issues.append({"level": "error", "type": "garbled", "message": f"{count} 章包含乱码"})

        return {"critical_count": count, "garbled_chapters": garbled_chapters}  # 返回详细列表

    def analyze_consistency(self) -> Dict[str, Any]:
        """重复检测 (基于内容 MD5)"""
        if len(self.chapters) < 2:
            return {"duplicates": []}
        fingerprints = {}
        duplicates = []
        for chapter in self.chapters:
            content = self._get_pure_text(chapter.content)
            if len(content) < 100:
                continue
            fp = hashlib.md5(content.encode("utf-8")).hexdigest()
            if fp in fingerprints:
                duplicates.append(
                    {
                        "dup_title": chapter.title,
                        "dup_id": chapter.id,
                        "orig_title": fingerprints[fp][1],
                        "orig_id": fingerprints[fp][0],
                        "preview": content[:40] + "...",
                    }
                )
            else:
                fingerprints[fp] = (chapter.id, chapter.title)
        if duplicates:
            self.issues.append({"level": "error", "type": "dup", "message": f"{len(duplicates)} 处内容重复"})
        return {"duplicates": duplicates}

    def analyze_duplicate_numbers(self) -> Dict[str, Any]:
        """检测重复的章节号"""
        num_map = {}
        for ch in self.chapters:
            num = extract_chapter_num(ch.title)
            if num is None:
                continue
            if num not in num_map:
                num_map[num] = []
            preview = self._get_pure_text(ch.content)[:25].replace("\n", "")
            num_map[num].append({"id": ch.id, "title": ch.title, "preview": preview})

        duplicates = []
        for num, items in num_map.items():
            if len(items) > 1:
                duplicates.append({"number": num, "items": items})

        duplicates.sort(key=lambda x: x["number"])

        if duplicates:
            self.issues.append({"level": "warning", "type": "dup_index", "message": f"{len(duplicates)} 个章节号重复"})

        return {"dup_indices": duplicates}

    def analyze_continuity(self) -> Dict[str, Any]:
        """校验章节连续性"""
        if not self.chapters:
            return {"missing_ranges": []}
        nums = []
        for ch in self.chapters:
            num = extract_chapter_num(ch.title)
            if num is not None:
                nums.append(num)

        if not nums:
            return {"missing_ranges": []}
        nums = sorted(list(set(nums)))
        missing_ranges = []

        for i in range(len(nums) - 1):
            current = nums[i]
            next_val = nums[i + 1]
            if next_val > current + 1:
                start_miss = current + 1
                end_miss = next_val - 1
                missing_ranges.append(str(start_miss) if start_miss == end_miss else f"{start_miss}-{end_miss}")

        if missing_ranges:
            total_missing = 0
            for r in missing_ranges:
                total_missing += (int(r.split("-")[1]) - int(r.split("-")[0]) + 1) if "-" in r else 1
            self.issues.append({"level": "warning", "type": "missing", "message": f"缺失 {total_missing} 章"})

        return {"missing_ranges": missing_ranges, "min": nums[0], "max": nums[-1]}

    def run(self):
        return {
            "empty": self.analyze_empty_content(),
            "garbled": self.analyze_garbled_text(),
            "consistency": self.analyze_consistency(),
            "continuity": self.analyze_continuity(),
            "dup_indices": self.analyze_duplicate_numbers(),
            "issues": self.issues,
        }


# --- 5. 命令定义 ---


@app.command(name="to-utf8")
def to_utf8(file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False)):
    """将非 UTF-8 编码的文件转换为 UTF-8"""
    console.print(f"[bold cyan]开始转换文件:[/bold cyan] {file.name}")
    encodings = ["utf-8", "gb18030", "gbk", "big5", "cp936", "utf-16", "shift_jis"]
    content, detected = "", None

    with console.status("检测编码并读取..."):
        raw = file.read_bytes()
        for enc in encodings:
            try:
                content = raw.decode(enc)
                detected = enc
                break
            except:
                continue

    if not detected:
        console.print("[red]❌ 无法识别编码[/red]")
        raise typer.Exit(1)

    out = get_unique_output_path(file)
    out.write_text(content, encoding="utf-8")
    console.print(f"✅ 转换完成: {detected} -> utf-8 | 保存至 {out.name}")


@app.command()
def check(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="输入的 .txt 文件路径"),
    encoding: str = typer.Option("utf-8", help="文件编码"),
):
    """
    校验 TXT 小说质量。
    包含：空章、重复内容、重复章节号(撞车)、断更、乱码。
    """
    console.print(f"[bold cyan]开始校验文件:[/bold cyan] {file.name}")

    volumes = parse_txt_to_volumes(file, encoding=encoding)
    if not volumes:
        console.print("[red]无法解析文件内容，请检查文件编码或格式。[/red]")
        raise typer.Exit(1)

    analyzer = TxtNovelAnalyzer(volumes)
    with console.status("[bold green]正在分析内容...[/bold green]"):
        results = analyzer.run()

    issues = results["issues"]

    if not issues:
        console.print("[green]✅ 文件质量良好，未发现明显问题。[/green]")
        return

    console.print(Panel(f"[yellow]发现 {len(issues)} 个问题[/yellow]", title="分析结果", border_style="yellow"))

    # 1. 章节号重复 (撞车)
    dup_indices = results.get("dup_indices", {}).get("dup_indices", [])
    if dup_indices:
        console.print("\n[bold red]❌ 章节号重复 (重号) 详情:[/bold red]")
        for item in dup_indices:
            console.print(f"  [bold]第 {item['number']} 章[/bold] 出现了 {len(item['items'])} 次:")
            for entry in item["items"]:
                console.print(f"    - ID:{entry['id']} | 标题: [cyan]{entry['title']}[/cyan]")
                console.print(f"      [dim]内容预览: {entry['preview']}...[/dim]")

    # 2. 缺失章节 (连续性)
    cont_data = results.get("continuity", {})
    missing = cont_data.get("missing_ranges", [])
    if missing:
        console.print(
            f"\n[bold red]❌ 章节连续性检查 (检测范围: {cont_data.get('min')}-{cont_data.get('max')}):[/bold red]"
        )
        display_ranges = missing[:20]
        ranges_str = ", ".join(display_ranges)
        console.print(f"  缺失章节号: {ranges_str}" + (" ..." if len(missing) > 20 else ""))

    # 3. 空内容章节
    empty_data = results.get("empty", {})
    empty_chapters = empty_data.get("empty_chapters", [])
    if empty_chapters:
        console.print("\n[bold red]❌ 空内容章节列表:[/bold red]")
        for ch in empty_chapters:
            console.print(f"  - ID:{ch['index']} [bold]{ch['title']}[/bold]")

    # 4. 内容过短章节
    short_chapters = empty_data.get("short_chapters", [])
    if short_chapters:
        console.print("\n[bold yellow]⚠️ 内容过短章节 (<50字):[/bold yellow]")
        for ch in short_chapters[:5]:
            console.print(f"  - ID:{ch['index']} [bold]{ch['title']}[/bold] (长度: {ch['length']})")
        if len(short_chapters) > 5:
            console.print(f"  ... 共 {len(short_chapters)} 章")

    # 5. 重复内容章节
    duplicates = results.get("consistency", {}).get("duplicates", [])
    if duplicates:
        console.print("\n[bold red]❌ 内容重复详情 (正文完全一样):[/bold red]")
        for dup in duplicates:
            console.print(f"  - [bold]{dup['dup_title']}[/bold] (ID:{dup['dup_id']})")
            console.print(f"    内容重复于 -> [dim]{dup['orig_title']} (ID:{dup['orig_id']})[/dim]")
            console.print(f"    [dim cyan]摘要: {dup['preview']}[/dim cyan]")

    # 6. 乱码 (修改版：显示具体列表)
    garbled_data = results.get("garbled", {})
    critical_count = garbled_data.get("critical_count", 0)
    garbled_list = garbled_data.get("garbled_chapters", [])

    if critical_count > 0:
        console.print(f"\n[bold red]❌ 严重乱码 ({critical_count} 章):[/bold red]")
        for item in garbled_list:
            console.print(f"  - ID:{item['index']} [bold]{item['title']}[/bold] (类型: {item['type']})")


@app.command()
def convert(
    file: Path = typer.Argument(..., exists=True, file_okay=True, dir_okay=False, help="输入的 .txt 文件路径"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="书籍标题"),
    author: str = typer.Option("未知", "--author", "-a", help="作者名"),
    cover: Optional[str] = typer.Option(None, "--cover", "-c", help="封面图片路径或 URL"),
    desc: Optional[str] = typer.Option(None, "--desc", "-d", help="书籍简介"),
    split_volume: bool = typer.Option(True, help="是否按卷分层"),
):
    """将 TXT 小说转换为 EPUB 格式。"""
    console.print(f"[bold green]开始处理文件:[/bold green] {file.name}")
    book_title = title if title else file.stem
    volumes = parse_txt_to_volumes(file)

    total_chapters = sum(len(v.chapters) for v in volumes)
    if total_chapters == 0:
        console.print("[bold red]错误：[/bold red] 未能识别到任何章节。")
        raise typer.Exit(code=1)

    if not split_volume and len(volumes) > 1:
        all_chapters = []
        for v in volumes:
            all_chapters.extend(v.chapters)
        volumes = [Volume(title="", chapters=all_chapters)]

    creator = EpubCreator(
        title=book_title,
        author=author,
        description=desc or "",
        cover_url=cover if cover else "",
        genre="Novel",
        output_dir=file.parent,
        logger=lambda msg: console.print(f"[dim]{msg}[/dim]"),
    )

    with console.status("[bold green]正在生成 EPUB...[/bold green]"):
        output_path = creator.export(volumes)

    if output_path:
        console.print(f"\n[bold green]✨ 转换成功![/bold green] 保存于: [underline]{output_path}[/underline]")


def main():
    app()


if __name__ == "__main__":
    main()
