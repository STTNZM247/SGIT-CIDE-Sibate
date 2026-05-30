import json
from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@lru_cache(maxsize=1)
def _load_css_manifest() -> dict[str, str]:
    if not getattr(settings, "USE_BUILT_CSS", False):
        return {}

    manifest_path = Path(
        getattr(
            settings,
            "CSS_ASSET_MANIFEST",
            settings.BASE_DIR / "inventario" / "static" / "inventario" / "css-build" / "manifest.json",
        )
    )

    if not manifest_path.is_file():
        return {}

    try:
        with manifest_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(data, dict):
        return {}

    return {str(k): str(v) for k, v in data.items()}


@register.simple_tag
def css_asset(path: str) -> str:
    manifest = _load_css_manifest()
    return static(manifest.get(path, path))
