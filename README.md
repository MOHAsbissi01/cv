# CvWebsite - Mohamed Sbissi / PFE 2027

Second iteration: a premium static portfolio and **exactly one A4 page** CV. The previous root website and two-page PDF are preserved. This folder is the active new version.

## Run

Open `CvWebsite/index.html` directly, or from the project root:

```powershell
python -m http.server 8000
```

Visit http://localhost:8000/CvWebsite/. CV source: `CvWebsite/cv.html`. Final PDF: `CvWebsite/assets/cv/CV.pdf`. Buttons download it as `Mohamed-Sbissi-CV.pdf`.

## Structure

- `data/profile.json`: canonical content, direct contributions, internship exposure, evidence, private review items.
- `scripts/render_portfolio.py`: existing portfolio's semantic structure carried into this version.
- `scripts/build.py`: presentation upgrade and concise CV generation.
- `css/style.css`, `responsive.css`, `print.css`: portfolio visual system.
- `css/cv.css`: independent one-page CV typography and A4 print rules.
- `js/main.js`: accessible mobile menu, project filters, navigation state.
- `assets/images/portrait.jpg`: retained personal portrait.
- `assets/qr/`: generated PNG/SVG QR.
- `assets/cv/CV.pdf`: final downloadable PDF.
- `validation/`: screenshots, PDF text, test report and page previews.
- `FACTS_TO_VERIFY.md`: owner review notes; intentionally not displayed in public portfolio cards.

## Update / regenerate

Edit `CvWebsite/data/profile.json`, not generated HTML. The professional email is `sbissi.mohamed@esprit.tn`.

From the project root:

```powershell
python CvWebsite/scripts/build.py --pdf
python CvWebsite/scripts/validate.py
```

Fresh setup uses `python -m pip install -r CvWebsite/requirements-build.txt` and `python -m playwright install chromium`. Existing workspace-local QR packages in the parent `.build-tools` are supported. No libraries are loaded by the website at runtime.

The build refuses to save a PDF unless page count equals **1** and key text is extractable. CV body is 9.5pt, with 10mm margins and a small 18mm QR. Compact section headings and selective content keep the PDF readable without shrinking the whole document.

## ODDO technology levels

`experience[id=oddo].stack` describes main implementation tools. `environment` lists categorized exposure, with no assertion of implementation ownership or deep proficiency. The PDF includes only Apache Kafka and OpenShift under an explicitly labeled environment exposure line. Node.js, WebSockets, Spring Batch, Camunda, Helm, Nginx, Keycloak, ELK and bot-related integration remain in the richer portfolio exposure panel.

The journal documents introductory OpenShift practical work; Camunda is also mentioned as future industrialization work. These do not prove ownership of enterprise infrastructure or workflows. Additional exposure comes from the user's update.

## QR / deploy

`personal.portfolio` retains the verified https://mohasbissi01.github.io/cv/ URL. Change it only when a replacement deployment URL is confirmed, then rebuild PDF and QR together. Publish the **contents** of CvWebsite to the existing `/cv/` site, not an extra nested folder unless you intentionally change the configured URL.

Deploy `index.html`, `cv.html`, `css/`, `js/`, `assets/`. The JSON/build tools/owner documents need not be publicly served. No deployment has been performed. Open Graph and canonical metadata use the configured portfolio URL; its updated image will be available after deployment.

## PDF editing choices

The CV keeps ODDO's three strongest bullets, two Ooredoo bullets, GreenOPS's award and verified data contribution, two Urban Mobility bullets, one business ML line, four skill rows, ESPRIT, two relevant certifications, and a language line. Recordati, Tunisie Telecom, EduTechHub, secondary education, other certificates, full team stack, and longer workflow details stay on the website.

Unknown competition dates, unconfirmed award details, and private author-review notes are omitted from public UI rather than rendered as placeholders. See `FACTS_TO_VERIFY.md` and `CHANGELOG.md`.

## Verification

`scripts/validate.py` checks preserved original file hashes, shared profile facts and email, HTML IDs/assets/anchors, heading hierarchy, public placeholder absence, ODDO's distinct tool levels, responsive widths, keyboard menu behavior, filter state, no-JS content, reduced-motion behavior, real PDF download, exact A4 page count, clickable PDF links, selectable text order, word bounds/overlap, and QR round-trip decoding. Original website integrity is checked against `docs/original-version-hashes.json`.

Live LinkedIn checks may return HTTP 999; URL is from the supplied profile. EduTechHub's unavailable repository is not shown as a working link.
