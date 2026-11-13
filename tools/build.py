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
LANG = "en"  # the language of the page being built; build_src sets it from the page's meta

# Every interface word that changes with the language. Page copy lives in src/*.html.
STR = {
    "en": {"skip": "Skip to content", "navLabel": "Main", "close": "Close", "menu": "Menu", "home": "/",
           "book": "Book a free call", "bookShort": "Book a call", "bookHref": "/contact.html#book",
           "langHref": "/es.html", "langOther": "es", "langName": "Español", "callText": "Call or text",
           "pagesLabel": "Pages", "areaLabel": "Web design near you", "privacy": "Privacy policy",
           "textBtn": "Text Andrew", "sign": "your name here", "ctaFine": "Or call %s. Replies %s.",
           "popular": "Most popular", "spots": "%d of %d spots left", "due": "Due today",
           "dueNote": "The %d-minute quote call is free.", "from": "from", "mo": "/mo",
           "care": ("Care plans", "We keep your site working and up to date. Cancel anytime."),
           "logo": "3 concepts, 2 rounds of changes and the full file pack.",
           "photos": "Up to 1 hour on-site and 25 edited photos."},
    "es": {"skip": "Ir al contenido", "navLabel": "Principal", "close": "Cerrar", "menu": "Menú", "home": "/es.html",
           "book": "Agende su llamada gratis", "bookShort": "Agendar", "bookHref": "/es.html#llamada",
           "langHref": "/", "langOther": "en", "langName": "English", "callText": "Llame o escriba al",
           "pagesLabel": "Páginas", "areaLabel": "Zonas de servicio (en inglés)", "tagline": "Con base en Elgin, IL. Servimos a todo Chicagoland.", "privacy": "Política de privacidad (en inglés)",
           "textBtn": "Escríbale a Andrew", "sign": "su nombre aquí", "ctaFine": "O llame al %s. Respondemos en menos de 24 horas.",
           "popular": "El más pedido", "spots": "Quedan %d de %d lugares", "due": "A pagar hoy",
           "dueNote": "La llamada de %d minutos es gratis.", "from": "desde", "mo": "/mes",
           "care": ("Planes de mantenimiento", "Mantenemos su sitio funcionando y al día. Cancele cuando quiera."),
           "logo": "3 propuestas, 2 rondas de cambios y todos los archivos.",
           "photos": "Hasta 1 hora en su negocio y 25 fotos editadas."},
}


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
          "replyTime": B["replyTime"], "tagline": B["tagline"], "base": BASE, "smsHref": B["smsHref"]}

NAV = [("home", "/", "Home"), ("pricing", "/pricing.html", "Website Packages"),
       ("care", "/care-plans.html", "Care Plans"), ("faq", "/faq.html", "FAQ"), ("contact", "/contact.html", "Contact")]
NAV_ES = [("home", "/es.html", "Inicio"), ("pricing", "/pricing.html", "Paquetes (en inglés)")]


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
    for x in D["packages"] + D["branding"] + [D["photos"]]:
        if x["key"] == key:
            return money(x["price"])
    p = find(D["carePlans"], key)
    return money(p["monthly"])


def t_from(what):
    if what == "websites":
        return money(min(p["price"] for p in D["packages"]))
    if what == "branding":
        return money(min(p["price"] for p in D["branding"]))
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
    L = STR[LANG]
    fine = L["ctaFine"] % ('<a href="%s">%s</a>' % (B["phoneHref"], B["phoneDisplay"]), B["replyTime"]) if LANG == "en" \
        else L["ctaFine"] % ('<a href="%s">%s</a>' % (B["phoneHref"], B["phoneDisplay"]))
    return fill(part("cta"), dict(COMMON, cta_title=title, cta_text=text, book=L["book"], bookHref=L["bookHref"],
                                  textBtn=L["textBtn"], sign=L["sign"], ctaFine=fine))


def spots_text():
    f = D["founding"]
    return STR[LANG]["spots"] % (f["spotsLeft"], f["spotsTotal"])


