from xml.sax.saxutils import escape


def build_sitemap(site, categories, articles, pages=()):
    rows = [(site + "/", max((a["updated"] for a in articles), default=None))]
    for cat in categories:
        items = [a for a in articles if a["cat"] == cat]
        rows.append((f"{site}/{cat}/", max((a["updated"] for a in items), default=None)))
    rows += [(f"{site}/{pg}/", None) for pg in pages]
    rows += [(a["canonical"], a["updated"]) for a in articles]
    out = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod in rows:
        out.append(f"<url><loc>{escape(loc)}</loc>" + (f"<lastmod>{mod.isoformat()}</lastmod>" if mod else "") + "</url>")
    out.append("</urlset>")
    return "\n".join(out)
