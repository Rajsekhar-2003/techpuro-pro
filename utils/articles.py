import html as htmllib
import re
import threading
import time
from datetime import date, datetime

import yaml
from flask import current_app

from config import BASE_DIR, CATEGORIES
from .markdown_renderer import render_markdown

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.S)
_cache = {"sig": None, "articles": None, "checked": 0.0}
_lock = threading.Lock()


def _to_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _as_list(v):
    if v is None:
        return []
    return [str(x) for x in v] if isinstance(v, list) else [str(v)]


def _parse(path, cat):
    m = FM_RE.match(path.read_text(encoding="utf-8"))
    if not m:
        raise ValueError("missing YAML frontmatter")
    meta = yaml.safe_load(m.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError("invalid frontmatter")
    if meta.get("draft"):
        return None
    title = str(meta.get("title", "")).strip()
    slug = str(meta.get("slug") or path.stem).strip()
    published = _to_date(meta.get("published"))
    if not title or not published or not SLUG_RE.match(slug):
        raise ValueError("title, published (YYYY-MM-DD) and a valid slug are required")
    updated = _to_date(meta.get("updated")) or published
    image = str(meta.get("featured_image") or "")
    if image.startswith("/static/"):
        if not (BASE_DIR / image.lstrip("/")).is_file():
            image = ""
    elif not image.startswith("https://"):
        image = ""
    body, toc, headings = render_markdown(m.group(2))
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", body))
    text = re.sub(r"\s+", " ", text).strip()
    site = current_app.config["SITE_URL"]
    url = f"/{cat}/{slug}/"
    canonical = str(meta.get("canonical") or "")
    if not canonical.startswith("https://"):
        canonical = site + url
    return {
        "cat": cat, "category_name": CATEGORIES[cat]["name"], "slug": slug, "url": url,
        "title": title, "description": str(meta.get("description") or text[:155]).strip(),
        "subcategory": str(meta.get("subcategory") or ""),
        "author": str(meta.get("author") or "TechPuro Editorial Team"),
        "author_type": "Person" if meta.get("author_type") == "Person" else "Organization",
        "published": published, "updated": updated, "image": image,
        "image_alt": str(meta.get("image_alt") or title), "tags": _as_list(meta.get("tags")),
        "featured": bool(meta.get("featured")), "trending": bool(meta.get("trending")),
        "canonical": canonical, "html": body, "toc": toc, "headings": headings,
        "text": text, "text_lower": text.lower(), "reading_time": max(1, round(len(text.split()) / 220)),
        "takeaways": _as_list(meta.get("takeaways")),
        "faq": [{"q": str(i["q"]), "a": str(i["a"])} for i in (meta.get("faq") or [])
                if isinstance(i, dict) and i.get("q") and i.get("a")],
        "references": [{"title": str(i.get("title") or i["url"]), "url": str(i["url"])}
                       for i in (meta.get("references") or [])
                       if isinstance(i, dict) and str(i.get("url", "")).startswith(("http://", "https://"))],
    }


def _scan(root):
    files, base = [], root.resolve()
    for cat in CATEGORIES:
        d = root / cat
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            try:
                p.resolve().relative_to(base)  # blocks symlink / traversal escapes
            except ValueError:
                continue
            files.append((cat, p, p.stat().st_mtime_ns))
    return files


def _build(files):
    out, seen = [], set()
    for cat, p, _ in files:
        try:
            a = _parse(p, cat)
        except Exception as e:
            current_app.logger.warning("Skipping %s: %s", p.name, e)
            continue
        if a and (cat, a["slug"]) not in seen:
            seen.add((cat, a["slug"]))
            out.append(a)
    out.sort(key=lambda a: (a["published"], a["updated"], a["title"]), reverse=True)
    return out


def get_articles():
    """Published articles, newest first. Re-parsed only when files change."""
    with _lock:
        now = time.monotonic()
        if _cache["articles"] is not None and now - _cache["checked"] < current_app.config["CACHE_CHECK_SECONDS"]:
            return _cache["articles"]
        files = _scan(current_app.config["CONTENT_DIR"])
        sig = tuple((str(p), m) for _, p, m in files)
        if sig != _cache["sig"]:
            _cache["articles"], _cache["sig"] = _build(files), sig
        _cache["checked"] = now
        return _cache["articles"]


def by_category(cat):
    return [a for a in get_articles() if a["cat"] == cat]


def find(cat, slug):
    return next((a for a in get_articles() if a["cat"] == cat and a["slug"] == slug), None)


def recently_updated(n=6):
    items = [a for a in get_articles() if a["updated"] > a["published"]]
    return sorted(items, key=lambda a: a["updated"], reverse=True)[:n]


def related(a, n=3):
    mine, scored = {t.lower() for t in a["tags"]}, []
    for b in get_articles():
        if b["cat"] == a["cat"] and b["slug"] == a["slug"]:
            continue
        s = 2 * len(mine & {t.lower() for t in b["tags"]}) + (1 if b["cat"] == a["cat"] else 0)
        if s:
            scored.append((s, b["published"], b))
    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [b for _, _, b in scored[:n]]
