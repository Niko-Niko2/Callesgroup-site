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


def swipe_dots(n):
    """Dots under a swipe row. Rendered in the HTML so nothing shifts when JS starts."""
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


def expander(uid, inner, label="See everything"):
    return ('<div class="acc-item xp"><div class="xp-h"><button type="button" class="acc-btn xp-btn" aria-expanded="false" aria-controls="x-%s" id="xb-%s">%s%s</button></div>'
            '<div class="acc-body" id="x-%s" role="region" aria-labelledby="xb-%s"><div><div class="acc-in">%s</div></div></div></div>'
            % (uid, uid, label, chev(), uid, uid, inner))


def not_timeline(items):
    return [i for i in items if not i.startswith("About ")]


def t_packages():
    """Website packages: one set of 3 cards that morph between Website only and Website + Brand Kit."""
    cards = []
    for p in D["packages"]:
        b = next(x for x in D["bundles"] if x["package"] == p["key"])
        kit_key = b["website"][:1] + b["brand"][:3]
        kit_more = (tick_list(b["website"][1:] + b["brand"][3:]) if b["website"][1:] + b["brand"][3:] else "") + \
            '<p class="xp-sub">The %s website includes</p>' % esc(p["name"]) + tick_list(not_timeline(p["keyFeatures"]) + p["moreFeatures"])
        short = b["name"].replace(" website", "")
        cards.append(
            '<article class="card pkg rv%s" id="p-%s">' % (" pop" if p.get("popular") else "", p["key"]) +
            ('<span class="tag">Most popular</span>' if p.get("popular") else "") +
            '<h3 data-kit-site="%s" data-kit-kit="%s">%s</h3>' % (esc(p["name"]), esc(short), esc(p["name"])) +
            '<div class="price"><span class="roll" data-kit-site="%s" data-kit-kit="%s">%s</span><s data-kit-site="" data-kit-kit="%s"></s></div>'
            % (money(p["price"]), money(b["price"]), money(p["price"]), money(b["regular"])) +
            '<p class="muted pitch" data-kit-site="%s" data-kit-kit="%s">%s</p>' % (esc(p["pitch"]), esc(b["pitch"]), esc(p["pitch"])) +
            '<div class="morph" data-kit-show="site">%s</div>' % tick_list(p["keyFeatures"]) +
            '<div class="morph" data-kit-show="kit" data-pre-hide><p class="save"><span class="nojs">%s: %s, regular %s. </span>Save %s vs. buying separately.</p>%s</div>'
            % (esc(b["name"]), money(b["price"]), money(b["regular"]), money(b["save"]), tick_list(kit_key)) +
            expander(p["key"],
                     '<div data-kit-show="site">%s</div><div data-kit-show="kit" data-pre-hide>%s<p class="xp-link"><a href="/%s">Full %s details</a></p></div>'
                     % (tick_list(p["moreFeatures"]), kit_more, b["page"], esc(short))) +
            '<a class="btn btn-primary" href="/contact.html?need=%s" data-kit-href-site="/contact.html?need=%s" data-kit-href-kit="/contact.html?need=%s">Get a free quote</a>'
            % (p["key"], p["key"], b["key"]) +
            "</article>")
    return ('<div class="switch-row rv"><div class="seg" data-switch="kit" role="group" aria-label="Show prices for">'
            '<button type="button" data-value="site" aria-pressed="true">Website only</button>'
            '<button type="button" data-value="kit" data-hash="bundles" aria-pressed="false">Website + Brand Kit</button></div>'
            '<span class="save-tag">%s</span></div>'
            '<div class="row swipe cards3">%s</div>%s<p class="swipe-hint muted" aria-hidden="true">Swipe to compare</p>'
            % (esc(D["bundleSaveTag"]), "".join(cards), swipe_dots(3)))


