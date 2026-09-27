# Mohamed Sbissi — portfolio / PFE 2027

The active portfolio uses the approved **CV-2.pdf** (user-reported score: 88). It has a midnight-green hero, warm light sections, workflow illustrations, responsive project cards, scroll reveals and a reading progress indicator. All assets are local; no runtime frameworks, remote fonts or tracking.

## Open

Open `index.html` directly, or serve the folder with `python -m http.server 8000` and visit `http://localhost:8000/`.

- Current CV: `assets/cv/CV-2.pdf`, exactly one A4 page.
- Printable current CV: `cv-2.html`; `cv.html` contains the same approved version.
- Previous CV preserved: `assets/cv/CV.pdf` and `cv-v1.html`.
- Previous canonical content: `data/archive/profile-v1.json`.

## Edit and build

`data/profile.json` is the portfolio content source. `data/cv-2.json` contains the approved concise CV wording. Keep contribution ownership, current coursework, internship exposure and NDA restrictions explicit.

From the parent workspace:

```powershell
python CvWebsite/scripts/build.py
python CvWebsite/scripts/validate.py
```

The normal build updates the website and printable alias, while retaining both PDFs. To regenerate CV-2 after deliberately editing its content:

```powershell
python CvWebsite/scripts/build.py --pdf
python CvWebsite/scripts/validate.py
```

The PDF generator requires exactly one page, readable 9.5pt body type, extractable text, valid links and a decodable QR. It renders a PNG for visual review. It never writes the previous `CV.pdf`.

## Files

- `scripts/build.py`, `render_portfolio.py`, `design.py`: semantic HTML and presentation generation.
- `css/style.css`, `responsive.css`, `premium.css`, `print.css`: portfolio design and responsive/print rules.
- `js/main.js`: keyboard-accessible mobile navigation, project filters, scroll reveals and progress.
- `css/cv.css`: separate CV typography, unaffected by portfolio styling.
- `scripts/build_cv2.py`: approved current CV generation and checks.
- `validation/`: browser screenshots, checks and CV previews.
- `FACTS_TO_VERIFY.md`: private owner review notes excluded from the public UI.

Workflow graphics are illustrations, not real dashboards or measured results. ODDO numbers come from the internship journal: 12 HR domains, 7 SQL views, 4 Power BI pages, 25 DAX measures and 10 authenticated analytics endpoints. Kafka, OpenShift and the broader enterprise stack remain labeled environment exposure. GreenOPS technology details remain withheld under NDA; its award is a team achievement.

## Accessibility and validation

The first visit opens a bilingual welcome dialog with English and French choices. The choice is stored locally; returning visitors go directly to their preferred language. Use EN / FR in navigation to switch later. `data/translations-fr.json` is the French translation source; the build annotates text without changing links or illustrations. Official technology and credential names are retained. The approved one-page CV remains in English. Without JavaScript, the English portfolio remains accessible.

Motion respects `prefers-reduced-motion`, including preference changes while the page is open. Without JavaScript, content and navigation remain accessible. Animations use opacity/transforms; scroll updates are scheduled through animation frames. No mouse-following effects or audio.

Validation checks six widths (320–1600px), overflow, mobile menu/Escape behavior, project filtering, environment disclosure, actual CV-2 downloads, errors, no-JS mode, motion preferences, link/asset integrity, one-page A4 PDF text and bounds, and QR decoding. Root deliverables and the previous one-page PDF are checked by hash.

## Publish

The portfolio is updated locally; it has not been deployed. Publish `index.html`, `cv.html`, `cv-2.html`, `cv-v1.html`, `css/`, `js/`, and `assets/` as the contents of the existing `/cv/` site. Canonical and QR destination: `https://mohasbissi01.github.io/cv/`. Owner notes, data and scripts do not need to be publicly served.
