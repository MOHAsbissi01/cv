"""Smoke tests for the portfolio. Starts its own server under /cv/ (like GitHub Pages).

Run from the repo root:  python scripts/check_site.py
Requires: pip install playwright && playwright install chromium
"""
import re, subprocess, sys, time, urllib.request, urllib.error
from html.parser import HTMLParser
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PORT = 8765
BASE = f"http://localhost:{PORT}/cv/"
failures = []


def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        failures.append(msg)


# ---------- static checks ----------
html = (SITE / "index.html").read_text(encoding="utf-8")


class Refs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids, self.h1, self.imgs_without_alt = [], set(), 0, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "img" and "alt" not in a:
            self.imgs_without_alt += 1
        for k in ("href", "src"):
            if k in a:
                self.refs.append(a[k])
        if "srcset" in a:
            self.refs += [x.strip().split(" ")[0] for x in a["srcset"].split(",")]


p = Refs()
p.feed(html)
local = [r for r in p.refs if not re.match(r"^(https?:|mailto:|#|data:)", r)]
missing = [r for r in local if not (SITE / r).exists()]
check(not missing, f"all {len(local)} local asset/link paths exist {missing or ''}")
check(not any(r.startswith("/") for r in local), "no root-absolute paths (safe under /cv/)")
frag = [r[1:] for r in p.refs if r.startswith("#") and len(r) > 1]
check(all(f in p.ids for f in frag), "all in-page anchors resolve")
check(p.h1 == 1, "exactly one h1")
check(p.imgs_without_alt == 0, "every img has alt text")
for needle in ('rel="canonical"', 'property="og:image"', 'name="twitter:card"', "application/ld+json", 'name="description"'):
    check(needle in html, f"head contains {needle}")
check("TODO" not in re.sub(r"<!--.*?-->", "", html, flags=re.S), "no visible TODO text in the rendered page")
for f in ("robots.txt", "sitemap.xml", "404.html", "assets/images/og.png", "assets/cv/CV-2.pdf"):
    check((SITE / f).exists(), f"{f} exists")

# ---------- browser checks ----------
srv = subprocess.Popen([sys.executable, str(ROOT / "scripts" / "serve.py"), str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(40):
        try:
            urllib.request.urlopen(BASE)
            break
        except Exception:
            time.sleep(0.25)

    for path, want in (("", 200), ("css/styles.css", 200), ("assets/cv/CV-2.pdf", 200), ("sitemap.xml", 200), ("nope", 404)):
        try:
            code = urllib.request.urlopen(BASE + path).status
        except urllib.error.HTTPError as e:
            code = e.code
        check(code == want, f"GET /cv/{path} -> {code}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()

        def page_for(w=1280, h=900, **kw):
            ctx = browser.new_context(viewport={"width": w, "height": h}, **kw)
            pg = ctx.new_page()
            errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.on("requestfailed", lambda r: errs.append("failed: " + r.url))
            return ctx, pg, errs

        # overflow at 8 widths
        for w in (320, 375, 414, 768, 1024, 1280, 1536, 1920):
            ctx, pg, errs = page_for(w, 900)
            pg.goto(BASE)
            over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            check(over <= 0 and not errs, f"{w}px: no horizontal overflow, no console errors {errs or ''}")
            ctx.close()

        # dashboard interaction
        ctx, pg, errs = page_for()
        pg.goto(BASE)
        pg.locator("#dash").scroll_into_view_if_needed()
        # content-visibility:auto renders the section only once it is near the viewport
        pg.wait_for_function("document.querySelector('.kpi[data-metric=att] .kpi-v').innerText.trim().length > 0")
        att = pg.locator('.kpi[data-metric="att"] .kpi-v').inner_text()
        pg.locator('.kpi[data-metric="hrs"]').click()
        check(pg.locator('.kpi[data-metric="hrs"]').get_attribute("aria-pressed") == "true", "KPI card selects a measure")
        check("SUM ( Training[Hours] )" in pg.locator("#dax").inner_text(), "DAX panel follows the measure")
        pg.locator('.col[data-month="2"]').click()
        check(pg.locator('.col[data-month="2"]').get_attribute("aria-pressed") == "true", "month bar selects")
        check(pg.locator(".col.dim").count() == 11, "other months are de-emphasised")
        pg.locator('.row[data-domain="Finance"]').click()
        check("Finance / Mar" in pg.locator("#scope").inner_text(), "domain + month filters combine")
        check(pg.locator("#clear").is_enabled(), "clear button enabled with filters")
        pg.locator("#clear").click()
        check("All domains / all months" in pg.locator("#scope").inner_text(), "clear resets filters")
        pg.locator('.kpi[data-metric="att"]').click()
        check(pg.locator('.kpi[data-metric="att"] .kpi-v').inner_text() == att, "values are deterministic")
        pg.locator('.col[data-month="0"]').focus()
        pg.keyboard.press("Enter")
        check(pg.locator('.col[data-month="0"]').get_attribute("aria-pressed") == "true", "keyboard selects a bar")
        check(not errs, f"no console errors during interaction {errs or ''}")
        ctx.close()

        # theme toggle + persistence
        ctx, pg, _ = page_for(color_scheme="light")
        pg.goto(BASE)
        check(pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(246, 244, 238)", "follows light OS preference")
        pg.locator("#theme-toggle").click()
        check(pg.evaluate("document.documentElement.dataset.theme") == "dark", "toggle switches to dark")
        pg.reload()
        check(pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(12, 15, 18)", "choice persists across reload")
        ctx.close()
        ctx, pg, _ = page_for(color_scheme="dark")
        pg.goto(BASE)
        check(pg.evaluate("getComputedStyle(document.body).backgroundColor") == "rgb(12, 15, 18)", "follows dark OS preference")
        ctx.close()

        # mobile menu
        ctx, pg, _ = page_for(375, 800)
        pg.goto(BASE)
        check(not pg.locator("#nav").is_visible(), "mobile nav collapsed by default")
        pg.locator("#menu-btn").click()
        check(pg.locator("#nav").is_visible() and pg.locator("#menu-btn").get_attribute("aria-expanded") == "true", "menu opens")
        pg.keyboard.press("Escape")
        check(not pg.locator("#nav").is_visible(), "Escape closes the menu")
        ctx.close()

        # reduced motion: content visible, animations off
        ctx, pg, _ = page_for(reduced_motion="reduce")
        pg.goto(BASE)
        check(pg.evaluate("getComputedStyle(document.querySelector('#experience .reveal')).opacity") == "1", "reduced motion: content visible without reveal")
        check(pg.evaluate("getComputedStyle(document.querySelector('.stage')).animationName") == "none", "reduced motion: pipeline animation off")
        ctx.close()

        # no JS: everything readable, nav usable
        ctx, pg, _ = page_for(375, 800, java_script_enabled=False)
        pg.goto(BASE)
        check(pg.locator("#nav").is_visible(), "no-JS: nav visible")
        check(pg.locator("#experience .reveal").first.evaluate("e => getComputedStyle(e).opacity") == "1", "no-JS: content visible")
        check(pg.locator("noscript").count() >= 1, "no-JS: dashboard has a fallback note")
        ctx.close()
        browser.close()
finally:
    srv.terminate()

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)