def t_extras():
    items = []
    for g in D["extras"]:
        rows = "".join('<li><span>%s</span><b>%s</b></li>' % (esc(i["name"]), esc(i["price"])) for i in g["items"])
        gid = re.sub(r"[^a-z]+", "-", g["group"].lower()).strip("-")
        items.append(("x-" + gid, g["group"], '<ul class="plist">%s</ul>' % rows))
    return accordion(items, "open-desktop extras")


def t_print():
    return esc(D["printNote"])


def t_care():
    """Care plans: 3 cards, Monthly | Yearly switch."""
    cards = []
    for c in D["carePlans"]:
        m, y = money(c["monthly"]), money(c["yearlyPerMonth"])
        ml = "Billed monthly. Cancel anytime."
        yl = "%s a year. Save %s." % (money(c["yearlyTotal"]), money(c["yearlySave"]))
        cards.append(
            '<article class="card plan rv%s" id="%s">' % (" pop" if c.get("popular") else "", c["key"]) +
            ('<span class="tag">Most popular</span>' if c.get("popular") else "") +
            '<h3>%s</h3>' % esc(c["name"]) +
            '<div class="price"><span class="roll" data-care-monthly="%s" data-care-yearly="%s">%s</span><small>/mo</small></div>' % (m, y, m) +
            '<p class="muted bill" data-care-monthly="%s" data-care-yearly="%s">%s<span class="nojs"> Or %s/mo paid yearly: %s</span></p>' % (ml, yl, ml, y, yl) +
            tick_list(c["keyFeatures"]) +
            expander(c["key"], tick_list(c["moreFeatures"])) +
            '<a class="btn btn-primary" href="/contact.html?need=%s">Get a free quote</a>' % c["key"] +
            "</article>")
    return ('<div class="switch-row rv"><div class="seg" data-switch="care" role="group" aria-label="Show prices">'
            '<button type="button" data-value="monthly" aria-pressed="true">Monthly</button>'
            '<button type="button" data-value="yearly" data-hash="yearly" aria-pressed="false">Yearly</button></div>'
            '<span class="save-tag">%s</span></div>'
            '<div class="row swipe cards3">%s</div>%s<p class="swipe-hint muted" aria-hidden="true">Swipe to compare</p>'
            % (esc(D["careYearlyTag"]), "".join(cards), swipe_dots(3)))


def t_carenotes():
    return " ".join(esc(n) for n in D["careNotes"])


def t_faqgroup(*words):
    return accordion([(f["id"], f["q"], "<p>%s</p>" % esc(f["a"])) for f in faq_items(group=" ".join(words))])


def t_needs():
    """The ?need= keys the contact page understands, built from offers.json.
    checks = which "What do you need?" boxes to tick on the Wix form; note = line written into the message box."""
    n = {"unsure": {"checks": ["Not sure yet"], "label": "", "note": ""},
         "care": {"checks": ["Care plan"], "label": "a care plan", "note": ""},
         "extras": {"checks": [], "label": "an extra", "note": "I'm asking about an extra: "}}
    for p in D["packages"]:
        lab = "the %s website (%s)" % (p["name"], money(p["price"]))
        n[p["key"]] = {"checks": ["Website"], "label": lab, "note": "I'm interested in %s." % lab}
    for b in D["bundles"]:
        lab = "the %s (%s)" % (b["name"], money(b["price"]))
        n[b["key"]] = {"checks": ["Website", "Logo or branding"], "label": lab, "note": "I'm interested in %s." % lab}
    for c in D["carePlans"]:
        lab = "the %s care plan (%s/mo)" % (c["name"], money(c["monthly"]))
        n[c["key"]] = {"checks": ["Care plan"], "label": lab, "note": "I'm interested in %s." % lab}
    return json.dumps(n, ensure_ascii=False)


def contact_ways():
    return ('<p class="ways-num">Call or text <a href="%s">%s</a> or email <a href="mailto:%s">%s</a></p>'
            '<ul class="ways">'
            '<li><a class="btn btn-ghost" href="%s">Call</a></li>'
            '<li><a class="btn btn-ghost" href="%s">Text</a></li>'
            '<li><a class="btn btn-ghost" href="mailto:%s">Email</a></li></ul>'
            % (B["phoneHref"], B["phoneDisplay"], B["email"], B["email"], B["phoneHref"], B["smsHref"], B["email"]))


