#!/usr/bin/env python3
"""Builds every page of callesgroup.com.

  python3 tools/build.py

Inputs
  data/offers.json   every price, package, plan, extra, policy and FAQ (the one source of truth)
  partials/*.html    head, header, footer and the closing call-to-action band
  src/*.html         the copy for each page, with {{tokens}} that pull from offers.json
  tools/towns.py     the local copy for each town page

Output: finished .html files in the repo root, plus sitemap.xml and site-pages.xml.

Each src file starts with a meta comment:
  <!--meta {"title": "...", "description": "...", "nav": "home", "index": true, "schema": ["business"]} -->

Tokens look like {{name}} or {{name arg arg}}. See TOKENS at the bottom of this file.
"""
import datetime
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
D = json.load(open(os.path.join(ROOT, "data", "offers.json"), encoding="utf-8"))
B = D["business"]
BASE = B["siteUrl"]
FLAGS = D["flags"]
esc = html.escape


def part(name):
    return open(os.path.join(ROOT, "partials", name + ".html"), encoding="utf-8").read()


def fill(t, values):
    return re.sub(r"\{\{(\w+)\}\}", lambda m: str(values.get(m.group(1), m.group(0))), t)


def money(n):
    return "${:,}".format(n)


def find(lst, key):
    for x in lst:
        if x["key"] == key:
            return x
    raise KeyError(key)


COMMON = {"phone": B["phoneDisplay"], "phoneHref": B["phoneHref"], "email": B["email"],
          "replyTime": B["replyTime"], "tagline": B["tagline"], "base": BASE}

NAV = [("home", "/", "Home"), ("pricing", "/pricing.html", "Website Packages"),
       ("care", "/care-plans.html", "Care Plans"), ("faq", "/faq.html", "FAQ"), ("contact", "/contact.html", "Contact")]


# ---------- shared pieces ----------

def chev():
    return '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>'


def tick_list(items):
    return '<ul class="ticks">' + "".join("<li>%s</li>" % esc(i) for i in items) + "</ul>"


def accordion(items, cls=""):
    """items: list of (id, question, answer_html). Works with JS off (all open)."""
    out = ['<div class="acc %s">' % cls]
    for i, q, a in items:
        out.append(
            '<div class="acc-item"><h3><button type="button" class="acc-btn" aria-expanded="false" aria-controls="a-%s" id="q-%s">%s%s</button></h3>'
            '<div class="acc-body" id="a-%s" role="region" aria-labelledby="q-%s"><div><div class="acc-in">%s</div></div></div></div>'
            % (i, i, esc(q), chev(), i, i, a))
    out.append("</div>")
    return "".join(out)


def faq_items(ids=None, group=None):
    fs = D["faqs"]
    if ids:
        fs = [next(f for f in fs if f["id"] == i) for i in ids]
    if group:
        fs = [f for f in fs if f["group"] == group]
    return fs


def swipe_dots(n, label):
    return '<div class="dots" aria-hidden="true">' + "<i></i>" * n + '</div>'


# ---------- tokens ----------

def t_price(key):
    for lst in (D["packages"], D["bundles"]):
        for x in lst:
            if x["key"] == key:
                return money(x["price"])
    p = find(D["carePlans"], key)
    return money(p["monthly"])


def t_from(what):
    if what == "websites":
        return money(min(p["price"] for p in D["packages"]))
    if what == "bundles":
        return money(min(p["price"] for p in D["bundles"]))
    if what == "care":
        return money(min(p["monthly"] for p in D["carePlans"]))
    raise KeyError(what)


def t_faq(*ids):
    return accordion([(f["id"], f["q"], "<p>%s</p>" % esc(f["a"])) for f in faq_items(ids=ids)])


def t_towns():
    chips = []
    for t in D["serviceArea"]["towns"]:
        if t.get("page"):
            chips.append('<a class="chip" href="/%s">%s</a>' % (t["page"], esc(t["name"])))
        else:
            chips.append('<span class="chip">%s</span>' % esc(t["name"]))
    return '<div class="chips">' + "".join(chips) + "</div>"


def t_cta(title, text):
    return fill(part("cta"), dict(COMMON, cta_title=title, cta_text=text))


TOKENS = {
    "price": t_price,      # {{price growth}}     -> $2,500
    "from": t_from,        # {{from websites}}    -> $1,500
    "faq": t_faq,          # {{faq own-site time-how}}
    "towns": t_towns,      # {{towns}}            -> service area chips
    "phone": lambda: '<a href="%s">%s</a>' % (B["phoneHref"], B["phoneDisplay"]),
    "email": lambda: '<a href="mailto:%s">%s</a>' % (B["email"], B["email"]),
    "reply": lambda: B["replyTime"],
    "partial": lambda name: part(name),  # {{partial before-after}}
}


