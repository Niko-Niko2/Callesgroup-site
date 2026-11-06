"""Builds the local service-area pages (web-design-<town>.html).

Each town gets its own copy, FAQ and structured data so the pages are not
near-duplicates. Run from the repo root: python3 tools/build-local-pages.py
"""
import html
import json

BASE = "https://www.callesgroup.com"
OG = "https://static.wixstatic.com/media/03855a_96c7c31bf029475a934ad5139d4f888e~mv2.png"

TOWNS = [
    {
        "slug": "elgin",
        "name": "Elgin",
        "title": "Web Design in Elgin, IL | Website Developer | Calles Group",
        "desc": "Elgin-based web design and development for local businesses. Mobile-friendly websites from $1,500, logos and Google Business Profile setup. Free quote in 24 hours.",
        "h1": "Web design in Elgin, IL",
        "lead": "Calles Group is an Elgin web design studio. We build mobile-friendly websites, logos and branding for the businesses that keep this city running, at flat prices you see before we start.",
        "why_h": "A web designer who's actually from here",
        "why": [
            "Elgin is home base. When you call 312-600-0590 or send a quote request, you reach Andrew Calles, the person who designs and builds your site, not a call center or an out-of-state agency.",
            "Most Elgin customers find a contractor, salon or restaurant on their phone, often by searching for something nearby. Every site we build is designed for phones first and set up so Google knows what you do and which part of Elgin and the Fox Valley you serve.",
        ],
        "who": ["Contractors, painters and home services", "Restaurants, cafes and food trucks", "Salons, barbers and personal care", "Shops and boutiques", "Cleaning, landscaping and auto services", "Professional offices and new startups"],
        "faq": [
            ("Do you only work with businesses in Elgin?", "Elgin is where we're based, and we work with businesses across the Fox Valley, the northwest suburbs and Chicago. Elgin businesses get the same flat prices as everyone else."),
            ("How much does a website cost in Elgin?", "Our websites start at $1,500 for a Launch site of up to 3 pages. A Growth site is $2,500 and a Premium site with full copywriting is $3,800. You get a flat price on your free quote call, before any work starts."),
            ("Can you help my Elgin business show up on Google Maps?", "Yes. Google Business Profile setup is included in the Growth and Premium packages, or $250 on its own. We set up your categories, service area, hours and photos so you can show up when people nearby search for what you do."),
        ],
    },
    {
        "slug": "south-elgin",
        "name": "South Elgin",
        "title": "Web Design in South Elgin, IL | Calles Group",
        "desc": "Websites, logos and branding for South Elgin businesses from a designer just up the Fox River in Elgin. Flat prices from $1,500 and a free quote in 24 hours.",
        "h1": "Web design in South Elgin, IL",
        "lead": "We're right next door in Elgin, building clean, phone-ready websites and logos for South Elgin businesses, with prices you see before we start.",
        "why_h": "Built for South Elgin's local businesses",
        "why": [
            "South Elgin runs on small, owner-operated businesses, and most of them get found by neighbors searching on their phones. A fast, simple site that clearly says what you do and where you work makes those searches turn into calls.",
            "Because we're just up the river in Elgin, we know the area you serve and can describe it properly on your site, from South Elgin itself to the surrounding Fox Valley towns.",
        ],
        "who": ["Home services and trades", "Landscaping and snow removal", "Childcare, tutoring and fitness", "Restaurants and takeout", "Pet care and grooming", "Side businesses going full-time"],
        "faq": [
            ("Are you close to South Elgin?", "Yes. Calles Group is based in Elgin, right next to South Elgin along the Fox River."),
            ("What does a basic website cost?", "A Launch site with up to 3 pages, a contact form and basic SEO is $1,500 and takes about 2 weeks once we have your text, photos and logo."),
            ("Do I own my website?", "Yes. Your Wix account and domain are set up in your name, so the site is yours, even if you stop working with us."),
        ],
    },
    {
        "slug": "bartlett",
        "name": "Bartlett",
        "title": "Web Design in Bartlett, IL | Calles Group",
        "desc": "Mobile-friendly websites, logos and Google Business Profile setup for Bartlett, IL businesses. Flat prices from $1,500. Elgin-based, free quote in 24 hours.",
        "h1": "Web design in Bartlett, IL",
        "lead": "Bartlett businesses deserve a website that looks as professional as the work they do. We design and build them from Elgin, a short drive west, at flat prices.",
        "why_h": "Websites that bring in Bartlett customers",
        "why": [
            "Your customers in Bartlett, Streamwood and Hanover Park compare a few businesses on their phone before they call anyone. We build sites that load fast, show your work clearly and put your phone number and quote button where people can tap them.",
            "We also set up the parts of Google that send local calls: your Business Profile, your service area and the page titles that tell Google you serve Bartlett.",
        ],
        "who": ["Contractors and remodelers", "Auto repair and detailing", "Health, wellness and fitness studios", "Restaurants and bakeries", "Real estate and insurance agents", "Retail and specialty shops"],
        "faq": [
            ("Do you work with Bartlett businesses?", "Yes. We're based in Elgin and work with businesses in Bartlett and the nearby northwest suburbs."),
            ("Can you redesign my existing website?", "Yes. Redesigning an existing site starts at $900, depending on how many pages it has and what needs to change."),
            ("How long does a website take?", "About 2 weeks for a Launch site, 3 weeks for Growth and 4 to 5 weeks for Premium. Timelines start once we have your text, photos and logo."),
        ],
    },
    {
        "slug": "schaumburg",
        "name": "Schaumburg",
        "title": "Web Design in Schaumburg, IL | Calles Group",
        "desc": "Web design and branding for Schaumburg small businesses: phone-ready websites from $1,500, logos and local SEO setup. Free quote reply within 24 hours.",
        "h1": "Web design in Schaumburg, IL",
        "lead": "Schaumburg is one of the busiest business areas in the suburbs. We help small businesses there stand out with a sharp, fast website and branding that looks established from day one.",
        "why_h": "Stand out in a crowded market",
        "why": [
            "In a place with as many businesses as Schaumburg, an outdated or slow website quietly sends customers to the competitor one search result down. A modern site with clear pricing, real photos and an easy quote form gives people a reason to pick you.",
            "We're a small studio based in Elgin, so you work directly with the designer, get flat prices instead of agency retainers, and own your site and domain outright.",
        ],
        "who": ["Professional services and consultants", "Restaurants and catering", "Salons, spas and med-spas", "Home services covering the northwest suburbs", "Retail and e-commerce shops", "Startups that need a logo and site together"],
        "faq": [
            ("Why hire an Elgin studio instead of a big Schaumburg agency?", "You work directly with the person building your site, you get flat package prices with no retainer, and your site and domain are in your name."),
            ("Can you build an online store?", "Yes. Online store setup is $750 for up to 20 products, then $15 for each additional product."),
            ("Do you offer branding too?", "Yes. Logos start at $500, and the full Brand Kit (logo, business cards, colors, fonts and a brand guide) is $900, or less when bundled with a website."),
        ],
    },
    {
        "slug": "st-charles",
        "name": "St. Charles",
        "title": "Web Design in St. Charles, IL | Calles Group",
        "desc": "Websites, logos and branding for St. Charles, IL businesses, from a Fox Valley studio in Elgin. Flat prices from $1,500 and a free quote in 24 hours.",
        "h1": "Web design in St. Charles, IL",
        "lead": "We build websites and brands for St. Charles businesses that want to look as polished online as they do in person, from a fellow Fox Valley studio in Elgin.",
        "why_h": "A Fox Valley studio for St. Charles businesses",
        "why": [
            "St. Charles has a strong mix of downtown shops, restaurants and service businesses, and customers often look you up before they visit. Your website should match the experience you give in person: clean, easy to use and clear about what you offer.",
            "We focus on what turns visits into customers: strong photos, simple menus or service lists, a quick way to book or request a quote, and setup on Google so people across St. Charles, Geneva and Batavia can find you.",
        ],
        "who": ["Downtown shops and boutiques", "Restaurants, bars and cafes", "Event, wedding and photography businesses", "Salons and wellness studios", "Contractors and home services", "Professional practices"],
        "faq": [
            ("Do you serve St. Charles and the Tri-Cities?", "Yes. We're based in Elgin and work with businesses in St. Charles, Geneva, Batavia and the rest of the Fox Valley."),
            ("Can customers book appointments on my site?", "Yes. Online booking setup is $250, and a booking or quote request form is included in the Growth and Premium packages."),
            ("Can you keep my site updated after launch?", "Yes. Monthly care plans start at $99 and include edit time, form and link checks and renewal reminders. You can cancel anytime."),
        ],
    },
    {
        "slug": "crystal-lake",
        "name": "Crystal Lake",
        "title": "Web Design in Crystal Lake, IL | Calles Group",
        "desc": "Phone-ready websites, logos and Google Business Profile setup for Crystal Lake and McHenry County businesses. Flat prices from $1,500. Free quote in 24 hours.",
        "h1": "Web design in Crystal Lake, IL",
        "lead": "From our base in Elgin, we design websites and branding for Crystal Lake businesses that want more calls from local searches, with flat prices and no long contracts.",
        "why_h": "Get found across McHenry County",
        "why": [
            "Crystal Lake customers search for businesses across a wide area, from Algonquin and Cary to the rest of McHenry County. We set up your site and Google Business Profile so they clearly list the towns you serve, which helps you show up in more of those searches.",
            "Every site is built mobile-first, loads fast and makes it easy to call, text or request a quote in one tap.",
        ],
        "who": ["Trades, roofing and remodeling", "Landscaping and outdoor services", "Restaurants and breweries", "Medical, dental and wellness offices", "Lake, boating and recreation businesses", "Local retail"],
        "faq": [
            ("Do you work with businesses in Crystal Lake and Algonquin?", "Yes. We're based in Elgin and serve Crystal Lake, Algonquin and the surrounding McHenry and Kane County towns."),
            ("What's included for local SEO?", "Every site gets page titles, descriptions and a sitemap. The Growth package adds Google Business Profile setup, Search Console and analytics, and the SEO starter setup is available on its own for $300."),
            ("Do I have to sign a long contract?", "No. Websites are a flat, one-time price, and monthly care plans can be canceled anytime."),
        ],
    },
]


