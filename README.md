# Calles Group website

The live site is https://www.callesgroup.com, a Wix headless static site (site ID 95f7b2da-02f4-4d86-b63c-1c979194352b). This repo holds every file, and `main` should always match what is live.

The pages are plain HTML, one stylesheet (`assets/styles.css`) and two small scripts (`assets/site.js` for menus and switches, `assets/tools.js` for the selling tools). There's no framework and nothing builds at runtime. Every page reads fine with JavaScript off.

**This branch (`v2-estimate`) is the staged redesign. Nothing here is live until it is merged into `main`.**

## The one rule: prices live in one file

Every price, package, feature, care plan, extra, policy and FAQ answer lives in **`data/offers.json`**. The pages are generated from it by **`tools/build.py`**. Don't edit the `.html` files in the root by hand, because the next build overwrites them.

```
data/offers.json     prices, packages, care plans, extras, policies, FAQs, service area, on/off flags
src/*.html           the words on each page, with {{tokens}} that pull from offers.json (src/es.html is the Spanish page)
partials/*.html      header, footer, page head, closing call-to-action band, before/after slider
tools/build.py       builds all pages + sitemap.xml + site-pages.xml
tools/towns.py       the local copy for each town page
tools/og-image.html  source for og-image.png (the link preview image)
assets/styles.css    all styles; colors are tokens at the top of the file
assets/site.js       menu, switches, accordions, swipe dots
assets/tools.js      the sample site in the phone, the what-if calculator, pitch links and the call request
assets/fonts/        the typeface (Montserrat, SIL Open Font License), hosted here
```

Build (needs Python 3, nothing to install):

```
python3 tools/build.py
```

## How the packages are organized

Every website package in `offers.json` carries the same facts in the same order: `pages`, `timeline`, `rounds` (of changes), then `includes` (what it adds) and `buildsOn` (the package below it). The package cards on `pricing.html` show those three rows identically on every card, then "What's included", so the three compare at a glance. The home page lists prices in three groups: Websites, Add-ons, Monthly care.

## How to change a price

1. Open `data/offers.json` and change the number. For example, Growth: find `"key": "growth"` and change `"price": 2500`.
2. If the number is also written out in sentences, search for it and update it too. These are the only places it appears in plain text:
   - `faqs`, `policies`, `founding`, `brandingNote` and `photosNote` in `offers.json`, and their Spanish twins (`es` inside packages, FAQs and `founding`, plus `brandingNote_es`)
   - page titles and descriptions at the top of each `src/*.html` file, and the town copy in `tools/towns.py`
   - `tools/og-image.html` ("Websites from $1,500")
   - the founding rate is also the number `founding.price` (it feeds the deposit table), so change both it and the sentence
   Quick check: `grep -rn '\$2,500' src partials tools data`
3. Run `python3 tools/build.py`, look at the page, then commit and publish.

The cards, care plan cards, "from" prices, quote form pre-fill and structured data all update on their own.

## Booking and payments

- **Booking** works today without any setup. On `contact.html` (and on the Spanish page) the visitor picks a day and one of Andrew's call times, then taps "Text Andrew this time" (opens their messages app with the request written out) or "Have Andrew call me" (opens the quote form with the time already in the message box). Andrew confirms by text.
  The call times are `business.booking.hours` in `data/offers.json`: the hours a call can start, on a 24-hour clock, for weekdays and for weekends (today: weekdays 18, 19, 20 and weekends 15 to 20). Change the sentence in `hoursNote` and `hoursNote_es` to match.
  To add a real calendar, paste a booking link (a Google Calendar appointment schedule or a Wix Bookings page) into `business.booking.url` in `data/offers.json` and rebuild. A "See open times" button then shows above the request.
- **Payments**: `policies.payment.methods` lists what Andrew takes today (Zelle, cash) and `policies.payment.soon` is the card-payments line. The same facts are written out in the `pay-how` FAQ answer, in English and Spanish. Online payment is switched off (`"flags": { "paymentsLive": false }`). Once there's a pay button or payment link, set it to `true` and rebuild. `pay-deposit.html` then shows `<div id="wix-payment-mount">` in place of the card / Zelle / check instructions. Put the button or link inside it (edit `t_payment()` in `tools/build.py` if it's a plain link).

## The selling tools on the home page

All three run in the visitor's browser (`assets/tools.js`). Nothing they type is sent anywhere unless they tap a text or call button.