def t_booking():
    bk = B["booking"]
    if FLAGS["bookingLive"]:
        # Wix Bookings installs its widget here. Service: "Free quote call", 20 minutes, in person or video.
        return ('<div class="card mount" id="wix-booking-mount" data-wix-bookings-service="%s"></div>' % esc(bk["service"]))
    return ('<div class="card placeholder"><span class="tag">Coming soon</span>'
            '<h2 class="h3">Online booking is coming soon.</h2>'
            '<p class="muted">For now, call or text <a href="%s">%s</a> to set up your free %d-minute quote call, %s. '
            'Or send your details and Andrew will reach out to set a time.</p>'
            '<div class="btns"><a class="btn btn-primary" href="%s">Call or text %s</a><a class="btn btn-ghost" href="/contact.html#details">Send your details</a></div></div>'
            % (B["phoneHref"], B["phoneDisplay"], bk["minutes"], bk["where"].lower(), B["phoneHref"], B["phoneDisplay"]))


def pay_methods():
    return "".join("<li>%s</li>" % esc(m) for m in D["policies"]["payment"]["methods"])


def t_payment():
    pay = D["policies"]["payment"]
    if FLAGS["paymentsLive"]:
        # Wix Payments: paste the pay button or payment link embed inside this mount.
        return '<div class="card mount" id="wix-payment-mount"></div>'
    return ('<div class="card placeholder"><span class="tag">Online payment coming soon</span>'
            '<h2 class="h3">How to pay today</h2>'
            '<ol class="pay-steps">'
            '<li><b>Card:</b> pay the Wix invoice Andrew emails you.</li>'
            '<li><b>Zelle or check:</b> call or text <a href="%s">%s</a> and Andrew will give you the details.</li></ol>'
            '<p class="muted small">%s</p></div>' % (B["phoneHref"], B["phoneDisplay"], esc(pay["invoiceDue"])))


def t_policy(*path):
    v = D["policies"]
    for k in path:
        v = v[k]
    return esc(v)


def t_faqall():
    out = []
    groups = []
    for f in D["faqs"]:
        if f["group"] not in groups:
            groups.append(f["group"])
    out.append('<nav class="chips faq-jump" aria-label="FAQ topics">' + "".join(
        '<a class="chip" href="#%s">%s</a>' % (re.sub(r"[^a-z]+", "-", g.lower()), esc(g)) for g in groups) + "</nav>")
    for g in groups:
        gid = re.sub(r"[^a-z]+", "-", g.lower())
        out.append('<section class="faq-group rv" id="%s" aria-labelledby="h-%s"><h2 id="h-%s">%s</h2>%s</section>'
                   % (gid, gid, gid, esc(g), t_faqgroup(*g.split())))
    return "".join(out)