def t_lineitems():
    """Home page: packages and extras set as estimate line items. Prices and words come from offers.json."""
    L, es = STR[LANG], LANG == "es"
    rows = []
    for p in D["packages"]:
        desc = (p["es"]["pitch"] + " " + p["es"]["detail"]) if es else "%s %s. %s." % (p["pitch"], p["keyFeatures"][0], p["timeline"].capitalize())
        tag = '<span class="tag">%s</span>' % L["popular"] if p.get("popular") else ""
        rows.append('<a class="item" href="/pricing.html#p-%s"><span class="item-n">%s%s</span><span class="item-p">%s</span><span class="item-d">%s</span></a>'
                    % (p["key"], esc(p["name"]), tag, money(p["price"]), esc(desc)))
    logo, kit, ph = find(D["branding"], "logo"), find(D["branding"], "brand-kit"), D["photos"]
    extras = [(logo["name"], L["logo"], money(logo["price"]), "/pricing.html#branding"),
              (kit["name"], D["brandingNote_es"] if es else D["brandingNote"], money(kit["price"]), "/pricing.html#branding"),
              ("Sesión de fotos" if es else ph["name"], L["photos"], money(ph["price"]), "/pricing.html#branding"),
              (L["care"][0], L["care"][1], "<small>%s</small> %s<small>%s</small>" % (L["from"], t_from("care"), L["mo"]), "/care-plans.html")]
    for n, d, pr, href in extras:
        rows.append('<a class="item sub" href="%s"><span class="item-n">%s</span><span class="item-p">%s</span><span class="item-d">%s</span></a>'
                    % (href, esc(n), pr, esc(d)))
    rows.append('<div class="item due"><span class="item-n">%s</span><span class="item-p">$0</span><span class="item-d">%s</span></div>'
                % (L["due"], L["dueNote"] % B["booking"]["minutes"]))
    return '<div class="items">' + "".join(rows) + "</div>"


def t_stamp():
    """The founding client offer as a rubber stamp."""
    f = D["founding"]
    title, text = (f["es"]["title"], f["es"]["text"]) if LANG == "es" else (f["title"], f["text"])
    return '<div class="stamp"><b>%s</b><span>%s</span><i>%s</i></div>' % (esc(title), esc(text), esc(spots_text()))


def t_pkgdata():
    """Package names and prices for the calculator's payback line, so the script never hardcodes a price."""
    return esc(json.dumps([{"k": p["key"], "n": p["name"], "p": p["price"]} for p in D["packages"]]), quote=True)


def t_faqes(*ids):
    return accordion([(f["id"], f["es"]["q"], "<p>%s</p>" % esc(f["es"]["a"])) for f in faq_items(ids=ids)])


def expander(uid, inner, label="See everything"):
    return ('<div class="acc-item xp"><div class="xp-h"><button type="button" class="acc-btn xp-btn" aria-expanded="false" aria-controls="x-%s" id="xb-%s">%s%s</button></div>'
            '<div class="acc-body" id="x-%s" role="region" aria-labelledby="xb-%s"><div><div class="acc-in">%s</div></div></div></div>'
            % (uid, uid, label, chev(), uid, uid, inner))


def t_packages():
    """Website packages: 3 cards."""
    cards = []
    for p in D["packages"]:
        cards.append(
            '<article class="card pkg rv%s" id="p-%s">' % (" pop" if p.get("popular") else "", p["key"]) +
            ('<span class="tag">Most popular</span>' if p.get("popular") else "") +
            '<h3>%s</h3>' % esc(p["name"]) +
            '<div class="price">%s</div>' % money(p["price"]) +
            '<p class="muted pitch">%s</p>' % esc(p["pitch"]) +
            tick_list(p["keyFeatures"]) +
            expander(p["key"], tick_list(p["moreFeatures"])) +
            '<a class="btn btn-primary" href="/contact.html?need=%s">Get a free quote</a>' % p["key"] +
            "</article>")
    return ('<div class="row swipe cards3">%s</div>%s<p class="swipe-hint muted" aria-hidden="true">Swipe to compare</p>'
            % ("".join(cards), swipe_dots(3)))


def t_founding():
    """Founding client banner."""
    f = D["founding"]
    return ('<div class="card teaser founding rv"><div><span class="save-tag">%s</span><p><b>%s:</b> %s</p></div>'
            '<a class="btn btn-primary" href="/contact.html?need=%s">Get a free quote</a></div>'
            % (esc(spots_text()), esc(f["title"]), esc(f["text"]), f["key"]))


