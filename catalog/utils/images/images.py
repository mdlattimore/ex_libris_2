from __future__ import annotations

import uuid
from io import BytesIO
from PIL import Image, ImageOps
from django.core.files.base import ContentFile

IMAGE_SIZES = {"thumb": 240, "display": 900, "detail": 1800}
WEBP_QUALITY = 85

def _to_rgb(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        alpha = img.split()[-1]
        bg.paste(img, mask=alpha)
        return bg
    if img.mode != "RGB":
        return img.convert("RGB")
    return img

def _resize_by_width(img: Image.Image, target_w: int) -> Image.Image:
    w, h = img.size
    if w <= target_w:
        return img
    target_h = round(h * (target_w / w))
    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

def _encode_webp(img: Image.Image, quality: int) -> ContentFile:
    buf = BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)
    return ContentFile(buf.getvalue())

def process_upload(uploaded_file, *, sizes=IMAGE_SIZES, quality=WEBP_QUALITY):
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img)
    img = _to_rgb(img)

    base = uuid.uuid4().hex[:12]  # 48 bits; scoped per-volume

    detail = _resize_by_width(img, sizes["detail"])
    display = _resize_by_width(img, sizes["display"])
    thumb = _resize_by_width(img, sizes["thumb"])

    return base, _encode_webp(thumb, quality), _encode_webp(display, quality), _encode_webp(detail, quality)