def expand(body):
    def rep(m):
        parts = m.group(1).split()
        fn = TOKENS.get(parts[0])
        if not fn:
            raise SystemExit("Unknown token {{%s}}" % m.group(1))
        return fn(*parts[1:])
    body = re.sub(r"\{\{([a-z][\w -]*?)\}\}", rep, body)
    # {{cta Title | Text}} runs last: its arguments contain spaces, HTML and other tokens.
    return re.sub(r"\{\{cta (.+?) \| (.+?)\}\}", lambda m: t_cta(m.group(1), m.group(2)), body, flags=re.S)


# ---------- structured data ----------

def schema_business():
    return {
        "@context": "https://schema.org", "@type": "ProfessionalService", "@id": BASE + "/#business",
        "name": B["name"], "url": BASE + "/", "telephone": "+1-312-600-0590", "email": B["email"],
        "image": BASE + "/og-image.png",
        "founder": {"@type": "Person", "name": B["owner"]},
        "address": {"@type": "PostalAddress", "addressLocality": B["city"], "addressRegion": B["state"], "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": t["name"] + ", IL"} for t in D["serviceArea"]["towns"]],
        "description": "Website design and branding for local businesses in Elgin, the Fox Valley, the northwest suburbs and Chicago.",
    }


def schema_faq(fs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fs]}


def schema_crumbs(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(trail)]}


def jsonld(objs):
    return "".join('<script type="application/ld+json">%s</script>\n' % json.dumps(o, ensure_ascii=False, separators=(",", ":")) for o in objs)


# ---------- page assembly ----------

def render(slug, meta, body, schemas=()):
    url = BASE + ("/" if slug == "index" else "/%s.html" % slug)
    navlinks = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if meta.get("nav") == k else "", n) for k, h, n in NAV)
    foot = "".join('<a href="%s">%s</a>' % (h, n) for k, h, n in NAV) + '<a href="/pay-deposit.html">Pay your deposit</a>'
    towns = "".join('<a href="/%s">Web design %s</a>' % (t["page"], esc(t["name"])) for t in D["serviceArea"]["towns"] if t.get("page"))
    head = fill(part("head"), dict(COMMON,
        title=esc(meta["title"]), description=esc(meta["description"]), url=url,
        robots="index, follow" if meta.get("index", True) else "noindex, follow",
        verify='<meta name="google-site-verification" content="ADdwPb9axnmWCbzpY3gyaaUnq09scu5mJBVPGQg933g">\n' if slug == "index" else "",
        jsonld=jsonld(schemas)))
    out = head + fill(part("header"), dict(COMMON, navlinks=navlinks)) + body.strip() + "\n" + \
        fill(part("footer"), dict(COMMON, footlinks=foot, townlinks=towns, year=datetime.date.today().year, scripts=meta.get("scripts", "")))
    open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8").write(out)
    return url if meta.get("index", True) else None


def build_src():
    urls = []
    for fn in sorted(os.listdir(os.path.join(ROOT, "src"))):
        if not fn.endswith(".html"):
            continue
        slug = fn[:-5]
        raw = open(os.path.join(ROOT, "src", fn), encoding="utf-8").read()
        m = re.match(r"\s*<!--meta (.+?)-->", raw, re.S)
        meta = json.loads(m.group(1))
        body = expand(raw[m.end():])
        schemas = []
        for s in meta.get("schema", []):
            if s == "business":
                schemas.append(schema_business())
            elif s.startswith("faq:"):
                fs = faq_items(group=s[4:]) if s[4:] != "all" else D["faqs"]
                schemas.append(schema_faq([(f["q"], f["a"]) for f in fs]))
        if meta.get("crumb"):
            schemas.append(schema_crumbs([("Home", "/"), (meta["crumb"], "/%s.html" % slug)]))
        u = render(slug, meta, body, schemas)
        if u:
            urls.append(u)
        print("built", slug + ".html")
    return urls


def sitemap(urls):
    today = datetime.date.today().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
        "".join("  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (u, today) for u in urls) + "</urlset>\n"
    for f in ("sitemap.xml", "site-pages.xml"):
        open(os.path.join(ROOT, f), "w", encoding="utf-8").write(xml)


if __name__ == "__main__":
    urls = build_src()
    sitemap(sorted(urls, key=lambda u: (u != BASE + "/", u)))
    print("sitemap.xml and site-pages.xml:", len(urls), "pages")
