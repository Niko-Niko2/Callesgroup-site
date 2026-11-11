# Calles Group website

The live site is https://www.callesgroup.com, a Wix headless static site (site ID 95f7b2da-02f4-4d86-b63c-1c979194352b). This repo holds every file, and `main` should always match what is live.

The pages are plain HTML, one stylesheet (`assets/styles.css`) and one small script (`assets/site.js`). There's no framework and nothing builds at runtime. Every page reads fine with JavaScript off.

## The one rule: prices live in one file

Every price, package, feature, care plan, extra, policy and FAQ answer lives in **`data/offers.json`**. The pages are generated from it by **`tools/build.py`**. Don't edit the `.html` files in the root by hand, because the next build overwrites them.

```
data/offers.json     prices, packages, care plans, extras, policies, FAQs, service area, on/off flags
src/*.html           the words on each page, with {{tokens}} that pull from offers.json
partials/*.html      header, footer, page head, closing call-to-action band, before/after slider
tools/build.py       builds all pages + sitemap.xml + site-pages.xml
tools/towns.py       the local copy for each town page
tools/og-image.html  source for og-image.png (the link preview image)
assets/styles.css    all styles; colors are tokens at the top of the file
assets/site.js       menu, switches, accordions, swipe dots, before/after slider, scroll fades
```

Build (needs Python 3, nothing to install):

```
python3 tools/build.py
```

## How to change a price

1. Open `data/offers.json` and change the number. For example, Growth: find `"key": "growth"` and change `"price": 2500`.
2. If the number is also written out in sentences, search for it and update it too. These are the only places it appears in plain text:
   - `faqs`, `policies`, `founding`, `brandingNote` and `photosNote` in `offers.json`
   - page titles and descriptions at the top of each `src/*.html` file, and the town copy in `tools/towns.py`
   - `tools/og-image.html` ("Websites from $1,500")
   Quick check: `grep -rn '\$2,500' src partials tools data`
3. Run `python3 tools/build.py`, look at the page, then commit and publish.

The cards, care plan cards, "from" prices, quote form pre-fill and structured data all update on their own.

## Turning on online booking or payments

Both are switched off in `data/offers.json`:

```json
"flags": { "bookingLive": false, "paymentsLive": false }
```

- **Booking**: once Wix Bookings has the "Free quote call" service (20 minutes, in person or video), set `"bookingLive": true` and rebuild. The contact page's "Book a call" side then shows the mount `<div id="wix-booking-mount">` in place of the "coming soon" box. Install the Wix Bookings widget into that div.
- **Payments**: once there's a Wix Payments pay button or payment link, set `"paymentsLive": true` and rebuild. `pay-deposit.html` then shows `<div id="wix-payment-mount">` in place of the card / Zelle / check instructions. Put the button or link inside it (edit `t_payment()` in `tools/build.py` if it's a plain link).

## The quote form

The form is the existing Wix Form `8b564ebe-a6cc-4e87-8255-c3ebdfde4c20`. `/js/wix/form-renderer.js` (in this repo) renders it, and `contact.html` mounts the form in `<div id="quote">`. Don't rebuild the form here.

Links like `/contact.html?need=growth` pre-tick the form's "What do you need?" boxes (Website, Logo or branding, Care plan, Not sure yet) and write the choice into the message box. The list of keys is built from `offers.json` (`t_needs()` in `tools/build.py`): every package, branding and care plan key, plus `care`, `founding` and `unsure`. If you rename an option in the Wix form, update `t_needs()` to match.

After sending, the visitor goes to `/thank-you.html`.

## How to add a town page

1. In `tools/towns.py`, copy one town entry and rewrite **every** line for the new town: title, description, H1, lead, the two reasons, the business list and 3 FAQs. Google treats pages that just swap the town name as doorway pages, so the copy has to be about that town.
2. In `data/offers.json`, under `serviceArea.towns`, add `"page": "web-design-<slug>.html"` to the town (or add the town).
3. Run `python3 tools/build.py`. The page, footer links, "Also serving nearby" chips, home page chips and both sitemaps all update.

## Changing colors

All colors are the tokens at the top of `assets/styles.css` (`--bg`, `--surface`, `--line`, `--ink`, `--muted`, `--accent`, `--accent-hover`, `--on-accent`). Change them there and nothing else needs to change. Keep body text at 4.5:1 contrast or better. The current palette is "Daylight": warm white `#FAF8F4`, ink `#1A1A1A`, forest green `#2F6B4F`. Also update `theme-color` in `partials/head.html`, `favicon.svg` and `tools/og-image.html`.

## Publishing

The site is hosted on GitHub Pages (deploy from `main`, root folder; custom domain in `CNAME`). DNS stays at Wix: `callesgroup.com` A records point to GitHub Pages and `www` is a CNAME to `niko-niko2.github.io`. Every push to `main` goes live.

1. `python3 tools/build.py`
2. Check it locally: `python3 -m http.server 8765`, then open http://localhost:8765 at phone and desktop widths.
3. Commit and push to `main`. GitHub Pages deploys it in about a minute.

`.assetsignore` keeps `src/`, `partials/`, `tools/`, `data/`, `README.md` and `palette-preview.html` off the public site. `html_handling: "none"` keeps every URL ending in `.html`.

Wix still runs the quote form, bookings and invoices. `js/wix/` holds Wix's form scripts, unchanged (`config.js` holds the site's public client ID). Don't edit them.

`sitemap.xml` and `site-pages.xml` are always identical. `site-pages.xml` is the one submitted to Google Search Console. Keep the `google-site-verification` meta tag on the home page (it's in `tools/build.py`).

## Hidden slots

- **Proof / reviews**: `src/index.html` has a `<section id="proof" hidden>`. Add real reviews or client work, remove `hidden`, rebuild.
- Don't add testimonials, ratings, client logos or portfolio items until they're real.

## Animation rules

Everything runs on transform and opacity, takes 150 to 450ms and uses one easing, `cubic-bezier(.2,.7,.2,1)` (`--ease`). With "reduce motion" turned on, everything appears instantly. There's no parallax, autoplay, looping or scroll-jacking.
