import json
import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


CSS_LINK_PATTERN = re.compile(r"(?:css_asset|static)\s+['\"](inventario/css/[^'\"]+\.css)['\"]")
IMPORT_PATTERN = re.compile(
    r"@import\s+(?:url\(\s*)?['\"](?P<path>[^'\"\)]+)['\"]\s*\)?\s*;",
    re.IGNORECASE,
)
COMMENT_PATTERN = re.compile(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", re.DOTALL)


class Command(BaseCommand):
    help = "Bundle and minify CSS entrypoints referenced by templates into static/inventario/css-build/."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-minify",
            action="store_true",
            help="Generate bundled output without minification.",
        )
        parser.add_argument(
            "--keep-old",
            action="store_true",
            help="Do not delete previous build outputs in css-build before generating.",
        )

    def handle(self, *args, **options):
        minify = not options["no_minify"]
        keep_old = options["keep_old"]

        templates_root = settings.BASE_DIR / "inventario" / "templates"
        static_root = settings.BASE_DIR / "inventario" / "static"
        source_css_root = static_root / "inventario" / "css"
        build_root = static_root / "inventario" / "css-build"
        manifest_path = build_root / "manifest.json"

        if not templates_root.exists():
            raise CommandError(f"Templates folder not found: {templates_root}")
        if not source_css_root.exists():
            raise CommandError(f"Source CSS folder not found: {source_css_root}")

        entrypoints = self._collect_css_entrypoints(templates_root)
        if not entrypoints:
            self.stdout.write(self.style.WARNING("No CSS entrypoints found in templates."))
            return

        if build_root.exists() and not keep_old:
            for path in sorted(build_root.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    try:
                        path.rmdir()
                    except OSError:
                        pass

        build_root.mkdir(parents=True, exist_ok=True)

        manifest = {}
        for rel in sorted(entrypoints):
            source_file = static_root / rel
            if not source_file.is_file():
                raise CommandError(f"CSS entrypoint not found: {source_file}")

            bundled = self._bundle_css(source_file, source_css_root, stack=[])
            if minify:
                bundled = self._minify_css(bundled)

            built_rel = rel.replace("inventario/css/", "inventario/css-build/")
            built_rel = built_rel[:-4] + ".min.css"
            target_file = static_root / built_rel
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text(bundled, encoding="utf-8")
            manifest[rel] = built_rel

        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

        self.stdout.write(self.style.SUCCESS(f"Built CSS files: {len(manifest)}"))
        self.stdout.write(f"Manifest: {manifest_path}")

    def _collect_css_entrypoints(self, templates_root: Path) -> set[str]:
        entrypoints: set[str] = set()
        for tpl in templates_root.rglob("*.html"):
            text = tpl.read_text(encoding="utf-8", errors="ignore")
            for match in CSS_LINK_PATTERN.finditer(text):
                entrypoints.add(match.group(1))
        return entrypoints

    def _bundle_css(self, css_file: Path, source_css_root: Path, stack: list[Path]) -> str:
        css_file = css_file.resolve()
        if css_file in stack:
            chain = " -> ".join(str(p) for p in stack + [css_file])
            raise CommandError(f"Circular CSS import detected: {chain}")

        try:
            text = css_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandError(f"Could not read CSS file {css_file}: {exc}") from exc

        def replace_import(match: re.Match) -> str:
            import_target = match.group("path").strip()
            if import_target.startswith(("http://", "https://", "data:")):
                return match.group(0)

            imported_file = (css_file.parent / import_target).resolve()
            if not imported_file.is_file():
                raise CommandError(f"Missing imported CSS file: {imported_file} (from {css_file})")

            try:
                imported_file.relative_to(source_css_root.resolve())
            except ValueError as exc:
                raise CommandError(
                    f"Imported CSS is outside source root: {imported_file}"
                ) from exc

            return "\n" + self._bundle_css(imported_file, source_css_root, stack + [css_file]) + "\n"

        return IMPORT_PATTERN.sub(replace_import, text)

    def _minify_css(self, css: str) -> str:
        css = COMMENT_PATTERN.sub("", css)
        css = re.sub(r"\s+", " ", css)
        css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
        css = css.replace(";}", "}")
        return css.strip() + "\n"
