# thiban1.com — Thiban Tech Solutions website

The official developer/company website for **Thiban Tech Solutions**, hosting
information, tutorials, privacy policies and support pages for our mobile apps
(currently **Countdown Keeper** and **Vault — Warranty Manager**).

- **Live site:** https://thiban1.com
- **Tech:** hand-written **static HTML5 + CSS3 + a little vanilla JavaScript**.
  No framework, no database, no backend, no build step is required to *serve* it.
- **Languages:** English (default) and Modern Standard **Arabic** with full RTL.
- **Privacy:** no cookies, no analytics, no third-party trackers.

## Local preview

Any static file server works. From the repository root:

```bash
python3 -m http.server 8099
# then open http://127.0.0.1:8099/
```

> Use a server (not `file://`) because internal links are root-absolute
> (e.g. `/apps/`).

## How the site is generated

The published files (`index.html`, `apps/…`, `sitemap.xml`, …) are **plain
static output** and can be edited directly. To keep ~15 bilingual pages
consistent (shared header/footer, SEO/Open-Graph tags, the language switch),
they are produced from one small script:

```bash
python3 tools/build.py    # regenerates all *.html + sitemap.xml + robots.txt + site.webmanifest
```

`tools/build.py` needs only Python 3 (no packages). The **output** it writes has
no dependencies at all, which keeps the site portable.

Both workflows are supported: edit the HTML by hand, **or** edit the content in
`tools/build.py` and re-run it. If you hand-edit HTML, don't re-run the builder
(it would overwrite your changes).

### Bilingual content

Every translatable string is emitted twice — `<... data-en>` and
`<... data-ar>` — and both ship in the HTML. CSS shows only the active
language based on `html[data-lang]`; `assets/js/site.js` toggles the language
(persisted in `localStorage`) and sets `dir="rtl"` for Arabic.

## Folder structure

```
/                     Home (index.html)
/apps/                Apps overview
/apps/<slug>/         One page per app
/tutorials/           Tutorials overview + /tutorials/<slug>/
/privacy/             Privacy overview + /privacy/<slug>/   (store-submittable URLs)
/support/             Support overview + /support/<slug>/
/about/  /contact/    Company pages
/404.html             Custom not-found page
/assets/css/          styles.css
/assets/js/           site.js
/assets/img/brand/    logo + favicons + Open-Graph image
/assets/img/apps/     app icons + screenshots (copied in, not referenced from other repos)
/tools/build.py       the generator
CNAME .nojekyll       GitHub Pages config
robots.txt sitemap.xml site.webmanifest
```

## Adding a new app

1. Copy the app's icon and 3–4 screenshots into `assets/img/apps/<slug>/`
   (copy the files — never reference another repository's path).
2. In `tools/build.py`, add an entry to the `APPS` dict (`name_en/ar`,
   `tagline_en/ar`, `icon`, `status` = `live` or `soon`, store URLs, `screens`).
3. Add page functions modelled on the existing ones:
   `page_app_<slug>`, `page_tutorial_<slug>`, `page_privacy_<slug>`,
   `page_support_<slug>`, and register them in `main()`.
4. Add the app to the cards in `page_apps`, `page_home`, and the index pages.
5. Run `python3 tools/build.py` and preview locally.

Only add a real, public store URL. If an app isn't released yet, set
`status: "soon"` (shows a subtle “Coming soon”) — never invent a store link.

## Adding / editing a tutorial

Edit the relevant `page_tutorial_<slug>` function: it takes a list of numbered
steps, tips, and FAQ entries, and an optional YouTube embed. Re-run the builder.

## Updating a privacy policy

Edit `page_privacy_<slug>` in `tools/build.py` (sections are `(id, heading_en,
heading_ar, html_en, html_ar)`), update the “Last updated” date passed at the
bottom of the function, and re-run the builder. Keep every statement accurate to
the app's actual behaviour.

## Deployment (GitHub Pages)

The site deploys straight from the `main` branch, repository root — no CI/Actions
needed.

- Repository: https://github.com/AlmalawiCode/thiban1.com (public)
- Pages: **Settings → Pages → Deploy from a branch → `main` / root**
- `.nojekyll` disables Jekyll so files/folders starting with `_` are served as-is.
- `CNAME` contains `thiban1.com` (do not delete — it preserves the custom domain).

## Custom domain & DNS

The apex domain **thiban1.com** and **www.thiban1.com** are used. DNS is managed
at the domain's DNS provider (**Cloudflare**). Required records:

| Type  | Name | Value |
|-------|------|-------|
| A     | @    | 185.199.108.153 |
| A     | @    | 185.199.109.153 |
| A     | @    | 185.199.110.153 |
| A     | @    | 185.199.111.153 |
| AAAA  | @    | 2606:50c0:8000::153 |
| AAAA  | @    | 2606:50c0:8001::153 |
| AAAA  | @    | 2606:50c0:8002::153 |
| AAAA  | @    | 2606:50c0:8003::153 |
| CNAME | www  | almalawicode.github.io |

On Cloudflare set these records to **DNS only** (grey cloud) while GitHub
provisions the HTTPS certificate, then optionally enable the proxy later.
GitHub domain verification may also ask for a `TXT` record under
`_github-pages-challenge-thiban1` — add exactly the value GitHub shows.

## Moving to another host later

Because the output is pure static files, migration is a copy:

- **Cloudflare Pages / Netlify / Vercel:** point the project at this repo; no
  build command, output directory = repository root. Remove `CNAME`/`.nojekyll`
  (they're GitHub-specific but harmless).
- **S3 / any web server:** upload the files; ensure `404.html` is the error
  document and directory URLs serve `index.html`.

No code changes are needed to move hosts.

## License / assets

App icons and screenshots belong to Thiban Tech Solutions and its apps. Site
code © Thiban Tech Solutions.
