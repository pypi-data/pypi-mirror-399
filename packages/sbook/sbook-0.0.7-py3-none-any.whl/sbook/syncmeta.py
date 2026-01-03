from pathlib import Path
import re
from dataclasses import dataclass
import typer
from ebooklib import epub
from sbook import get_version

app = typer.Typer(help="EPUB 文件名 / 元数据 双向同步工具")


@app.callback(invoke_without_command=True)
def main(version_flag: bool = typer.Option(False, "--version", "-v", help="显示版本")):
    if version_flag:
        typer.echo(get_version())
        raise typer.Exit()


INVALID_CHARS = r'[\\/:*?"<>|]'
DEFAULT_AUTHOR = "佚名"


# -------------------------
# 数据类
# -------------------------
@dataclass
class BookInfo:
    title: str
    author: str

    def to_filename(self) -> str:
        """生成标准文件名格式"""
        return f"{self.title}-{self.author}.epub"


# -------------------------
# 工具函数
# -------------------------
def safe_name(name: str) -> str:
    """移除文件名中的非法字符"""
    return re.sub(INVALID_CHARS, "_", name.strip())


def read_epub_meta(epub_path: Path) -> BookInfo:
    """从 EPUB 文件读取元数据"""
    book = epub.read_epub(str(epub_path))

    # 使用完整的命名空间读取
    dc_ns = "http://purl.org/dc/elements/1.1/"

    title = DEFAULT_AUTHOR  # 默认值
    author = DEFAULT_AUTHOR

    # 尝试从完整命名空间读取
    if dc_ns in book.metadata:
        title_list = book.metadata[dc_ns].get("title", [])
        author_list = book.metadata[dc_ns].get("creator", [])

        if title_list:
            title = title_list[0][0] if isinstance(title_list[0], tuple) else title_list[0]
        if author_list:
            author = author_list[0][0] if isinstance(author_list[0], tuple) else author_list[0]

    # 兜底方案：使用 get_metadata
    if title == DEFAULT_AUTHOR:
        title_list = book.get_metadata("DC", "title")
        title = title_list[0][0] if title_list else epub_path.stem

    if author == DEFAULT_AUTHOR:
        author_list = book.get_metadata("DC", "creator")
        author = author_list[0][0] if author_list else DEFAULT_AUTHOR

    return BookInfo(safe_name(title), safe_name(author))


def parse_filename(epub_path: Path) -> BookInfo:
    """从文件名解析书名和作者"""
    stem = epub_path.stem

    if not stem or not stem.strip():
        return BookInfo(DEFAULT_AUTHOR, DEFAULT_AUTHOR)

    # 从右向左找最后一个 '-'，作为书名和作者的分隔符
    if "-" in stem:
        last_dash = stem.rfind("-")
        title = stem[:last_dash].strip()
        author = stem[last_dash + 1 :].strip()

        # 如果解析出的任一部分为空，使用默认值
        if not title:
            title = stem.strip()
            author = DEFAULT_AUTHOR
        elif not author:
            author = DEFAULT_AUTHOR
    else:
        title = stem.strip()
        author = DEFAULT_AUTHOR

    return BookInfo(title, author)


def find_epub_files(directory: Path) -> list[Path]:
    """查找目录下所有 EPUB 文件"""
    files = list(directory.rglob("*.epub"))
    if not files:
        typer.echo("❌ 未找到 EPUB 文件", err=True)
        raise typer.Exit(1)
    return files


def update_epub_metadata(epub_path: Path, info: BookInfo) -> None:
    """更新 EPUB 文件的元数据"""
    book = epub.read_epub(str(epub_path))

    # 使用完整的 Dublin Core 命名空间
    dc_ns = "http://purl.org/dc/elements/1.1/"

    # 确保命名空间存在
    if dc_ns not in book.metadata:
        book.metadata[dc_ns] = {}

    # 更新标题
    book.metadata[dc_ns]["title"] = [(info.title, {})]

    # 清空旧作者后添加新作者
    book.metadata[dc_ns]["creator"] = []
    book.add_author(info.author)

    # 写入文件
    epub.write_epub(str(epub_path), book, {})


# -------------------------
# 统计类
# -------------------------
@dataclass
class OperationStats:
    total: int = 0
    success: int = 0
    skipped: int = 0
    failed: int = 0

    def print_summary(self, operation: str):
        """打印操作统计"""
        typer.echo("\n" + "=" * 50)
        typer.echo(f"📊 {operation} 统计")
        typer.echo(f"总计: {self.total} | 成功: {self.success} | " f"跳过: {self.skipped} | 失败: {self.failed}")
        typer.echo("=" * 50)


