# CV-2 changes

CV-2 was created as a separate one-page variant, initially preserving the entire website. After the user's validation (reported score: 88), it became the default portfolio download. The earlier CV.pdf, printable source (cv-v1.html) and profile (data/archive/profile-v1.json) remain preserved.

- Made ODDO scope explicit: 12 HR domains, 7 SQL views, 4 report pages, 25 DAX measures and 10 authenticated analytics endpoints. All figures come from the internship journal; none is a made-up impact percentage.
- Kept Ooredoo's value grounded in contract/service KPI visibility and data consolidation. No data-volume, latency or time-saving figures were available.
- Added explicit intended decision value to Urban Mobility and business ML, without claiming adoption or taking ownership of the entire team platform.
- Standardized every experience/project bullet to start with a past-tense action verb. Retained conservative 'Contributed' wording where exclusive authorship is unconfirmed.
- Split skills into Data & BI, ML & Programming, Application Engineering, Cloud & DevOps coursework, and ERP & SAP coursework.
- Kept Kafka/OpenShift as environment exposure, SAP/cloud as coursework, and GreenOPS tools undisclosed under NDA.
- No new PFE job posting was provided. Existing verified keywords are used; Airflow, Spark, Azure and other posting examples are not added as skills without evidence.
- The user reported an external score of 88. No independent score or hiring outcome is promised.

## Files

- Final PDF: assets/cv/CV-2.pdf
- Editable variant content: data/cv-2.json
- Printable source: cv-2.html
- Regenerate from project root: python CvWebsite/scripts/build_cv2.py
- Verification and preview: validation/cv-2/

The CV-2 generator reads the current profile and applies the concise variant overrides. It never overwrites CV.pdf. The main website build uses CV-2 as the default and keeps cv.html aligned with cv-2.html.
