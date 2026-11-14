---
title: "Internet Infrastructure Explained"
slug: "internet-infrastructure-explained"
category: "Technology"
subcategory: "Networking"
description: "How the internet works physically and logically: data centres, submarine cables, ISPs, DNS and CDNs explained simply."
author: "TechPuro Editorial Team"
published: "2026-11-09"
updated: "2026-11-13"
tags: [Internet, Networking, DNS, CDN, Technology]
draft: false
takeaways:
  - The internet is a network of networks connected by cables, exchange points and routing agreements.
  - DNS translates domain names to IP addresses; CDNs bring content closer to users.
  - Most intercontinental traffic travels through undersea fibre-optic cables.
references:
  - title: "Cloudflare Learning Center"
    url: "https://www.cloudflare.com/learning/"
  - title: "MDN – How the Web Works"
    url: "https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_Web_works"
---

When you open a website, your request crosses several layers of infrastructure in milliseconds.

## Key components

| Component | Role |
|-----------|------|
| ISP | Connects homes and businesses to the wider internet |
| Internet exchange points | Places where networks interconnect |
| Submarine cables | Carry most traffic between continents |
| Data centres | Host servers, storage and cloud services |
| DNS | Maps domain names to IP addresses |
| CDN | Caches content near users to reduce latency |

## What happens when you visit a website

1. Your browser asks a DNS resolver for the site's IP address.
2. Your ISP routes the request across networks to that address.
3. A secure connection is established using TLS.
4. The server, or a CDN edge, returns the page.

## Why it matters

Understanding these layers helps developers diagnose slow sites, choose hosting and design resilient systems.

## Conclusion

The internet is less a single system than a cooperative web of independent networks. Reliability comes from redundancy at every layer.
