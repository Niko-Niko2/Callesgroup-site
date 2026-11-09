"""Local copy for each town page (web-design-<slug>.html).

Every town gets its own lead, reasons, business list and 3 FAQs, so the pages are
not near-duplicates. Prices in this copy must match data/offers.json.
To add a town: copy one entry, rewrite every line for that town, then add the town
with its "page" to serviceArea.towns in data/offers.json and run tools/build.py.
"""

TOWNS = [{'slug': 'elgin',
  'name': 'Elgin',
  'title': 'Web Design in Elgin, IL | Website Developer | Calles Group',
  'desc': 'Elgin-based web design for local businesses. Mobile-friendly websites from '
          '$1,500, logos and Google Business Profile setup. Free quote in 24 hours.',
  'h1': 'Web design in Elgin, IL',
  'lead': 'Calles Group is an Elgin web design studio. We build mobile-friendly websites, logos and branding '
          'for the businesses that keep this city running, at flat prices you see before we start.',
  'why_h': "A web designer who's actually from here",
  'why': ['Elgin is home base. When you call 312-600-0590 or send a quote request, you reach Andrew Calles, '
          'the person who designs and builds your site, not a call center or an out-of-state agency.',
          'Most Elgin customers find a contractor, salon or restaurant on their phone, often by searching '
          'for something nearby. Every site we build is designed for phones first and set up so Google knows '
          'what you do and which part of Elgin and the Fox Valley you serve.'],
  'who': ['Contractors, painters and home services',
          'Restaurants, cafes and food trucks',
          'Salons, barbers and personal care',
          'Shops and boutiques',
          'Cleaning, landscaping and auto services',
          'Professional offices and new startups'],
  'faq': [['Do you only work with businesses in Elgin?',
           "Elgin is where we're based, and we work with businesses across the Fox Valley, the northwest "
           'suburbs and Chicago. Elgin businesses get the same flat prices as everyone else.'],
          ['How much does a website cost in Elgin?',
           'Our websites start at $1,500 for a Launch site of up to 3 pages. A Growth site is $2,500 and a '
           'Premium site with full copywriting is $3,800. You get a flat price on your free quote call, '
           'before any work starts.'],
          ['Can you help my Elgin business show up on Google Maps?',
           'Yes. Google Business Profile setup is included in the Growth and Premium packages, or $250 on '
           'its own. We set up your categories, service area, hours and photos so you can show up when '
           'people nearby search for what you do.']]},
 {'slug': 'south-elgin',
  'name': 'South Elgin',
  'title': 'Web Design in South Elgin, IL | Calles Group',
  'desc': 'Websites, logos and branding for South Elgin businesses from a designer just up the Fox River in '
          'Elgin. Flat prices from $1,500 and a free quote in 24 hours.',
  'h1': 'Web design in South Elgin, IL',
  'lead': "We're right next door in Elgin, building clean, phone-ready websites and logos for South Elgin "
          'businesses, with prices you see before we start.',
  'why_h': "Built for South Elgin's local businesses",
  'why': ['South Elgin runs on small, owner-operated businesses, and most of them get found by neighbors '
          'searching on their phones. A fast, simple site that clearly says what you do and where you work '
          'makes those searches turn into calls.',
          "Because we're just up the river in Elgin, we know the area you serve and can describe it properly "
          'on your site, from South Elgin itself to the surrounding Fox Valley towns.'],
  'who': ['Home services and trades',
          'Landscaping and snow removal',
          'Childcare, tutoring and fitness',
          'Restaurants and takeout',
          'Pet care and grooming',
          'Side businesses going full-time'],
  'faq': [['Are you close to South Elgin?',
           'Yes. Calles Group is based in Elgin, right next to South Elgin along the Fox River.'],
          ['What does a basic website cost?',
           'A Launch site with up to 3 pages, a contact form and basic SEO is $1,500 and takes about 2 weeks '
           'once we have your text, photos and logo.'],
          ['Do I own my website?',
           'Yes. Your Wix account and domain are set up in your name, so the site is yours, even if you stop '
           'working with us.']]},
 {'slug': 'bartlett',
  'name': 'Bartlett',
  'title': 'Web Design in Bartlett, IL | Calles Group',
  'desc': 'Mobile-friendly websites, logos and Google Business Profile setup for Bartlett, IL businesses. '
          'Flat prices from $1,500. Elgin-based, free quote in 24 hours.',
  'h1': 'Web design in Bartlett, IL',
  'lead': 'Bartlett businesses deserve a website that looks as professional as the work they do. We design '
          'and build them from Elgin, a short drive west, at flat prices.',
  'why_h': 'Websites that bring in Bartlett customers',
  'why': ['Your customers in Bartlett, Streamwood and Hanover Park compare a few businesses on their phone '
          'before they call anyone. We build sites that load fast, show your work clearly and put your phone '
          'number and quote button where people can tap them.',
          'We also set up the parts of Google that send local calls: your Business Profile, your service '
          'area and the page titles that tell Google you serve Bartlett.'],
  'who': ['Contractors and remodelers',
          'Auto repair and detailing',
          'Health, wellness and fitness studios',
          'Restaurants and bakeries',
          'Real estate and insurance agents',
          'Retail and specialty shops'],
  'faq': [['Do you work with Bartlett businesses?',
           "Yes. We're based in Elgin and work with businesses in Bartlett and the nearby northwest "
           'suburbs.'],
          ['Can you redesign my existing website?',
           'Yes. Redesigning an existing site starts at $900, depending on how many pages it has and what '
           'needs to change.'],
          ['How long does a website take?',
           'About 2 weeks for a Launch site, 3 weeks for Growth and 4 to 5 weeks for Premium. Timelines '
           'start once we have your text, photos and logo.']]},
 {'slug': 'schaumburg',
  'name': 'Schaumburg',
  'title': 'Web Design in Schaumburg, IL | Calles Group',
  'desc': 'Web design and branding for Schaumburg small businesses: phone-ready websites from $1,500, logos '
          'and local SEO setup. Free quote reply within 24 hours.',
  'h1': 'Web design in Schaumburg, IL',
  'lead': 'Schaumburg is one of the busiest business areas in the suburbs. We help small businesses there '
          'stand out with a sharp, fast website and branding that looks established from day one.',
  'why_h': 'Stand out in a crowded market',
  'why': ['In a place with as many businesses as Schaumburg, an outdated or slow website quietly sends '
          'customers to the competitor one search result down. A modern site with clear pricing, real photos '
          'and an easy quote form gives people a reason to pick you.',
          "We're a small studio based in Elgin, so you work directly with the designer, get flat prices "
          'instead of agency retainers, and own your site and domain outright.'],
  'who': ['Professional services and consultants',
          'Restaurants and catering',
          'Salons, spas and med-spas',
          'Home services covering the northwest suburbs',
          'Retail and e-commerce shops',
          'Startups that need a logo and site together'],
  'faq': [['Why hire an Elgin studio instead of a big Schaumburg agency?',
           'You work directly with the person building your site, you get flat package prices with no '
           'retainer, and your site and domain are in your name.'],
          ['Can you build an online store?',
           'Yes. Online store setup is $750 for up to 20 products, then $15 for each additional product.'],
          ['Do you offer branding too?',
           'Yes. Logo design is $500 with 3 concepts, 2 rounds of changes and files in PNG, SVG and PDF, '
           'light and dark. Or pair a website with a Brand Kit and save up to $300.']]},
 {'slug': 'st-charles',
  'name': 'St. Charles',
  'title': 'Web Design in St. Charles, IL | Calles Group',
  'desc': 'Websites, logos and branding for St. Charles, IL businesses, from a Fox Valley studio in Elgin. '
          'Flat prices from $1,500 and a free quote in 24 hours.',
  'h1': 'Web design in St. Charles, IL',
  'lead': 'We build websites and brands for St. Charles businesses that want to look as polished online as '
          'they do in person, from a fellow Fox Valley studio in Elgin.',
  'why_h': 'A Fox Valley studio for St. Charles businesses',
  'why': ['St. Charles has a strong mix of downtown shops, restaurants and service businesses, and customers '
          'often look you up before they visit. Your website should match the experience you give in person: '
          'clean, easy to use and clear about what you offer.',
          'We focus on what turns visits into customers: strong photos, simple menus or service lists, a '
          'quick way to book or request a quote, and setup on Google so people across St. Charles, Geneva '
          'and Batavia can find you.'],
  'who': ['Downtown shops and boutiques',
          'Restaurants, bars and cafes',
          'Event, wedding and photography businesses',
          'Salons and wellness studios',
          'Contractors and home services',
          'Professional practices'],
  'faq': [['Do you serve St. Charles and the Tri-Cities?',
           "Yes. We're based in Elgin and work with businesses in St. Charles, Geneva, Batavia and the rest "
           'of the Fox Valley.'],
          ['Can customers book appointments on my site?',
           'Yes. Online booking setup is $250, and a booking or quote request form is included in the Growth '
           'and Premium packages.'],
          ['Can you keep my site updated after launch?',
           'Yes. Monthly care plans start at $99 and include edit time, form and link checks and renewal '
           'reminders. You can cancel anytime.']]},
 {'slug': 'crystal-lake',
  'name': 'Crystal Lake',
  'title': 'Web Design in Crystal Lake, IL | Calles Group',
  'desc': 'Phone-ready websites, logos and Google Business Profile setup for Crystal Lake and McHenry County '
          'businesses. Flat prices from $1,500. Free quote in 24 hours.',
  'h1': 'Web design in Crystal Lake, IL',
  'lead': 'From our base in Elgin, we design websites and branding for Crystal Lake businesses that want '
          'more calls from local searches, with flat prices and no long contracts.',
  'why_h': 'Get found across McHenry County',
  'why': ['Crystal Lake customers search for businesses across a wide area, from Algonquin and Cary to the '
          'rest of McHenry County. We set up your site and Google Business Profile so they clearly list the '
          'towns you serve, which helps you show up in more of those searches.',
          'Every site is built mobile-first, loads fast and makes it easy to call, text or request a quote '
          'in one tap.'],
  'who': ['Trades, roofing and remodeling',
          'Landscaping and outdoor services',
          'Restaurants and breweries',
          'Medical, dental and wellness offices',
          'Lake, boating and recreation businesses',
          'Local retail'],
  'faq': [['Do you work with businesses in Crystal Lake and Algonquin?',
           "Yes. We're based in Elgin and serve Crystal Lake, Algonquin and the surrounding McHenry and Kane "
           'County towns.'],
          ["What's included for local SEO?",
           'Every site gets page titles, descriptions and a sitemap. The Growth package adds Google Business '
           'Profile setup, Search Console and analytics, and the SEO starter setup is available on its own '
           'for $300.'],
          ['Do I have to sign a long contract?',
           'No. Websites are a flat, one-time price, and monthly care plans can be canceled anytime.']]}]
