#!/usr/bin/env python3
"""Browser tests for the pricing boxes and the motion (price roll, box reveal, sample build-in).
Run with the site served on :8765 (python3 -m http.server 8765 in the repo)."""
import json
import re
import sys
from playwright.sync_api import sync_playwright

B = "http://localhost:8765"
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = json.load(open(os.path.join(ROOT, "data", "offers.json"), encoding="utf-8"))
money = lambda n: "${:,}".format(n)
PK = [money(p["price"]) for p in D["packages"]]
ok = 0; bad = []
def check(name, cond, detail=""):
    global ok
    if cond: ok += 1
    else: bad.append("%s %s" % (name, detail))

TXT = "(sel)=>[...document.querySelectorAll(sel)].map(e=>e.textContent.replace(/\\s+/g,' ').trim())"
WID = "(sel)=>[...document.querySelectorAll(sel)].map(e=>e.getBoundingClientRect().width)"
PRICES = ".item-p,.price,.prow-p,.total-n,.total-s b"

with sync_playwright() as p:
    # A true 2x screen, like a phone. (Plain emulation rounds a 1.5px outline down to 1px, which real phones do not.)
    br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--force-device-scale-factor=2"])
    br1 = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])  # an ordinary 1x desktop screen

    # ---------- home page, phone, normal motion ----------
    c = br.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, has_touch=True)
    pg = c.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)  # the Wix form cannot load in this sandbox
    pg.goto(B + "/index.html", wait_until="load"); pg.wait_for_timeout(500)
    cells = lambda: pg.evaluate("document.querySelectorAll('.reel-c').length")
    before_t, before_w = pg.evaluate(TXT, "#price .item-p"), pg.evaluate(WID, "#price .item-p")
    check("home shows the three package prices", before_t[:3] == PK, str(before_t[:3]))
    check("nothing rolls before the prices are on screen", pg.evaluate("document.querySelectorAll('#price .reel-c').length") == 0)
    check("three package boxes", pg.locator("#price .boxes .box").count() == 3)
    check("popular box is marked", pg.locator("#price .boxes .box.pop").count() == 1 and "Growth" in pg.inner_text("#price .boxes .box.pop"))
    check("add-ons and care sit in grouped boxes", pg.locator("#price .box.group").count() == 2 and pg.locator("#price .box.group .item").count() == 4)
    check("boxes are links to the packages page", pg.get_attribute("#price .boxes .box >> nth=0", "href") == "/pricing.html#p-launch")
    bw = pg.evaluate("getComputedStyle(document.querySelector('#price .box')).borderTopWidth")
    check("box outline is 1.5px", bw == "1.5px", bw)
    pg.evaluate("document.querySelector('#price').scrollIntoView()"); pg.wait_for_timeout(560)
    check("prices roll once on screen", pg.evaluate("document.querySelectorAll('#price .reel-c').length") >= 12, str(cells()))
    sr = pg.evaluate(TXT, "#price .sr")
    check("screen readers still get the real price while it rolls", sr[:3] == PK, str(sr[:3]))
    check("the rolling digits are hidden from screen readers", pg.evaluate("[...document.querySelectorAll('#price .reel-c')].every(c=>c.closest('[aria-hidden=true]'))"))
    mid_w = pg.evaluate(WID, "#price .item-p")
    check("no width jump while rolling", all(abs(a - b) < 0.6 for a, b in zip(before_w, mid_w)), str([round(a - b, 2) for a, b in zip(before_w, mid_w)]))
    pg.wait_for_timeout(1500)
    check("box lights when the price lands", pg.locator("#price .box.lit").count() >= 1)
    pg.wait_for_timeout(1900)
    after_t, after_w = pg.evaluate(TXT, "#price .item-p"), pg.evaluate(WID, "#price .item-p")
    check("prices are exactly as before after the roll", after_t == before_t, str(after_t))
    check("widths are exactly as before after the roll", all(abs(a - b) < 0.05 for a, b in zip(before_w, after_w)))
    check("roll parts are removed", pg.evaluate("document.querySelectorAll('#price .reel-c,#price .sr').length") == 0)
    check("light goes off again", pg.locator("#price .box.lit").count() == 0)
    check("boxes on screen are revealed", pg.evaluate("[...document.querySelectorAll('#price .boxes .box.rv')].every(b=>b.classList.contains('in')&&getComputedStyle(b).opacity==='1')"))
    # scrolling back does not roll again
    pg.evaluate("scrollTo(0,0)"); pg.wait_for_timeout(200); pg.evaluate("document.querySelector('#price').scrollIntoView()"); pg.wait_for_timeout(400)
    check("rolls only once", pg.evaluate("document.querySelectorAll('#price .reel-c').length") == 0)

    # ---------- calculator total ----------
    pg.goto(B + "/index.html", wait_until="load"); pg.wait_for_timeout(400)
    pg.evaluate("document.querySelector('#worth .total').scrollIntoView({block:'center'})"); pg.wait_for_timeout(450)
    check("calculator total rolls", pg.evaluate("document.querySelectorAll('#cYear .reel-c').length") == 6)
    pg.wait_for_timeout(2600)
    check("calculator total is right after the roll", pg.inner_text("#cYear") == "$172,800", pg.inner_text("#cYear"))
    check("monthly figure is right after the roll", pg.inner_text("#cMonth") == "$14,400", pg.inner_text("#cMonth"))
    pg.fill("#cJob", "5000"); pg.wait_for_timeout(700)
    check("calculator still updates after the roll", pg.inner_text("#cYear") == "$72,000", pg.inner_text("#cYear"))
    # change a number in the middle of a roll: the new number wins and nothing is left behind
    pg.goto(B + "/index.html", wait_until="load"); pg.wait_for_timeout(400)
    pg.evaluate("document.querySelector('#worth .total').scrollIntoView({block:'center'})"); pg.wait_for_timeout(350)
    pg.fill("#cJob", "2000"); pg.wait_for_timeout(2600)
    check("changing a number mid-roll gives the new total", pg.inner_text("#cYear") == "$28,800", pg.inner_text("#cYear"))
    check("no roll parts left in the calculator", pg.evaluate("document.querySelectorAll('#worth .reel-c,#worth .sr').length") == 0)
    check("calculator box has the strong outline", pg.evaluate("getComputedStyle(document.querySelector('#worth .total')).borderTopWidth") == "1.5px")

    # ---------- care plans: switch monthly / yearly during and after a roll ----------
    pg.goto(B + "/care-plans.html", wait_until="load"); pg.wait_for_timeout(400)
    first = "document.querySelector('.plan .price').textContent.replace(/\\s+/g,'')"
    pg.evaluate("document.querySelector('.plan .price').scrollIntoView({block:'center'})"); pg.wait_for_timeout(400)
    rolling = pg.evaluate("document.querySelectorAll('.plan .reel-c').length")
    check("care plan prices roll", rolling >= 2, str(rolling))
    pg.click('.seg [data-value="yearly"]'); pg.wait_for_timeout(2600)
    yearly = money(D["carePlans"][0]["yearlyTotal"]) + "/yr"
    check("yearly switch mid-roll shows the yearly price", pg.evaluate(first) == yearly, pg.evaluate(first))
    pg.click('.seg [data-value="monthly"]'); pg.wait_for_timeout(700)
    check("back to monthly", pg.evaluate(first) == money(D["carePlans"][0]["monthly"]) + "/mo", pg.evaluate(first))
    check("no roll parts left on care plans", pg.evaluate("document.querySelectorAll('.reel-c').length") == 0)
    check("plan cards have the strong outline", pg.evaluate("getComputedStyle(document.querySelector('.card.plan')).borderTopWidth") == "1.5px")

    # ---------- packages page: cards roll, also the ones you swipe to ----------
    pg.goto(B + "/pricing.html", wait_until="load"); pg.wait_for_timeout(400)
    pg.evaluate("document.querySelector('#p-launch .price').scrollIntoView({block:'center'})"); pg.wait_for_timeout(450)
    check("first package card rolls", pg.evaluate("document.querySelectorAll('#p-launch .reel-c').length") == 4)
    check("the card you have not swiped to waits", pg.evaluate("document.querySelectorAll('#p-premium .reel-c').length") == 0)
    pg.wait_for_timeout(2400)
    pg.evaluate("document.querySelector('.row.swipe').scrollToCard(2)"); pg.wait_for_timeout(500)
    check("swiping to a card rolls its price", pg.evaluate("document.querySelectorAll('#p-premium .reel-c').length") == 4)
    pg.wait_for_timeout(2400)
    check("package prices right after rolling", pg.evaluate(TXT, ".pkg .price")[:3] == PK, str(pg.evaluate(TXT, ".pkg .price")[:3]))
    check("package cards have the strong outline", pg.evaluate("getComputedStyle(document.querySelector('#p-launch')).borderTopWidth") == "1.5px")
    check("popular card uses the accent outline", pg.evaluate("getComputedStyle(document.querySelector('#p-growth')).borderTopColor") == pg.evaluate("getComputedStyle(document.querySelector('#p-growth .btn-primary')).backgroundColor"))

    # ---------- every page: scroll through, nothing left behind, no errors, text unchanged ----------
    pages = ["index.html", "es.html", "pricing.html", "care-plans.html", "contact.html", "faq.html", "pay-deposit.html", "thank-you.html",
             "privacy-policy.html", "web-design-elgin.html", "web-design-bartlett.html", "web-design-st-charles.html"]
    for page in pages:
        pg.goto(B + "/" + page, wait_until="load"); pg.wait_for_timeout(2700)  # let anything on the first screen finish rolling
        t0 = pg.evaluate(TXT, PRICES)
        check("first-screen rolls finish on " + page, cells() == 0, str(cells()))
        h = pg.evaluate("document.documentElement.scrollHeight")
        y = 0
        while y < h:
            pg.evaluate("scrollTo(0,%d)" % y); pg.wait_for_timeout(120); y += 500
        pg.wait_for_timeout(2900)
        t1 = pg.evaluate(TXT, PRICES)
        check("prices unchanged after scrolling " + page, t0 == t1 and all(re.search(r"\d", t) for t in t1), str([(a, b) for a, b in zip(t0, t1) if a != b][:3]))
        check("nothing left rolling on " + page, cells() == 0, str(cells()))
        check("nothing hidden on " + page, pg.evaluate("[...document.querySelectorAll('.rv')].filter(e=>e.offsetParent&&e.getBoundingClientRect().left<innerWidth-8&&getComputedStyle(e).opacity!=='1').length") == 0)  # cards still off to the side wait for the swipe
        check("no sideways scroll on " + page, pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth") == 0)
    es = pg.goto(B + "/es.html", wait_until="load"); pg.wait_for_timeout(300)
    check("Spanish care price intact", "desde $99/mes" in " ".join(pg.evaluate(TXT, "#price .item-p")))
    check("town page rows sit in a box", (pg.goto(B + "/web-design-elgin.html"), pg.evaluate("getComputedStyle(document.querySelector('.prows')).borderTopWidth"))[1] == "1.5px")
    check("no page errors", not errs, str(errs[:4]))
    c.close()

    # ---------- desktop ----------
    c = br1.new_context(viewport={"width": 1280, "height": 800})
    pg = c.new_page(); pg.goto(B + "/index.html", wait_until="load"); pg.wait_for_timeout(1300)
    check("sample phone is marked in", pg.evaluate("document.querySelector('.phone').classList.contains('in')"))
    check("sample content fully visible after build-in", pg.evaluate("[...document.querySelectorAll('.ps>*')].every(e=>getComputedStyle(e).opacity==='1')"))
    tops = pg.evaluate("[...document.querySelectorAll('#price .boxes .item-p')].map(e=>Math.round(e.getBoundingClientRect().top))")
    check("desktop: three prices on one line", len(set(tops)) == 1, str(tops))
    chips = pg.evaluate("[...document.querySelectorAll('#price .boxes .item-s')].map(e=>Math.round(e.getBoundingClientRect().top))")
    check("desktop: chips line up", len(set(chips)) == 1, str(chips))
    check("desktop no sideways scroll", pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth") == 0)
    check("ordinary desktop screens get a 2px outline", pg.evaluate("getComputedStyle(document.querySelector('#price .box')).borderTopWidth") == "2px")
    c.close()

    # ---------- reduced motion: nothing moves, everything is there ----------
    c = br.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
    pg = c.new_page(); pg.goto(B + "/index.html", wait_until="load"); pg.wait_for_timeout(300)
    check("reduced motion: boxes visible at once", pg.evaluate("[...document.querySelectorAll('.box.rv')].every(b=>getComputedStyle(b).opacity==='1')"))
    check("reduced motion: sample visible at once", pg.evaluate("[...document.querySelectorAll('.ps>*')].every(e=>getComputedStyle(e).opacity==='1')"))
    pg.evaluate("document.querySelector('#price').scrollIntoView()"); pg.wait_for_timeout(450)
    check("reduced motion: prices do not roll", pg.evaluate("document.querySelectorAll('.reel-c').length") == 0)
    check("reduced motion: prices shown", pg.evaluate(TXT, "#price .item-p")[:3] == PK)
    c.close()

    # ---------- scripts off ----------
    c = br.new_context(viewport={"width": 390, "height": 844}, java_script_enabled=False)
    pg = c.new_page(); pg.goto(B + "/index.html", wait_until="load")
    check("scripts off: boxes and prices visible", pg.is_visible("#price .box") and pg.inner_text("#price .box >> nth=0 >> .item-p") == PK[0])
    check("scripts off: sample visible", pg.is_visible("#psName"))
    pg.goto(B + "/pricing.html", wait_until="load")
    check("scripts off: package cards visible", pg.is_visible("#p-launch .price"))
    c.close()

    # ---------- a browser that never reports what is on screen: everything still shows ----------
    c = br.new_context(viewport={"width": 390, "height": 844})
    c.add_init_script("window.IntersectionObserver=function(){this.observe=function(){};this.unobserve=function(){};this.disconnect=function(){}};")
    pg = c.new_page(); pg.goto(B + "/pricing.html", wait_until="load"); pg.wait_for_timeout(2700)
    check("safety net shows the boxes", pg.evaluate("[...document.querySelectorAll('.card.rv')].every(b=>getComputedStyle(b).opacity==='1')"))
    c.close()

    # ---------- no sideways scroll, at seven widths, on a true 2x screen ----------
    for w in (320, 344, 360, 390, 430, 900, 1280):
        c = br.new_context(viewport={"width": w, "height": 844}, device_scale_factor=2, has_touch=True, reduced_motion="reduce")
        pg = c.new_page(); over = []
        for page in ("index.html", "es.html", "pricing.html", "care-plans.html", "contact.html", "pay-deposit.html", "faq.html", "web-design-elgin.html", "thank-you.html", "privacy-policy.html"):
            pg.goto(B + "/" + page, wait_until="load"); pg.wait_for_timeout(100)
            o = pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
            if o: over.append("%s:%d" % (page, o))
        check("no sideways scroll at %dpx" % w, not over, str(over))
        if w <= 430:
            m = pg.goto(B + "/index.html") and pg.evaluate("innerWidth-document.querySelector('.hdr-m').getBoundingClientRect().right")
            check("header buttons keep a margin at %dpx" % w, m >= 13.5, str(m))
        c.close()
    br.close(); br1.close()

print("passed", ok, "failed", len(bad))
for b in bad: print("  FAIL", b)
sys.exit(1 if bad else 0)
