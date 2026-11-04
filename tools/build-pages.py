import re, json, os, sys
SRC = '/home/claude/callesgroup-site/index.html'
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
s = open(SRC).read()
DOMAIN = 'https://www.callesgroup.com'

css = s[s.index('<style>') + 7:s.index('</style>')].strip('\n')
header = s[s.index('<header>'):s.index('</header>') + 9]
footer = s[s.index('<footer>'):s.index('</footer>') + 9]
form_script = s[s.index('<script type="module">'):s.index('</script>', s.index('<script type="module">')) + 9].replace('document.querySelector("#page-contact")', 'document.querySelector("main")')

def page(pid):
    start = s.index(f'<div class="page" id="page-{pid}"')
    start = s.index('>', start) + 1
    nxt = [m.start() for m in re.finditer(r'\n<!-- ', s) if m.start() > start]
    end_main = s.index('</main>', start)
    end = min(nxt[0] if nxt else end_main, end_main)
    body = s[start:end].rstrip()
    assert body.endswith('</div>')
    return body[:-6].strip('\n') + '\n'

pages = {k: page(k) for k in ['home', 'pricing', 'faq', 'contact', 'bundle-launch', 'bundle-growth', 'bundle-premium']}

FILES = {'home': 'index.html', 'pricing': 'pricing.html', 'faq': 'faq.html', 'contact': 'contact.html',
         'bundle-launch': 'launch-bundle.html', 'bundle-growth': 'growth-bundle.html', 'bundle-premium': 'premium-bundle.html'}
URL = {k: ('/' if v == 'index.html' else '/' + v) for k, v in FILES.items()}
SECS = ['websites', 'bundles', 'branding', 'addons', 'care']

def links(html, current):
    for k in FILES:
        html = html.replace(f'href="#{k}"', f'href="{URL[k]}"')
    for sec in SECS:
        html = html.replace(f'href="#{sec}"', f'href="#{sec}"' if current == 'pricing' else f'href="/pricing.html#{sec}"')
    for sec in SECS:
        html = html.replace(f'id="sec-{sec}"', f'id="{sec}"')
    return html

def must(html, a, b, n=1):
    assert html.count(a) == n, (a[:70], html.count(a))
    return html.replace(a, b)

# ---------- heading / copy upgrades ----------
h = pages['home']
h = must(h, '<h1>Look polished. Get found. Win more customers.</h1>',
         '<h1><span class="h1-eyebrow">Website design &amp; branding in Elgin, IL</span> Look polished. Get found. Win more customers.</h1>')
h = must(h, '<h2>What we do</h2>', '<h2>Websites, branding and care plans</h2>')
h = must(h, '<h2>Why Calles Group</h2>', '<h2>Why local businesses choose Calles Group</h2>')
h = must(h, '<h2>How it works</h2>', '<h2>How a website project works</h2>')
h = must(h, '<h2>Common questions</h2>', '<h2>Common questions about our web design services</h2>')
h = must(h, '<h2>Areas we serve</h2>', '<h2>Web design for Elgin, the Fox Valley and the northwest suburbs</h2>')
h = must(h, 'in person or over video.</p>\n    </div>',
         'in person or over video.</p>\n      <a class="tlink" href="/contact.html">Get a free quote for your business &rarr;</a>\n    </div>')
h = must(h, '<span class="go">See website pricing &rarr;</span>', '<span class="go">See website design pricing &rarr;</span>')
h = must(h, '<span class="go">See branding pricing &rarr;</span>', '<span class="go">See logo and branding pricing &rarr;</span>')
h = must(h, '<span class="go">See care plans &rarr;</span>', '<span class="go">See website care plans &rarr;</span>')
h = must(h, '<svg viewBox="0 0 28 28" aria-hidden="true"><rect', '<svg viewBox="0 0 28 28" aria-hidden="true" focusable="false"><rect')
h = must(h, '<div class="mock" aria-hidden="true">', '<div class="mock" role="img" aria-label="Example of a clean, mobile-friendly local business website">')
h = h.replace('<a class="tlink" href="#faq">See all FAQs &rarr;</a>', '<a class="tlink" href="/faq.html">See all web design FAQs &rarr;</a>')
pages['home'] = h

p = pages['pricing']
p = must(p, '<p class="lead">Simple, flat pricing. Every project starts with a free quote call so we can match the right package to your business.</p>',
         '<p class="lead">Simple, flat pricing for websites, logos and care plans in Elgin, the Fox Valley and Chicagoland. Every project starts with a free quote call so we can match the right package to your business.</p>')