- **The sample site.** The visitor types their business name on the estimate, picks a trade and a town, and the phone shows a sample home page with their name on it. The sample never shows invented reviews, photos or credentials: those spots say "Your job photos go here" and "Your Google reviews show here".
- **The what-if calculator.** Average job, estimates won out of 10, and extra calls a month give a yearly figure and how fast each package would be paid back. Every number is the visitor's own. The average job starts as a guess per trade (the `TRADES` list at the top of `tools.js`) and the page says to replace it. Package prices come from `offers.json`, never from the script. Keep the "not a promise" line under the result.
- **Pitch links.** Add the owner's details to the home page address and it opens already filled in, with a hello by name:

  ```
  https://www.callesgroup.com/?b=Garcia+Roofing&t=roofing&c=Elgin
  https://www.callesgroup.com/es.html?b=Techos+Garc%C3%ADa&t=roofing&c=Elgin
  ```

  `b` business name, `t` trade (roofing hvac plumbing remodeling electrical landscaping painting concrete detailing washing other), `c` town, `p` sample colors (0 white and gold, 1 graphite and copper, 2 midnight and gold, 3 forest and sage). Add `#worth` to land on the calculator.

## The Spanish page

`src/es.html` builds `es.html`, one complete page in Spanish: the sample, the calculator, prices, the call request and three FAQs. Its Spanish prices and policy sentences live in `offers.json` next to the English ones (`es` inside each package, `founding.es`, `brandingNote_es`, and `es` inside the three FAQs it shows), so a price change is still made in one file. The English home page and the Spanish page point at each other with `hreflang` tags. Interface words (menu, buttons) for both languages are in `STR` at the top of `tools/build.py`.

## The quote form

The form is the existing Wix Form `8b564ebe-a6cc-4e87-8255-c3ebdfde4c20`. `/js/wix/form-renderer.js` (in this repo) renders it, and `contact.html` mounts the form in `<div id="quote">`. Don't rebuild the form here.

Links like `/contact.html?need=growth` pre-tick the form's "What do you need?" boxes (Website, Logo or branding, Care plan, Not sure yet) and write the choice into the message box. The list of keys is built from `offers.json` (`t_needs()` in `tools/build.py`): every package, branding and care plan key, plus `care`, `founding` and `unsure`. If you rename an option in the Wix form, update `t_needs()` to match.

After sending, the visitor goes to `/thank-you.html`.

## How to add a town page

1. In `tools/towns.py`, copy one town entry and rewrite **every** line for the new town: title, description, H1, lead, the two reasons, the business list and 3 FAQs. Google treats pages that just swap the town name as doorway pages, so the copy has to be about that town.
2. In `data/offers.json`, under `serviceArea.towns`, add `"page": "web-design-<slug>.html"` to the town (or add the town).
3. Run `python3 tools/build.py`. The page, footer links, "Also serving nearby" chips, home page chips and both sitemaps all update.

## The look: Graphite & Gold

Andrew's graphite background, off-white text and **one** accent, gold. Gold is only for what can be tapped and for the number that matters (a price that is due, the calculator's total). Everything else stays neutral, with hairlines instead of boxes and plenty of room between sections. If a page starts to feel busy, take something away before adding a color.

All colors are the tokens at the top of `assets/styles.css`: `--bg` (#151515), `--band`, `--surface`, `--field`, `--line`, `--line-2`, `--ink`, `--muted`, `--accent` (#C9A962), `--accent-hover`, `--on-accent`. Keep body text at 4.5:1 contrast or better. If the graphite or gold changes, also update `theme-color` in `partials/head.html`, `favicon.svg` and `tools/og-image.html`.

One typeface, Montserrat, hosted on the site (`assets/fonts/montserrat.woff2`). No script or handwriting faces: everything a visitor types or reads is set in the same plain face. Headings are set as one piece, with no accented last phrase.

The sample site inside the phone has its own colors on purpose, because it stands for the visitor's site. Its four palettes are in `styles.css` under `.ps`.

To redraw the link preview image, open `tools/og-image.html` at 1200 by 630 in a headless browser and save a screenshot as `og-image.png`.

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

Motion only answers something the visitor did (a switch, an accordion, a button press, the sample changing trade). The one exception is the handwritten hello on a pitch link. Sections do not fade in on scroll. Everything uses one easing, `cubic-bezier(.2,.7,.2,1)` (`--ease`), and with "reduce motion" turned on everything appears instantly.