def esc(s):
    return html.escape(s, quote=True)


def header():
    return """<header>
  <div class="wrap bar">
    <a class="logo" href="/" aria-label="Calles Group home"><span class="wm"><span class="wm-top">CALLES<span class="wm-dot"></span></span><span class="wm-sub"><span>GROUP</span></span></span></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="siteNav">Menu</button>
    <nav id="siteNav" aria-label="Main">
      <a class="nl" href="/" data-page="home">Home</a>
      <a class="nl" href="/pricing.html" data-page="pricing">Packages</a>
      <a class="nl" href="/custom-merchandise.html" data-page="merch">Print &amp; Signs</a>
      <a class="nl" href="/faq.html" data-page="faq">FAQ</a>
      <a class="nl" href="/contact.html" data-page="contact">Contact</a>
      <a class="btn sm" href="/contact.html">Get a free quote</a>
    </nav>
  </div>
</header>"""


def areas_col():
    links = " &middot; ".join(f'<a href="/web-design-{t["slug"]}.html">{esc(t["name"])}</a>' for t in TOWNS)
    return f'<span class="areas">Web design in {links}</span>'


def footer():
    return """<footer><div class="wrap">
  <div class="fcol">
    <a class="logo" href="/" aria-label="Calles Group home"><span class="wm"><span class="wm-top">CALLES<span class="wm-dot"></span></span><span class="wm-sub"><span>GROUP</span></span></span></a>
    <span>Based in Elgin, IL. Serving Chicagoland.</span>
    <a href="mailto:andrew@callesgroup.com">andrew@callesgroup.com</a>
    <a href="tel:+13126000590">312-600-0590</a>
  </div>
  <div class="fcol links">
    <a href="/">Home</a><a href="/pricing.html">Packages</a><a href="/custom-merchandise.html">Print &amp; Signs</a><a href="/faq.html">FAQ</a><a href="/contact.html">Contact</a>
  </div>
  <div class="fcol links">
    <a href="/launch-bundle.html">Launch + Starter Kit</a><a href="/growth-bundle.html">Growth + Brand Kit</a><a href="/premium-bundle.html">Premium + Brand Kit</a>
  </div>
  <div class="fcol copy">""" + areas_col() + """<span>&copy; <span id="yr">2026</span> Calles Group &middot; <a href="/privacy-policy.html">Privacy policy</a></span></div>
</div></footer>"""