p = must(p, '<h2>Websites</h2>', '<h2>Website design packages</h2>')
p = must(p, '<h2>Bundle and save.</h2>', '<h2>Bundle and save: website and branding packages</h2>')
p = must(p, '<h2>Branding</h2>', '<h2>Logo and branding</h2>')
p = must(p, '<h2>Add-ons</h2>', '<h2>Add-ons and extras</h2>')
p = must(p, '<h2>Monthly care plans</h2>', '<h2>Monthly website care plans</h2>')
p = must(p, '<a class="tlink" href="#bundle-launch">See what\'s included &rarr;</a>', '<a class="tlink" href="#bundle-launch">See what\'s in the Launch bundle &rarr;</a>')
p = must(p, '<a class="tlink" href="#bundle-growth">See what\'s included &rarr;</a>', '<a class="tlink" href="#bundle-growth">See what\'s in the Growth bundle &rarr;</a>')
p = must(p, '<a class="tlink" href="#bundle-premium">See what\'s included &rarr;</a>', '<a class="tlink" href="#bundle-premium">See what\'s in the Premium bundle &rarr;</a>')
p = must(p, '<p class="wrap soon">Coming soon: Facebook and Instagram ad campaigns. Ask us about it.</p>',
         '<p class="wrap soon">Coming soon: Facebook and Instagram ad campaigns. <a href="/contact.html">Ask us about it.</a> Questions about payment or timelines? <a href="/faq.html">Read the FAQ</a>.</p>')
pages['pricing'] = p

f = pages['faq']
f = must(f, '<div class="wrap page-head"><h1>FAQ</h1></div>',
         '<div class="wrap page-head"><h1>Web design FAQ</h1><p class="lead">Answers about payment, ownership, timelines and care plans. Still unsure? <a href="/pricing.html">See our pricing</a> or <a href="/contact.html">get a free quote</a>.</p></div>')
pages['faq'] = f

c = pages['contact']
c = must(c, '<h1>Get a free quote</h1>', '<h1>Get a free website quote</h1>')
c = must(c, '<p class="lead">Tell us a little about your business.</p>',
         '<p class="lead">Tell us a little about your business. Serving Elgin, the Fox Valley, the northwest suburbs and Chicago. <a href="/pricing.html">See pricing</a> first if you like.</p>')
pages['contact'] = c

for k, name in [('bundle-launch', 'Launch bundle'), ('bundle-growth', 'Growth bundle'), ('bundle-premium', 'Premium bundle')]:
    b = pages[k]
    b = must(b, '<a class="back" href="#bundles">&larr; Back to pricing</a>\n    <span class="eyebrow">Bundle</span>',
             f'<a class="back" href="#bundles">&larr; Back to pricing</a>\n    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/pricing.html">Services &amp; Pricing</a> <span aria-hidden="true">/</span> <span aria-current="page">{name}</span></nav>')
    b = b.replace('href="#bundles"', 'href="/pricing.html#bundles"')
    b = must(b, '<h2>Good to know</h2>', '<h2>Good to know</h2>\n    <p class="muted">Compare with our <a href="/pricing.html#websites">other website packages</a>, or read the <a href="/faq.html">FAQ</a>.</p>')
    pages[k] = b

# ---------- meta ----------
META = {
 'home': ('Website Design & Branding in Elgin, IL | Calles Group',
          'Mobile-friendly Wix websites, logos and branding for local businesses in Elgin, Schaumburg, Bartlett and the Fox Valley. Flat prices from $1,500.'),
 'pricing': ('Pricing | Websites, Logos & Care Plans | Calles Group',
          'Flat pricing for websites from $1,500, logos from $500, bundles and care plans from $99/mo. Serving Elgin, the Fox Valley and Chicagoland.'),
 'faq': ('Web Design FAQ | Calles Group | Elgin, IL',
          'Answers about payment, website ownership, timelines, rounds of changes and care plans from Calles Group, a web design studio in Elgin, IL.'),
 'contact': ('Get a Free Website Quote | Calles Group | Elgin, IL',
          'Request a free quote for a website, logo or care plan. Calles Group serves Elgin, the Fox Valley, the northwest suburbs and Chicago.'),
 'bundle-launch': ('Website + Logo + Business Cards Bundle | Calles Group',
          'Launch website, logo and business cards for $1,950. Save $225 vs. buying separately. Web design and branding in Elgin, IL.'),
 'bundle-growth': ('Growth Website + Brand Kit Bundle | Calles Group',
          'A custom Growth website plus a full Brand Kit for $3,200. Save $200 vs. buying separately. Serving Elgin and Chicagoland.'),
 'bundle-premium': ('Premium Website + Brand Kit Bundle | Calles Group',
          'A Premium website with copywriting plus a full Brand Kit for $4,400. Save $300 vs. buying separately. Serving Elgin and Chicagoland.'),
}
for k, (t, d) in META.items():
    assert len(t) <= 60, (k, len(t)); assert len(d) <= 160, (k, len(d))

