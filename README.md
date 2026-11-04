# Calles Group Website

The live site is hosted on Wix (headless site "Calles Group", site ID 26a9ed6b-069a-439d-bf8c-4c4a64176f46).
This repo is the backup: every change to the live site is committed here first, so any commit is a restore point.

## How changes work
1. Claude edits `index.html` here and commits it (one commit per change, with a plain-English message).
2. Claude uploads the same file to the Wix site.
3. To go back: pick any commit in this repo's history and ask Claude to restore it. That version is re-uploaded to Wix.

## What's in the site
- `index.html`: the whole site. Pages switch by link: #home, #pricing, #faq, #contact, plus #bundle-launch, #bundle-growth, #bundle-premium.
- The quote form is a Wix Form ("Quote request", ID c2ac0265-7048-492b-91ae-4718707d2a22). Its code (`/js/wix/*`) is installed on Wix by Wix's own module installer and is not stored here.
- Wix adds its own `wix-site-script` tag to the page on upload; that tag is not stored here.

## Still to do
- Add a phone number (tap-to-call) once there's a business line.
- Move callesgroup.com and the Premium plan to this site.
