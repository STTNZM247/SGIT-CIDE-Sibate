from __future__ import annotations

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


MAX_PRODUCT_IMAGE_SIDE = 1280
PRODUCT_IMAGE_QUALITY = 78


def optimize_image_field_to_webp(image_field, *, max_side=MAX_PRODUCT_IMAGE_SIDE, quality=PRODUCT_IMAGE_QUALITY):
    """Optimize an ImageField file in-memory and replace it with a WEBP version.

    Returns True if optimization succeeded and field was updated.
    """
    if not image_field:
        return False

    try:
        image_field.open("rb")
        with Image.open(image_field) as img:
            img = ImageOps.exif_transpose(img)

            # Convert to RGB-friendly mode before WEBP export.
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

            img.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)

            out = BytesIO()
            img.save(out, format="WEBP", optimize=True, quality=quality, method=6)
            out.seek(0)

        original_name = Path(getattr(image_field, "name", "imagen")).name
        base_name = Path(original_name).stem or "imagen"
        new_name = f"{base_name}.webp"
        image_field.save(new_name, ContentFile(out.read()), save=False)
        return True
    except Exception:
        return False
    finally:
        try:
            image_field.close()
        except Exception:
            pass