CITIES = ['Elgin', 'South Elgin', 'Bartlett', 'Schaumburg', 'Hoffman Estates', 'Barrington', 'South Barrington', 'Inverness', 'St. Charles', 'Geneva', 'Algonquin', 'Crystal Lake', 'Naperville', 'Chicago']
BIZ = {
  "@context": "https://schema.org", "@type": "ProfessionalService", "@id": DOMAIN + "/#business",
  "name": "Calles Group", "url": DOMAIN + "/", "email": "andrew@callesgroup.com",
  "image": DOMAIN + "/og-image.png", "logo": DOMAIN + "/favicon.svg",
  "description": "Web design, logos and branding for local businesses in Elgin, IL, the Fox Valley and Chicagoland.",
  "founder": {"@type": "Person", "name": "Andrew Calles"},
  "address": {"@type": "PostalAddress", "addressLocality": "Elgin", "addressRegion": "IL", "addressCountry": "US"},
  "areaServed": [{"@type": "City", "name": c + ", IL"} for c in CITIES],
  "priceRange": "$$",
  "makesOffer": [
    {"@type": "Offer", "name": "Launch website", "price": "1500", "priceCurrency": "USD", "url": DOMAIN + "/pricing.html#websites"},
    {"@type": "Offer", "name": "Growth website", "price": "2500", "priceCurrency": "USD", "url": DOMAIN + "/pricing.html#websites"},
    {"@type": "Offer", "name": "Premium website", "price": "3800", "priceCurrency": "USD", "url": DOMAIN + "/pricing.html#websites"},
    {"@type": "Offer", "name": "Logo design", "price": "500", "priceCurrency": "USD", "url": DOMAIN + "/pricing.html#branding"}
  ]
}
def faq_ld(html):
    qa = re.findall(r'<details><summary>(.*?)</summary><p class="ans">(.*?)</p></details>', html)
    strip = lambda x: re.sub(r'<[^>]+>', '', x).replace('&amp;', '&')
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qa]}
def crumbs_ld(name, path):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": "Services & Pricing", "item": DOMAIN + "/pricing.html"},
        {"@type": "ListItem", "position": 3, "name": name, "item": DOMAIN + path}]}

LD = {'home': [BIZ], 'faq': [faq_ld(pages['faq'])],
      'bundle-launch': [crumbs_ld('Launch bundle', '/launch-bundle.html')],
      'bundle-growth': [crumbs_ld('Growth bundle', '/growth-bundle.html')],
      'bundle-premium': [crumbs_ld('Premium bundle', '/premium-bundle.html')]}

def esc(x): return x.replace('&', '&amp;').replace('"', '&quot;')

def head(k):
    t, d = META[k]
    url = DOMAIN + URL[k]
    ld = ''.join('<script type="application/ld+json">' + json.dumps(o, separators=(',', ':')) + '</script>\n' for o in LD.get(k, []))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(t)}</title>
