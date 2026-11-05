# Calles Group Website

The live site is https://www.callesgroup.com, hosted on Wix (Premium site "Calles Group", site ID 95f7b2da-02f4-4d86-b63c-1c979194352b). It moved there from the headless test site 26a9ed6b-069a-439d-bf8c-4c4a64176f46 on November 4, 2026. The site's form code lives in js/wix/ on Wix and is not stored here.
This repo is the backup: every change to the live site is committed here first, so any commit is a restore point.

## How changes work
1. Claude edits the files here and commits them (one commit per change, with a plain-English message).
2. Claude uploads the same files to the Wix site.
3. To go back: pick any commit in this repo's history and ask Claude to restore it. That version is re-uploaded to Wix.

## Pages
| File | Page |
| --- | --- |
| `index.html` | Home |
| `pricing.html` | Packages (menu label; was Services & Pricing) (sections: #websites, #bundles, #branding, #addons, #care) |
| `custom-merchandise.html` | Print & Signs (menu label; was Custom Merchandise): starter packs and print products (sections: #packs, #how, #products, #faq). Testimonials section is hidden until real quotes are added. |
| `faq.html` | FAQ |
| `contact.html` | Get a free quote (Wix Form "Quote request", ID 8b564ebe-a6cc-4e87-8255-c3ebdfde4c20) |
| `launch-bundle.html`, `growth-bundle.html`, `premium-bundle.html` | Bundle detail pages |

Shared files: `styles.css`, `site.js` (menu, add-on accordions, old `/#page` link redirects), `favicon.svg`, `og-image.png` (link preview image), `robots.txt`, `sitemap.xml`.

## SEO
- Each page has its own title, meta description, canonical URL, Open Graph tags and one H1.
- Structured data: ProfessionalService on Home, FAQPage on FAQ, BreadcrumbList on bundle pages.
- Canonical URLs, sitemap and share image use https://www.callesgroup.com. They are correct once the domain is moved to this site.

## Not stored here
- The Wix form code (`/js/wix/*`) is installed on Wix by Wix's own module installer.
- Wix adds its own `wix-site-script` tag to each page on upload.

## Tools
- `tools/build-pages.py`: how these pages were generated from the earlier one-page site (kept for reference).
- `tools/og-image.html`: source for `og-image.png` (1200x630).

## Still to do
- Add a phone number (tap-to-call) once there's a business line.
- Quote form (Wix form 8b564ebe…): 3 steps. 1) What do you need? (required), budget. 2) Business type, current website, logo. 3) Name, business name, email, phone, message. The plan caps forms at 10 fields, so start date, "how did you hear about us" and best way to reach were left out; a Core plan or higher would allow more fields and a file upload.
- Move callesgroup.com and the Premium plan to this site, then submit the sitemap in Google Search Console.
