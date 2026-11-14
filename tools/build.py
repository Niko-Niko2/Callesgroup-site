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
           "textBtn": "Text Andrew", "ctaFine": "Or call %s. Replies %s.",
           "popular": "Recommended", "spots": "%d of %d spots left", "due": "Due today",
           "dueNote": "The %d-minute quote call is free.", "from": "from", "mo": "/mo",
           "care": ("Care plans", "We keep your site working and up to date. Cancel anytime."),
           "logo": "3 concepts, 2 rounds of changes and the full file pack.",
           "photos": "Up to 1 hour on-site and 25 edited photos.",
           "groups": ("Websites", "Add-ons", "Monthly care"), "pages": "%s pages",
           "est": {"hint": "Tap a website and any extras. Your total adds up as you go.", "pick": "Pick one", "optional": "Optional",
                   "incl": "What's included", "plus": "Everything in %s, plus:", "title": "Your estimate",
                   "total": "One-time total", "start": "To start (50% deposit)", "monthly": "Monthly care", "bar": "Your estimate",
                   "fine": "This is an estimate, not a quote. You get your exact price in writing on the free call.",
                   "text": "Text Andrew this estimate", "kit": "Includes: %s.", "alone": "%s on its own.", "withSite": "with a website",
                   "carePlans": "See the three plans", "compare": "Compare the packages side by side",
                   "site": "%s website", "inKit": "In the Brand Kit", "inPremium": "In Premium", "founding": "Founding client rate: %s for %s.",
                   "sms": "Hi Andrew%s. My estimate from your site: %s. One-time total %s%s. I'd like a free quote call.",
                   "smsMe": ", it's %s", "smsCare": ", plus a monthly care plan"}},
    "es": {"skip": "Ir al contenido", "navLabel": "Principal", "close": "Cerrar", "menu": "Menú", "home": "/es.html",
           "book": "Agende su llamada gratis", "bookShort": "Agendar", "bookHref": "/es.html#llamada",
           "langHref": "/", "langOther": "en", "langName": "English", "callText": "Llame o escriba al",
           "pagesLabel": "Páginas", "areaLabel": "Zonas de servicio (en inglés)", "tagline": "Con base en Elgin, IL. Servimos a todo Chicagoland.", "privacy": "Política de privacidad (en inglés)",
           "textBtn": "Escríbale a Andrew", "ctaFine": "O llame al %s. Respondemos en menos de 24 horas.",
           "popular": "Recomendado", "spots": "Quedan %d de %d lugares", "due": "A pagar hoy",
           "dueNote": "La llamada de %d minutos es gratis.", "from": "desde", "mo": "/mes",
           "care": ("Planes de mantenimiento", "Mantenemos su sitio funcionando y al día. Cancele cuando quiera."),
           "logo": "3 propuestas, 2 rondas de cambios y todos los archivos.",
           "photos": "Hasta 1 hora en su negocio y 25 fotos editadas.",
           "groups": ("Sitios web", "Extras", "Mantenimiento mensual"), "pages": "%s páginas",
           "est": {"hint": "Toque un sitio web y los extras que quiera. Su total se suma solo.", "pick": "Elija uno", "optional": "Opcional",
                   "incl": "Qué incluye", "plus": "Todo lo de %s, más:", "title": "Su estimado",
                   "total": "Total de un solo pago", "start": "Para empezar (depósito del 50%)", "monthly": "Mantenimiento mensual", "bar": "Su estimado",
                   "fine": "Es un estimado, no una cotización. Su precio exacto se lo doy por escrito en la llamada gratis.",
                   "text": "Mandarle este estimado a Andrew", "kit": "Incluye: %s.", "alone": "%s por separado.", "withSite": "con un sitio web",
                   "carePlans": "Ver los tres planes", "compare": "",
                   "site": "Sitio web %s", "inKit": "En el Brand Kit", "inPremium": "En Premium", "founding": "Precio de cliente fundador: %s por %s.",
                   "sms": "Hola Andrew%s. Mi estimado de su sitio: %s. Total de un solo pago %s%s. Quiero una llamada gratis.",
                   "smsMe": ", soy de %s", "smsCare": ", más un plan de mantenimiento mensual"}},
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
                                  textBtn=L["textBtn"], ctaFine=fine))


