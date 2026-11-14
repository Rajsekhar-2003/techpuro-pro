"""Create a draft article: python scripts/new_article.py <category> "<Title>" """
import re, sys
from datetime import date
from pathlib import Path

CATS = ["ai", "programming", "software", "guides", "technology"]
if len(sys.argv) != 3 or sys.argv[1] not in CATS:
    sys.exit(f'Usage: python scripts/new_article.py <{"|".join(CATS)}> "Article title"')
cat, title = sys.argv[1], sys.argv[2]
slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
path = Path(__file__).resolve().parent.parent / "content" / cat / f"{slug}.md"
if path.exists():
    sys.exit(f"Already exists: {path}")
today = date.today().isoformat()
path.write_text(f'''---
title: "{title}"
slug: "{slug}"
subcategory: ""
description: "Write a clear 150-160 character summary."
author: "TechPuro Editorial Team"
published: "{today}"
updated: "{today}"
featured_image: ""
image_alt: ""
tags: []
featured: false
draft: true
takeaways: []
---

## Introduction

Write your article here.
''', encoding="utf-8")
print("Created", path)
