from flask import current_app


def _site():
    return current_app.config["SITE_URL"]


def abs_url(path_or_url):
    return path_or_url if path_or_url.startswith("http") else _site() + path_or_url


def default_og():
    return _site() + "/static/images/og-default.png"


def meta(title, description, path, image=None, robots=None, og_type="website", ld=None):
    name = current_app.config["SITE_NAME"]
    full = title if name in title else f"{title} | {name}"
    return {"title": full, "description": description[:300], "canonical": abs_url(path),
            "og_image": abs_url(image) if image else default_og(), "og_type": og_type,
            "robots": robots or "index,follow,max-image-preview:large", "ld": ld or []}


def organization_ld():
    return {"@context": "https://schema.org", "@type": "Organization", "name": current_app.config["SITE_NAME"],
            "url": _site(), "logo": _site() + "/static/logo/logo.svg"}


def website_ld():
    return {"@context": "https://schema.org", "@type": "WebSite", "name": current_app.config["SITE_NAME"],
            "url": _site(), "potentialAction": {"@type": "SearchAction",
            "target": _site() + "/search/?q={search_term_string}", "query-input": "required name=search_term_string"}}


def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i, "name": n, "item": abs_url(u)} for i, (n, u) in enumerate(items, 1)]}


def article_ld(a):
    return {"@context": "https://schema.org", "@type": "BlogPosting", "headline": a["title"][:110],
            "description": a["description"], "image": [abs_url(a["image"]) if a["image"] else default_og()],
            "datePublished": a["published"].isoformat(), "dateModified": a["updated"].isoformat(),
            "author": {"@type": a["author_type"], "name": a["author"]},
            "publisher": {"@type": "Organization", "name": current_app.config["SITE_NAME"],
                          "logo": {"@type": "ImageObject", "url": _site() + "/static/logo/logo.svg"}},
            "mainEntityOfPage": {"@type": "WebPage", "@id": a["canonical"]},
            "articleSection": a["category_name"], "keywords": ", ".join(a["tags"])}


def faq_ld(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq]}
