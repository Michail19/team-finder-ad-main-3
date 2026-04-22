import io
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent

AVATAR_SIZE = (200, 200)
AVATAR_FONT_SIZE = 100
AVATAR_TEXT_Y_OFFSET = 10
DEFAULT_AVATAR_LETTER = "U"
DEFAULT_AVATAR_FILENAME_TEMPLATE = "default_avatar_{email}.png"
AVATAR_FONT_PATH = BASE_DIR / "assets" / "fonts" / "DejaVuSans-Bold.ttf"
AVATAR_BACKGROUND_COLORS = (
    "#5E81AC",
    "#6A8E7F",
    "#8F7A66",
    "#7B8FA1",
    "#8C7AA9",
    "#6D8299",
)


def get_avatar_font(size):
    try:
        return ImageFont.truetype(str(AVATAR_FONT_PATH), size)
    except OSError:
        return ImageFont.load_default()


def generate_avatar(name):
    image = Image.new("RGB", AVATAR_SIZE, random.choice(AVATAR_BACKGROUND_COLORS))
    draw = ImageDraw.Draw(image)

    letter = (name[:1] or DEFAULT_AVATAR_LETTER).upper()
    font = get_avatar_font(AVATAR_FONT_SIZE)

    bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (AVATAR_SIZE[0] - text_width) / 2
    y = (AVATAR_SIZE[1] - text_height) / 2 - AVATAR_TEXT_Y_OFFSET

    draw.text((x, y), letter, fill="white", font=font)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
