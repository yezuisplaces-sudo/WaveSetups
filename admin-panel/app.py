import json
import os
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename


ROOT_DIR = Path(__file__).resolve().parent.parent
DOCS_JSON_PATH = ROOT_DIR / "docs.json"
IMAGE_UPLOAD_DIR = ROOT_DIR / "images" / "uploads"
ALLOWED_EDIT_EXTENSIONS = {".md", ".mdx", ".json"}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
SYSTEM_DIRS = {"admin-panel", "node_modules", ".git", "docs", "images"}
ROOT_EDITABLE_FILES = {"support.mdx", "docs.json"}


def slugify(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or "yeni-sayfa"


def prettify_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-")).strip() or "Kategori"


def normalize_text(value: str) -> str:
    # Fixes Windows CRLF expansion creating extra empty lines on repeated saves.
    return value.replace("\r\n", "\n").replace("\r", "\n")


def read_docs_json() -> dict:
    if not DOCS_JSON_PATH.exists():
        return {}
    return json.loads(DOCS_JSON_PATH.read_text(encoding="utf-8"))


def write_docs_json(data: dict) -> None:
    with DOCS_JSON_PATH.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")




def write_text_file(path: Path, content: str) -> None:
    normalized = normalize_text(content)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(normalized)
def is_allowed_image(filename: str) -> bool:
    suffix = Path(filename).suffix.lower()
    return suffix in ALLOWED_IMAGE_EXTENSIONS


def list_uploaded_images() -> list[dict]:
    IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    items: list[dict] = []
    for file in sorted(IMAGE_UPLOAD_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True):
        if not file.is_file():
            continue
        rel = file.relative_to(ROOT_DIR).as_posix()
        web_path = f"/{rel}"
        items.append(
            {
                "name": file.name,
                "web_path": web_path,
                "markdown": f"![{file.stem}]({web_path})",
            }
        )
    return items


def create_page_template(title: str, category_slug: str) -> str:
    description_map = {
        "pluginler": "Bu eklentiye ait kurulum, komut ve yapÄ±landÄ±rma dokÃ¼mantasyonu.",
        "paketler": "Bu pakete ait kurulum, yapÄ±landÄ±rma ve kullanÄ±m dokÃ¼mantasyonu.",
        "ana-sayfa": "Bu sayfada ilgili konuya ait temel bilgiler yer alÄ±r.",
    }
    return f"""---
title: {title}
description: {description_map.get(category_slug, "Bu sayfaya ait dokÃ¼mantasyon iÃ§eriÄŸi.")}
icon: file-text
---

## Genel BakÄ±ÅŸ

Bu bÃ¶lÃ¼mde **{title}** iÃ§in temel bilgileri bulabilirsiniz.

## Kurulum

1. Buraya kurulum adÄ±mlarÄ±nÄ± ekleyin.
2. Gerekli dosyalarÄ± ve sÃ¼rÃ¼mleri belirtin.
3. Varsa Ã¶zel notlarÄ± ekleyin.

## Komutlar ve Yetkiler

| Komut | AÃ§Ä±klama | Yetki |
| --- | --- | --- |
| `/ornek` | Ã–rnek komut aÃ§Ä±klamasÄ± | Oyuncu |

## Sorun Giderme

- SÄ±k karÅŸÄ±laÅŸÄ±lan hatalarÄ± ve Ã§Ã¶zÃ¼mlerini bu alana yazÄ±n.
"""


def get_docs_pages_root(docs: dict) -> list:
    try:
        return docs["navigation"]["tabs"][0]["dropdowns"][0]["pages"]
    except (KeyError, IndexError, TypeError):
        return []


def group_matches_category(group_entry: dict, category_slug: str) -> bool:
    pages = group_entry.get("pages", [])
    if any(isinstance(p, str) and p.startswith(f"{category_slug}/") for p in pages):
        return True
    # Fallback for empty or custom groups.
    return slugify(group_entry.get("group", "")) == category_slug


def ensure_category_group(docs: dict, category_slug: str, category_label: str) -> dict:
    pages_root = get_docs_pages_root(docs)
    for entry in pages_root:
        if isinstance(entry, dict) and group_matches_category(entry, category_slug):
            entry.setdefault("pages", [])
            return entry

    new_group = {"group": category_label, "pages": []}
    pages_root.append(new_group)
    return new_group


def add_page_to_navigation(category_slug: str, page_slug: str) -> None:
    docs = read_docs_json()
    pages_root = get_docs_pages_root(docs)
    if not pages_root:
        return

    full_page_path = (
        f"ana-sayfa/{page_slug}" if category_slug == "ana-sayfa" else f"{category_slug}/{page_slug}"
    )

    if category_slug == "ana-sayfa":
        if full_page_path not in pages_root:
            insert_idx = 0
            while insert_idx < len(pages_root) and isinstance(pages_root[insert_idx], str):
                insert_idx += 1
            pages_root.insert(insert_idx, full_page_path)
        write_docs_json(docs)
        return

    if category_slug == "pluginler":
        group_label = "Pluginler"
    elif category_slug == "paketler":
        group_label = "Plugin Paketleri"
    else:
        group_label = prettify_slug(category_slug)

    group = ensure_category_group(docs, category_slug, group_label)
    group_pages = group.setdefault("pages", [])
    if full_page_path not in group_pages:
        group_pages.append(full_page_path)
    write_docs_json(docs)


def remove_page_from_navigation(page_path: str) -> None:
    docs = read_docs_json()
    pages_root = get_docs_pages_root(docs)
    if not pages_root:
        return

    normalized_path = page_path.replace("\\", "/").strip()
    no_ext_path = normalized_path
    if no_ext_path.endswith(".mdx"):
        no_ext_path = no_ext_path[:-4]
    elif no_ext_path.endswith(".md"):
        no_ext_path = no_ext_path[:-3]

    remove_candidates = {normalized_path, no_ext_path}

    new_root = []
    for entry in pages_root:
        if isinstance(entry, str):
            if entry not in remove_candidates:
                new_root.append(entry)
            continue

        if isinstance(entry, dict):
            group_pages = entry.get("pages", [])
            if isinstance(group_pages, list):
                group_pages = [p for p in group_pages if p not in remove_candidates]
                if group_pages:
                    entry["pages"] = group_pages
                    new_root.append(entry)
            else:
                new_root.append(entry)
            continue

        new_root.append(entry)

    docs["navigation"]["tabs"][0]["dropdowns"][0]["pages"] = new_root
    write_docs_json(docs)


def prune_missing_navigation_pages() -> int:
    docs = read_docs_json()
    pages_root = get_docs_pages_root(docs)
    if not pages_root:
        return 0

    removed = 0

    def page_exists(page_entry: str) -> bool:
        rel = page_entry.replace("\\", "/").strip()
        candidates = [ROOT_DIR / f"{rel}.mdx", ROOT_DIR / f"{rel}.md"]
        return any(p.exists() and p.is_file() for p in candidates)

    new_root = []
    for entry in pages_root:
        if isinstance(entry, str):
            if page_exists(entry):
                new_root.append(entry)
            else:
                removed += 1
            continue

        if isinstance(entry, dict):
            group_pages = entry.get("pages", [])
            if isinstance(group_pages, list):
                kept_pages = []
                for p in group_pages:
                    if isinstance(p, str) and page_exists(p):
                        kept_pages.append(p)
                    elif isinstance(p, str):
                        removed += 1
                    else:
                        kept_pages.append(p)
                if kept_pages:
                    entry["pages"] = kept_pages
                    new_root.append(entry)
            else:
                new_root.append(entry)
            continue

        new_root.append(entry)

    docs["navigation"]["tabs"][0]["dropdowns"][0]["pages"] = new_root
    write_docs_json(docs)
    return removed


def get_category_options() -> list[dict]:
    docs = read_docs_json()
    pages_root = get_docs_pages_root(docs)

    options = []
    seen = set()

    # Top-level (e.g., ana-sayfa)
    for entry in pages_root:
        if isinstance(entry, str) and "/" in entry:
            slug = entry.split("/", 1)[0]
            if slug not in seen:
                seen.add(slug)
                label = "Ana Sayfa" if slug == "ana-sayfa" else prettify_slug(slug)
                options.append({"slug": slug, "label": label})

    # Group-based categories
    for entry in pages_root:
        if not isinstance(entry, dict):
            continue
        group_label = entry.get("group", "").strip() or "Kategori"
        group_pages = entry.get("pages", [])
        if isinstance(group_pages, list) and group_pages:
            first = next((p for p in group_pages if isinstance(p, str) and "/" in p), "")
            slug = first.split("/", 1)[0] if first else slugify(group_label)
        else:
            slug = slugify(group_label)

        if slug not in seen:
            seen.add(slug)
            options.append({"slug": slug, "label": group_label})

    # Safety defaults
    defaults = [
        {"slug": "ana-sayfa", "label": "Ana Sayfa"},
        {"slug": "pluginler", "label": "Pluginler"},
        {"slug": "paketler", "label": "Plugin Paketleri"},
    ]
    for item in defaults:
        if item["slug"] not in seen:
            options.append(item)

    options.sort(key=lambda x: (x["slug"] != "ana-sayfa", x["label"].lower()))
    return options


def create_app() -> Flask:
    templates_dir = Path(__file__).resolve().parent / "templates"
    app = Flask(__name__, template_folder=str(templates_dir))
    app.secret_key = os.getenv("WAVE_ADMIN_SECRET", "change-this-secret")
    app.config["ADMIN_PASSWORD"] = os.getenv("WAVE_ADMIN_PASSWORD", "wavesetups-admin")

    def is_logged_in() -> bool:
        return bool(session.get("admin_ok"))

    def normalize_rel_path(rel_path: str) -> Path:
        candidate = (ROOT_DIR / rel_path).resolve()
        if ROOT_DIR not in candidate.parents and candidate != ROOT_DIR:
            raise ValueError("Invalid path")
        return candidate

    def list_editable_files() -> list[str]:
        items: list[str] = []

        for rel_file in ROOT_EDITABLE_FILES:
            abs_file = ROOT_DIR / rel_file
            if abs_file.exists():
                items.append(rel_file)

        for child in ROOT_DIR.iterdir():
            if not child.is_dir():
                continue
            if child.name in SYSTEM_DIRS:
                continue
            for path in child.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in ALLOWED_EDIT_EXTENSIONS:
                    continue
                items.append(path.relative_to(ROOT_DIR).as_posix())

        items.sort()
        return items

    @app.before_request
    def require_login():
        if request.endpoint in {"login", "static"}:
            return
        if not is_logged_in():
            return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            password = request.form.get("password", "")
            if password == app.config["ADMIN_PASSWORD"]:
                session["admin_ok"] = True
                return redirect(url_for("dashboard"))
            flash("Åifre hatalÄ±.")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/")
    def dashboard():
        prune_missing_navigation_pages()
        files = list_editable_files()
        categories = get_category_options()
        uploaded_images = list_uploaded_images()
        return render_template(
            "dashboard.html",
            files=files,
            categories=categories,
            uploaded_images=uploaded_images,
        )
    @app.route("/upload-image", methods=["POST"])
    def upload_image():
        file = request.files.get("image_file")
        if file is None or not file.filename:
            flash("Gorsel secilmedi.")
            return redirect(url_for("dashboard"))

        safe_name = secure_filename(file.filename)
        if not safe_name:
            flash("Dosya adi gecersiz.")
            return redirect(url_for("dashboard"))

        if not is_allowed_image(safe_name):
            flash("Desteklenmeyen gorsel formati.")
            return redirect(url_for("dashboard"))

        IMAGE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        suffix = Path(safe_name).suffix.lower()
        stem = slugify(Path(safe_name).stem)
        final_name = f"{stem}-{timestamp}{suffix}"
        target = IMAGE_UPLOAD_DIR / final_name

        file.save(target)
        flash(f"Gorsel yuklendi: images/uploads/{final_name}")
        return redirect(url_for("dashboard"))    @app.route("/create-category", methods=["POST"])
    def create_category():
        category_label = request.form.get("category_label", "").strip()
        if not category_label:
            flash("Kategori adÄ± boÅŸ olamaz.")
            return redirect(url_for("dashboard"))

        category_slug_input = request.form.get("category_slug", "").strip()
        category_slug = slugify(category_slug_input or category_label)
        first_page_title = request.form.get("first_page_title", "").strip() or "BaÅŸlangÄ±Ã§"
        first_page_slug = slugify(first_page_title)

        folder = ROOT_DIR / category_slug
        folder.mkdir(parents=True, exist_ok=True)

        page_rel = f"{category_slug}/{first_page_slug}.mdx"
        page_abs = normalize_rel_path(page_rel)
        if page_abs.exists():
            flash("Kategori veya baÅŸlangÄ±Ã§ sayfasÄ± zaten mevcut.")
            return redirect(url_for("edit_file", file=page_rel))

        write_text_file(page_abs, create_page_template(first_page_title, category_slug))

        docs = read_docs_json()
        pages_root = get_docs_pages_root(docs)
        if pages_root:
            group = ensure_category_group(docs, category_slug, category_label)
            group_pages = group.setdefault("pages", [])
            if page_rel not in group_pages:
                group_pages.append(page_rel)
            write_docs_json(docs)

        flash(f"Kategori oluÅŸturuldu: {category_label}")
        return redirect(url_for("edit_file", file=page_rel))

    @app.route("/create", methods=["POST"])
    def create_file():
        category = request.form.get("category", "").strip()
        title = request.form.get("title", "").strip()

        valid_categories = {item["slug"] for item in get_category_options()}
        if category not in valid_categories:
            flash("GeÃ§ersiz kategori seÃ§imi.")
            return redirect(url_for("dashboard"))

        if not title:
            flash("BaÅŸlÄ±k boÅŸ olamaz.")
            return redirect(url_for("dashboard"))

        page_slug = slugify(title)
        rel_path = f"{category}/{page_slug}.mdx"
        abs_path = normalize_rel_path(rel_path)

        if abs_path.exists():
            flash("Bu isimde bir dosya zaten var.")
            return redirect(url_for("edit_file", file=rel_path))

        abs_path.parent.mkdir(parents=True, exist_ok=True)
        write_text_file(abs_path, create_page_template(title, category))
        add_page_to_navigation(category, page_slug)
        flash(f"Yeni sayfa oluÅŸturuldu: {rel_path}")
        return redirect(url_for("edit_file", file=rel_path))

    @app.route("/edit", methods=["GET", "POST"])
    def edit_file():
        rel_path = request.args.get("file", "").strip()
        if not rel_path:
            flash("Dosya seÃ§imi yapÄ±lmadÄ±.")
            return redirect(url_for("dashboard"))

        try:
            abs_path = normalize_rel_path(rel_path)
        except ValueError:
            flash("GeÃ§ersiz dosya yolu.")
            return redirect(url_for("dashboard"))

        if not abs_path.exists() or not abs_path.is_file():
            flash("Dosya bulunamadÄ±.")
            return redirect(url_for("dashboard"))

        if abs_path.suffix.lower() not in ALLOWED_EDIT_EXTENSIONS:
            flash("Bu dosya tÃ¼rÃ¼ panelden dÃ¼zenlenemez.")
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            content = request.form.get("content", "")
            write_text_file(abs_path, content)
            flash(f"Kaydedildi: {rel_path}")
            return redirect(url_for("edit_file", file=rel_path))

        content = abs_path.read_text(encoding="utf-8")
        can_delete = rel_path.endswith(".md") or rel_path.endswith(".mdx")
        return render_template(
            "edit_file.html", rel_path=rel_path, content=content, can_delete=can_delete
        )

    @app.route("/delete", methods=["POST"])
    def delete_file():
        rel_path = request.form.get("file", "").strip()
        if not rel_path:
            flash("Silinecek dosya belirtilmedi.")
            return redirect(url_for("dashboard"))

        if rel_path in ROOT_EDITABLE_FILES:
            flash("Bu dosya panelden silinemez.")
            return redirect(url_for("edit_file", file=rel_path))

        try:
            abs_path = normalize_rel_path(rel_path)
        except ValueError:
            flash("GeÃ§ersiz dosya yolu.")
            return redirect(url_for("dashboard"))

        if not abs_path.exists() or not abs_path.is_file():
            flash("Dosya bulunamadÄ±.")
            return redirect(url_for("dashboard"))

        if abs_path.suffix.lower() not in {".md", ".mdx"}:
            flash("YalnÄ±zca iÃ§erik dosyalarÄ± silinebilir.")
            return redirect(url_for("edit_file", file=rel_path))

        abs_path.unlink()
        remove_page_from_navigation(rel_path)
        prune_missing_navigation_pages()
        flash(f"Dosya silindi: {rel_path}")
        return redirect(url_for("dashboard"))

    @app.route("/settings", methods=["GET", "POST"])
    def settings():
        if not DOCS_JSON_PATH.exists():
            flash("docs.json bulunamadÄ±.")
            return redirect(url_for("dashboard"))

        docs = read_docs_json()

        if request.method == "POST":
            docs["name"] = request.form.get("site_name", docs.get("name", "")).strip()
            docs["description"] = request.form.get(
                "site_description", docs.get("description", "")
            ).strip()

            colors = docs.setdefault("colors", {})
            colors["primary"] = request.form.get(
                "color_primary", colors.get("primary", "")
            ).strip()
            colors["light"] = request.form.get("color_light", colors.get("light", "")).strip()
            colors["dark"] = request.form.get("color_dark", colors.get("dark", "")).strip()

            primary = docs.setdefault("navbar", {}).setdefault("primary", {})
            primary["label"] = request.form.get(
                "navbar_button_label", primary.get("label", "")
            ).strip()
            primary["href"] = request.form.get(
                "navbar_button_href", primary.get("href", "")
            ).strip()

            socials = docs.setdefault("footer", {}).setdefault("socials", {})
            socials["discord"] = request.form.get(
                "social_discord", socials.get("discord", "")
            ).strip()
            socials["youtube"] = request.form.get(
                "social_youtube", socials.get("youtube", "")
            ).strip()
            socials["website"] = request.form.get(
                "social_website", socials.get("website", "")
            ).strip()

            write_docs_json(docs)
            flash("Site ayarlarÄ± kaydedildi.")
            return redirect(url_for("settings"))

        return render_template("settings.html", docs=docs)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="127.0.0.1", port=5050, debug=True)








