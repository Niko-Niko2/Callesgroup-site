#!/usr/bin/env python3
"""Browser tests for the selling tools. Run against a local server on :8765."""
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
B = "http://localhost:8765"; fails = []
def ok(name, cond, got=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -> " + str(got)[:200]))
    if not cond: fails.append(name)
def body(href): return unquote(href.split("body=")[1])
with sync_playwright() as p:
    br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    def page(w=390, h=844):
        c = br.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce"); pg = c.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e))); pg.errs = errs; return pg
    # 1. sample site follows the form
    pg = page(); pg.goto(B + "/index.html"); pg.wait_for_timeout(300)
    ok("default sample name", pg.inner_text("#psName") == "Your Business Name", pg.inner_text("#psName"))
    pg.fill("#dBiz", "Garcia Roofing"); pg.fill("#dTown", "South Elgin")
    ok("name lands in the phone", pg.inner_text("#psName") == "Garcia Roofing")
    ok("town lands in the phone", "South Elgin" in pg.inner_text("#psKick") and "South Elgin" in pg.inner_text("#psFoot"), pg.inner_text("#psKick"))
    pg.click("#dTrades button[data-k=painting]")
    ok("trade switches the sample", pg.inner_text("#psS1") == "Interior painting" and pg.inner_text("#psKick").startswith("Painting in"), pg.inner_text("#psKick"))
    ok("demo text message", body(pg.get_attribute("#demoText", "href")) == "Hi Andrew, it's Garcia Roofing. I saw the sample site for my painting business in South Elgin. I'd like a free quote call.", body(pg.get_attribute("#demoText", "href")))
    ok("sms link format", pg.get_attribute("#demoText", "href").startswith("sms:+13126000590?&body="))
    pg.click(".sw[data-pal='3']"); ok("color swatch applies", pg.get_attribute("#ps", "data-pal") == "3")
    # 2. calculator math
    ok("trade sets starting job value", pg.input_value("#cJob") == "3500", pg.input_value("#cJob"))
    ok("year total 4 calls x 3/10 x $3,500 x 12", pg.inner_text("#cYear") == "$50,400", pg.inner_text("#cYear"))
    ok("month total", pg.inner_text("#cMonth") == "$4,200", pg.inner_text("#cMonth"))
    ok("jobs a month", pg.inner_text("#cJobs") == "1.2", pg.inner_text("#cJobs"))
    ok("payback line (Launch)", "about 11 days" in pg.inner_text("#cPay") and "$1,500" in pg.inner_text("#cPay") and "1 job." in pg.inner_text("#cPay"), pg.inner_text("#cPay"))
    pg.click("#cPkgs button:nth-child(3)")
    ok("payback line (Premium $4,100: 29 days -> about 4 weeks, 2 jobs)", "about 4 weeks" in pg.inner_text("#cPay") and "$4,100" in pg.inner_text("#cPay") and "2 jobs." in pg.inner_text("#cPay"), pg.inner_text("#cPay"))
    pg.fill("#cJob", "800"); pg.click("#cWinUp"); pg.click("#cWinUp")
    pg.evaluate("document.getElementById('cCalls').value=10;document.getElementById('cCalls').dispatchEvent(new Event('input'))")
    ok("custom numbers 10 x 5/10 x $800 x 12 = $48,000", pg.inner_text("#cYear") == "$48,000", pg.inner_text("#cYear"))
    pg.click("#dTrades button[data-k=roofing]")
    ok("typed job value survives a trade change", pg.input_value("#cJob") == "800", pg.input_value("#cJob"))
    ok("calc text message", "average job $800, 10 extra calls a month, about $48,000 a year" in body(pg.get_attribute("#cText", "href")), body(pg.get_attribute("#cText", "href")))
    ok("no script errors on home", not pg.errs, pg.errs)
    # 3. booking: Andrew's hours (weekdays from 6pm, weekends from 3pm), name carried over from the home page
    pg.clock.install(time="2026-11-13T15:00:00")   # a Friday, 3pm
    pg.goto(B + "/contact.html"); pg.wait_for_timeout(400)
    ok("book side is the default", pg.is_visible("[data-bk]") and not pg.is_visible("#formCard"))
    ok("business name carried over", pg.input_value("#bkBiz") == "Garcia Roofing", pg.input_value("#bkBiz"))
    days = pg.locator("[data-bk-days] button").all_inner_texts()
    ok("six days, today first", len(days) == 6 and days[0] == "Today" and days[1] == "Sat, Nov 14", days)
    ok("weekday times start at 6pm", pg.locator("[data-bk-times] button").all_inner_texts() == ["6:00 PM", "7:00 PM", "8:00 PM"], pg.locator("[data-bk-times] button").all_inner_texts())
    ok("default summary", pg.inner_text("[data-bk-sum]") == "Today at 6:00 PM", pg.inner_text("[data-bk-sum]"))
    pg.click("[data-bk-days] button:nth-child(2)")
    ok("weekend times start at 3pm", pg.locator("[data-bk-times] button").all_inner_texts() == ["3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM"], pg.locator("[data-bk-times] button").all_inner_texts())
    pg.click("[data-bk-times] button:nth-child(2)")
    ok("summary shows the pick", pg.inner_text("[data-bk-sum]") == "Sat, Nov 14 at 4:00 PM", pg.inner_text("[data-bk-sum]"))
    ok("booking text message", body(pg.get_attribute("[data-bk-text]", "href")) == "Hi Andrew, it's Garcia Roofing. I'd like a free quote call Sat, Nov 14 at 4:00 PM.", body(pg.get_attribute("[data-bk-text]", "href")))
    ok("hours are stated on the page", "Weekdays after 6pm. Saturday and Sunday after 3pm." in pg.inner_text("[data-bk]"))
    pg.click("[data-bk-form]"); pg.wait_for_timeout(500)
    ok("call-me opens the form side with the note ready", pg.is_visible("#formCard") and pg.evaluate("window.CG_CALL_NOTE") == "Please call me Sat, Nov 14 at 4:00 PM. Business: Garcia Roofing.", pg.evaluate("window.CG_CALL_NOTE"))
    pg.goto(B + "/contact.html?need=growth"); pg.wait_for_timeout(400)
    ok("package buttons open the form side", pg.is_visible("#formCard") and not pg.is_visible("[data-bk]") and "Growth website" in pg.inner_text("#needLine"))
    late = page(); late.clock.install(time="2026-11-13T19:30:00"); late.goto(B + "/contact.html"); late.wait_for_timeout(300)
    ok("tonight drops off once it is too late", late.locator("[data-bk-days] button").first.inner_text() == "Sat, Nov 14" and late.inner_text("[data-bk-sum]") == "Sat, Nov 14 at 3:00 PM", late.inner_text("[data-bk-sum]"))
    # 4. pitch links, in both languages, and hostile input
    pg = page(1280, 900); pg.goto(B + "/index.html?b=Aguilera%27s+Painters&t=painting&c=Bartlett&p=1"); pg.wait_for_timeout(300)
    ok("pitch link fills everything", pg.inner_text("#hello") == "Aguilera's Painters, this sample is for you." and pg.input_value("#dBiz") == "Aguilera's Painters" and pg.inner_text("#psFoot") == "Serving Bartlett and nearby towns" and pg.get_attribute("#ps", "data-pal") == "1" and pg.input_value("#cJob") == "3500", pg.inner_text("#hello"))
    pg = page(); pg.goto(B + "/es.html?b=Techos+Garc%C3%ADa&t=roofing&c=Elgin"); pg.wait_for_timeout(300)
    ok("Spanish pitch link", pg.inner_text("#hello") == "Hola, Techos García. Esta muestra es para usted." and pg.inner_text("#psCall") == "Llamar ahora" and "Techos en Elgin" in pg.inner_text("#psKick"), pg.inner_text("#hello"))
    ok("Spanish payback line", "se pagaría en" in pg.inner_text("#cPay") and "$1,500" in pg.inner_text("#cPay"), pg.inner_text("#cPay"))
    ok("Spanish booking text", body(pg.get_attribute("[data-bk-text]", "href")).startswith("Hola Andrew, soy de Techos García. Quiero una llamada gratis ") and " a las " in body(pg.get_attribute("[data-bk-text]", "href")), body(pg.get_attribute("[data-bk-text]", "href")))
    ok("Spanish hours note", "Entre semana después de las 6 pm" in pg.inner_text("[data-bk]"))
    ok("Spanish page lang and alternates", pg.get_attribute("html", "lang") == "es" and pg.locator('link[hreflang="en"]').count() == 1)
    ok("no script errors on es", not pg.errs, pg.errs)
    pg = page(); pg.goto(B + "/index.html?b=%3Cimg+src%3Dx+onerror%3Dwindow.__x%3D1%3E&t=nope&c=%3Cb%3E&p=9"); pg.wait_for_timeout(400)
    ok("hostile link is inert", pg.evaluate("window.__x") is None and pg.locator("#psName img").count() == 0 and pg.locator("#hello img").count() == 0 and "<" not in pg.input_value("#dBiz"), pg.input_value("#dBiz"))
    ok("bad trade and color fall back", pg.get_attribute("#ps", "data-pal") == "0" and pg.inner_text("#psKick").startswith("Roofing in"), pg.inner_text("#psKick"))
    # 5. keyboard and no-script
    pg = page(1280, 900); pg.goto(B + "/index.html"); pg.keyboard.press("Tab")
    ok("skip link is first", pg.evaluate("document.activeElement.className") == "skip")
    c = br.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844}); pg = c.new_page(); pg.goto(B + "/index.html")
    ok("reads with scripts off", pg.is_visible("h1") and pg.is_visible(".items") and pg.is_visible("#psName") and pg.is_visible(".acc-in"))
    pg.goto(B + "/pricing.html"); ok("package cards share the same three rows", pg.locator(".pkg .specs").count() == 3 and pg.locator("#p-growth .specs dd").all_inner_texts() == ["Up to 5", "2 to 3 weeks", "3"] and "Everything in Launch, plus:" in pg.inner_text("#p-growth"), pg.locator("#p-growth .specs dd").all_inner_texts())
    pg.goto(B + "/contact.html"); ok("contact shows both sides with scripts off", pg.is_visible("[data-bk]") and pg.is_visible("#formCard"))
    br.close()
print("\n%d failed" % len(fails) if fails else "\nall passed")
