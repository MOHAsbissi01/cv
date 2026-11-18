# Mohamed Sbissi: portfolio

Live at **https://mohasbissi01.github.io/cv/** (this URL is the QR code on the CV, so it must not change).

A hand-written static site: plain HTML, one CSS file and two small scripts. There is no build step, no framework and no runtime dependency. Fonts are system fonts, so nothing loads from a third party.

```
site/                 <- the only folder that gets published
  index.html          single page, all real text (ATS friendly)
  css/styles.css      tokens, light/dark themes, layout, animation
  js/main.js          theme toggle, mobile menu, scroll reveal
  js/dashboard.js     "Featured: Data & BI" interactive report (synthetic data)
  assets/cv/CV-2.pdf  the CV that every "Download CV" button serves
  assets/images/      portrait (WebP), OG image, favicon
  robots.txt, sitemap.xml, 404.html
scripts/              local tooling (not published)
docs/                 private notes (not published)
analytics/            dormant Cloudflare Worker, see below (not published)
```

## Run locally

```powershell
python scripts/serve.py          # http://localhost:8000/cv/
```

The server mounts `site/` under `/cv/`, exactly as GitHub Pages does, so a path that would break in production breaks locally too. All asset paths in the site are relative.

## Test

```powershell
pip install playwright pillow
playwright install chromium
python scripts/check_site.py
```

It checks local links and assets, the single `<h1>`, image alt text, SEO tags, 404 behaviour, horizontal overflow at 8 widths (320 to 1920px), the dashboard interactions (mouse and keyboard), theme toggle and persistence, the mobile menu, `prefers-reduced-motion` and no-JavaScript mode.

For Lighthouse: `npx lighthouse http://localhost:8000/cv/ --preset=desktop` (omit `--preset` for mobile).

## Deploy

`.github/workflows/static.yml` publishes **only `site/`** to GitHub Pages on every push to `main` (or manually from the Actions tab). One-time setting: *Settings → Pages → Build and deployment → Source: GitHub Actions* (already the case, since the previous workflow used the same deploy action).

Because only `site/` is uploaded, `docs/`, `scripts/` and `analytics/` are never public. (The previous workflow uploaded the whole repo, which exposed `FACTS_TO_VERIFY.md`.)

## Editing content

- **Text and sections:** edit `site/index.html`. Content you still have to supply is marked `<!-- TODO(owner): ... -->` in the source (and listed below), never as visible placeholder text.
- **CV PDF:** replace `site/assets/cv/CV-2.pdf` with your file, keeping the name. Or rename it and update the three `href="assets/cv/CV-2.pdf"` links in `index.html` plus the check in `scripts/check_site.py`.
- **Accent colour and themes:** the tokens at the top of `css/styles.css`. Light and dark values are separate, and both were chosen for WCAG AA contrast.
- **Dashboard data:** `js/dashboard.js` generates deterministic *synthetic* numbers from a fixed seed. They are labelled on the page as sample data and are not ODDO BHF data. Keep that label.
- **OG image (link previews):** edit `scripts/og-template.html`, then `python scripts/make_og.py`.
- **Sitemap date:** update `<lastmod>` in `site/sitemap.xml` when content changes.

## Honesty rules the site follows

- SAP BW / ABAP / Fiori (and AWS Fundamentals, DevOps/MLOps) are shown as **"Learning, coursework only"**, never as experience.
- Kafka and OpenShift at ODDO BHF are labelled **"Exposure, not ownership"**.
- GreenOPS AI: team award; tools withheld under NDA; LLM work credited to teammates.
- No invented metrics, clients, testimonials or certificates. Every number on the page comes from the ODDO BHF internship summary.

## TODO: content only you can supply

- [ ] **CV PDF**: confirm `site/assets/cv/CV-2.pdf` is the version you want recruiters to get.
- [ ] **Project screenshots** (Urban Mobility, Business Performance / Superstore). Add an `<img>` (WebP, with width/height and alt text) to each project card.
- [ ] **Measurable outcomes** for both projects (model metric, data volume, users) if you can share them. The cards currently describe outcomes without numbers.
- [ ] **Certification details**: issuer, date and credential link for AWS Academy Cloud Foundations, Fundamentals of Deep Learning, and Introduction to Transformer-Based NLP.
- [ ] **Dates for Road Anomaly Detection and CyberIntel**: their READMEs don't state them, so the cards show none (source comments mark the spot).
- [ ] **CyberIntel gold labels**: its README says the gold labels and NER gold were AI-annotated and await your review. The card's Limits line says "pending review"; update it once you have reviewed them.
- [ ] **Optional screenshots**: the CyberIntel repo already has app screenshots in `docs/screenshots/` (Graph-RAG answer, refusal, knowledge-graph explorer) you could add as WebP. The Road Anomaly repo has none.
- [ ] **Project repository access**: confirm the Urban Mobility team repo and commit link are public and show your work.
- [ ] **GreenOPS AI**: competition date and organiser, if you want them shown (see `docs/FACTS_TO_VERIFY.md`).
- [ ] **Phone number**: intentionally not on the site (your brief lists email, LinkedIn and GitHub). Add it to the Contact section if you want it public.

## What changed from the previous version

The previous site was generated by a Python/BeautifulSoup pipeline (five stacked stylesheets, translation and analytics layers). It was replaced with the hand-written site above. Everything removed is still in git history (last version: commit `a6daeb2`):

- the EN/FR language switch and French translations
- the contact-card (vCard) and share dialogs, and the consent banner
- `privacy.html` (not needed while nothing collects data) and the printable `cv.html` / `cv-2.html`
- the old two-page `CV.pdf`

The `analytics/` folder (Cloudflare Worker + dashboard) is untouched. It was never deployed, and the static-site hooks that fed it were removed with the old front end, so reconnecting it means re-adding a small client script.