# -------------------------
# 命令 1：元数据 → 文件名
# -------------------------
@app.command()
def rename(
    directory: Path = typer.Argument(..., exists=True, file_okay=False, help="包含 EPUB 文件的目录"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="预览模式，不实际重命名"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r/-R", help="是否递归搜索子目录"),
):
    """
    根据 EPUB 元数据重命名文件为：书名-作者.epub
    """
    typer.echo(f"🔍 扫描目录: {directory}")
    if dry_run:
        typer.echo("⚠️  预览模式（不会实际修改文件）\n")

    epub_files = find_epub_files(directory) if recursive else list(directory.glob("*.epub"))
    stats = OperationStats(total=len(epub_files))

    for epub_file in epub_files:
        try:
            info = read_epub_meta(epub_file)
            new_name = info.to_filename()
            new_path = epub_file.with_name(new_name)

            # 跳过已经正确命名的文件
            if epub_file.name == new_name:
                stats.skipped += 1
                continue

            # 检查目标文件是否存在
            if new_path.exists() and new_path != epub_file:
                typer.echo(f"⚠️  目标文件已存在，跳过: {epub_file.name}")
                stats.skipped += 1
                continue

            typer.echo(f"📝 {epub_file.name}")
            typer.echo(f"   → {new_name}")

            if not dry_run:
                epub_file.rename(new_path)

            stats.success += 1

        except Exception as e:
            typer.echo(f"❌ 失败: {epub_file.name}\n   错误: {e}", err=True)
            stats.failed += 1

    stats.print_summary("重命名")


# -------------------------
# 命令 2：文件名 → 元数据
# -------------------------
@app.command("sync-meta")
def sync_meta(
    directory: Path = typer.Argument(..., exists=True, file_okay=False, help="包含 EPUB 文件的目录"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="预览模式，不实际写入"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", "-r/-R", help="是否递归搜索子目录"),
    overwrite: bool = typer.Option(False, "--overwrite", "-o", help="覆盖已有的元数据"),
):
    """
    根据文件名（书名-作者.epub）更新 EPUB 元数据
    """
    typer.echo(f"🔍 扫描目录: {directory}")
    if dry_run:
        typer.echo("⚠️  预览模式（不会实际修改文件）\n")

    epub_files = find_epub_files(directory) if recursive else list(directory.glob("*.epub"))
    stats = OperationStats(total=len(epub_files))

    for epub_file in epub_files:
        try:
            # 从文件名解析信息
            info = parse_filename(epub_file)

            # 如果不覆盖，检查现有元数据是否与文件名匹配
            if not overwrite:
                try:
                    current_info = read_epub_meta(epub_file)
                    # 如果元数据已经和文件名一致，跳过
                    if current_info.title == info.title and current_info.author == info.author:
                        typer.echo(f"⏭️  元数据已是最新，跳过: {epub_file.name}")
                        stats.skipped += 1
                        continue
                except:
                    # 如果读取元数据失败，继续更新
                    pass

            typer.echo(f"📝 {epub_file.name}")
            typer.echo(f"   标题: {info.title}")
            typer.echo(f"   作者: {info.author}")

            if not dry_run:
                update_epub_metadata(epub_file, info)

            stats.success += 1

        except Exception as e:
            typer.echo(f"❌ 失败: {epub_file.name}\n   错误: {e}", err=True)
            stats.failed += 1

    stats.print_summary("元数据同步")


# -------------------------
# 命令 3：查看元数据
# -------------------------
@app.command("info")
def show_info(
    file: Path = typer.Argument(..., exists=True, dir_okay=False),
):
    """
    显示 EPUB 文件的元数据信息
    """
    try:
        info = read_epub_meta(file)
        filename_info = parse_filename(file)

        typer.echo(f"\n📚 文件: {file.name}")
        typer.echo(f"{'=' * 50}")
        typer.echo(f"元数据标题: {info.title}")
        typer.echo(f"元数据作者: {info.author}")
        typer.echo(f"\n文件名标题: {filename_info.title}")
        typer.echo(f"文件名作者: {filename_info.author}")

        if info.title != filename_info.title or info.author != filename_info.author:
            typer.echo(f"\n⚠️  元数据与文件名不一致")
        else:
            typer.echo(f"\n✅ 元数据与文件名一致")

    except Exception as e:
        typer.echo(f"❌ 读取失败: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
