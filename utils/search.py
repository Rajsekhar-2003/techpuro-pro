import re
from markupsafe import Markup, escape


def terms_of(q):
    return list(dict.fromkeys(re.findall(r"\w+", q.lower())))[:6]


def search_articles(articles, q, cat=None, limit=30):
    terms = terms_of(q)
    if not terms:
        return [], terms
    results = []
    for a in articles:
        if cat and a["cat"] != cat:
            continue
        total, ok = 0, True
        for t in terms:
            s = 0
            if t in a["title"].lower(): s += 10
            if t in a["description"].lower(): s += 4
            if any(t in h.lower() for h in a["headings"]): s += 4
            if any(t in g.lower() for g in a["tags"]): s += 6
            s += min(a["text_lower"].count(t), 5)
            if s == 0:
                ok = False
                break
            total += s
        if ok:
            results.append((total, a))
    results.sort(key=lambda x: (x[0], x[1]["published"]), reverse=True)
    return [a for _, a in results[:limit]], terms


def highlight(text, terms):
    safe = str(escape(text))
    if not terms:
        return Markup(safe)
    pat = re.compile("(" + "|".join(re.escape(t) for t in terms) + ")", re.I)
    return Markup(pat.sub(r"<mark>\1</mark>", safe))


def snippet(a, terms, width=170):
    text, low = a["text"], a["text_lower"]
    pos = min([p for p in (low.find(t) for t in terms) if p >= 0], default=-1)
    if pos < 0:
        return highlight(a["description"], terms)
    start = max(0, pos - 60)
    piece = text[start:start + width]
    return highlight(("…" if start else "") + piece + "…", terms)
