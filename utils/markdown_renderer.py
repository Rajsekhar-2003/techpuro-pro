import re
import markdown
import bleach

TAGS = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "br", "hr", "a", "strong", "em", "b", "i", "u", "del",
        "ul", "ol", "li", "blockquote", "code", "pre", "table", "thead", "tbody", "tr", "th", "td",
        "img", "dl", "dt", "dd", "sup", "sub", "kbd", "figure", "figcaption", "div", "span"]
ATTRS = {"*": ["id", "class"], "a": ["href", "title", "target", "rel"],
         "img": ["src", "alt", "title", "width", "height"], "th": ["align"], "td": ["align"]}


def _flatten(tokens, out):
    for t in tokens:
        if t["level"] in (2, 3):
            out.append({"level": t["level"], "id": t["id"], "name": t["name"]})
        _flatten(t.get("children", []), out)
    return out


def render_markdown(text):
    """Return (safe_html, toc, headings). TOC is built from H2/H3."""
    md = markdown.Markdown(extensions=["extra", "toc", "sane_lists"],
                           extension_configs={"toc": {"toc_depth": "2-3"}})
    html = md.convert(text)
    toc = _flatten(md.toc_tokens, [])
    html = re.sub(r"<(/?)h1\b", r"<\1h2", html)  # one H1 per page: the template owns it
    html = bleach.clean(html, tags=TAGS, attributes=ATTRS, protocols=["http", "https", "mailto"], strip=True)
    html = html.replace("<table>", '<div class="table-responsive"><table class="table table-striped table-bordered align-middle">')
    html = html.replace("</table>", "</table></div>")
    html = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener noreferrer"', html)
    html = html.replace("<img ", '<img loading="lazy" ')
    return html, toc, [t["name"] for t in toc]
