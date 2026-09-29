# GitHub Pages + private analytics backend

Keep the portfolio on GitHub Pages. This folder supplies a separate Cloudflare Worker, D1 database and private dashboard. **It is not deployed.** The public portfolio ships with collection disabled. Do not publish a dashboard secret in source or a URL.

## What is measured

Only after explicit optional consent: a random per-tab visit code, server timestamps, allowlisted interaction events and approximate foreground active milliseconds. The clock pauses in hidden tabs and after 60 seconds idle. Events can be missed by blockers, offline navigation or browser shutdown. A click is not proof of a completed CV download, saved contact, sent email or shared link. These are visit sessions, not verified people. The database contains no names, email addresses, IPs, browser fingerprints, device identifiers or full URLs/referrers.

Rejecting consent leaves all portfolio features usable. A footer control allows withdrawal or deletion. GPC and DNT disable analytics. Event records expire after 30 days; inactive visits expire 30 days after their last update. After deletion, the random visit code is retained in an erasure blocklist for up to 30 days to prevent delayed requests recreating the record. Hosting providers process network traffic separately under their terms.

## Before live activation

1. Sign in to your Cloudflare account; choose the Workers Free plan and check current service limits and terms. Do not enable paid upgrades automatically.
2. Review the public `privacy.html`, controller contact, hosting region/data-transfer requirements and applicable privacy rules. Consent alone does not certify legal compliance in every jurisdiction.
3. In this folder, run `npx wrangler login --device --use-keyring --scopes account:read workers:write workers_scripts:write d1:write` and `npx wrangler d1 create portfolio-analytics`. Put the returned database ID in `wrangler.jsonc`, replacing the all-zero placeholder. Choose an appropriate database location during creation.
4. Run `npx wrangler d1 execute portfolio-analytics --remote --file schema.sql`.
5. Generate a random private token (at least 32 characters), keep it in a password manager, and run `npx wrangler secret put ADMIN_TOKEN`. Enter it at the prompt. Never add it to GitHub, the frontend, screenshots or query parameters.
6. Run `npx wrangler deploy`. Open the deployed Worker URL for your private dashboard and unlock it with the token. The dashboard uses a Bearer credential kept only in memory and clears it at logout. Its APIs deny unauthorized access. Add Cloudflare Access/WAF controls and rate limits for stronger public-service abuse protection.
7. From the parent workspace, run `python CvWebsite/scripts/configure_analytics.py https://YOUR-DEPLOYED-WORKER.workers.dev`. This public URL is not a secret. Publish the updated `js/analytics-config.js` along with the site assets to GitHub Pages.
8. Verify from a fresh browser: decline → no collector requests; allow → a visit appears; withdraw → no further collection; delete → the record disappears. Check your real iPhone/Android contact import too.

The allowed public origin is exactly `https://mohasbissi01.github.io`; no wildcard CORS. If your portfolio domain changes, update `PORTFOLIO_ORIGIN` in the Worker. API request bodies are bounded, validated and limited to known actions. Credentials never cross to the public site. The dashboard renders database values as text. A nightly scheduled job prunes old records. Disable collection immediately by restoring `window.MS_ANALYTICS={enabled:false,endpoint:""};` in the public config, and remove stored data separately if needed.

## Tests / local preview

`node CvWebsite/analytics/test-worker.mjs` uses Node 22's in-memory SQLite to test the actual SQL and handler: CORS, consent, input bounds, deduplication, authorization, erasure and retention. No production credentials or visitor data are used.

For a full local Worker preview, use `npx wrangler d1 execute portfolio-analytics --local --file schema.sql`, put a **local-only** ADMIN_TOKEN in ignored `.dev.vars`, then `npx wrangler dev`. Do not expose a development server publicly. The static site does not send telemetry to HTTP localhost; browser validation mocks an HTTPS collector to exercise consent and timing without uploading data.

## References

- [Cloudflare D1 pricing](https://developers.cloudflare.com/d1/platform/pricing/)
- [Worker secret configuration](https://developers.cloudflare.com/workers/configuration/secrets/)
- [CNIL tracker consent principles](https://www.cnil.fr/fr/cookies-et-autres-traceurs/que-dit-la-loi)
- [Web Share specification](https://www.w3.org/TR/web-share/)
- [Apple vCard import](https://support.apple.com/en-euro/guide/iphone/iph356499f31/ios)
- [Google Contacts VCF import](https://support.google.com/contacts/answer/15147365?co=GENIE.Platform%3DAndroid&hl=en-uk)
