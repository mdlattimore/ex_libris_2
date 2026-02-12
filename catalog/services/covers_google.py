from __future__ import annotations

import os
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.db import transaction

from catalog.models import Volume, VolumeImage


def _https(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("http://"):
        return "https://" + url[len("http://"):]
    return url


def _guess_ext(url: str, content_type: str) -> str:
    ct = (content_type or "").lower()
    if "png" in ct:
        return ".png"
    if "webp" in ct:
        return ".webp"
    if "jpeg" in ct or "jpg" in ct:
        return ".jpg"

    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    return ext if ext in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"


def _download_image_bytes(url: str, timeout: int = 12) -> tuple[bytes, str]:
    r = requests.get(
        url,
        timeout=timeout,
        allow_redirects=True,
        headers={
            "User-Agent": "ExLibrisCoverFetcher/1.0",
            "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        },
    )
    r.raise_for_status()
    return r.content, (r.headers.get("Content-Type") or "")


@transaction.atomic
def cache_google_cover_for_volume(volume: Volume) -> bool:
    """
    Download volume.cover_url once (Google thumbnail), store it into a VolumeImage
    (thumb/display/detail), set kind=COVER, and attach to volume.cover_image.

    Returns True if cached, False if skipped/failed.
    """
    # already cached or user-set cover
    if volume.cover_image_id:
        return False

    cover_url = getattr(volume, "cover_url", None)
    if not cover_url:
        return False

    url = _https(cover_url)

    try:
        data, ctype = _download_image_bytes(url)

        # reject tiny payloads (often non-image responses)
        if len(data) < 2_000:
            return False

        ext = _guess_ext(url, ctype)
        base = f"vol-{volume.pk}-cover{ext}"
        content = ContentFile(data)

        vi = VolumeImage(
            volume=volume,
            kind="COVER",
            caption="Stock cover (cached from Google)",
            sort_order=0,
        )

        # Save the SAME bytes into all three fields.
        # If you later want different sizes, you can generate them in your ingest pipeline.
        vi.image_thumb.save(base.replace(ext, f"-thumb{ext}"), ContentFile(data), save=False)
        vi.image_display.save(base.replace(ext, f"-display{ext}"), ContentFile(data), save=False)
        vi.image_detail.save(base.replace(ext, f"-detail{ext}"), ContentFile(data), save=False)
        vi.save()

        volume.cover_image = vi
        volume.save(update_fields=["cover_image"])
        return True

    except Exception:
        return False
