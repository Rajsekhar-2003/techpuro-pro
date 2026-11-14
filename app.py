import math
from datetime import datetime

from flask import Flask, Response, abort, render_template, request

from config import CATEGORIES, PAGES, Config
from utils import articles as store
from utils import seo
from utils.search import search_articles, highlight, snippet
from utils.sitemap import build_sitemap


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.context_processor
    def inject():
        return {"categories": CATEGORIES, "site_name": app.config["SITE_NAME"],
                "site_url": app.config["SITE_URL"], "year": datetime.now().year,
                "menu": {c: store.by_category(c)[:6] for c in CATEGORIES}}

    @app.template_filter("datefmt")
    def datefmt(d):
        return d.strftime("%b %d, %Y") if d else ""

    @app.route("/")
    def index():
        arts = store.get_articles()
        featured = [a for a in arts if a["featured"]]
        hero = featured[0] if featured else (arts[0] if arts else None)
        rest = [a for a in featured if a is not hero][:3]
        sections = {c: store.by_category(c)[:3] for c in CATEGORIES}
        s = seo.meta(f"{app.config['SITE_NAME']} – {app.config['SITE_TAGLINE']}",
                     "TechPuro publishes in-depth articles on artificial intelligence, programming, software, "
                     "technical guides and the technology industry.", "/",
                     ld=[seo.organization_ld(), seo.website_ld()])
        return render_template("index.html", seo=s, hero=hero, featured=rest, sections=sections,
                               latest=arts[:6], trending=[a for a in arts if a["trending"]][:4],
                               updated=store.recently_updated(4))

    @app.route("/search/")
    def search():
        q = request.args.get("q", "").strip()[:app.config["MAX_QUERY_LEN"]]
        cat = request.args.get("category", "")
        cat = cat if cat in CATEGORIES else None
        found, terms = search_articles(store.get_articles(), q, cat)
        results = [{"a": a, "title_html": highlight(a["title"], terms), "snippet": snippet(a, terms)} for a in found]
        s = seo.meta("Search", "Search TechPuro articles.", "/search/", robots="noindex,follow")
        return render_template("search.html", seo=s, q=q, cat=cat, results=results)

    @app.route("/sitemap.xml")
    def sitemap():
        return Response(build_sitemap(app.config["SITE_URL"], CATEGORIES, store.get_articles(), PAGES),
                        mimetype="application/xml")

    @app.route("/robots.txt")
    def robots():
        body = f"User-agent: *\nAllow: /\nDisallow: /search/\n\nSitemap: {app.config['SITE_URL']}/sitemap.xml\n"
        return Response(body, mimetype="text/plain")

    @app.route("/<cat>/")
    def category(cat):
        if cat not in CATEGORIES:
            abort(404)
        items = store.by_category(cat)
        per = app.config["PER_PAGE"]
        pages = max(1, math.ceil(len(items) / per))
        page = max(1, request.args.get("page", 1, type=int))
        if page > pages:
            abort(404)
        info, base = CATEGORIES[cat], f"/{cat}/"
        path = base if page == 1 else f"{base}?page={page}"
        s = seo.meta(f"{info['name']} Articles and Guides", info["desc"], path, ld=[
            seo.breadcrumb_ld([("Home", "/"), (info["name"], base)])])
        return render_template("category.html", seo=s, cat=cat, info=info, items=items[(page - 1) * per:page * per],
                               page=page, pages=pages, base=base)

    @app.route("/<cat>/<slug>/")
    def article(cat, slug):
        if cat not in CATEGORIES:
            abort(404)
        a = store.find(cat, slug)
        if not a:
            abort(404)
        crumbs = [("Home", "/"), (a["category_name"], f"/{cat}/"), (a["title"], a["url"])]
        ld = [seo.article_ld(a), seo.breadcrumb_ld(crumbs)]
        if a["faq"] and app.config["ENABLE_FAQ_SCHEMA"]:
            ld.append(seo.faq_ld(a["faq"]))
        s = seo.meta(a["title"], a["description"], a["url"], image=a["image"], og_type="article", ld=ld)
        s["canonical"] = a["canonical"]
        return render_template("article.html", seo=s, a=a, crumbs=crumbs, related=store.related(a))

    def make_page(slug, title, desc):
        def view():
            s = seo.meta(title, desc, f"/{slug}/", ld=[seo.breadcrumb_ld([("Home", "/"), (title, f"/{slug}/")])])
            return render_template("page.html", seo=s, slug=slug, title=title, email=app.config["CONTACT_EMAIL"])
        view.__name__ = "page_" + slug.replace("-", "_")
        return view

    for slug, (title, desc) in PAGES.items():
        app.add_url_rule(f"/{slug}/", view_func=make_page(slug, title, desc))

    @app.errorhandler(404)
    def not_found(_):
        return render_template("404.html", seo=seo.meta("Page not found", "Page not found.", "/", robots="noindex,follow")), 404

    @app.errorhandler(500)
    def server_error(_):
        return render_template("500.html", seo=seo.meta("Server error", "Something went wrong.", "/", robots="noindex,nofollow")), 500

    @app.after_request
    def headers(resp):
        resp.headers.update({
            "X-Content-Type-Options": "nosniff", "X-Frame-Options": "SAMEORIGIN",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": "default-src 'self'; img-src 'self' data: https:; style-src 'self'; "
                                       "script-src 'self'; font-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self'"})
        if request.is_secure or request.headers.get("X-Forwarded-Proto") == "https":
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        if request.method == "GET" and resp.status_code == 200 and resp.mimetype in ("text/html", "application/xml", "text/plain"):
            resp.headers["Cache-Control"] = f"public, max-age={app.config['PAGE_CACHE_SECONDS']}"
        return resp

    return app


if __name__ == "__main__":
    create_app().run(debug=False, port=8000)
