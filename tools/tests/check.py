#!/usr/bin/env python3
"""Site checks: internal links and anchors, titles and descriptions, structured data, prices against offers.json."""
import json, os, re, sys, html
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = json.load(open(os.path.join(ROOT, "data/offers.json"), encoding="utf-8"))
pages = sorted(f for f in os.listdir(ROOT) if f.endswith(".html") and f != "palette-preview.html")
ids = {}; bad = []; notes = []
for f in pages:
    t = open(os.path.join(ROOT, f), encoding="utf-8").read()
    ids[f] = set(re.findall(r'\sid="([^"]+)"', t))
for f in pages:
    t = open(os.path.join(ROOT, f), encoding="utf-8").read()
    if "{{" in re.sub(r"<script[\s\S]*?</script>", "", t): bad.append((f, "unfilled token"))
    if f.endswith("-bundle.html"): continue
    title = re.search(r"<title>(.*?)</title>", t).group(1); desc = re.search(r'name="description" content="(.*?)"', t).group(1)
    title, desc = html.unescape(title), html.unescape(desc)
    if len(title) > 62: notes.append((f, "title %d chars" % len(title)))
    if len(desc) > 160: notes.append((f, "description %d chars" % len(desc)))
    if len(re.findall(r"<h1[ >]", t)) != 1: bad.append((f, "h1 count %d" % len(re.findall(r"<h1[ >]", t))))
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try: json.loads(m.group(1))
        except Exception as e: bad.append((f, "bad JSON-LD %s" % e))
    for href in re.findall(r'(?:href|src)="([^"]+)"', t):
        if href.startswith(("http", "mailto:", "tel:", "sms:", "data:")): continue
        path, _, frag = href.partition("#"); path = path.split("?")[0]
        if path in ("", "/"): target = "index.html" if path == "/" else f
        else: target = path.lstrip("/")
        if not os.path.exists(os.path.join(ROOT, target)): bad.append((f, "missing " + href)); continue
        if frag and target.endswith(".html") and frag not in ids.get(target, ()) and frag not in ("yearly",):
            bad.append((f, "missing anchor " + href))
    for a in re.findall(r"<a [^>]*>", t):
        if "href=" not in a: bad.append((f, "anchor without href"))
    for i in re.findall(r"<(?:input|select|textarea)[^>]*>", t):
        if 'type="range"' in i and "aria-label" not in i and not re.search(r'id="([^"]+)"', i): bad.append((f, "unlabeled control"))
# prices on the home pages must be the ones in offers.json
for f in ("index.html", "es.html", "pricing.html"):
    t = open(os.path.join(ROOT, f), encoding="utf-8").read()
    for p in D["packages"]:
        if "${:,}".format(p["price"]) not in t: bad.append((f, "price missing for " + p["key"]))
sm = open(os.path.join(ROOT, "sitemap.xml")).read(); print("sitemap urls:", sm.count("<loc>"), "es in sitemap:", "es.html" in sm, "identical twins:", sm == open(os.path.join(ROOT, "site-pages.xml")).read())
print("pages checked:", len(pages)); print("PROBLEMS:", bad or "none"); print("notes:", notes or "none")