def spots_text():
    f = D["founding"]
    return STR[LANG]["spots"] % (f["spotsLeft"], f["spotsTotal"])


def sentence(items):
    """["Logo", "Color palette", "Fonts"] -> "logo, color palette and fonts" (Spanish joins with "y")."""
    low = [items[0]] + [x[0].lower() + x[1:] for x in items[1:]]
    return ", ".join(low[:-1]) + (" y " if LANG == "es" else " and ") + low[-1] if len(low) > 1 else low[0]


def est_parts():
    """Everything the estimate on the home page can add up, straight from offers.json."""
    es = LANG == "es"
    logo, kit, ph = find(D["branding"], "logo"), find(D["branding"], "brand-kit"), D["photos"]
    # The bundle price is written out in the note under the branding cards. Fail loudly if the two ever disagree.
    assert money(kit["withWebsite"]) in D["brandingNote"] and money(kit["withWebsite"]) in D["brandingNote_es"], "Brand Kit bundle price differs from brandingNote"
    return logo, kit, ph, es


def t_lineitems():
    """Home page prices as an estimate builder. Each website package is a box you tap to pick (nothing leaves the page),
    add-ons and monthly care tick on and off, and the box at the bottom adds it up. Prices and words come from offers.json.
    With scripts off it still reads as a price list, with the popular package's total shown."""
    L, E = STR[LANG], STR[LANG]["est"]
    logo, kit, ph, es = est_parts()
    web, addons, care = L["groups"]
    pop = next(p for p in D["packages"] if p.get("popular"))
    boxes = []
    for p in D["packages"]:
        pitch, pages, time, inc = (p["es"]["pitch"], p["es"]["pages"], p["es"]["timeline"], p["es"]["includes"]) if es \
            else (p["pitch"], p["pages"], p["timeline"].capitalize(), p["includes"])
        on = p is pop
        tag = '<span class="tag">%s</span>' % L["popular"] if p.get("popular") else ""
        plus = '<p class="plus">%s</p>' % esc(E["plus"] % p["buildsOn"]) if p.get("buildsOn") else ""
        boxes.append(
            '<div class="box pk rv%s%s" data-k="%s"><label class="item"><input class="pk-in" type="radio" name="est-site" value="%s"%s>'
            '<span class="item-n"><i class="mark" aria-hidden="true"></i>%s%s</span><span class="item-p">%s</span><span class="item-d">%s</span>'
            '<span class="item-s"><i>%s</i><i>%s</i></span></label>'
            '<details class="more"><summary>%s</summary>%s%s</details></div>'
            % (" pop" if p.get("popular") else "", " on" if on else "", p["key"], p["key"], " checked" if on else "",
               esc(p["name"]), tag, money(p["price"]), esc(pitch), esc(L["pages"] % pages), esc(time), esc(E["incl"]), plus, tick_list(inc)))
    kit_feats = kit["es"]["features"] if es else kit["features"]
    rows = [("logo", logo["name"], money(logo["price"]), "", esc(L["logo"])),
            ("brand-kit", kit["name"], money(kit["withWebsite"]), "<small>%s</small>" % esc(E["withSite"]),
             esc(E["kit"] % sentence(kit_feats)) + " " + esc(E["alone"] % money(kit["price"]))),
            ("photo-shoot", "Sesión de fotos" if es else ph["name"], money(ph["price"]), "", esc(L["photos"]))]
    subs = "".join(
        '<label class="item sub" data-k="%s"><input class="pk-in" type="checkbox" value="%s"><span class="item-n"><i class="mark sq" aria-hidden="true"></i>%s</span>'
        '<span class="item-p">%s%s</span><span class="item-d">%s</span></label>' % (k, k, esc(n), pr, (" " + small) if small else "", d)
        for k, n, pr, small, d in rows)
    carerow = ('<label class="item sub" data-k="care"><input class="pk-in" type="checkbox" value="care"><span class="item-n"><i class="mark sq" aria-hidden="true"></i>%s</span>'
               '<span class="item-p"><small>%s</small> %s<small>%s</small></span><span class="item-d">%s <a href="/care-plans.html">%s</a></span></label>'
               % (esc(L["care"][0]), L["from"], t_from("care"), L["mo"], esc(L["care"][1]), esc(E["carePlans"])))
    pay = D["policies"]["payment"]
    data = {
        "sites": [{"k": p["key"], "n": p["name"], "p": p["price"]} for p in D["packages"]],
        "adds": [{"k": "logo", "n": logo["name"], "p": logo["price"]},
                 {"k": "brand-kit", "n": kit["name"], "p": kit["withWebsite"], "covers": kit["includesKeys"]},
                 {"k": "photo-shoot", "n": "Sesión de fotos" if es else ph["name"], "p": ph["price"], "inside": ph["includedIn"]}],
        "care": {"from": min(c["monthly"] for c in D["carePlans"])},
        "founding": {"k": "launch", "p": D["founding"]["price"], "left": D["founding"]["spotsLeft"]},
        "pay": [pay["es"]["deposit"] if es else pay["deposit"], pay["es"]["over2500"] if es else pay["over2500"]],
        "t": {k: E[k] for k in ("site", "inKit", "inPremium", "founding", "sms", "smsMe", "smsCare")},
        "from": L["from"], "mo": L["mo"], "careName": L["care"][0], "spots": spots_text(),
    }
    summary = (
        '<div class="est-stick"><a class="est-bar" id="estBar" href="#estSum" hidden><span>%s</span><b id="estBarN">%s</b></a></div>'
        '<div class="box sum rv" id="estSum"><h3 class="sum-h">%s</h3><ul class="sum-lines" id="estLines"><li><span>%s</span><b>%s</b></li></ul>'
        '<p class="sum-row sum-total"><span>%s</span><b class="est-n" id="estTotal">%s</b></p>'
        '<p class="sum-row"><span>%s</span><b id="estDep">%s</b></p><p class="fine" id="estPay">%s</p>'
        '<p class="sum-row" id="estCare" hidden><span>%s</span><b><small>%s</small> %s<small>%s</small></b></p>'
        '<p class="sum-row sum-due"><span>%s</span><b>$0</b></p>'
        '<p class="fine" id="estNote">%s %s</p>'
        '<div class="btns"><a class="btn btn-primary" href="%s">%s</a><a class="btn btn-ghost btn-wrap" id="estText" href="%s">%s</a></div></div>'
        % (esc(E["bar"]), money(pop["price"]), esc(E["title"]), esc(E["site"] % pop["name"]), money(pop["price"]),
           esc(E["total"]), money(pop["price"]), esc(E["start"]), money(pop["price"] // 2),
           esc((pay["es"] if es else pay)["over2500" if pop["price"] > 2500 else "deposit"]),
           esc(E["monthly"]), L["from"], t_from("care"), L["mo"], esc(L["due"]),
           esc(L["dueNote"] % B["booking"]["minutes"]), esc(E["fine"]), L["bookHref"], esc(L["book"]), B["smsHref"], esc(E["text"])))
    head = lambda title, note: '<h3 class="items-h">%s <span>%s</span></h3>' % (title, esc(note))
    return ('<div class="items boxed est" id="est" data-est="%s"><p class="est-hint">%s</p>%s<div class="boxes">%s</div>'
            '<div class="pair"><div class="pair-c">%s<div class="box group rv">%s</div></div>'
            '<div class="pair-c">%s<div class="box group rv">%s</div></div></div>%s</div>'
            % (esc(json.dumps(data, ensure_ascii=False), quote=True), esc(E["hint"]), head(web, E["pick"]), "".join(boxes),
               head(addons, E["optional"]), subs, head(care, E["optional"]), carerow, summary))


# The sample site's color sets. The colors themselves are in assets/styles.css (.ps and .sw share them);
# these are only the names, in the same order. tools.js accepts p=0..5 on a pitch link.
PALETTES = [("Daylight", "Luz de día"), ("Ember", "Brasa"), ("Evergreen", "Siempre verde"), ("Barn red", "Rojo granero"), ("Harbor", "Puerto"), ("Glacier", "Glaciar")]


def t_swatches():
    es = LANG == "es"
    names = [n[1] if es else n[0] for n in PALETTES]
    btns = "".join('<button type="button" class="sw" data-pal="%d" aria-pressed="%s" aria-label="%s" data-name="%s"></button>'
                   % (i, "true" if i == 0 else "false", esc(n), esc(n)) for i, n in enumerate(names))
    return ('<div class="swatches" role="group" aria-label="%s"><span class="sw-l">%s <b id="swName">%s</b></span><div class="sw-row">%s</div></div>'
            % ("Colores de muestra" if es else "Sample colors", "Colores:" if es else "Colors:", esc(names[0]), btns))


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
    """Website packages: 3 cards. Each card has the same three rows in the same order (pages, timeline, rounds),
    then what is included, so the three compare at a glance."""
    cards = []
    for p in D["packages"]:
        specs = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (k, esc(str(v))) for k, v in
                        (("Pages", p["pages"]), ("Timeline", p["timeline"].capitalize()), ("Rounds of changes", p["rounds"])))
        plus = '<p class="plus">Everything in %s, plus:</p>' % esc(p["buildsOn"]) if p.get("buildsOn") else ""
        cards.append(
            '<article class="card pkg rv%s" id="p-%s">' % (" pop" if p.get("popular") else "", p["key"]) +
            ('<span class="tag">Recommended</span>' if p.get("popular") else "") +
            '<h3>%s</h3>' % esc(p["name"]) +
            '<div class="price">%s</div>' % money(p["price"]) +
            '<p class="muted pitch">%s</p>' % esc(p["pitch"]) +
            '<dl class="specs">%s</dl>' % specs +
            expander(p["key"], plus + tick_list(p["includes"]), "What's included") +
            '<a class="btn btn-primary" href="/contact.html?need=%s">Get a free quote</a>' % p["key"] +
            "</article>")
    return ('<div class="row swipe cards3 open-desktop">%s</div>%s<p class="swipe-hint muted" aria-hidden="true">Swipe to compare</p>'
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
            ('<span class="tag">Recommended</span>' if c.get("popular") else "") +
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
    """Book a call. The visitor picks a day and one of Andrew's call times, then texts it or asks for a call back.
    The times come from business.booking.hours in offers.json (24-hour clock, the hours a call can start).
    Put a real scheduler link in business.booking.url to add a "See open times" button on top."""
    bk, es = B["booking"], LANG == "es"
    T = {"open": "Vea los horarios disponibles", "or": "O pida un horario aquí abajo.", "day": "¿Qué día?", "time": "¿A qué hora?",
         "biz": "El nombre de su negocio", "sum": "Usted pide:", "text": "Mandar por mensaje a Andrew", "call": "Llamar ahora",
         "hours": bk["hoursNote_es"],
         "fine": "Llamada gratis de %d minutos, en persona o por video. Andrew le confirma la hora por mensaje. Desde una computadora, escriba al %s."} if es else \
        {"open": "See open times", "or": "Or ask for a time below.", "day": "Which day?", "time": "What time?",
         "biz": "Your business name", "sum": "You're asking for:", "text": "Text Andrew this time", "call": "Have Andrew call me",
         "hours": bk["hoursNote"],
         "fine": "Free %d-minute quote call, in person or video. Andrew confirms the time by text. On a computer, text %s."}
    top = ('<a class="btn btn-primary" href="%s" rel="noopener">%s</a><p class="muted">%s</p>' % (esc(bk["url"]), T["open"], T["or"])) if bk.get("url") else ""
    second = '<a class="btn btn-ghost" href="%s">%s</a>' % (B["phoneHref"], T["call"]) if es else \
        '<a class="btn btn-ghost" data-bk-form href="/contact.html#details">%s</a>' % T["call"]
    hrs = bk["hours"]
    return ('<div class="bk" data-bk data-weekday="%s" data-weekend="%s">%s'
            '<fieldset class="bk-group"><legend>%s</legend><div class="bk-picks" data-bk-days></div></fieldset>'
            '<fieldset class="bk-group"><legend>%s</legend><div class="bk-picks" data-bk-times></div><p class="small muted">%s</p></fieldset>'
            '<div><label class="bk-l" for="bkBiz">%s</label><input class="bk-in" id="bkBiz" type="text" maxlength="40" autocomplete="organization"></div>'
            '<p class="bk-sum" aria-live="polite">%s <span data-bk-sum></span></p>'
            '<div class="btns"><a class="btn btn-primary" data-bk-text href="%s">%s</a>%s</div>'
            '<p class="small muted">%s</p></div>'
            % (",".join(map(str, hrs["weekday"])), ",".join(map(str, hrs["weekend"])), top, T["day"], T["time"], esc(T["hours"]),
               T["biz"], T["sum"], B["smsHref"], T["text"], second, T["fine"] % (bk["minutes"], B["phoneDisplay"])))


def pay_methods():
    return "".join("<li>%s</li>" % esc(m) for m in D["policies"]["payment"]["methods"])


def t_payment():
    pay = D["policies"]["payment"]
    if FLAGS["paymentsLive"]:
        # Paste the pay button or payment link inside this mount.
        return '<div class="card mount" id="wix-payment-mount"></div>'
    how = " or ".join(m.lower() if i else m for i, m in enumerate(pay["methods"]))
    return ('<div class="card placeholder"><span class="tag">%s</span>'
            '<h2 class="h3">How to pay today</h2>'
            '<p><b>%s.</b> Call or text <a href="%s">%s</a> and Andrew will give you the details.</p>'
            '<p class="muted small">%s</p></div>' % (esc(pay["soon"]), esc(how), B["phoneHref"], B["phoneDisplay"], esc(pay["invoiceDue"])))


def t_deposits():
    """Pay your deposit page: the 50% that starts each package, worked out from offers.json."""
    f = D["founding"]
    rows = [("%s, founding client rate" % find(D["packages"], "launch")["name"], f["price"])] if f.get("spotsLeft") else []
    rows += [(p["name"], p["price"]) for p in D["packages"]]
    out = []
    for name, price in rows:
        out.append('<div class="item"><span class="item-n">%s</span><span class="item-p">%s</span><span class="item-d">Half of %s starts the work.</span></div>'
                   % (esc(name), money(price // 2), money(price)))
    return '<div class="items">' + "".join(out) + "</div>"


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
    "swatches": t_swatches,  # the sample site's color buttons
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
    "deposits": t_deposits,    # deposit amount per package
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
        # Inner pages get a "Home / This page" line at the top, so there is always a way back.
        if meta.get("crumb") and '<div class="hero-copy">' in body:
            body = body.replace('<div class="hero-copy">', '<div class="hero-copy">' + crumbs([("Home", "/"), (meta["crumb"], None)]), 1)
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
            '<div class="prows rv">%s</div><p class="sec-end rv"><a href="/pricing.html">Compare website packages and branding</a></p></div></section>' % (esc(t["name"]), esc(t["name"]), rows) +
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
