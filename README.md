# Mohamed Sbissi — portfolio / PFE 2027

The active portfolio uses the approved **CV-2.pdf** (user-reported score: 88). It has a midnight-green hero, a compact employer/award proof strip, warm light sections, three selected project cards, scroll reveals and a reading progress indicator. All assets are local; no runtime framework or remote font is used.

## Open

Open `index.html` directly, or serve the folder with `python -m http.server 8000` and visit `http://localhost:8000/`.

- Current CV: `assets/cv/CV-2.pdf`, exactly one A4 page.
- Printable current CV: `cv-2.html`; `cv.html` contains the same approved version.
- Previous CV preserved: `assets/cv/CV.pdf` and `cv-v1.html`.
- Previous canonical content: `data/archive/profile-v1.json`.

## Edit and build

`data/profile.json` is the portfolio content source. `data/cv-2.json` contains the approved concise CV wording. Keep contribution ownership, current coursework, internship exposure and NDA restrictions explicit.

From this repository:

```powershell
python scripts/build.py
python scripts/validate.py
```

The normal build updates the website and printable alias, while retaining both PDFs. To regenerate CV-2 after deliberately editing its content:

```powershell
python scripts/build.py --pdf
python scripts/validate.py
```

The PDF generator requires exactly one page, readable 9.5pt body type, extractable text, valid links and a decodable QR. It renders a PNG for visual review. It never writes the previous `CV.pdf`.

## Files

- `scripts/build.py`, `render_portfolio.py`, `design.py`: semantic HTML and presentation generation.
- `css/style.css`, `responsive.css`, `premium.css`, `print.css`: portfolio design and responsive/print rules.
- `js/main.js`: keyboard-accessible mobile navigation, scroll reveals and progress.
- `css/cv.css`: separate CV typography, unaffected by portfolio styling.
- `scripts/build_cv2.py`: approved current CV generation and checks.
- `validation/`: browser screenshots, checks and CV previews.
- `FACTS_TO_VERIFY.md`: private owner review notes excluded from the public UI.

ODDO numbers come from the internship journal: 12 HR domains, 7 SQL views, 4 Power BI pages, 25 DAX measures and 10 authenticated analytics endpoints. Kafka, OpenShift and the broader enterprise stack remain labeled environment exposure. GreenOPS technology details remain withheld under NDA; its award is a team achievement.

## Accessibility and validation

The first visit opens the English portfolio immediately. Use EN / FR in navigation to choose French; the choice is stored locally for later visits. `data/translations-fr.json` is the French translation source; the build annotates text without changing links. Official technology and credential names are retained. The approved one-page CV remains in English. Without JavaScript, the English portfolio remains accessible.

Motion respects `prefers-reduced-motion`, including preference changes while the page is open. Without JavaScript, content and navigation remain accessible. Animations use opacity/transforms; scroll updates are scheduled through animation frames. No mouse-following effects or audio.

Validation checks eight widths (320–1920px), overflow, mobile menu/Escape behavior, project cards, environment disclosure, actual CV downloads, errors, no-JS mode, motion preferences, link/asset integrity, one-page A4 PDF text and bounds, and QR decoding. The previous one-page PDF is checked by hash.

## Publish

Contact-card and native sharing controls are implemented. Tapping the displayed phone number opens the prefilled VCF; a separate Call link keeps dialing available. Mobile OS/browser import steps vary, and users confirm saving. The photo is embedded in the card. The share button uses the native Web Share API with a copy-link dialog fallback.

Optional, opt-in analytics and a private Cloudflare Worker/D1 dashboard are prepared in `analytics/`. **The backend is not deployed or connected; static collection is disabled.** See [analytics setup](analytics/README.md). The dashboard records consenting visit sessions and approximate active time, not named recruiter identities. Run `python scripts/validate_engagement.py` and `node analytics/test-worker.mjs` for the interaction/security checks. `validation/dashboard-test-fixture.png` contains explicitly synthetic test data.

The portfolio is updated locally; it has not been deployed. The existing GitHub Pages workflow deploys the repository on a push to `main`. Keep the `/cv/` URL: `https://mohasbissi01.github.io/cv/` is the canonical and QR destination. The separate analytics backend is not part of the static site.