<meta name="description" content="{esc(d)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#151515">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Calles Group">
<meta property="og:title" content="{esc(t)}">
<meta property="og:description" content="{esc(d)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Calles Group: website design and branding in Elgin, IL">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="/styles.css">
{ld}</head>
<body>
'''

def nav_for(k):
    navk = 'pricing' if k.startswith('bundle') else k
    hd = links(header, k)
    hd = hd.replace(' aria-current="page"', '')
    target = {'home': 'home', 'pricing': 'pricing', 'faq': 'faq', 'contact': 'contact'}[navk]
    hd = must(hd, f'data-page="{target}">', f'data-page="{target}" aria-current="page">')
    return hd

PAGE_JS = '<script src="/site.js" defer></script>\n'
for k, fn in FILES.items():
    body = links(pages[k], k)
    mcta = '' if k == 'contact' else '\n<div class="mcta" id="mcta"><a class="btn" href="/contact.html">Get a free quote</a></div>\n'
    extra = ('\n' + form_script + '\n') if k == 'contact' else ''
    ft = links(footer, k).replace('<span id="yr">2026</span>', '<span id="yr">2026</span>')
    html = head(k) + nav_for(k) + '\n\n<main>\n' + body + '</main>\n\n' + ft + '\n' + mcta + '\n' + PAGE_JS + extra + '</body>\n</html>\n'
    if k != 'contact':
        html = html.replace('<body>\n', '<body class="has-mcta">\n', 1)
    open(os.path.join(OUT, fn), 'w').write(html)

# ---------- footer: add bundle links ----------
# (applied after write so header/footer edits stay in one place)
for fn in FILES.values():
    path = os.path.join(OUT, fn); x = open(path).read()
    x = must(x, '<a href="/contact.html">Contact</a>\n  </div>',
             '<a href="/contact.html">Contact</a>\n  </div>\n  <div class="fcol links">\n    <a href="/launch-bundle.html">Website + logo bundle</a><a href="/growth-bundle.html">Growth + Brand Kit</a><a href="/premium-bundle.html">Premium + Brand Kit</a>\n  </div>')
    open(path, 'w').write(x)

# ---------- CSS ----------
css = css.replace('/* Layout: mobile-first, hash-routed pages (home, pricing, faq, contact, 3 bundle pages)', '/* Layout: mobile-first, one HTML file per page (home, pricing, faq, contact, 3 bundle pages)')
css += '''

/* SEO pages */
.h1-eyebrow{display:block;font-size:.8rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);margin-bottom:14px}
nav.crumbs{font-size:.88rem;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-left:0}
.crumbs a{color:var(--muted);text-decoration:none;display:inline-flex;align-items:center;min-height:32px}
.crumbs a:hover{color:var(--ink)}
.lead a,.soon a,.notes a,.psec .muted a{color:var(--accent)}
@media (min-width:961px){footer .wrap{grid-template-columns:1fr auto auto}footer .fcol.links{flex-wrap:wrap}}
'''
open(os.path.join(OUT, 'styles.css'), 'w').write(css.strip('\n') + '\n')

# ---------- site.js ----------
js = '''(function () {
  // Old one-page links (/#pricing) go to the real page.
  var old = { pricing: "/pricing.html", faq: "/faq.html", contact: "/contact.html",
    "bundle-launch": "/launch-bundle.html", "bundle-growth": "/growth-bundle.html", "bundle-premium": "/premium-bundle.html",
    websites: "/pricing.html#websites", bundles: "/pricing.html#bundles", branding: "/pricing.html#branding",
    addons: "/pricing.html#addons", care: "/pricing.html#care" };
  var h = location.hash.replace("#", "");
  if ((location.pathname === "/" || location.pathname === "/index.html") && old[h]) { location.replace(old[h]); return; }

  var nav = document.getElementById("siteNav"), btn = document.getElementById("menuBtn");
  if (btn && nav) btn.addEventListener("click", function () {
    var o = nav.classList.toggle("open"); btn.setAttribute("aria-expanded", o ? "true" : "false");
  });
  // Add-ons open on desktop, collapsed on phones.
  if (window.matchMedia("(min-width:801px)").matches) {
    document.querySelectorAll(".addons details").forEach(function (d) { d.open = true; });
  }
  var yr = document.getElementById("yr"); if (yr) yr.textContent = new Date().getFullYear();
})();
'''
open(os.path.join(OUT, 'site.js'), 'w').write(js)

# ---------- favicon ----------
open(os.path.join(OUT, 'favicon.svg'), 'w').write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#151515"/><circle cx="32" cy="32" r="24" fill="none" stroke="#C9A962" stroke-width="3"/><text x="32" y="40" text-anchor="middle" font-family="Montserrat,Arial,Helvetica,sans-serif" font-weight="700" font-size="20" fill="#C9A962" letter-spacing="1">CG</text></svg>\n')

# ---------- robots + sitemap ----------
open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n')
pri = {'home': '1.0', 'pricing': '0.9', 'contact': '0.8', 'faq': '0.6', 'bundle-launch': '0.7', 'bundle-growth': '0.7', 'bundle-premium': '0.7'}
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(
    f'  <url><loc>{DOMAIN}{URL[k]}</loc><lastmod>2026-11-04</lastmod><priority>{pri[k]}</priority></url>\n' for k in FILES) + '</urlset>\n'
open(os.path.join(OUT, 'sitemap.xml'), 'w').write(sm)
print('built', sorted(os.listdir(OUT)))
