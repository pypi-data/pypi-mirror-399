from pathlib import Path
from io import BytesIO
import random
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
import math


# ========== 字体路径函数 ==========
def font_path(filename: str) -> Path:
    """获取字体文件路径"""
    return Path(__file__).resolve().parent.parent / "static" / filename


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    """安全加载字体，找不到时使用默认字体"""
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


# ========== 主函数 ==========
def _draw_star(
    draw: ImageDraw.ImageDraw, center: tuple[int, int], height: int, color: tuple[int, int, int] = (249, 249, 249)
):
    x, y = center
    outer_radius = height / 2
    inner_radius = outer_radius * 0.382
    rotation = math.radians(random.uniform(0, 360))

    points = []
    for i in range(10):
        angle = rotation + math.pi / 5 * i
        radius = outer_radius if i % 2 == 0 else inner_radius
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))

    draw.polygon(points, fill=color)


def _draw_border(draw: ImageDraw.ImageDraw, width: int, height: int, border_size: int, border_color: str = "black"):
    if border_size <= 0:
        return

    # 外层矩形坐标
    outer = (0, 0, width - 1, height - 1)

    # 内层矩形坐标（去掉边框厚度）
    inner = (border_size, border_size, width - border_size - 1, height - border_size - 1)

    # 先画外框矩形
    draw.rectangle(outer, outline=border_color, width=border_size)

    # 或者如果希望边框是“实心包边”的，可以这样绘制四个边：
    # left
    draw.rectangle([0, 0, border_size - 1, height - 1], fill=border_color)
    # right
    draw.rectangle([width - border_size, 0, width - 1, height - 1], fill=border_color)
    # top
    draw.rectangle([0, 0, width - 1, border_size - 1], fill=border_color)
    # bottom
    draw.rectangle([0, height - border_size, width - 1, height - 1], fill=border_color)


def create_book_cover(
    title: str,
    author: str = "未知作者",
    title_color: Tuple[int, int, int] = (249, 249, 249),
    title_size: int = 110,
    author_color: Tuple[int, int, int] = (47, 46, 52),
    author_size: int = 80,
    cover_width: int = 960,
    cover_height: int = 1280,
    background_color: Tuple[int, int, int] = (249, 249, 249),
    top_color: Tuple[int, int, int] = (47, 46, 52),
    top_rate: float = 0.6,
    line_size: int = 4,
    line_space: int = 14,
    line_height: int = 18,
) -> bytes:
    """生成一本简洁优雅的电子书封面"""
    # 创建画布
    cover = Image.new("RGBA", (cover_width, cover_height), background_color)
    draw = ImageDraw.Draw(cover)

    # 绘制上半部分色块
    top_rect = [(0, 0), (cover_width, cover_height * top_rate)]
    draw.rectangle(top_rect, fill=top_color)

    # 分隔线1
    top_height = cover_height * top_rate

    for i in range(line_size):
        line_top = top_height + line_space * (i + 1) + line_height * i
        line_bottom = line_top + line_height
        draw.rectangle([(0, line_top), (cover_width, line_bottom)], fill=top_color)

    _draw_border(draw=draw, width=cover_width, height=cover_height, border_size=8, border_color=top_color)

    # 加载字体
    title_font = load_font(font_path("DouyinSansBold.otf"), title_size)
    author_font = load_font(font_path("hanyiyoukaifanti.ttf"), author_size)

    # ========== 文本排版 ==========
    # 自动折行标题（若标题太长）
    max_title_width = int(cover_width * 0.9)
    words = list(title)
    lines = []
    current = ""
    for w in words:
        test = current + w
        if draw.textlength(test, font=title_font) > max_title_width:
            lines.append(current)
            current = w
        else:
            current = test
    if current:
        lines.append(current)

    # 绘制标题（多行居中）
    total_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] for line in lines)
    y = (cover_height * top_rate - total_height) / 2
    for line in lines:
        text_width = draw.textlength(line, font=title_font)
        x = (cover_width - text_width) / 2
        draw.text((x, y), line, fill=title_color, font=title_font)
        y += title_size * 1.1

    # 绘制作者名
    x1, y1, x2, y2 = draw.textbbox((0, 0), author, font=author_font)
    author_width = x2 - x1
    author_height = y2 - y1
    author_x = (cover_width - author_width) / 2
    author_y = line_bottom + (cover_height - line_bottom - author_height) / 2 - y1
    draw.text((author_x, author_y), author, fill=author_color, font=author_font)

    # 保存到内存
    buffer = BytesIO()
    cover.save(buffer, format="PNG")
    return buffer.getvalue()


def create_simple_book_cover(title: str, author: str = "未知作者", output: str = "") -> str:
    """
    创建简洁电子书封面并保存到指定目录，文件名固定为 cover.png。
    """
    # 生成封面
    image_bytes = create_book_cover(title=title, author=author)

    # 输出目录处理
    output_dir = Path(output) if output else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 文件名固定
    output_file = output_dir / "cover.png"

    # 保存文件
    with open(output_file, "wb") as f:
        f.write(image_bytes)

    return str(output_file)


# ========== 主方法（测试入口） ==========
if __name__ == "__main__":
    output_path = Path(__file__).resolve().parent / "test_cover.png"

    print("🎨 正在生成测试封面...")
    image_bytes = create_book_cover(title="月光下的旅人", author="李清晨")

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    print(f"✅ 测试封面已生成：{output_path}")