TOKENS = {
    "price": t_price,      # {{price growth}}     -> $2,500
    "from": t_from,        # {{from websites}}    -> $1,500
    "faq": t_faq,          # {{faq own-site time-how}}
    "towns": t_towns,      # {{towns}}            -> service area chips
    "phone": lambda: '<a href="%s">%s</a>' % (B["phoneHref"], B["phoneDisplay"]),
    "email": lambda: '<a href="mailto:%s">%s</a>' % (B["email"], B["email"]),
    "reply": lambda: B["replyTime"],
    "partial": lambda name: part(name),  # {{partial before-after}}
    "packages": t_packages,  # the 3 morphing website/bundle cards
    "extras": t_extras,      # grouped extras accordion
    "printnote": t_print,
    "care": t_care,          # the 3 care plan cards with Monthly | Yearly
    "carenotes": t_carenotes,
    "faqgroup": t_faqgroup,  # {{faqgroup Care plans}}
    "faqall": t_faqall,      # every FAQ, grouped
    "needs": t_needs,        # JSON map of ?need= keys for the contact page
    "booking": t_booking,    # booking mount, or the placeholder while flags.bookingLive is false
    "payment": t_payment,    # payment mount, or the placeholder while flags.paymentsLive is false
    "ways": contact_ways,    # call / text / email buttons
    "policy": t_policy,      # {{policy payment deposit}}
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
    foot = "".join('<a href="%s">%s</a>' % (h, n) for k, h, n in NAV) + '<a href="/contact.html#book">Book a free call</a><a href="/pay-deposit.html">Pay your deposit</a>'
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


def emlast(text, n=2):
    w = text.split()
    return esc(" ".join(w[:-n])) + " <em>" + esc(" ".join(w[-n:])) + "</em>"


def crumbs(trail):
    parts = ['<a href="%s">%s</a>' % (u, esc(n)) for n, u in trail[:-1]] + ["<span>%s</span>" % esc(trail[-1][0])]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"


def build_bundles():
    urls = []
    for b in D["bundles"]:
        p = find(D["packages"], b["package"])
        slug = b["page"][:-5]
        kit = "Starter Kit" if "Starter" in b["name"] else "Brand Kit"
        trail = [("Home", "/"), ("Website Packages", "/pricing.html"), (b["name"], "/" + b["page"])]
        site_list = p["keyFeatures"] + p["moreFeatures"] + b["website"][1:]
        body = (
            '<section class="hero hero-short"><div class="wrap"><div class="hero-copy">' + crumbs(trail) +
            ('<span class="tag">Most popular</span>' if b.get("popular") else "") +
            '<h1>%s website + <em>%s</em></h1>' % (esc(p["name"]), kit) +
            '<div class="price big">%s <s>%s</s></div>' % (money(b["price"]), money(b["regular"])) +
            '<p class="save">Save %s vs. buying separately.</p>' % money(b["save"]) +
            '<p class="lede">%s</p>' % esc(b["pitch"]) +
            '<div class="btns"><a class="btn btn-primary" href="/contact.html?need=%s">Get a free quote</a><a class="btn btn-ghost" href="/contact.html#book">Book a free call</a></div>' % b["key"] +
            '</div></div></section>'
            '<section class="sec sec-tight" aria-label="What\'s included"><div class="wrap"><div class="two">'
            '<div class="card rv"><h2 class="h3">The website</h2><p class="muted">%s, %s</p>%s</div>' % (esc(p["name"]), money(p["price"]) + " on its own", tick_list(site_list)) +
            '<div class="card rv"><h2 class="h3">The %s</h2>%s</div>' % (kit, tick_list(b["brand"])) +
            '</div><p class="note-line rv">Timelines start once we have your text, photos and logo.</p>'
            '<p class="sec-end rv"><a href="/pricing.html#bundles">Compare all packages and bundles</a></p></div></section>' +
            t_cta("Ready when <em>you are.</em>", "Tell us about your business and Andrew will reply %s with a plan and a flat price." % B["replyTime"]))
        meta = {"title": "%s | %s | Calles Group" % (b["name"], money(b["price"])),
                "description": "%s for %s (regular %s). %s Elgin, IL. Free quote in 24 hours." % (b["name"], money(b["price"]), money(b["regular"]), b["pitch"]),
                "nav": "pricing"}
        urls.append(render(slug, meta, body, [schema_crumbs(trail)]))
        print("built", b["page"])
    return urls


def build_towns():
    from towns import TOWNS
    urls = []
    linked = [t for t in D["serviceArea"]["towns"] if t.get("page")]
    for t in TOWNS:
        page = "web-design-%s.html" % t["slug"]
        url = BASE + "/" + page
        trail = [("Home", "/"), ("Web design " + t["name"], "/" + page)]
        rows = "".join(
            '<a class="prow rv" href="/pricing.html#p-%s"><b>%s</b><span class="muted">%s</span><span class="prow-p">%s</span></a>'
            % (p["key"], esc(p["name"]), esc(p["pitch"]), money(p["price"])) for p in D["packages"])
        faq = accordion([("%s-%d" % (t["slug"], i), q, "<p>%s</p>" % esc(a)) for i, (q, a) in enumerate(t["faq"])])
        others = "".join('<a class="chip" href="/%s">%s</a>' % (o["page"], esc(o["name"])) for o in linked if o["page"] != page)
        body = (
            '<section class="hero hero-short"><div class="wrap"><div class="hero-copy">' + crumbs(trail) +
            '<h1>%s</h1>' % emlast(t["h1"], len(t["name"].split()) + 1) +
            '<p class="lede">%s</p>' % esc(t["lead"]) +
            '<div class="btns"><a class="btn btn-primary" href="/contact.html">Get a free quote</a><a class="btn btn-ghost" href="/contact.html#book">Book a free call</a></div>'
            '</div></div></section>'
            '<section class="sec sec-tight"><div class="wrap"><div class="prose rv"><h2>%s</h2>%s</div></div></section>' % (emlast(t["why_h"]), "".join("<p class=\"muted\">%s</p>" % esc(w) for w in t["why"])) +
            '<section class="sec band"><div class="wrap"><div class="sec-head rv"><h2>Website packages for %s <em>businesses</em></h2><p class="muted">Flat prices, the same in %s as everywhere else.</p></div>'
            '<div class="prows">%s</div><p class="sec-end rv"><a href="/pricing.html">Compare packages, Brand Kits and extras</a></p></div></section>' % (esc(t["name"]), esc(t["name"]), rows) +
            '<section class="sec"><div class="wrap"><div class="sec-head rv"><h2>Who we build for in <em>%s</em></h2></div><div class="chips rv">%s</div></div></section>'
            % (esc(t["name"]), "".join('<span class="chip">%s</span>' % esc(w) for w in t["who"])) +
            '<section class="sec band"><div class="wrap narrow"><div class="sec-head rv"><h2>Questions from %s <em>business owners</em></h2></div><div class="rv">%s</div>'
            '<p class="sec-end rv"><a href="/faq.html">More answers in the FAQ</a></p></div></section>' % (esc(t["name"]), faq) +
            '<section class="sec sec-mid"><div class="wrap"><div class="sec-head rv"><h2>Also serving <em>nearby</em></h2><p class="muted">%s</p></div><div class="chips rv">%s</div></div></section>'
            % (esc(D["serviceArea"]["note"]), others) +
            t_cta("Let's get your %s business <em>more calls.</em>" % esc(t["name"]), "Tell us about your business and Andrew will reply %s with a plan and a flat price." % B["replyTime"]))
        service = {"@context": "https://schema.org", "@type": "Service", "serviceType": "Web design", "name": t["h1"], "url": url,
                   "description": t["desc"], "provider": {"@id": BASE + "/#business", "@type": "ProfessionalService", "name": B["name"],
                   "telephone": "+1-312-600-0590", "url": BASE + "/"},
                   "areaServed": {"@type": "City", "name": t["name"] + ", IL"},
                   "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": str(min(p["price"] for p in D["packages"])),
                              "highPrice": str(max(p["price"] for p in D["packages"])), "offerCount": str(len(D["packages"]))}}
        meta = {"title": t["title"], "description": t["desc"], "nav": ""}
        urls.append(render(page[:-5], meta, body, [service, schema_crumbs(trail), schema_faq(t["faq"])]))
        print("built", page)
    return urls


def sitemap(urls):
    today = datetime.date.today().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
        "".join("  <url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (u, today) for u in urls) + "</urlset>\n"
    for f in ("sitemap.xml", "site-pages.xml"):
        open(os.path.join(ROOT, f), "w", encoding="utf-8").write(xml)


if __name__ == "__main__":
    urls = build_src() + build_bundles() + build_towns()
    sitemap(sorted(urls, key=lambda u: (u != BASE + "/", u)))
    print("sitemap.xml and site-pages.xml:", len(urls), "pages")