def page(t):
    url = f"{BASE}/web-design-{t['slug']}.html"
    city = f"{t['name']}, IL"
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": "Web design",
        "name": f"Web design in {city}",
        "url": url,
        "description": t["desc"],
        "provider": {"@id": f"{BASE}/#business", "@type": "ProfessionalService", "name": "Calles Group", "telephone": "+1-312-600-0590", "url": f"{BASE}/"},
        "areaServed": {"@type": "City", "name": city},
        "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": "1500", "highPrice": "3800", "offerCount": "3"},
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE}/"},
            {"@type": "ListItem", "position": 2, "name": f"Web design {t['name']}", "item": url},
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]],
    }
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(x, separators=(",", ":"))}</script>' for x in (service, crumbs, faq))
    why = "\n".join(f"    <p>{esc(p)}</p>" for p in t["why"])
    who = "".join(f"<li>{esc(w)}</li>" for w in t["who"])
    faqs = "\n".join(f'      <details class="lfaq"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in t["faq"])
    others = " &middot; ".join(f'<a href="/web-design-{o["slug"]}.html">{esc(o["name"])}</a>' for o in TOWNS if o is not t)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(t['title'])}</title>
<meta name="description" content="{esc(t['desc'])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#151515">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Calles Group">
<meta property="og:title" content="{esc(t['title'])}">
<meta property="og:description" content="{esc(t['desc'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Calles Group: website design and branding in {esc(city)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/styles.css">
{ld}
<style>
.lfaq{{border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin-bottom:10px}}
.lfaq summary{{cursor:pointer;font-weight:600}}
.lfaq p{{margin:10px 0 0}}
.lprose p{{max-width:68ch}}
footer .fcol.copy .areas{{display:block;margin-bottom:6px}}
footer .fcol.copy .areas a{{min-height:0;display:inline}}
</style>
</head>
<body class="has-mcta">
{header()}

