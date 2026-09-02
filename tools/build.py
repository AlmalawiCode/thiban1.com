#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static site generator for thiban1.com (Thiban Tech Solutions).

Why a generator: the site is bilingual (English + Modern Standard Arabic,
with real RTL) across ~15 routes, and every page shares the same header,
footer, SEO/Open-Graph head and language switch. Authoring that by hand in
~15 files would drift out of sync. This script emits plain, dependency-free
static HTML into the repository root — the OUTPUT needs no Node, no runtime,
and is fully portable to Netlify / Cloudflare Pages / Vercel / S3.

Run:  python3 tools/build.py
It only writes *.html, sitemap.xml, robots.txt (never touches /assets except
to read). Safe to run repeatedly.

To add a new app: add an entry to APPS below and a page function, then re-run.
"""

import os
import json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE_URL = "https://thiban1.com"
SUPPORT_EMAIL = "thibantechsolutions@gmail.com"
WHATSAPP_DISPLAY = "+966 55 426 0804"          # shown to visitors
WHATSAPP_NUMBER = "966554260804"               # E.164 digits for wa.me
WHATSAPP_LINK = f"https://wa.me/{WHATSAPP_NUMBER}"
WHATSAPP_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" width="20" height="20" fill="currentColor">'
                '<path d="M.06 24l1.68-6.13A11.87 11.87 0 0 1 .16 11.9C.16 5.34 5.5.02 12.06.02c3.18 0 '
                '6.17 1.24 8.42 3.49a11.8 11.8 0 0 1 3.49 8.4c0 6.56-5.35 11.88-11.9 11.88a11.9 11.9 0 0 '
                '1-5.7-1.45L.06 24zM6.6 20.13c1.68.99 3.28 1.59 5.45 1.59 5.45 0 9.9-4.43 9.9-9.88a9.8 '
                '9.8 0 0 0-2.9-6.99A9.8 9.8 0 0 0 12.06 2c-5.45 0-9.9 4.43-9.9 9.88 0 2.24.66 3.92 1.75 '
                '5.68l-1 3.63 3.69-.96zM17.6 14.6c-.07-.12-.27-.2-.56-.34-.3-.15-1.75-.86-2.02-.96-.27-.1-'
                '.47-.15-.66.15-.2.3-.76.96-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.25-.46-2.38-1.47-.88-.78-'
                '1.47-1.75-1.65-2.05-.17-.3-.02-.46.13-.6.13-.14.3-.35.44-.53.15-.17.2-.3.3-.5.1-.2.05-.37-'
                '.02-.52-.08-.15-.66-1.6-.9-2.18-.24-.58-.48-.5-.66-.5l-.57-.02c-.2 0-.52.07-.8.37-.27.3-'
                '1.04 1.02-1.04 2.48s1.07 2.88 1.22 3.08c.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.7.63.71.23 '
                '1.36.2 1.87.12.57-.08 1.75-.72 2-1.4.24-.7.24-1.28.17-1.4z"/></svg>')


def whatsapp_button():
    return (f'<a class="wa-btn" href="{WHATSAPP_LINK}" target="_blank" rel="noopener">'
            f'{WHATSAPP_SVG}<span><span data-en>WhatsApp</span><span data-ar>واتساب</span>'
            f' · <span dir="ltr">{WHATSAPP_DISPLAY}</span></span></a>')


YEAR = "2026"

# ---------------------------------------------------------------------------
# small bilingual helpers — each text node is emitted twice (data-en/data-ar);
# CSS shows only the active language. Both languages ship in the HTML so the
# page is crawlable and readable even before JavaScript runs.
# ---------------------------------------------------------------------------

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def t(en, ar):
    return f'<span data-en>{en}</span><span data-ar>{ar}</span>'

def p(en, ar, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<p{c} data-en>{en}</p><p{c} data-ar>{ar}</p>'

def h(n, en, ar, cls="", _id=""):
    c = f' class="{cls}"' if cls else ""
    i = f' id="{_id}"' if _id else ""
    return f'<h{n}{i}{c} data-en>{en}</h{n}><h{n}{i}{c} data-ar>{ar}</h{n}>'

def li(en, ar):
    return f'<li data-en>{en}</li><li data-ar>{ar}</li>'

def ul(items):
    lis = "".join(li(e, a) for e, a in items)
    return f"<ul>{lis}</ul>"

def feature(icon, en_t, ar_t, en_d, ar_d):
    return (f'<div class="feature"><div class="dot" aria-hidden="true">{icon}</div><div>'
            f'<h4 data-en>{en_t}</h4><h4 data-ar>{ar_t}</h4>'
            f'<p data-en>{en_d}</p><p data-ar>{ar_d}</p></div></div>')

def steps(items):
    out = []
    for en_t, ar_t, en_d, ar_d in items:
        out.append(f'<li><h4 data-en>{en_t}</h4><h4 data-ar>{ar_t}</h4>'
                   f'<p data-en>{en_d}</p><p data-ar>{ar_d}</p></li>')
    return f'<ol class="steps">{"".join(out)}</ol>'

def faq(items):
    out = []
    for en_q, ar_q, en_a, ar_a in items:
        out.append('<details><summary>'
                   f'<span data-en>{en_q}</span><span data-ar>{ar_q}</span></summary>'
                   f'<p data-en>{en_a}</p><p data-ar>{ar_a}</p></details>')
    return f'<div class="faq">{"".join(out)}</div>'

# ---------------------------------------------------------------------------
# store buttons
# ---------------------------------------------------------------------------
APPLE_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.4 1.6c.1 1-.3 2-1 2.8-.7.8-1.8 1.4-2.9 1.3-.1-1 .4-2 1-2.7.7-.8 1.9-1.4 2.9-1.4zM19 17.3c-.5 1.2-.8 1.7-1.5 2.8-1 1.5-2.3 3.3-4 3.3-1.5 0-1.9-1-4-1-2 0-2.5 1-4 1-1.6 0-2.9-1.6-3.9-3.1-2.7-4.2-3-9.1-1.3-11.7 1.2-1.8 3-2.9 4.8-2.9 1.8 0 2.9 1 4.4 1 1.4 0 2.3-1 4.4-1 1.6 0 3.2.9 4.4 2.4-3.9 2.1-3.2 7.6.2 9.1z"/></svg>')
PLAY_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.6 2.2c-.3.3-.5.7-.5 1.3v17c0 .6.2 1 .5 1.3l.1.1L13 12.6v-.2L3.7 2.1l-.1.1zm11.9 8.5L5.9 1.4l11.7 6.7-2.1 2.6zM5.9 22.6l9.6-9.3 2.1 2.6-11.7 6.7zM19.6 9.3l-2.5 1.4 2.4 3-2.4 3 2.5 1.4c.9-.5 1.5-1.3 1.5-2.4v-4c0-1.1-.6-1.9-1.5-2.4l-.5.6.5-.6z"/></svg>')
YT_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M23 7.5s-.2-1.6-.9-2.3c-.9-.9-1.8-.9-2.3-1C16.6 4 12 4 12 4s-4.6 0-7.8.2c-.5.1-1.4.1-2.3 1C1.2 5.9 1 7.5 1 7.5S.8 9.4.8 11.3v1.4C.8 14.6 1 16.5 1 16.5s.2 1.6.9 2.3c.9.9 2 .9 2.6 1 1.9.2 7.5.2 7.5.2s4.6 0 7.8-.3c.5-.1 1.4-.1 2.3-1 .7-.7.9-2.3.9-2.3s.2-1.9.2-3.8v-1.4c0-1.9-.2-3.7-.2-3.7zM9.8 15.1V8.9l6 3.1-6 3.1z"/></svg>')

def store_button(kind, url):
    if kind == "apple":
        return (f'<a class="store-btn" href="{url}" target="_blank" rel="noopener">{APPLE_SVG}'
                f'<span><small data-en>Download on the</small><small data-ar>حمّله من</small>'
                f'<strong>App Store</strong></span></a>')
    if kind == "play":
        return (f'<a class="store-btn" href="{url}" target="_blank" rel="noopener">{PLAY_SVG}'
                f'<span><small data-en>Get it on</small><small data-ar>احصل عليه من</small>'
                f'<strong>Google Play</strong></span></a>')
    if kind == "youtube":
        return (f'<a class="store-btn" style="background:#c4302b" href="{url}" target="_blank" rel="noopener">{YT_SVG}'
                f'<span><small data-en>Watch on</small><small data-ar>شاهده على</small>'
                f'<strong>YouTube</strong></span></a>')
    return ""

# ---------------------------------------------------------------------------
# app registry
# ---------------------------------------------------------------------------
APPS = {
    "countdown-keeper": {
        "slug": "countdown-keeper",
        "name_en": "Countdown Keeper",
        "name_ar": "العدّاد",
        "icon": "/assets/img/apps/countdown/icon.png",
        "tagline_en": "Count down to what matters — and count up from what already happened.",
        "tagline_ar": "عُدّ تنازليًا لما يهمّك، وتصاعديًا لما مضى من أحداثك.",
        "status": "soon",   # not yet on stores
        # Language availability is tracked per CONTENT TYPE — an app may ship
        # its privacy policy in more languages than its other content.
        "overview_langs": ["en", "ar"],
        "privacy_langs": ["en", "ar"],
        "tutorial_langs": ["en", "ar"],
        "support_langs": ["en", "ar"],
        "screens": [
            ("/assets/img/apps/countdown/Countdown_Home.jpg", "Countdown Keeper home screen with event counters", "الشاشة الرئيسية لتطبيق العدّاد تعرض عدّادات المناسبات"),
            ("/assets/img/apps/countdown/event.jpg", "Creating an event in Countdown Keeper", "إنشاء مناسبة في تطبيق العدّاد"),
            ("/assets/img/apps/countdown/tools.jpg", "Date and time tools in Countdown Keeper", "أدوات التاريخ والوقت في تطبيق العدّاد"),
            ("/assets/img/apps/countdown/Countdown_Settings.jpg", "Countdown Keeper settings screen", "شاشة الإعدادات في تطبيق العدّاد"),
        ],
    },
    "vault": {
        "slug": "vault",
        "name_en": "Vault — Warranty Manager",
        "name_ar": "خزنة الضمانات",
        "icon": "/assets/img/apps/vault/icon.png",
        "tagline_en": "Keep your invoices, organize your products, and never miss a warranty expiry.",
        "tagline_ar": "احفظ فواتيرك، ونظّم منتجاتك، ولا يفوتك موعد انتهاء أي ضمان.",
        "status": "live",
        "appstore": "https://apps.apple.com/app/id6773164894",
        "playstore": "https://play.google.com/store/apps/details?id=com.vault.warranty",
        "youtube": "https://www.youtube.com/watch?v=SjafmkwycsA&t=167s",
        "youtube_embed": "https://www.youtube.com/embed/SjafmkwycsA?start=167",
        # Vault ships its privacy policy in 8 languages (real, authoritative
        # translations preserved from the app project); other content is EN/AR.
        "overview_langs": ["en", "ar"],
        "privacy_langs": ["en", "ar", "fr", "de", "es", "tr", "ja", "ko"],
        "tutorial_langs": ["en", "ar"],
        "support_langs": ["en", "ar"],
        "screens": [
            ("/assets/img/apps/vault/dashboard.jpg", "Vault dashboard showing warranty overview", "لوحة معلومات خزنة الضمانات تعرض ملخّص الضمانات"),
            ("/assets/img/apps/vault/list.jpg", "List of saved purchases in Vault", "قائمة المشتريات المحفوظة في خزنة الضمانات"),
            ("/assets/img/apps/vault/invoice.jpg", "A scanned invoice inside Vault", "فاتورة ممسوحة داخل خزنة الضمانات"),
            ("/assets/img/apps/vault/warranty.jpg", "A warranty countdown in Vault", "عدّاد انتهاء ضمان في خزنة الضمانات"),
        ],
    },
}

# Native display name + text direction for every content language we support.
# The GLOBAL website language is only English/Arabic; these extra languages
# exist purely for APP-SPECIFIC content (e.g. Vault's privacy policy).
LANG_META = {
    "en": ("English",  "ltr"),
    "ar": ("العربية",  "rtl"),
    "fr": ("Français", "ltr"),
    "de": ("Deutsch",  "ltr"),
    "es": ("Español",  "ltr"),
    "tr": ("Türkçe",   "ltr"),
    "ja": ("日本語",    "ltr"),
    "ko": ("한국어",    "ltr"),
}

NAV = [
    ("home", "Home", "الرئيسية", "/"),
    ("services", "Services", "الخدمات", "/#services"),
    ("apps", "Apps", "التطبيقات", "/apps/"),
    ("tutorials", "Tutorials", "الشروحات", "/tutorials/"),
    ("support", "Support", "الدعم", "/support/"),
    ("about", "About", "من نحن", "/about/"),
]

# pre-paint language script (kept as a plain string to avoid f-string braces)
PREPAINT = (
    "<script>(function(){try{var l=localStorage.getItem('thiban-lang');"
    "if(!l){l=((navigator.language||navigator.userLanguage||'en')"
    ".slice(0,2)==='ar')?'ar':'en';}var d=document.documentElement;"
    "d.setAttribute('data-lang',l);d.setAttribute('lang',l);"
    "d.setAttribute('dir',l==='ar'?'rtl':'ltr');"
    "var m={en:d.getAttribute('data-title-en'),ar:d.getAttribute('data-title-ar')};"
    "if(m[l]){document.title=m[l];}}catch(e){}})();</script>"
)

TITLE_SYNC = (
    "<script>document.addEventListener('click',function(e){"
    "var b=e.target.closest&&e.target.closest('[data-lang-toggle]');if(!b)return;"
    "setTimeout(function(){var d=document.documentElement,l=d.getAttribute('data-lang');"
    "var m={en:d.getAttribute('data-title-en'),ar:d.getAttribute('data-title-ar')};"
    "if(m[l]){document.title=m[l];}},0);});</script>"
)


def header(active):
    links = []
    for key, en, ar, href in NAV:
        cur = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{href}"{cur}><span data-en>{en}</span><span data-ar>{ar}</span></a>')
    links_html = "".join(links)
    return f'''<a class="skip" href="#main"><span data-en>Skip to content</span><span data-ar>تخطَّ إلى المحتوى</span></a>
<header class="site-header"><div class="container"><nav class="nav" aria-label="Main">
  <a class="brand" href="/"><img src="/assets/img/brand/icon-192.png" alt="" width="34" height="34">
    <span data-en>Thiban Tech Solutions</span><span data-ar>ذيبان للحلول التقنية</span></a>
  <button class="nav-toggle" data-nav-toggle aria-expanded="false" aria-controls="nav-links" aria-label="Menu">☰</button>
  <div class="nav-links" id="nav-links">{links_html}
    <button class="lang-btn" data-lang-toggle type="button" aria-label="التبديل إلى العربية">العربية</button>
  </div>
</nav></div></header>'''


def footer():
    def col(title_en, title_ar, items):
        lis = "".join(
            f'<li><a href="{href}"><span data-en>{en}</span><span data-ar>{ar}</span></a></li>'
            for en, ar, href in items)
        return (f'<div><h4><span data-en>{title_en}</span><span data-ar>{title_ar}</span></h4>'
                f'<ul>{lis}</ul></div>')

    apps_col = col("Apps", "التطبيقات", [
        ("Countdown Keeper", "العدّاد", "/apps/countdown-keeper/"),
        ("Vault — Warranty Manager", "خزنة الضمانات", "/apps/vault/"),
        ("All apps", "كل التطبيقات", "/apps/"),
    ])
    help_col = col("Help", "المساعدة", [
        ("Tutorials", "الشروحات", "/tutorials/"),
        ("Support", "الدعم", "/support/"),
        ("Contact", "تواصل معنا", "/contact/"),
    ])
    legal_col = col("Company", "الشركة", [
        ("About", "من نحن", "/about/"),
        ("Privacy", "الخصوصية", "/privacy/"),
    ])
    return f'''<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div>
      <div class="footer-brand"><img src="/assets/img/brand/icon-192.png" alt="" width="32" height="32">
        <span data-en>Thiban Tech Solutions</span><span data-ar>ذيبان للحلول التقنية</span></div>
      <p style="color:rgba(255,255,255,.7);max-width:34ch" data-en>Web &amp; mobile application development — plus our own privacy-first apps.</p>
      <p style="color:rgba(255,255,255,.7);max-width:34ch" data-ar>تطوير تطبيقات الويب والجوال — إضافةً إلى تطبيقاتنا الخاصة التي تحترم الخصوصية.</p>
      <p style="color:#94a3b8;margin-top:8px"><a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>
      <p style="color:#94a3b8;margin-top:4px"><a href="{WHATSAPP_LINK}" target="_blank" rel="noopener">WhatsApp: <span dir="ltr">{WHATSAPP_DISPLAY}</span></a></p>
    </div>
    {apps_col}{help_col}{legal_col}
  </div>
  <div class="footer-bottom">
    <span>&copy; {YEAR} Thiban Tech Solutions.
      <span data-en>All rights reserved.</span><span data-ar>جميع الحقوق محفوظة.</span></span>
    <span><a href="/privacy/"><span data-en>Privacy</span><span data-ar>الخصوصية</span></a>
      &nbsp;·&nbsp;
      <a href="/support/"><span data-en>Support</span><span data-ar>الدعم</span></a></span>
  </div>
</div></footer>'''


def crumbs(items):
    # items: list of (en, ar, href or None)
    parts = []
    for i, (en, ar, href) in enumerate(items):
        sep = '<span aria-hidden="true">/</span>' if i > 0 else ''
        if href:
            parts.append(f'{sep}<a href="{href}"><span data-en>{en}</span><span data-ar>{ar}</span></a>')
        else:
            parts.append(f'{sep}<span data-en>{en}</span><span data-ar>{ar}</span>')
    return f'<div class="container"><nav class="crumbs" aria-label="Breadcrumb">{"".join(parts)}</nav></div>'


def render(path, title_en, title_ar, desc_en, desc_ar, body,
           active="", og_image="/assets/img/brand/og-default.png", is404=False,
           canonical_override=None, head_extra=""):
    """Write <path>/index.html (or a bare file for 404).

    canonical_override lets a page point its canonical elsewhere (used by the
    /privacy/<app>/ entry point, which canonicalises to its /en/ URL).
    head_extra injects extra <head> markup (used for hreflang alternates)."""
    if is404:
        canonical = ""
        out_file = os.path.join(ROOT, "404.html")
    else:
        url = path if path.endswith("/") else path + "/"
        canonical = SITE_URL + url
        rel = url.strip("/")
        out_dir = ROOT if rel == "" else os.path.join(ROOT, rel)
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "index.html")

    canonical_href = canonical_override or canonical
    og_abs = SITE_URL + og_image
    canonical_tag = f'<link rel="canonical" href="{canonical_href}">' if canonical_href else ''
    og_url = f'<meta property="og:url" content="{canonical_href}">' if canonical_href else ''

    html = f'''<!DOCTYPE html>
<html lang="en" dir="ltr" data-lang="en" data-title-en="{esc(title_en)}" data-title-ar="{esc(title_ar)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{PREPAINT}
<title>{esc(title_en)}</title>
<meta name="description" content="{esc(desc_en)}">
{canonical_tag}
<meta name="theme-color" content="#165dff">
<meta name="color-scheme" content="light">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Thiban Tech Solutions">
<meta property="og:title" content="{esc(title_en)}">
<meta property="og:description" content="{esc(desc_en)}">
{og_url}
<meta property="og:image" content="{og_abs}">
<meta property="og:locale" content="en_US">
<meta property="og:locale:alternate" content="ar_SA">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title_en)}">
<meta name="twitter:description" content="{esc(desc_en)}">
<meta name="twitter:image" content="{og_abs}">
{head_extra}
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/favicon-16.png" sizes="16x16" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/site.js" defer></script>
{TITLE_SYNC}
</body>
</html>'''

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    return canonical


# ---------------------------------------------------------------------------
# reusable app-card (used on home + apps overview)
# ---------------------------------------------------------------------------

def app_card(app):
    if app["status"] == "live":
        badge = '<span class="badge badge-live"><span data-en>Available now</span><span data-ar>متاح الآن</span></span>'
        stores = []
        if app.get("appstore"):
            stores.append(store_button("apple", app["appstore"]))
        if app.get("playstore"):
            stores.append(store_button("play", app["playstore"]))
        stores_html = f'<div class="stores">{"".join(stores)}</div>'
    else:
        badge = '<span class="badge badge-soon"><span data-en>Coming soon</span><span data-ar>قريبًا</span></span>'
        stores_html = ('<div class="chips"><span class="chip">'
                       '<span data-en>App Store — coming soon</span><span data-ar>App Store — قريبًا</span></span>'
                       '<span class="chip"><span data-en>Google Play — coming soon</span>'
                       '<span data-ar>Google Play — قريبًا</span></span></div>')

    slug = app["slug"]
    links = (f'<div class="linkrow">'
             f'<a href="/apps/{slug}/"><span data-en>Learn more</span><span data-ar>اعرف المزيد</span></a>'
             f'<a href="/tutorials/{slug}/"><span data-en>Tutorial</span><span data-ar>الشرح</span></a>'
             f'<a href="/privacy/{slug}/"><span data-en>Privacy</span><span data-ar>الخصوصية</span></a>'
             f'<a href="/support/{slug}/"><span data-en>Support</span><span data-ar>الدعم</span></a>'
             f'</div>')

    return f'''<article class="card app-card">
  <div class="app-head">
    <img src="{app['icon']}" alt="{esc(app['name_en'])} icon" width="66" height="66">
    <div>
      <h3><a href="/apps/{slug}/"><span data-en>{app['name_en']}</span><span data-ar>{app['name_ar']}</span></a></h3>
      {badge}
    </div>
  </div>
  <p data-en>{app['tagline_en']}</p>
  <p data-ar>{app['tagline_ar']}</p>
  {stores_html}
  {links}
</article>'''


def shots(app):
    imgs = "".join(
        f'<img src="{src}" alt="{esc(alt_en)}" loading="lazy" width="230">'
        for src, alt_en, alt_ar in app["screens"])
    return f'<div class="shots">{imgs}</div>'


# ===========================================================================
# PAGES
# ===========================================================================

def featured_app_card(app, shot, desc_en, desc_ar):
    slug = app["slug"]
    if app["status"] == "live":
        actions = []
        if app.get("appstore"):
            actions.append(store_button("apple", app["appstore"]))
        if app.get("playstore"):
            actions.append(store_button("play", app["playstore"]))
        action_block = f'<div class="stores">{"".join(actions)}</div>'
    else:
        action_block = ('<div class="chips"><span class="chip">'
                        '<span data-en>App Store &amp; Google Play — coming soon</span>'
                        '<span data-ar>App Store وGoogle Play — قريبًا</span></span></div>')
    links = (f'<div class="linkrow">'
             f'<a href="/apps/{slug}/"><span data-en>Learn more</span><span data-ar>اعرف المزيد</span></a>'
             f'<a href="/tutorials/{slug}/"><span data-en>Tutorial</span><span data-ar>الشرح</span></a>'
             f'<a href="/privacy/{slug}/"><span data-en>Privacy</span><span data-ar>الخصوصية</span></a>'
             f'<a href="/support/{slug}/"><span data-en>Support</span><span data-ar>الدعم</span></a></div>')
    return f'''<article class="app-card-large">
  <div class="app-visual"><div class="device">
    <img class="app-icon" src="{app['icon']}" alt="{esc(app['name_en'])} icon" width="76" height="76">
    <img class="app-shot" src="{shot}" alt="{esc(app['name_en'])} screenshot" loading="lazy">
  </div></div>
  <div class="app-body">
    <h3><a href="/apps/{slug}/"><span data-en>{app['name_en']}</span><span data-ar>{app['name_ar']}</span></a></h3>
    <p data-en>{desc_en}</p><p data-ar>{desc_ar}</p>
    {action_block}
    {links}
  </div>
</article>'''


def page_home():
    hero = f'''<section class="hero" id="home"><div class="container hero-grid">
  <div>
    <span class="eyebrow" data-en>Web &amp; Mobile Application Development</span><span class="eyebrow" data-ar>تطوير تطبيقات الويب والجوال</span>
    {h(1, "Modern web and mobile applications, built with purpose.", "تطبيقات ويب وجوال حديثة، تُبنى لهدف واضح.")}
    {p("Thiban Tech Solutions designs and develops reliable web and mobile applications — and publishes its own privacy-first apps for everyday life.",
       "تصمّم ذيبان للحلول التقنية وتطوّر تطبيقات ويب وجوال موثوقة — وتنشر تطبيقاتها الخاصة التي تضع الخصوصية أولًا لحياتك اليومية.", "lead")}
    <div class="btn-row">
      <a class="btn btn-primary" href="/#services"><span data-en>Our Services</span><span data-ar>خدماتنا</span></a>
      <a class="btn btn-secondary" href="/apps/"><span data-en>View Apps</span><span data-ar>عرض التطبيقات</span></a>
    </div>
  </div>
  <div class="device-stage" aria-hidden="true">
    <div class="glow"></div>
    <div class="fbadge web"><span>&lt;/&gt;</span><b data-en>Web Apps</b><b data-ar>تطبيقات الويب</b></div>
    <div class="fbadge mobile"><span>▣</span><b data-en>Mobile Apps</b><b data-ar>تطبيقات الجوال</b></div>
    <div class="laptop"><div class="screen">
      <div class="screen-top"><div class="mini-logo"></div><div class="dots"><i></i><i></i><i></i></div></div>
      <div class="dash">
        <div class="panel"><div class="bars"><span></span><span></span><span></span><span></span></div></div>
        <div class="panel"><div class="rowline"></div><div class="rowline"></div><div class="rowline"></div><div class="rowline"></div></div>
      </div>
    </div></div>
    <div class="phone"><img src="/assets/img/apps/countdown/Countdown_Home.jpg" alt="" loading="lazy"></div>
  </div>
</div></section>'''

    services = f'''<section id="services"><div class="container">
  <div class="section-head">
    {h(2, "What we build", "ما الذي نطوره")}
    {p("A focused software studio specializing in two core areas: modern web applications and mobile applications.",
       "استوديو برمجيّ متخصّص في مجالين أساسيين: تطبيقات الويب الحديثة وتطبيقات الجوال.")}
  </div>
  <div class="services">
    <article class="service-card">
      <div class="service-icon" aria-hidden="true">&lt;/&gt;</div>
      {h(3, "Web Application Development", "تطوير تطبيقات الويب")}
      {p("Responsive, secure, and maintainable web applications designed around real business and user requirements.",
         "تطبيقات ويب متجاوبة وآمنة وقابلة للصيانة، مصمّمة وفق احتياجات العمل والمستخدم الفعلية.")}
    </article>
    <article class="service-card">
      <div class="service-icon" aria-hidden="true">▣</div>
      {h(3, "Mobile Application Development", "تطوير تطبيقات الجوال")}
      {p("Polished cross-platform mobile applications for Android and iOS, with a strong focus on usability, reliability, performance, and a consistent experience.",
         "تطبيقات جوال متقنة تعمل على أندرويد و iOS، مع تركيز قوي على سهولة الاستخدام والموثوقية والأداء وتجربة متناسقة.")}
    </article>
  </div>
</div></section>'''

    apps_section = f'''<section class="apps-section" id="apps"><div class="container">
  <div class="section-head">
    {h(2, "Featured applications", "التطبيقات المميّزة")}
    {p("Our own published apps — private by design, and available in Arabic and English.",
       "تطبيقاتنا المنشورة — خاصّة بطبيعتها، ومتوفّرة بالعربية والإنجليزية.")}
  </div>
  <div class="app-grid">
    {featured_app_card(APPS['countdown-keeper'], "/assets/img/apps/countdown/event.jpg",
        "A clean way to track important dates — countdowns, elapsed time, recurring Hijri/Gregorian events, reminders, and handy date tools.",
        "طريقة أنيقة لمتابعة التواريخ المهمة — عدّ تنازلي، ووقت منقضٍ، وأحداث متكرّرة هجرية/ميلادية، وتذكيرات، وأدوات تاريخ عملية.")}
    {featured_app_card(APPS['vault'], "/assets/img/apps/vault/dashboard.jpg",
        "Organize invoices and warranty records, scan receipts and ZATCA QR codes, and get reminded before a warranty expires.",
        "نظّم الفواتير وسجلّات الضمان، وامسح الإيصالات ورموز QR الضريبية، واحصل على تذكير قبل انتهاء الضمان.")}
  </div>
</div></section>'''

    why = f'''<section id="about"><div class="container">
  <div class="section-head center">{h(2, "Why Thiban Tech Solutions?", "لماذا ذيبان للحلول التقنية؟")}</div>
  <div class="why-grid">
    <article class="why-card"><div class="service-icon" aria-hidden="true">◎</div>
      <strong data-en>Focused</strong><strong data-ar>تركيز واضح</strong>
      {p("We concentrate on web and mobile application development — not services we don't provide.",
         "نركّز على تطوير تطبيقات الويب والجوال — لا على خدمات لا نقدّمها.")}</article>
    <article class="why-card"><div class="service-icon" aria-hidden="true">✓</div>
      <strong data-en>Reliable</strong><strong data-ar>موثوقية</strong>
      {p("Every application is understandable, maintainable, tested, and practical for real users.",
         "كل تطبيق واضح وقابل للصيانة ومختبَر وعمليّ للمستخدم الحقيقي.")}</article>
    <article class="why-card"><div class="service-icon" aria-hidden="true">♥</div>
      <strong data-en>User-centered</strong><strong data-ar>يركّز على المستخدم</strong>
      {p("Simple, professional, and consistent across desktop and mobile — in Arabic and English.",
         "بسيط واحترافيّ ومتناسق على الحاسب والجوال — بالعربية والإنجليزية.")}</article>
  </div>
</div></section>'''

    cta = f'''<section style="padding-top:0"><div class="container"><div class="cta-band">
  <div>
    {h(2, "Have an application idea?", "لديك فكرة لتطبيق؟")}
    {p("Let's turn it into a clear, useful web or mobile application.", "لنحوّلها إلى تطبيق ويب أو جوال واضح ومفيد.")}
  </div>
  <a class="btn btn-secondary" href="/contact/"><span data-en>Contact us</span><span data-ar>تواصل معنا</span></a>
</div></div></section>'''

    return hero + services + apps_section + why + cta


def page_apps():
    body = f'''{crumbs([("Home","الرئيسية","/"),("Apps","التطبيقات",None)])}
<section class="section"><div class="container">
  {h(1, "Our Apps", "تطبيقاتنا")}
  {p("Every Thiban app is private by design and available in Arabic and English. Choose an app to learn more, read a tutorial, or view its privacy policy.",
     "كل تطبيق من ذيبان خاصٌّ بطبيعته ومتوفّر بالعربية والإنجليزية. اختر تطبيقًا لتعرف المزيد، أو لقراءة شرحه، أو لمطالعة سياسة خصوصيته.", "lead")}
  <div class="grid grid-2" style="margin-top:36px">
    {app_card(APPS['countdown-keeper'])}
    {app_card(APPS['vault'])}
  </div>
</div></section>'''
    return render("/apps/",
                  "Our Apps — Thiban Tech Solutions",
                  "تطبيقاتنا — ذيبان للحلول التقنية",
                  "Explore mobile apps by Thiban Tech Solutions: Countdown Keeper and Vault — Warranty Manager. Private, offline-first, in Arabic and English.",
                  "استعرض تطبيقات ذيبان للحلول التقنية: العدّاد وخزنة الضمانات. تطبيقات خاصة تعمل دون اتصال، بالعربية والإنجليزية.",
                  body, active="apps")


def app_overview_body(app, features_list, intro_en, intro_ar, extra=""):
    slug = app["slug"]
    if app["status"] == "live":
        stores = []
        if app.get("appstore"):
            stores.append(store_button("apple", app["appstore"]))
        if app.get("playstore"):
            stores.append(store_button("play", app["playstore"]))
        if app.get("youtube"):
            stores.append(store_button("youtube", app["youtube"]))
        store_block = f'<div class="stores" style="margin-top:8px">{"".join(stores)}</div>'
    else:
        store_block = ('<div class="chips" style="margin-top:8px">'
                       '<span class="chip"><span data-en>App Store — coming soon</span><span data-ar>App Store — قريبًا</span></span>'
                       '<span class="chip"><span data-en>Google Play — coming soon</span><span data-ar>Google Play — قريبًا</span></span></div>')

    feats = "".join(feature(*f) for f in features_list)

    # Available languages — tracked per content type (privacy may exceed the rest)
    priv_pills = "".join(
        f'<a class="lang-pill" href="/privacy/{slug}/{L}/" hreflang="{L}" lang="{L}">{LANG_META[L][0]}</a>'
        for L in app["privacy_langs"])
    other_langs = " · ".join(LANG_META[L][0] for L in app["overview_langs"])
    availability = f'''<section class="section section-soft"><div class="container">
  {h(2, "Available languages", "اللغات المتوفّرة", "center")}
  {p("Privacy Policy is available in every language below. App overview, tutorials, and support are available in English and Arabic.",
     "سياسة الخصوصية متوفّرة بكل اللغات أدناه. أمّا نبذة التطبيق والشروحات والدعم فمتوفّرة بالعربية والإنجليزية.", "lead center")}
  <div class="avail">
    <div class="avail-row">
      <span class="avail-label"><span data-en>Privacy Policy</span><span data-ar>سياسة الخصوصية</span></span>
      <div class="lang-pills">{priv_pills}</div>
    </div>
    <div class="avail-row">
      <span class="avail-label"><span data-en>Overview · Tutorials · Support</span><span data-ar>النبذة · الشروحات · الدعم</span></span>
      <div class="lang-pills"><span class="lang-pill static">{other_langs}</span></div>
    </div>
  </div>
</div></section>'''

    return f'''{crumbs([("Home","الرئيسية","/"),("Apps","التطبيقات","/apps/"),(app['name_en'],app['name_ar'],None)])}
<section class="section"><div class="container">
  <div class="app-head" style="margin-bottom:18px">
    <img src="{app['icon']}" alt="{esc(app['name_en'])} icon" width="80" height="80" style="border-radius:18px;box-shadow:var(--shadow-md)">
    <div>{h(1, app['name_en'], app['name_ar'])}
      <p class="muted" data-en>{app['tagline_en']}</p><p class="muted" data-ar>{app['tagline_ar']}</p></div>
  </div>
  {p(intro_en, intro_ar, "lead")}
  {store_block}
  <div class="linkrow" style="margin-top:16px">
    <a href="/tutorials/{slug}/"><span data-en>Tutorial</span><span data-ar>الشرح</span></a>
    <a href="/support/{slug}/"><span data-en>Support</span><span data-ar>الدعم</span></a>
    <a href="/privacy/{slug}/"><span data-en>Privacy policy</span><span data-ar>سياسة الخصوصية</span></a>
  </div>
</div></section>
<section class="section section-soft"><div class="container">
  {h(2, "Screenshots", "لقطات من التطبيق", "center")}
  {shots(app)}
</div></section>
<section class="section"><div class="container">
  {h(2, "Features", "المزايا", "center")}
  <div class="features" style="margin-top:30px">{feats}</div>
  {extra}
</div></section>
{availability}'''


def page_app_countdown():
    app = APPS["countdown-keeper"]
    features_list = [
        ("⏳", "Countdown &amp; count-up", "عدّ تنازلي وتصاعدي", "Count down to a future date or count up from a past one, updated live to the second.", "عُدّ تنازليًا نحو تاريخ قادم أو تصاعديًا منذ حدثٍ مضى، بتحديث حيّ حتى الثانية."),
        ("🗂️", "Organize events", "تنظيم المناسبات", "A searchable, sortable list with pinned favourites, custom colours, an emoji or your own photo, and notes.", "قائمة قابلة للبحث والفرز مع تثبيت المهمّ، وألوان مخصّصة، ورمزٍ تعبيري أو صورتك الخاصة، وملاحظات."),
        ("🔁", "Recurring events", "أحداث متكرّرة", "Repeat an event monthly in either the Gregorian or Hijri calendar.", "كرِّر الحدث شهريًا وفق التقويم الميلادي أو الهجري."),
        ("🔔", "Reminders", "تذكيرات", "Optional local notifications before an event — at the time, a day, or a week ahead.", "إشعارات محلية اختيارية قبل الحدث — عند موعده، أو قبله بيوم، أو بأسبوع."),
        ("♻️", "Recycle bin", "سلة المحذوفات", "Deleted events can be restored before they are permanently removed.", "يمكن استعادة المناسبات المحذوفة قبل إزالتها نهائيًا."),
        ("🧮", "Date &amp; time tools", "أدوات التاريخ والوقت", "A Hijri↔Gregorian converter, age calculator, date difference, add/subtract days, and a retirement estimator.", "محوّل هجري↔ميلادي، وحاسبة العمر، وفرق التاريخين، وإضافة/طرح الأيام، ومقدّر تاريخ التقاعد."),
        ("📅", "Dual calendar", "تقويم مزدوج", "See every date in the Gregorian or Hijri (Umm al-Qura) calendar you prefer.", "اعرض كل تاريخ بالتقويم الميلادي أو الهجري (أم القرى) حسب تفضيلك."),
        ("↔️", "Import &amp; export", "استيراد وتصدير", "Share selected events as a JSON file and import them back — you control the file.", "شارك مناسبات مختارة كملف JSON واستوردها مجددًا — الملف بين يديك."),
        ("🔒", "Private &amp; offline", "خاص وبلا اتصال", "Works fully offline with no accounts and no tracking; add an optional biometric app lock.", "يعمل دون اتصال تمامًا، بلا حسابات وبلا تتبّع؛ مع قفلٍ اختياري بالبصمة."),
    ]
    intro_en = ("Countdown Keeper answers one question instantly: how long until — or since — this "
                "event? It is a fast, private counter for birthdays, anniversaries, deadlines, holidays "
                "and more, with a set of handy date and time tools built in.")
    intro_ar = ("يجيب تطبيق العدّاد عن سؤال واحد فورًا: كم بقي على هذا الحدث — أو كم مضى عليه؟ إنه عدّاد "
                "سريع وخاص للمواليد والذكرى السنوية والمواعيد النهائية والإجازات وغيرها، مع مجموعة من أدوات "
                "التاريخ والوقت العملية.")
    extra = f'''<div class="callout" style="margin-top:30px">
      {p("Countdown Keeper is in active development and will be published on the App Store and Google Play soon.",
         "تطبيق العدّاد قيد التطوير النشِط، وسيُنشر قريبًا على App Store وGoogle Play.")}
    </div>'''
    body = app_overview_body(app, features_list, intro_en, intro_ar, extra)
    return render("/apps/countdown-keeper/",
                  "Countdown Keeper — Event & Date Countdown App | Thiban Tech Solutions",
                  "العدّاد — تطبيق العدّ التنازلي للمناسبات والتواريخ | ذيبان",
                  "Countdown Keeper counts down to future events and up from past ones, with recurring Hijri/Gregorian dates, reminders, and date tools. Private and offline.",
                  "تطبيق العدّاد يعدّ تنازليًا للمناسبات القادمة وتصاعديًا للماضية، مع تواريخ متكرّرة هجرية/ميلادية وتذكيرات وأدوات للتاريخ. خاصّ ويعمل دون اتصال.",
                  body, active="apps")


def page_app_vault():
    app = APPS["vault"]
    features_list = [
        ("🧾", "Invoices &amp; receipts", "الفواتير والإيصالات", "Capture receipts with your camera or import them from files and photos, all in one place.", "التقط الإيصالات بالكاميرا أو استوردها من الملفات والصور، في مكان واحد."),
        ("📸", "Smart scanning", "مسح ذكي", "Scan paper receipts with edge detection and auto-capture, and read ZATCA invoice QR codes.", "امسح الإيصالات الورقية مع كشف الحواف والالتقاط التلقائي، واقرأ رموز QR لفواتير هيئة الزكاة والضريبة."),
        ("🛡️", "Warranty tracking", "تتبّع الضمانات", "Record warranty periods and get a reminder on your device before a warranty expires.", "سجّل مدد الضمان واحصل على تذكير على جهازك قبل انتهاء الضمان."),
        ("📦", "Products", "المنتجات", "Organize the products under each invoice with their own photos and details.", "نظّم المنتجات ضمن كل فاتورة بصورها وتفاصيلها الخاصة."),
        ("📍", "Store &amp; location", "المتجر والموقع", "Save where you bought an item, optionally capture the store's location, and reopen it in your maps app.", "احفظ مكان الشراء، مع إمكانية التقاط موقع المتجر، وأعد فتحه في تطبيق الخرائط لديك."),
        ("📄", "Reports &amp; PDF", "تقارير وPDF", "Turn a receipt into a shareable PDF and export bulk warranty reports to print or send.", "حوّل الإيصال إلى ملف PDF قابل للمشاركة، وصدّر تقارير ضمان مجمّعة للطباعة أو الإرسال."),
        ("📥", "Share into Vault", "المشاركة إلى الخزنة", "Send a PDF or image from another app straight into Vault.", "أرسل ملف PDF أو صورة من تطبيق آخر مباشرةً إلى الخزنة."),
        ("🔐", "Encrypted backup", "نسخ احتياطي مشفّر", "Create a password-protected backup (AES-256) and restore it whenever you need — you choose where it is stored.", "أنشئ نسخة احتياطية محمية بكلمة مرور (AES-256) واستعدها متى شئت — وأنت تختار مكان تخزينها."),
        ("🔒", "Private &amp; secure", "خاص وآمن", "Local-first with an optional Face ID / biometric app lock; no ads and no tracking.", "يعمل محليًا مع قفلٍ اختياري ببصمة الوجه أو البصمة؛ بلا إعلانات وبلا تتبّع."),
    ]
    intro_en = ("Vault — Warranty Manager keeps your purchase invoices, products and warranty dates "
                "organized in one private place, and reminds you before a warranty runs out. It is free "
                "to get started, with a one-time Lifetime Access that unlocks unlimited invoices and products.")
    intro_ar = ("خزنة الضمانات تحفظ فواتير مشترياتك ومنتجاتك وتواريخ ضماناتها منظّمةً في مكان واحد خاص، "
                "وتذكّرك قبل انتهاء الضمان. تبدأ مجانًا، مع خيار «الوصول مدى الحياة» بدفعة واحدة يفتح عددًا "
                "غير محدود من الفواتير والمنتجات.")
    embed = APPS["vault"]["youtube_embed"]
    extra = f'''<div style="max-width:760px;margin:40px auto 0">
      {h(3, "Watch it in action", "شاهده أثناء العمل", "center")}
      <div class="video-wrap" style="margin-top:16px">
        <iframe src="{embed}" title="Vault — Warranty Manager video" loading="lazy"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen></iframe>
      </div>
    </div>'''
    body = app_overview_body(app, features_list, intro_en, intro_ar, extra)
    return render("/apps/vault/",
                  "Vault — Warranty Manager | Thiban Tech Solutions",
                  "خزنة الضمانات — إدارة الفواتير والضمانات | ذيبان",
                  "Vault — Warranty Manager stores invoices, organizes products, scans receipts and ZATCA QR codes, and reminds you before warranties expire. Private and local-first.",
                  "خزنة الضمانات تحفظ الفواتير وتنظّم المنتجات وتمسح الإيصالات ورموز QR الضريبية وتذكّرك قبل انتهاء الضمان. خاصّة وتعمل محليًا.",
                  body, active="apps")


# ---------------------------- tutorials ------------------------------------

def page_tutorials():
    cards = []
    for slug in ("countdown-keeper", "vault"):
        a = APPS[slug]
        cards.append(f'''<article class="card">
          <div class="app-head"><img src="{a['icon']}" alt="" width="56" height="56" style="width:56px;height:56px;border-radius:14px">
          <h3><a href="/tutorials/{slug}/"><span data-en>{a['name_en']}</span><span data-ar>{a['name_ar']}</span></a></h3></div>
          <p style="margin-top:12px" data-en>Step-by-step guides, tips and answers to common questions.</p>
          <p style="margin-top:12px" data-ar>أدلة خطوة بخطوة ونصائح وإجابات عن الأسئلة الشائعة.</p>
          <p style="margin-top:10px"><a href="/tutorials/{slug}/"><span data-en>Open tutorials →</span><span data-ar>افتح الشروحات →</span></a></p>
        </article>''')
    body = f'''{crumbs([("Home","الرئيسية","/"),("Tutorials","الشروحات",None)])}
<section class="section"><div class="container">
  {h(1, "Tutorials", "الشروحات")}
  {p("Learn how to get the most out of each Thiban app. Guides grow over time — pick an app to begin.",
     "تعلّم كيف تستفيد من كل تطبيق من ذيبان استفادةً كاملة. تنمو الأدلة مع الوقت — اختر تطبيقًا لتبدأ.", "lead")}
  <div class="grid grid-2" style="margin-top:32px">{"".join(cards)}</div>
</div></section>'''
    return render("/tutorials/",
                  "Tutorials — Thiban Tech Solutions",
                  "الشروحات — ذيبان للحلول التقنية",
                  "Step-by-step tutorials and guides for Thiban apps: Countdown Keeper and Vault — Warranty Manager.",
                  "شروحات وأدلة خطوة بخطوة لتطبيقات ذيبان: العدّاد وخزنة الضمانات.",
                  body, active="tutorials")


def tutorial_page(slug, title_en, title_ar, desc_en, desc_ar, intro_en, intro_ar,
                  steps_list, tips, faqs, video_embed=None):
    a = APPS[slug]
    video = ""
    if video_embed:
        video = f'''<div style="margin:28px 0">
          <div class="video-wrap"><iframe src="{video_embed}" title="{esc(title_en)}" loading="lazy"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div></div>'''
    tips_html = ""
    if tips:
        tips_html = f'{h(2,"Tips","نصائح")}{ul(tips)}'
    body = f'''{crumbs([("Home","الرئيسية","/"),("Tutorials","الشروحات","/tutorials/"),(a['name_en'],a['name_ar'],None)])}
<section class="section"><div class="container prose">
  {h(1, title_en, title_ar)}
  {p(intro_en, intro_ar, "lead")}
  {video}
  {h(2, "Getting started", "البداية")}
  {steps(steps_list)}
  {tips_html}
  {h(2, "Frequently asked questions", "أسئلة شائعة")}
  {faq(faqs)}
  <div class="callout" style="margin-top:28px">
    {p(f'Need more help? Visit <a href="/support/{slug}/">{a["name_en"]} support</a> or email us.',
       f'تحتاج مزيدًا من المساعدة؟ تفضّل بزيارة <a href="/support/{slug}/">دعم {a["name_ar"]}</a> أو راسلنا عبر البريد.')}
  </div>
</div></section>'''
    return render(f"/tutorials/{slug}/", title_en, title_ar, desc_en, desc_ar, body, active="tutorials")


def page_tutorial_countdown():
    steps_list = [
        ("Add your first event", "أضِف مناسبتك الأولى", "Tap the + button, type a title, and pick the date (and time, if it matters).", "اضغط زر +، واكتب عنوانًا، واختر التاريخ (والوقت إن كان مهمًّا)."),
        ("Choose a calendar", "اختر التقويم", "Pick Gregorian or Hijri for how the date is calculated and shown.", "اختر التقويم الميلادي أو الهجري لطريقة حساب التاريخ وعرضه."),
        ("Make it recognizable", "اجعلها مميّزة", "Give the event a colour and an emoji, or attach your own photo, and add notes.", "امنح المناسبة لونًا ورمزًا تعبيريًا، أو أرفق صورتك الخاصة، وأضِف ملاحظات."),
        ("Turn on a reminder", "فعّل التذكير", "Optionally enable a notification for the time, a day, or a week before.", "فعّل — إن شئت — إشعارًا عند الموعد أو قبله بيوم أو بأسبوع."),
        ("Pin what matters", "ثبّت المهمّ", "Pin important events to keep them at the top of your list.", "ثبّت المناسبات المهمّة لتبقى أعلى قائمتك."),
    ]
    tips = [
        ("Repeat an event monthly from the event editor to track recurring dates automatically.",
         "كرِّر المناسبة شهريًا من محرّر المناسبة لتتبّع التواريخ المتكرّرة تلقائيًا."),
        ("Use the Tools tab for the age calculator, date difference, and the retirement estimator.",
         "استخدم تبويب الأدوات لحاسبة العمر وفرق التاريخين ومقدّر التقاعد."),
        ("Export your events to a JSON file as a personal backup you fully control.",
         "صدّر مناسباتك إلى ملف JSON كنسخة احتياطية شخصية تتحكّم بها تمامًا."),
    ]
    faqs = [
        ("Do I need an internet connection?", "هل أحتاج إلى اتصال بالإنترنت؟",
         "No. Countdown Keeper works fully offline; your events stay on your device.",
         "لا. يعمل تطبيق العدّاد دون اتصال تمامًا، وتبقى مناسباتك على جهازك."),
        ("How do I recover a deleted event?", "كيف أستعيد مناسبة محذوفة؟",
         "Open the Recycle bin and restore it before it is permanently purged.",
         "افتح سلة المحذوفات واستعد المناسبة قبل إزالتها نهائيًا."),
        ("Can I show dates in the Hijri calendar?", "هل يمكن عرض التواريخ بالتقويم الهجري؟",
         "Yes. You can view dates in the Hijri (Umm al-Qura) or Gregorian calendar, and even repeat events on Hijri dates.",
         "نعم. يمكنك عرض التواريخ بالتقويم الهجري (أم القرى) أو الميلادي، بل وتكرار المناسبات على تواريخ هجرية."),
    ]
    return tutorial_page("countdown-keeper",
                         "Countdown Keeper Tutorials",
                         "شروحات تطبيق العدّاد",
                         "How to use Countdown Keeper: add events, set recurring Hijri/Gregorian dates, reminders, and use the built-in date tools.",
                         "كيفية استخدام تطبيق العدّاد: إضافة المناسبات، وضبط التواريخ المتكرّرة الهجرية/الميلادية، والتذكيرات، واستخدام أدوات التاريخ.",
                         "Learn how to add events, use reminders, recurring dates and the built-in date tools.",
                         "تعلّم كيف تضيف المناسبات، وتستخدم التذكيرات والتواريخ المتكرّرة وأدوات التاريخ المدمجة.",
                         steps_list, tips, faqs)


def page_tutorial_vault():
    steps_list = [
        ("Add a purchase", "أضِف عملية شراء", "Tap add and scan the paper receipt, read its QR code, or import an existing image or PDF.", "اضغط «إضافة» وامسح الإيصال الورقي، أو اقرأ رمز QR، أو استورد صورة أو ملف PDF موجودًا."),
        ("Fill in the details", "أدخِل التفاصيل", "Add the store, purchase date and the products, each with its own warranty period.", "أضِف المتجر وتاريخ الشراء والمنتجات، لكلٍّ منها مدة ضمانه."),
        ("Set the warranty", "حدّد الضمان", "Enter the warranty length so Vault can remind you before it expires.", "أدخِل مدة الضمان لتذكّرك الخزنة قبل انتهائه."),
        ("Save the store location", "احفظ موقع المتجر", "Optionally capture the store's location so you can reopen it in your maps app later.", "التقط — إن شئت — موقع المتجر لتعيد فتحه لاحقًا في تطبيق الخرائط."),
        ("Back up your data", "انسخ بياناتك احتياطيًا", "Create an encrypted, password-protected backup and keep it somewhere safe.", "أنشئ نسخة احتياطية مشفّرة ومحمية بكلمة مرور واحفظها في مكان آمن."),
    ]
    tips = [
        ("Share a PDF or photo from WhatsApp, Gmail or Files directly into Vault to file it instantly.",
         "شارك ملف PDF أو صورة من واتساب أو Gmail أو الملفات مباشرةً إلى الخزنة لحفظها فورًا."),
        ("Export a bulk warranty report as a PDF to print or send.",
         "صدّر تقرير ضمانات مجمّعًا بصيغة PDF للطباعة أو الإرسال."),
        ("Lifetime Access removes the free limit of 3 invoices with one product each.",
         "يزيل «الوصول مدى الحياة» حدَّ النسخة المجانية البالغ 3 فواتير بمنتج واحد لكلٍّ منها."),
    ]
    faqs = [
        ("Where is my data stored?", "أين تُخزَّن بياناتي؟",
         "On your device. Vault is local-first and does not upload your invoices to any server.",
         "على جهازك. تعمل الخزنة محليًا ولا ترفع فواتيرك إلى أي خادم."),
        ("How do reminders work?", "كيف تعمل التذكيرات؟",
         "Vault schedules a local notification on your device before a warranty's expiry date.",
         "تجدول الخزنة إشعارًا محليًا على جهازك قبل تاريخ انتهاء الضمان."),
        ("Is the backup safe?", "هل النسخة الاحتياطية آمنة؟",
         "Backups are encrypted with AES-256 using a password you set. Keep the password safe — it cannot be recovered.",
         "تُشفَّر النسخ الاحتياطية بمعيار AES-256 بكلمة مرور تحدّدها. احتفظ بكلمة المرور — إذ لا يمكن استعادتها."),
        ("What is Lifetime Access?", "ما هو «الوصول مدى الحياة»؟",
         "A single one-time purchase that unlocks unlimited invoices and products. There are no subscriptions.",
         "عملية شراء واحدة تفتح عددًا غير محدود من الفواتير والمنتجات. ولا توجد اشتراكات."),
    ]
    return tutorial_page("vault",
                         "Vault — Warranty Manager Tutorials",
                         "شروحات خزنة الضمانات",
                         "How to use Vault: scan receipts and QR codes, track warranties, save store locations, export reports, and create encrypted backups.",
                         "كيفية استخدام خزنة الضمانات: مسح الإيصالات ورموز QR، وتتبّع الضمانات، وحفظ مواقع المتاجر، وتصدير التقارير، وإنشاء نسخ احتياطية مشفّرة.",
                         "Learn how to scan receipts, track warranties, and back up your data securely.",
                         "تعلّم كيف تمسح الإيصالات، وتتبّع الضمانات، وتنسخ بياناتك احتياطيًا بأمان.",
                         steps_list, tips, faqs,
                         video_embed=APPS["vault"]["youtube_embed"])


# ---------------------------- privacy --------------------------------------

def page_privacy_index():
    cards = []
    for slug in ("countdown-keeper", "vault"):
        a = APPS[slug]
        cards.append(f'''<article class="card">
          <div class="app-head"><img src="{a['icon']}" alt="" width="56" height="56" style="width:56px;height:56px;border-radius:14px">
          <h3><a href="/privacy/{slug}/"><span data-en>{a['name_en']}</span><span data-ar>{a['name_ar']}</span></a></h3></div>
          <p style="margin-top:12px"><a href="/privacy/{slug}/"><span data-en>Read the privacy policy →</span><span data-ar>اقرأ سياسة الخصوصية →</span></a></p>
        </article>''')
    body = f'''{crumbs([("Home","الرئيسية","/"),("Privacy","الخصوصية",None)])}
<section class="section"><div class="container prose">
  {h(1, "Privacy", "الخصوصية")}
  {p("We build privacy-first apps. Our apps are local-first: your data stays on your device, we do not run accounts or servers for your content, and we do not use ads, analytics, or third-party trackers.",
     "نحن نبني تطبيقات تضع الخصوصية أولًا. تطبيقاتنا تعمل محليًا: بياناتك تبقى على جهازك، ولا نُشغّل حسابات أو خوادم لمحتواك، ولا نستخدم إعلانات أو تحليلات أو أدوات تتبّع من طرف ثالث.", "lead")}
  {h(2, "Per-app privacy policies", "سياسات الخصوصية لكل تطبيق")}
  {p("Each app has its own policy describing exactly what it handles:", "لكل تطبيق سياسته الخاصة التي تصف بدقّة ما يتعامل معه:")}
</div>
<div class="container"><div class="grid grid-2" style="margin-top:20px">{"".join(cards)}</div></div>
</section>'''
    return render("/privacy/",
                  "Privacy — Thiban Tech Solutions",
                  "الخصوصية — ذيبان للحلول التقنية",
                  "Privacy at Thiban Tech Solutions: local-first apps with no ads, analytics, or third-party tracking. Read each app's privacy policy.",
                  "الخصوصية في ذيبان للحلول التقنية: تطبيقات تعمل محليًا بلا إعلانات أو تحليلات أو تتبّع من طرف ثالث. اقرأ سياسة خصوصية كل تطبيق.",
                  body, active="privacy")


def load_privacy(slug, lang):
    with open(os.path.join(ROOT, "content", "privacy", slug, f"{lang}.json"), encoding="utf-8") as f:
        return json.load(f)


def privacy_hreflang(slug, langs):
    tags = [f'<link rel="alternate" hreflang="{L}" href="{SITE_URL}/privacy/{slug}/{L}/">' for L in langs]
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/privacy/{slug}/en/">')
    return "\n".join(tags)


def privacy_doc(app, lang, data, canonical):
    """A fully self-contained, single-language privacy document.

    No global site header, footer, or language switcher — opening the Japanese
    URL shows only the Japanese policy. Language discovery lives on the app page
    and the /privacy/ overview; hreflang tags below keep the set linked for SEO
    and store crawlers. Works with zero JavaScript."""
    slug = app["slug"]
    d = data["dir"]
    app_name = app["name_ar"] if lang == "ar" else app["name_en"]
    parts = []
    for b in data["blocks"]:
        if b["t"] == "h2":
            parts.append(f'<h2>{b["html"]}</h2>')
        elif b["t"] == "p":
            parts.append(f'<p>{b["html"]}</p>')
        else:
            parts.append(b["html"])
    hreflang = privacy_hreflang(slug, app["privacy_langs"])
    if lang == "ar":
        foot = f'© {YEAR} ذيبان للحلول التقنية · <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>'
    else:
        foot = f'© {YEAR} Thiban Tech Solutions · <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>'
    title = f"{data['title']} — {app['name_en']}"
    return f'''<!DOCTYPE html>
<html lang="{lang}" dir="{d}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(data['title'])}">
<link rel="canonical" href="{canonical}">
{hreflang}
<meta name="theme-color" content="#165dff">
<meta name="color-scheme" content="light">
<meta name="robots" content="index,follow">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body class="doc">
<main class="doc-wrap">
  <header class="doc-head">
    <img class="doc-icon" src="{app['icon']}" alt="{esc(app['name_en'])} icon" width="72" height="72">
    <div class="doc-app">{esc(app_name)}</div>
    <h1 class="doc-title">{data['title']}</h1>
    <p class="doc-date">{data['effective']}</p>
  </header>
  <article class="policy prose">
    {"".join(parts)}
  </article>
  <footer class="doc-foot">{foot}</footer>
</main>
</body>
</html>'''


def _write(path, html):
    rel = path.strip("/")
    out_dir = os.path.join(ROOT, rel)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return SITE_URL + (path if path.endswith("/") else path + "/")


def gen_privacy(slug):
    """Write one standalone page per privacy language + a canonical entry point
    at /privacy/<slug>/ (English, canonicalised to /en/). Returns localized URLs
    for the sitemap."""
    app = APPS[slug]
    langs = app["privacy_langs"]
    sitemap_urls = []
    for L in langs:
        data = load_privacy(slug, L)
        canonical = f"{SITE_URL}/privacy/{slug}/{L}/"
        u = _write(f"/privacy/{slug}/{L}/", privacy_doc(app, L, data, canonical))
        sitemap_urls.append(u)
    # entry point = English document, canonical -> /en/
    data = load_privacy(slug, "en")
    _write(f"/privacy/{slug}/", privacy_doc(app, "en", data, f"{SITE_URL}/privacy/{slug}/en/"))
    return sitemap_urls


# ---------------------------- support --------------------------------------

def page_support_index():
    cards = []
    for slug in ("countdown-keeper", "vault"):
        a = APPS[slug]
        cards.append(f'''<article class="card">
          <div class="app-head"><img src="{a['icon']}" alt="" width="56" height="56" style="width:56px;height:56px;border-radius:14px">
          <h3><a href="/support/{slug}/"><span data-en>{a['name_en']}</span><span data-ar>{a['name_ar']}</span></a></h3></div>
          <p style="margin-top:12px"><a href="/support/{slug}/"><span data-en>Open support →</span><span data-ar>افتح الدعم →</span></a></p>
        </article>''')
    body = f'''{crumbs([("Home","الرئيسية","/"),("Support","الدعم",None)])}
<section class="section"><div class="container prose">
  {h(1, "Support", "الدعم")}
  {p("We're here to help. Choose your app below for common questions and troubleshooting, or contact us directly.",
     "نحن هنا للمساعدة. اختر تطبيقك أدناه لتطّلع على الأسئلة الشائعة وحلول المشكلات، أو تواصل معنا مباشرةً.", "lead")}
  <div class="callout">
    {p(f'Email us any time: <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>',
       f'راسلنا في أي وقت: <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>')}
    <div style="margin-top:10px">{whatsapp_button()}</div>
  </div>
</div>
<div class="container"><div class="grid grid-2" style="margin-top:8px">{"".join(cards)}</div></div>
</section>'''
    return render("/support/",
                  "Support — Thiban Tech Solutions",
                  "الدعم — ذيبان للحلول التقنية",
                  "Get help with Thiban apps. Common questions, troubleshooting, and how to contact support for Countdown Keeper and Vault.",
                  "احصل على المساعدة لتطبيقات ذيبان. أسئلة شائعة وحلول للمشكلات وطريقة التواصل مع الدعم لتطبيقَي العدّاد وخزنة الضمانات.",
                  body, active="support")


def support_page(slug, title_en, title_ar, desc_en, desc_ar, faqs, trouble):
    a = APPS[slug]
    body = f'''{crumbs([("Home","الرئيسية","/"),("Support","الدعم","/support/"),(a['name_en'],a['name_ar'],None)])}
<section class="section"><div class="container prose">
  {h(1, a['name_en'] + " Support", "دعم " + a['name_ar'])}
  {p("Find quick answers below. If you still need help, email us and we'll respond as soon as we can.",
     "ستجد إجابات سريعة أدناه. وإن بقيت بحاجة إلى المساعدة، فراسلنا عبر البريد وسنردّ في أقرب وقت ممكن.", "lead")}
  {h(2, "Common questions", "أسئلة شائعة")}
  {faq(faqs)}
  {h(2, "Troubleshooting", "حلّ المشكلات")}
  {ul(trouble)}
  {h(2, "More help", "مزيد من المساعدة")}
  <p><a href="/tutorials/{slug}/"><span data-en>Read the {a['name_en']} tutorials</span><span data-ar>اقرأ شروحات {a['name_ar']}</span></a>
     &nbsp;·&nbsp;
     <a href="/privacy/{slug}/"><span data-en>Privacy policy</span><span data-ar>سياسة الخصوصية</span></a></p>
  <div class="callout">
    {p(f'Contact support: <a href="mailto:{SUPPORT_EMAIL}?subject={a["name_en"]} support">{SUPPORT_EMAIL}</a>',
       f'تواصل مع الدعم: <a href="mailto:{SUPPORT_EMAIL}?subject={a["name_ar"]} - دعم">{SUPPORT_EMAIL}</a>')}
    <div style="margin-top:10px">{whatsapp_button()}</div>
  </div>
</div></section>'''
    return render(f"/support/{slug}/", title_en, title_ar, desc_en, desc_ar, body, active="support")


def page_support_countdown():
    faqs = [
        ("Is Countdown Keeper free?", "هل تطبيق العدّاد مجاني؟",
         "The app is in development and will be available on the App Store and Google Play soon.",
         "التطبيق قيد التطوير وسيتوفّر قريبًا على App Store وGoogle Play."),
        ("Will my data sync between devices?", "هل تتزامن بياناتي بين الأجهزة؟",
         "No. Data is stored on each device. Use the JSON export/import to move events between devices.",
         "لا. تُخزَّن البيانات على كل جهاز. استخدم تصدير/استيراد JSON لنقل المناسبات بين الأجهزة."),
        ("How do I turn on reminders?", "كيف أفعّل التذكيرات؟",
         "Enable a reminder when adding or editing an event, then allow notifications when prompted.",
         "فعّل التذكير عند إضافة مناسبة أو تعديلها، ثم اسمح بالإشعارات عند الطلب."),
    ]
    trouble = [
        ("Reminders not appearing? Make sure notifications are allowed for the app in your device settings and that the reminder time is in the future.",
         "لا تظهر التذكيرات؟ تأكّد من السماح بالإشعارات للتطبيق في إعدادات جهازك، وأن وقت التذكير في المستقبل."),
        ("A date looks off by a day? Check whether the event uses the Hijri or Gregorian calendar in its settings.",
         "يبدو التاريخ مزاحًا بيوم؟ تحقّق مما إذا كانت المناسبة تستخدم التقويم الهجري أو الميلادي في إعداداتها."),
        ("Restoring events on a new phone? Use Import and select your exported JSON file.",
         "تستعيد المناسبات على هاتف جديد؟ استخدم «استيراد» واختر ملف JSON الذي صدّرته."),
    ]
    return support_page("countdown-keeper",
                        "Countdown Keeper Support — Thiban Tech Solutions",
                        "دعم تطبيق العدّاد — ذيبان",
                        "Support for Countdown Keeper: common questions, troubleshooting reminders and calendars, and how to contact us.",
                        "دعم تطبيق العدّاد: أسئلة شائعة، وحلول لمشكلات التذكيرات والتقويم، وطريقة التواصل معنا.",
                        faqs, trouble)


def page_support_vault():
    faqs = [
        ("How do I restore a backup?", "كيف أستعيد نسخة احتياطية؟",
         "Open the backup screen, choose Restore, select your backup file, and enter the password you used to create it.",
         "افتح شاشة النسخ الاحتياطي، واختر «استعادة»، وحدّد ملف نسختك، وأدخِل كلمة المرور التي أنشأتها بها."),
        ("I forgot my backup password.", "نسيت كلمة مرور النسخة الاحتياطية.",
         "Backups are encrypted and the password cannot be recovered. Your current data on the device is unaffected.",
         "النسخ الاحتياطية مشفّرة ولا يمكن استعادة كلمة المرور. أمّا بياناتك الحالية على الجهاز فلا تتأثّر."),
        ("What does Lifetime Access include?", "ماذا يتضمّن «الوصول مدى الحياة»؟",
         "A one-time purchase that unlocks unlimited invoices and products. There are no subscriptions.",
         "عملية شراء لمرة واحدة تفتح عددًا غير محدود من الفواتير والمنتجات. ولا توجد اشتراكات."),
        ("Does scanning work offline?", "هل يعمل المسح دون اتصال؟",
         "Yes. Receipt and QR scanning is processed on your device and does not require an internet connection.",
         "نعم. يُعالَج مسح الإيصالات ورموز QR على جهازك ولا يتطلّب اتصالًا بالإنترنت."),
    ]
    trouble = [
        ("Scanner won't open? Allow camera access for Vault in your device settings.",
         "لا يفتح الماسح؟ اسمح بالوصول إلى الكاميرا للخزنة في إعدادات جهازك."),
        ("Warranty reminder didn't arrive? Allow notifications for Vault, and note reminders may be delayed slightly to save battery.",
         "لم يصل تذكير الضمان؟ اسمح بالإشعارات للخزنة، وانتبه إلى أن التذكيرات قد تتأخّر قليلًا لتوفير البطارية."),
        ("\"Use my current location\" not working? Allow location access when prompted; it is only used to save a store's location.",
         "لا يعمل «استخدام موقعي الحالي»؟ اسمح بالوصول إلى الموقع عند الطلب؛ فهو يُستخدم فقط لحفظ موقع المتجر."),
        ("Purchase not recognized? Use the Restore Purchases option on the store/paywall screen.",
         "لم يُتعرَّف على عملية الشراء؟ استخدم خيار «استعادة المشتريات» في شاشة المتجر أو الاشتراك."),
    ]
    return support_page("vault",
                        "Vault — Warranty Manager Support — Thiban Tech Solutions",
                        "دعم خزنة الضمانات — ذيبان",
                        "Support for Vault — Warranty Manager: backups, purchases, scanning, notifications and location troubleshooting, and how to contact us.",
                        "دعم خزنة الضمانات: النسخ الاحتياطي والمشتريات والمسح والإشعارات وحلّ مشكلات الموقع، وطريقة التواصل معنا.",
                        faqs, trouble)


# ---------------------------- contact & about ------------------------------

def page_contact():
    body = f'''{crumbs([("Home","الرئيسية","/"),("Contact","تواصل معنا",None)])}
<section class="section"><div class="container prose">
  {h(1, "Contact us", "تواصل معنا")}
  {p("Questions, feedback, or need help with one of our apps? We'd love to hear from you.",
     "أسئلة أو ملاحظات أو تحتاج إلى مساعدة في أحد تطبيقاتنا؟ يسعدنا أن نسمع منك.", "lead")}
  <div class="grid grid-2" style="margin-top:24px">
    <div class="card">
      {h(3, "WhatsApp", "واتساب")}
      <p style="font-size:1.15rem"><a href="{WHATSAPP_LINK}" target="_blank" rel="noopener" dir="ltr">{WHATSAPP_DISPLAY}</a></p>
      {p("Message us on WhatsApp for the quickest reply.", "راسلنا على واتساب لأسرع ردّ.")}
      <div style="margin-top:14px">{whatsapp_button()}</div>
    </div>
    <div class="card">
      {h(3, "Email", "البريد الإلكتروني")}
      <p style="font-size:1.15rem"><a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>
      {p("We aim to respond to support requests as soon as possible.", "نسعى للردّ على طلبات الدعم في أقرب وقت ممكن.")}
    </div>
  </div>
  <div style="margin-top:24px">
    {p("Looking for something specific?", "تبحث عن شيء محدّد؟")}
    <p><a href="/support/"><span data-en>Support center</span><span data-ar>مركز الدعم</span></a>
       &nbsp;·&nbsp;
       <a href="/tutorials/"><span data-en>Tutorials</span><span data-ar>الشروحات</span></a>
       &nbsp;·&nbsp;
       <a href="/privacy/"><span data-en>Privacy</span><span data-ar>الخصوصية</span></a></p>
  </div>
</div></section>'''
    return render("/contact/",
                  "Contact — Thiban Tech Solutions",
                  "تواصل معنا — ذيبان للحلول التقنية",
                  f"Contact Thiban Tech Solutions by email at {SUPPORT_EMAIL} for questions, feedback, or app support.",
                  f"تواصل مع ذيبان للحلول التقنية عبر البريد {SUPPORT_EMAIL} للأسئلة أو الملاحظات أو دعم التطبيقات.",
                  body, active="")


def page_about():
    body = f'''{crumbs([("Home","الرئيسية","/"),("About","من نحن",None)])}
<section class="section"><div class="container prose">
  {h(1, "About Thiban Tech Solutions", "عن ذيبان للحلول التقنية")}
  {p("Thiban Tech Solutions is a focused software studio specializing in web and mobile application development. We also design and publish our own privacy-first apps for everyday life.",
     "ذيبان للحلول التقنية استوديو برمجيّ متخصّص في تطوير تطبيقات الويب والجوال. كما نصمّم وننشر تطبيقاتنا الخاصة التي تضع الخصوصية أولًا لحياتك اليومية.", "lead")}
  {h(2, "What we build", "ما الذي نطوره")}
  <div class="services" style="margin-top:20px">
    <article class="service-card"><div class="service-icon" aria-hidden="true">&lt;/&gt;</div>
      {h(3, "Web Application Development", "تطوير تطبيقات الويب")}
      {p("Responsive, secure, and maintainable web applications designed around real business and user requirements.",
         "تطبيقات ويب متجاوبة وآمنة وقابلة للصيانة، مصمّمة وفق احتياجات العمل والمستخدم الفعلية.")}</article>
    <article class="service-card"><div class="service-icon" aria-hidden="true">▣</div>
      {h(3, "Mobile Application Development", "تطوير تطبيقات الجوال")}
      {p("Polished cross-platform mobile applications for Android and iOS, focused on usability, reliability, and performance.",
         "تطبيقات جوال متقنة تعمل على أندرويد و iOS، مع تركيز على سهولة الاستخدام والموثوقية والأداء.")}</article>
  </div>
  {h(2, "What we believe", "بماذا نؤمن")}
  <div class="features" style="margin-top:20px">
    {feature("🔒","Privacy by default","الخصوصية افتراضيًا","Your data belongs to you and stays on your device. No ads, no analytics, no tracking.","بياناتك مِلكك وتبقى على جهازك. بلا إعلانات ولا تحليلات ولا تتبّع.")}
    {feature("✨","Simplicity","البساطة","We remove everything that gets in the way, so each app does its job quickly.","نزيل كل ما يعترض الطريق، ليؤدّي كل تطبيق مهمّته بسرعة.")}
    {feature("🌍","Arabic &amp; English","العربية والإنجليزية","First-class Arabic with proper right-to-left layout, alongside English.","لغة عربية من الطراز الأول مع تخطيط سليم من اليمين إلى اليسار، إلى جانب الإنجليزية.")}
    {feature("🛠️","Craftsmanship","الإتقان","Careful engineering and attention to the details that make apps reliable.","هندسة دقيقة واهتمام بالتفاصيل التي تجعل التطبيقات موثوقة.")}
  </div>
  {h(2, "Our apps", "تطبيقاتنا")}
  {p("We currently publish Countdown Keeper and Vault — Warranty Manager, with more to come.",
     "ننشر حاليًا تطبيقَي العدّاد وخزنة الضمانات، والمزيد قادم.")}
  <p><a class="btn btn-primary" href="/apps/"><span data-en>See our apps</span><span data-ar>شاهد تطبيقاتنا</span></a></p>
  {h(2, "Get in touch", "تواصل معنا")}
  {p(f'For anything at all, email <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>.',
     f'لأي أمر، راسلنا على <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a>.')}
</div></section>'''
    return render("/about/",
                  "About — Thiban Tech Solutions",
                  "من نحن — ذيبان للحلول التقنية",
                  "Thiban Tech Solutions is an independent studio building simple, private, useful mobile apps in Arabic and English.",
                  "ذيبان للحلول التقنية استوديو مستقلّ يبني تطبيقات جوّال بسيطة وخاصة ومفيدة بالعربية والإنجليزية.",
                  body, active="about")


def page_404():
    body = f'''<div class="center-screen">
  <div>
    <img src="/assets/img/brand/icon-192.png" alt="" width="72" height="72" style="margin:0 auto 20px;border-radius:16px">
    {h(1, "Page not found", "الصفحة غير موجودة")}
    {p("The page you were looking for doesn't exist or has moved.", "الصفحة التي تبحث عنها غير موجودة أو تم نقلها.", "lead")}
    <div class="btn-row" style="justify-content:center;margin-top:20px">
      <a class="btn btn-primary" href="/"><span data-en>Go home</span><span data-ar>العودة للرئيسية</span></a>
      <a class="btn btn-ghost" href="/apps/"><span data-en>Browse apps</span><span data-ar>تصفّح التطبيقات</span></a>
    </div>
  </div>
</div>'''
    return render("/404", "Page not found — Thiban Tech Solutions",
                  "الصفحة غير موجودة — ذيبان للحلول التقنية",
                  "The page you were looking for doesn't exist or has moved.",
                  "الصفحة التي تبحث عنها غير موجودة أو تم نقلها.",
                  body, is404=True)


# ---------------------------- sitemap & robots -----------------------------

def write_sitemap(urls):
    lastmod = "2026-09-02"
    items = "".join(
        f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod></url>\n" for u in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           f"{items}</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)


def write_robots():
    txt = ("User-agent: *\n"
           "Allow: /\n\n"
           f"Sitemap: {SITE_URL}/sitemap.xml\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(txt)


def write_manifest():
    import json
    manifest = {
        "name": "Thiban Tech Solutions",
        "short_name": "Thiban",
        "start_url": "/",
        "display": "browser",
        "background_color": "#ffffff",
        "theme_color": "#165dff",
        "icons": [
            {"src": "/assets/img/brand/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/img/brand/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def main():
    urls = []
    urls.append(render_home_and_collect())
    for fn in (page_apps, page_app_countdown, page_app_vault,
               page_tutorials, page_tutorial_countdown, page_tutorial_vault,
               page_privacy_index,
               page_support_index, page_support_countdown, page_support_vault,
               page_contact, page_about):
        urls.append(fn())
    # Localized privacy policies (one direct URL per language, per app).
    priv_count = 0
    for slug in APPS:
        localized = gen_privacy(slug)   # also writes the /privacy/<slug>/ entry
        urls.extend(localized)          # /privacy/<slug>/<lang>/ in sitemap
        priv_count += len(localized)
    page_404()  # not in sitemap
    write_sitemap([u for u in urls if u])
    write_robots()
    write_manifest()
    print(f"Built {len(urls)} sitemap URLs ({priv_count} localized privacy pages) + 404, sitemap, robots, manifest.")


def render_home_and_collect():
    body = page_home()
    return render("/",
                  "Thiban Tech Solutions — Simple, useful mobile apps",
                  "ذيبان للحلول التقنية — تطبيقات جوّال بسيطة ومفيدة",
                  "Thiban Tech Solutions builds simple, private, useful mobile apps in Arabic and English — including Countdown Keeper and Vault, the Warranty Manager.",
                  "ذيبان للحلول التقنية تبني تطبيقات جوّال بسيطة وخاصة ومفيدة بالعربية والإنجليزية — منها تطبيق العدّاد وخزنة الضمانات.",
                  body, active="home")


if __name__ == "__main__":
    main()
