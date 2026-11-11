from __future__ import annotations

import re
import sys
from pathlib import Path


FONT_CANDIDATES = [
    "C:/Windows/Fonts/malgun.ttf",
    "/System/Library/Fonts/AppleSDGothicNeo.ttc",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
]

PADDING = 24
LINE_HEIGHT = 30
FONT_SIZE = 18
BG_COLOR = "#1e1e1e"
TITLE_COLOR = "#4ec9b0"
HEADER_COLOR = "#dcdcaa"
TEXT_COLOR = "#d4d4d4"
GRID_COLOR = "#555555"
COLUMN_GAP = 28


def load_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow 가 필요합니다. 다음 명령으로 설치하세요: pip install pillow", file=sys.stderr)
        raise SystemExit(1)
    return Image, ImageDraw, ImageFont


def load_font(image_font_module):
    for candidate in FONT_CANDIDATES:
        path = Path(candidate)
        if path.exists():
            return image_font_module.truetype(str(path), FONT_SIZE)
    print(
        "사용 가능한 한글 폰트를 찾지 못했습니다. 다음 경로 중 하나에 폰트를 준비하세요: "
        + ", ".join(FONT_CANDIDATES),
        file=sys.stderr,
    )
    raise SystemExit(1)


def is_separator_line(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and re.fullmatch(r"[-+ ]+", stripped) is not None


def parse_table_rows(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            break
        if is_separator_line(line):
            index += 1
            continue
        if "|" not in line:
            break
        rows.append([cell.strip() for cell in line.split("|")])
        index += 1
    return rows, index


def compute_table_widths(rows: list[list[str]], font) -> list[int]:
    column_count = max(len(row) for row in rows)
    widths = [0] * column_count
    for row in rows:
        for i in range(column_count):
            cell = row[i] if i < len(row) else ""
            widths[i] = max(widths[i], int(font.getlength(cell)))
    return widths


def build_blocks(lines: list[str], font) -> list[dict]:
    blocks: list[dict] = []
    index = 0
    while index < len(lines):
        if (
            index + 1 < len(lines)
            and "|" in lines[index]
            and is_separator_line(lines[index + 1])
        ):
            rows, next_index = parse_table_rows(lines, index)
            if rows:
                widths = compute_table_widths(rows, font)
                blocks.append(
                    {
                        "type": "table",
                        "rows": rows,
                        "widths": widths,
                    }
                )
                index = next_index
                continue

        blocks.append(
            {
                "type": "text",
                "text": lines[index],
            }
        )
        index += 1
    return blocks


def measure_block_width(block: dict, font) -> int:
    if block["type"] == "text":
        return int(font.getlength(block["text"]))
    widths = block["widths"]
    if not widths:
        return 0
    return int(sum(widths) + (COLUMN_GAP * (len(widths) - 1)))


def compute_canvas_size(blocks: list[dict], font) -> tuple[int, int]:
    max_width = 0
    line_count = 0
    for block in blocks:
        max_width = max(max_width, measure_block_width(block, font))
        if block["type"] == "text":
            line_count += 1
        else:
            line_count += len(block["rows"])

    width = int(max_width + (PADDING * 2))
    height = int((line_count * LINE_HEIGHT) + (PADDING * 2))
    return width, height


def draw_text_block(draw, font, text: str, y: int) -> None:
    color = TITLE_COLOR if text.startswith("===") else TEXT_COLOR
    draw.text((int(PADDING), int(y)), text, font=font, fill=color)


def draw_table_block(draw, font, rows: list[list[str]], widths: list[int], y: int) -> None:
    x_positions: list[int] = []
    current_x = int(PADDING)
    for i, width in enumerate(widths):
        x_positions.append(int(current_x))
        current_x = int(current_x + width + COLUMN_GAP)
        if i < len(widths) - 1:
            line_x = int(x_positions[-1] + width + (COLUMN_GAP // 2))
            draw.line(
                [(line_x, int(y)), (line_x, int(y + (len(rows) * LINE_HEIGHT)))],
                fill=GRID_COLOR,
                width=1,
            )

    for row_index, row in enumerate(rows):
        row_y = int(y + (row_index * LINE_HEIGHT))
        for col_index, x in enumerate(x_positions):
            cell = row[col_index] if col_index < len(row) else ""
            color = HEADER_COLOR if row_index == 0 else TEXT_COLOR
            draw.text((int(x), int(row_y)), cell, font=font, fill=color)

        if row_index == 0:
            line_y = int(row_y + LINE_HEIGHT - 6)
            left_x = int(PADDING)
            right_x = int(PADDING + sum(widths) + (COLUMN_GAP * (len(widths) - 1)))
            draw.line([(left_x, line_y), (right_x, line_y)], fill=GRID_COLOR, width=1)


def render_file(input_path: Path, output_path: Path, image_module, image_draw_module, font) -> None:
    text = input_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    blocks = build_blocks(lines, font)
    width, height = compute_canvas_size(blocks, font)

    image = image_module.new("RGB", (int(width), int(height)), BG_COLOR)
    draw = image_draw_module.Draw(image)

    current_y = int(PADDING)
    for block in blocks:
        if block["type"] == "text":
            draw_text_block(draw, font, block["text"], current_y)
            current_y = int(current_y + LINE_HEIGHT)
        else:
            draw_table_block(draw, font, block["rows"], block["widths"], current_y)
            current_y = int(current_y + (len(block["rows"]) * LINE_HEIGHT))

    image.save(output_path)


def main() -> int:
    image_module, image_draw_module, image_font_module = load_pillow()
    font = load_font(image_font_module)

    root = Path(__file__).resolve().parent.parent
    results_dir = root / "results"
    screenshots_dir = results_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    targets: list[tuple[Path, Path]] = []
    for i in range(1, 16):
        name = f"Q{i:02d}"
        targets.append((results_dir / f"{name}.txt", screenshots_dir / f"{name}.png"))
    targets.append((results_dir / "all_queries.txt", screenshots_dir / "all_queries.png"))

    created = 0
    for input_path, output_path in targets:
        try:
            render_file(input_path, output_path, image_module, image_draw_module, font)
            created += 1
        except Exception as exc:
            print(f"실패: {input_path.name}: {exc}", file=sys.stderr)
            return 1

    print(created)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