<main>
  <div class="wrap page-head">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">/</span> <span aria-current="page">Web design {esc(t['name'])}</span></nav>
    <h1>{esc(t['h1'])}</h1>
    <p class="lead">{esc(t['lead'])}</p>
    <div class="btns"><a class="btn" href="/contact.html">Get a free quote</a> <a class="btn ghost" href="tel:+13126000590">Call 312-600-0590</a></div>
  </div>
  <div class="wrap psec lprose">
    <h2>{esc(t['why_h'])}</h2>
{why}
  </div>
  <div class="wrap psec">
    <h2>Website packages for {esc(t['name'])} businesses</h2>
    <div class="cards c3">
      <div class="card"><h3>Launch &middot; $1,500</h3><ul class="check"><li>Up to 3 pages</li><li>Built for mobile</li><li>Contact form</li><li>Basic SEO</li><li>About 2 weeks</li></ul></div>
      <div class="card"><h3>Growth &middot; $2,500</h3><ul class="check"><li>Up to 5 pages, custom layout</li><li>Google Business Profile setup</li><li>Search Console and analytics</li><li>Booking or quote form</li><li>About 3 weeks</li></ul></div>
      <div class="card"><h3>Premium &middot; $3,800</h3><ul class="check"><li>Up to 8 pages</li><li>Full copywriting</li><li>Blog or project gallery</li><li>30 days of free edits</li><li>About 4 to 5 weeks</li></ul></div>
    </div>
    <p class="muted">See <a href="/pricing.html">all packages and pricing</a>, including logos, bundles and monthly care plans. Need print too? See <a href="/custom-merchandise.html">Print &amp; Signs</a>.</p>
  </div>
  <div class="wrap psec">
    <h2>Who we build for in {esc(t['name'])}</h2>
    <ul class="check">{who}</ul>
  </div>
  <div class="wrap psec">
    <h2>Questions from {esc(t['name'])} business owners</h2>
{faqs}
    <p class="muted">More answers in the <a href="/faq.html">FAQ</a>.</p>
  </div>
  <div class="wrap psec">
    <h2>Ready to get started?</h2>
    <p>Tell us about your business and we'll reply within 24 hours with a flat-price quote.</p>
    <div class="btns"><a class="btn" href="/contact.html">Get a free quote</a></div>
    <p class="muted">We also build websites in {others}.</p>
  </div>
</main>

{footer()}

<div class="mcta" id="mcta"><a class="btn" href="/contact.html">Get a free quote</a></div>

<script src="/site.js" defer></script>
</body>
</html>
"""


if __name__ == "__main__":
    for t in TOWNS:
        with open(f"web-design-{t['slug']}.html", "w") as f:
            f.write(page(t))
    # footer column snippet for the existing pages
    with open("tools/areas-footer.html", "w") as f:
        f.write(areas_col())
    print("built", len(TOWNS), "pages")
