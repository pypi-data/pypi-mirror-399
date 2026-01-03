from pathlib import Path
from typing import List, Optional

import typer
from pydantic import BaseModel, Field, ValidationError
from sbook.core.book import EpubCreator, Chapter


class ChapterModel(BaseModel):
    id: int | str
    title: str
    content: str


class NovelModel(BaseModel):
    title: str = "Unknown Title"
    author: str = "Unknown Author"
    description: Optional[str] = ""
    cover: Optional[str] = ""
    genre: Optional[str] = ""
    novel_id: Optional[int] = None
    chapters: List[ChapterModel] = Field(default_factory=list)


def process_content_text(text: str) -> str:
    if not text:
        return ""

    if any(tag in text for tag in ("<p>", "<div>", "<br")):
        return text

    lines = text.split("\n")
    return "".join(f"<p>{line.strip()}</p>" for line in lines if line.strip())


class EpubConvertService:
    @staticmethod
    def load_novel(json_path: Path) -> NovelModel:
        try:
            return NovelModel.model_validate_json(json_path.read_text(encoding="utf-8"))
        except ValidationError as e:
            raise ValueError(f"JSON 校验失败:\n{e}")

    @staticmethod
    def build_chapters(novel: NovelModel) -> List[Chapter]:
        if not novel.chapters:
            raise ValueError("chapters 不能为空")

        return [
            Chapter(
                id=c.id,
                title=c.title,
                content=c.content,
            )
            for c in novel.chapters
        ]

    @staticmethod
    def export_epub(
        novel: NovelModel,
        chapters: List[Chapter],
        output_dir: Path,
        logger,
    ) -> Path | None:
        creator = EpubCreator(
            title=novel.title,
            author=novel.author,
            description=novel.description,
            cover_url=novel.cover,
            genre=novel.genre,
            novel_id=novel.novel_id,
            output_dir=output_dir,
            logger=logger,
            content_processor=process_content_text,
        )
        return creator.export(chapters)


app = typer.Typer(help="将 JSON 小说数据转换为 EPUB 电子书")


@app.command()
def convert(
    json_path: Path = typer.Argument(..., exists=True, file_okay=True, readable=True),
    output_dir: Path = typer.Option(None, "-o", "--output-dir", help="EPUB 输出目录"),
):
    if output_dir is None:
        output_dir = json_path.parent

    typer.secho(f"📖 正在读取: {json_path}", fg=typer.colors.CYAN)

    try:
        novel = EpubConvertService.load_novel(json_path)
        chapters = EpubConvertService.build_chapters(novel)
        epub_path = EpubConvertService.export_epub(
            novel,
            chapters,
            output_dir,
            logger=lambda m: typer.echo(f"   >> {m}"),
        )
    except Exception as e:
        typer.secho(f"❌ {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.secho("🎉 导出完成", fg=typer.colors.GREEN, bold=True)
    typer.secho(f"📚 文件路径: {epub_path}", fg=typer.colors.BLUE)


if __name__ == "__main__":
    app()