def t_brandcards():
    """Branding and photo shoot cards."""
    cards = []
    for x in D["branding"] + [D["photos"]]:
        cards.append(
            '<article class="card pkg rv" id="%s"><h3>%s</h3><div class="price">%s</div>%s'
            '<a class="btn btn-primary" href="/contact.html?need=%s">Get a free quote</a></article>'
            % (x["key"], esc(x["name"]), money(x["price"]), tick_list(x["features"]), x["key"]))
    return ('<div class="row swipe cards3">%s</div>%s<p class="swipe-hint muted" aria-hidden="true">Swipe to compare</p>'
            % ("".join(cards), swipe_dots(len(cards))))


def t_band():
    return ('<div class="card teaser rv"><p>%s</p><a class="btn btn-ghost" href="/contact.html#details">Get a free quote</a></div>'
            % esc(D["customBand"]))


def t_care():
    """Care plans: 3 cards, Monthly | Yearly switch."""
    cards = []
    for c in D["carePlans"]:
        m, y = money(c["monthly"]), money(c["yearlyTotal"])
        ml = "Billed monthly. Cancel anytime."
        yl = "Billed yearly. 1 month free."
        cards.append(
            '<article class="card plan rv%s" id="%s">' % (" pop" if c.get("popular") else "", c["key"]) +
            ('<span class="tag">Most popular</span>' if c.get("popular") else "") +
            '<h3>%s</h3>' % esc(c["name"]) +
            '<div class="price"><span class="roll" data-care-monthly="%s" data-care-yearly="%s">%s</span><small data-care-monthly="/mo" data-care-yearly="/yr">/mo</small></div>' % (m, y, m) +
            '<p class="muted bill" data-care-monthly="%s" data-care-yearly="%s">%s<span class="nojs"> Or %s/yr paid yearly (1 month free).</span></p>' % (ml, yl, ml, y) +
            tick_list(c["keyFeatures"]) +
            (expander(c["key"], tick_list(c["moreFeatures"])) if c["moreFeatures"] else "") +
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
    checks = which "What do you need?" boxes to tick on the quote form; note = line written into the message box."""
    n = {"unsure": {"checks": ["Not sure yet"], "label": "", "note": ""},
         "care": {"checks": ["Care plan"], "label": "a care plan", "note": ""},
         "founding": {"checks": ["Website"], "label": "the founding client offer (Launch for $1,200)",
                      "note": "I'm interested in the founding client offer (Launch for $1,200)."}}
    for p in D["packages"]:
        lab = "the %s website (%s)" % (p["name"], money(p["price"]))
        n[p["key"]] = {"checks": ["Website"], "label": lab, "note": "I'm interested in %s." % lab}
    for b in D["branding"]:
        lab = "the %s (%s)" % (b["name"], money(b["price"]))
        n[b["key"]] = {"checks": ["Logo or branding"], "label": lab, "note": "I'm interested in %s." % lab}
    ph = D["photos"]
    lab = "the %s (%s)" % (ph["name"].lower(), money(ph["price"]))
    n[ph["key"]] = {"checks": [], "label": lab, "note": "I'm interested in %s." % lab}
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
    """Book a call. The visitor picks a day and a time of day, then texts it or asks for a call back.
    Put a real scheduler link in business.booking.url (offers.json) to add a "See open times" button on top."""
    bk, es = B["booking"], LANG == "es"
    T = {"open": "Vea los horarios disponibles", "or": "O pida un horario aquí abajo.", "day": "¿Qué día?", "time": "¿A qué hora?",
         "times": [("morning", "En la mañana"), ("midday", "A mediodía"), ("evening", "Después de las 5")],
         "biz": "El nombre de su negocio", "sum": "Usted pide:", "text": "Mandar por mensaje a Andrew", "call": "Llamar ahora",
         "fine": "Llamada gratis de %d minutos, en persona o por video. Andrew le confirma la hora exacta por mensaje. Desde una computadora, escriba al %s."} if es else \
        {"open": "See open times", "or": "Or ask for a time below.", "day": "Which day?", "time": "What time of day?",
         "times": [("morning", "Morning"), ("midday", "Midday"), ("evening", "After 5pm")],
         "biz": "Your business name", "sum": "You're asking for:", "text": "Text Andrew this time", "call": "Have Andrew call me",
         "fine": "Free %d-minute quote call, in person or video. Andrew confirms the exact time by text. On a computer, text %s."}
    top = ('<a class="btn btn-primary" href="%s" rel="noopener">%s</a><p class="muted">%s</p>' % (esc(bk["url"]), T["open"], T["or"])) if bk.get("url") else ""
    times = "".join('<button type="button" class="pick" aria-pressed="%s" data-v="%s">%s</button>' % ("true" if k == "evening" else "false", k, n) for k, n in T["times"])
    second = '<a class="btn btn-ghost" href="%s">%s</a>' % (B["phoneHref"], T["call"]) if es else \
        '<a class="btn btn-ghost" data-bk-form href="/contact.html#details">%s</a>' % T["call"]
    return ('<div class="bk" data-bk>%s'
            '<fieldset class="bk-group"><legend>%s</legend><div class="bk-picks" data-bk-days></div></fieldset>'
            '<fieldset class="bk-group"><legend>%s</legend><div class="bk-picks" data-bk-times>%s</div></fieldset>'
            '<div><label class="bk-l" for="bkBiz">%s</label><input class="bk-in" id="bkBiz" type="text" maxlength="40" autocomplete="organization"></div>'
            '<p class="bk-sum" aria-live="polite">%s <span class="hand" data-bk-sum></span></p>'
            '<div class="btns"><a class="btn btn-primary" data-bk-text href="%s">%s</a>%s</div>'
            '<p class="small muted">%s</p></div>'
            % (top, T["day"], T["time"], times, T["biz"], T["sum"], B["smsHref"], T["text"], second,
               T["fine"] % (bk["minutes"], B["phoneDisplay"])))


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
            '<li><b>Card:</b> pay the invoice Andrew emails you.</li>'
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
    "packages": t_packages,  # the 3 website cards
    "founding": t_founding,  # founding client banner
    "brandcards": t_brandcards,  # logo, Brand Kit and photo shoot cards
    "brandnote": lambda: esc(D["brandingNote"]),
    "photonote": lambda: esc(D["photosNote"]),
    "band": t_band,          # "Need something that's not here?" band
    "care": t_care,          # the 3 care plan cards with Monthly | Yearly
    "carenotes": t_carenotes,
    "faqgroup": t_faqgroup,  # {{faqgroup Care plans}}
    "faqall": t_faqall,      # every FAQ, grouped
    "needs": t_needs,        # JSON map of ?need= keys for the contact page
    "booking": t_booking,    # the call request (day, time of day, text or call back)
    "payment": t_payment,    # payment mount, or the placeholder while flags.paymentsLive is false
    "ways": contact_ways,    # call / text / email buttons
    "policy": t_policy,      # {{policy payment deposit}}
    "lineitems": t_lineitems,  # home: packages and extras as estimate line items
    "stamp": t_stamp,          # the founding offer as a rubber stamp
    "pkgdata": t_pkgdata,      # package prices for the calculator
    "faqes": t_faqes,          # {{faqes own-site time-how}} in Spanish
    "sms": lambda: B["smsHref"],
    "tel": lambda: B["phoneHref"],
    "phonenum": lambda: B["phoneDisplay"],
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
        "knowsLanguage": ["en", "es"],
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
    lang = meta.get("lang", "en")
    L = STR[lang]
    url = BASE + ("/" if slug == "index" else "/%s.html" % slug)
    nav = NAV_ES if lang == "es" else NAV
    navlinks = "".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if meta.get("nav") == k else "", n) for k, h, n in nav)
    foot = "".join('<a href="%s">%s</a>' % (h, n) for k, h, n in nav)
    foot += ('<a href="/es.html#llamada">%s</a><a href="/" lang="en">English</a>' % L["book"]) if lang == "es" else \
        '<a href="/contact.html#book">Book a free call</a><a href="/pay-deposit.html">Pay your deposit</a><a href="/es.html" lang="es">Español</a>'
    towns = "".join('<a href="/%s">Web design %s</a>' % (t["page"], esc(t["name"])) for t in D["serviceArea"]["towns"] if t.get("page"))
    # The English home page and the Spanish page point at each other for search engines.
    alt = ('<link rel="alternate" hreflang="en" href="%s/">\n<link rel="alternate" hreflang="es" href="%s/es.html">\n'
           '<link rel="alternate" hreflang="x-default" href="%s/">\n' % (BASE, BASE, BASE)) if slug in ("index", "es") else ""
    head = fill(part("head"), dict(COMMON, lang=lang, skip=L["skip"], alternates=alt,
        title=esc(meta["title"]), description=esc(meta["description"]), url=url,
        robots="index, follow" if meta.get("index", True) else "noindex, follow",
        verify='<meta name="google-site-verification" content="ADdwPb9axnmWCbzpY3gyaaUnq09scu5mJBVPGQg933g">\n' if slug == "index" else "",
        jsonld=jsonld(schemas)))
    out = head + fill(part("header"), {**COMMON, **L, "navlinks": navlinks}) + body.strip() + "\n" + \
        fill(part("footer"), {**COMMON, **L, "footlinks": foot, "townlinks": towns, "year": datetime.date.today().year, "scripts": meta.get("scripts", "")})
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
        global LANG
        LANG = meta.get("lang", "en")
        body = expand(raw[m.end():])
        LANG = "en"
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
    """Headings used to accent their last words. The current look sets them as one piece."""
    return esc(text)


def crumbs(trail):
    parts = ['<a href="%s">%s</a>' % (u, esc(n)) for n, u in trail[:-1]] + ["<span>%s</span>" % esc(trail[-1][0])]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"


OLD_PAGES = ["launch-bundle", "growth-bundle", "premium-bundle"]


def build_redirects():
    """Bundles are retired. Their old URLs forward to the pricing page so old links don't break."""
    for slug in OLD_PAGES:
        open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8").write(
            '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><title>Website Packages | Calles Group</title>'
            '<meta name="robots" content="noindex, follow"><link rel="canonical" href="%s/pricing.html">'
            '<meta http-equiv="refresh" content="0; url=/pricing.html"></head>'
            '<body><p><a href="/pricing.html">See website packages and prices</a></p></body></html>\n' % BASE)
        print("built", slug + ".html (redirect)")


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
            '<div class="btns"><a class="btn btn-primary" href="/contact.html#book">Book a free call</a><a class="btn btn-ghost" href="/contact.html#details">Get a free quote</a></div>'
            '</div></div></section>'
            '<section class="sec sec-tight"><div class="wrap"><div class="prose rv"><h2>%s</h2>%s</div></div></section>' % (emlast(t["why_h"]), "".join("<p class=\"muted\">%s</p>" % esc(w) for w in t["why"])) +
            '<section class="sec band"><div class="wrap"><div class="sec-head rv"><h2>Website packages for %s businesses</h2><p class="muted">Flat prices, the same in %s as everywhere else.</p></div>'
            '<div class="prows">%s</div><p class="sec-end rv"><a href="/pricing.html">Compare website packages and branding</a></p></div></section>' % (esc(t["name"]), esc(t["name"]), rows) +
            '<section class="sec"><div class="wrap"><div class="sec-head rv"><h2>Who we build for in %s</h2></div><div class="chips rv">%s</div></div></section>'
            % (esc(t["name"]), "".join('<span class="chip">%s</span>' % esc(w) for w in t["who"])) +
            '<section class="sec band"><div class="wrap narrow"><div class="sec-head rv"><h2>Questions from %s business owners</h2></div><div class="rv">%s</div>'
            '<p class="sec-end rv"><a href="/faq.html">More answers in the FAQ</a></p></div></section>' % (esc(t["name"]), faq) +
            '<section class="sec sec-mid"><div class="wrap"><div class="sec-head rv"><h2>Also serving nearby</h2><p class="muted">%s</p></div><div class="chips rv">%s</div></div></section>'
            % (esc(D["serviceArea"]["note"]), others) +
            t_cta("Let's get your %s business more calls." % esc(t["name"]), "Tell us about your business and Andrew will reply %s with a plan and a flat price." % B["replyTime"]))
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
    build_redirects()
    urls = build_src() + build_towns()
    sitemap(sorted(urls, key=lambda u: (u != BASE + "/", u)))
    print("sitemap.xml and site-pages.xml:", len(urls), "pages")
