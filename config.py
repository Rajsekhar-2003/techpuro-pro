import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CATEGORIES = {
    "ai": {"name": "Artificial Intelligence", "icon": "bi-cpu",
           "desc": "AI companies, tools, models, applications and the infrastructure behind modern machine intelligence."},
    "programming": {"name": "Programming", "icon": "bi-code-slash",
           "desc": "Languages, frameworks, editors and practical comparisons for developers and students."},
    "software": {"name": "Software", "icon": "bi-window-stack",
           "desc": "Operating systems, developer tools, hosting and business software compared."},
    "guides": {"name": "Guides", "icon": "bi-journal-text",
           "desc": "Step-by-step tutorials on websites, hosting, DNS, deployment, SEO and security."},
    "technology": {"name": "Technology", "icon": "bi-globe2",
           "desc": "Technology companies, industry research, infrastructure and emerging trends."},
}


PAGES = {
    "about": ("About TechPuro", "Learn about TechPuro, an independent technology publication covering AI, programming, software and guides."),
    "contact": ("Contact TechPuro", "How to contact the TechPuro editorial team for corrections, feedback and partnerships."),
    "privacy-policy": ("Privacy Policy", "How TechPuro handles visitor data, cookies and third-party services."),
    "disclaimer": ("Disclaimer", "Editorial disclaimer for information published on TechPuro."),
}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
    SITE_NAME = "TechPuro"
    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "contact@techpuro.com")
    SITE_TAGLINE = "Technology, AI, programming and software explained"
    SITE_URL = os.environ.get("SITE_URL", "https://techpuro.com").rstrip("/")
    CONTENT_DIR = BASE_DIR / "content"
    PER_PAGE = 12
    MAX_QUERY_LEN = 80
    CACHE_CHECK_SECONDS = int(os.environ.get("CACHE_CHECK_SECONDS", "2"))
    ENABLE_FAQ_SCHEMA = os.environ.get("ENABLE_FAQ_SCHEMA", "0") == "1"
    PAGE_CACHE_SECONDS = int(os.environ.get("PAGE_CACHE_SECONDS", "300"))
    DEBUG = False
