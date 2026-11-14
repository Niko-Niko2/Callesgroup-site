#!/usr/bin/env python3
"""Color options for the PRIVATE preview. Temporary: delete this file once a look is chosen and its colors are
moved into the tokens at the top of assets/styles.css.

  python3 tools/build.py && python3 tools/preview.py && python3 tools/looks.py     adds the switcher to _preview/
  python3 tools/looks.py --check                                                    prints the contrast of every option

What it does to the preview copy (never to the real pages):
  - writes _preview/assets/looks.css: one set of color tokens per option, switched by <html data-look="a">
  - swaps the preview bar for one with a button per option
  - adds a small floating control so the options can be flipped from anywhere on a page
The choice is remembered in the viewer's own browser only. With no data-look the page is the normal build.

Each option is the same eleven tokens the stylesheet already uses. A two-tone option (frame=) gives the header,
the top section of each page, the closing band and the footer their own dark set."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREVIEW = os.path.join(ROOT, "_preview")

TOKENS = ("bg", "band", "surface", "field", "line", "line-2", "ink", "muted", "accent", "accent-hover", "on-accent")

THEMES = [
    dict(id="a", letter="A", name="Paper & Cobalt", feel="Bank clean. Light page, one blue button.", scheme="light",
         t=dict(zip(TOKENS, "#F9F8F4 #F1EFE8 #FFFFFF #FFFFFF #E3E0D6 #ACA79B #14171C #5A606B #1B45D4 #1535A8 #FFFFFF".split()))),
    dict(id="b", letter="B", name="Stone & Wine", feel="Warm, established, least expected.", scheme="light",
         t=dict(zip(TOKENS, "#F4F1EA #EBE6DC #FBF9F4 #FFFFFF #DFD8CA #ADA392 #1E1A18 #645B54 #7F1D2D #651623 #FFF9F3".split()))),
    dict(id="c", letter="C", name="Chalk & Ink", feel="No color at all. Black buttons on white.", scheme="light",
         t=dict(zip(TOKENS, "#FFFFFF #F5F5F2 #F7F7F4 #FFFFFF #E5E5E0 #AFAFA8 #111111 #5C5C58 #111111 #3A3A3A #FFFFFF".split()))),
    dict(id="d", letter="D", name="Midnight & Ice", feel="Deep navy, pale blue button. Calm.", scheme="dark",
         t=dict(zip(TOKENS, "#0A1424 #0D192C #122038 #08101D #1D2E49 #334766 #EDF1F7 #A0AEC4 #8FC0FF #B4D5FF #0A1424".split()))),
    dict(id="e", letter="E", name="Graphite & Bone", feel="Your graphite, gold removed. Smallest change.", scheme="dark",
         t=dict(zip(TOKENS, "#151515 #1A1918 #1E1E1E #121212 #2E2C29 #45413B #EDEAE6 #A8A49E #EDEAE6 #FFFFFF #151515".split()))),
    dict(id="f", letter="F", name="Fog & Teal", feel="Cool and fresh. Softer than blue.", scheme="light",
         t=dict(zip(TOKENS, "#F2F5F5 #E8EDED #FFFFFF #FFFFFF #DAE1E1 #9FACAD #0F1E20 #53646A #0B6A72 #08545B #FFFFFF".split()))),
    dict(id="g", letter="G", name="Midnight & Paper", feel="Navy first screen, light body.", scheme="light",
         t=dict(zip(TOKENS, "#F9F8F4 #F1EFE8 #FFFFFF #FFFFFF #E3E0D6 #ACA79B #14171C #5A606B #1B45D4 #1535A8 #FFFFFF".split())),
         frame=dict(zip(TOKENS, "#0A1424 #0D192C #122038 #08101D #1D2E49 #334766 #EDF1F7 #A0AEC4 #8FC0FF #B4D5FF #0A1424".split()))),
    # --- greens (second round) ---
    dict(id="h", letter="H", name="Linen & Moss", feel="Moss green on a light page.", scheme="light",
         t=dict(zip(TOKENS, "#F6F5EE #EDECE2 #FFFFFF #FFFFFF #E1E0D3 #A8A996 #1A1D16 #5A5F51 #4D6630 #3D5325 #FFFFFF".split()))),
    dict(id="i", letter="I", name="Sage & Evergreen", feel="The whole page leans green.", scheme="light",
         t=dict(zip(TOKENS, "#EDF1EA #E3E9DF #F9FBF7 #FFFFFF #D5DDD0 #9CA897 #142019 #4F5E55 #1F5A44 #174735 #FFFFFF".split()))),
    dict(id="j", letter="J", name="Evergreen & Paper", feel="Green first screen, light body.", scheme="light",
         t=dict(zip(TOKENS, "#F8F7F2 #EFEEE6 #FFFFFF #FFFFFF #E2E0D5 #A9A899 #141A16 #586058 #1F6B4A #175538 #FFFFFF".split())),
         frame=dict(zip(TOKENS, "#0E2A20 #113025 #17392D #0A2019 #23473A #3A6252 #EEF3EC #A5B8AC #A8DDB9 #C6EBD2 #0E2A20".split())), dark=("#price",)),
    dict(id="k", letter="K", name="Evergreen & Mint", feel="Deep green all the way down.", scheme="dark",
         t=dict(zip(TOKENS, "#0E2A20 #113025 #17392D #0A2019 #23473A #3A6252 #EEF3EC #A5B8AC #A8DDB9 #C6EBD2 #0E2A20".split()))),
]
BY_ID = {t["id"]: t for t in THEMES}
FRAME = (".hdr", ".hero", ".cta-band", ".ftr")  # the parts that take the second (dark) token set in a two-tone theme


def css(th, root=":root"):
    """Override CSS for one option. root is the selector that carries the tokens (':root' or 'html[data-look=a]')."""
    t = th["t"]
    light = th["scheme"] == "light"
    loss = ";--loss:#B92A18" if light else ""
    out = ["%s{%s%s;color-scheme:%s}" % (root, ";".join("--%s:%s" % (k, t[k]) for k in TOKENS), loss, th["scheme"])]
    if light:
        out.append("%s .phone{box-shadow:0 0 0 1px var(--line-2),0 34px 60px -34px rgba(20,22,30,.38)}" % root)
        out.append("%s #quote .form-error,%s #quote .form-form-error{color:#B3261E}" % (root, root))
        out.append("%s #quote .form-control[aria-invalid=\"true\"]{border-color:#B3261E}" % root)
    if th.get("frame"):
        f = th["frame"]
        sel = ",".join("%s %s" % (root, x) for x in FRAME)
        dark = ";".join("--%s:%s" % (k, f[k]) for k in TOKENS) + ";--loss:#FF7A6E"
        out.append("%s{%s;color:var(--ink);color-scheme:dark}" % (sel, dark))
        # A test on some looks: named sections go dark too, and the boxes inside keep the light set so they stand out.
        for sec in th.get("dark", ()):
            out.append("%s %s{%s;background:var(--bg);color:var(--ink);color-scheme:dark}" % (root, sec, dark))
            out.append("%s %s .box{%s;--loss:#B92A18;color:var(--ink);color-scheme:light}" % (root, sec, ";".join("--%s:%s" % (k, t[k]) for k in TOKENS)))
        out.append("%s .hero,%s .ftr{background:var(--bg)}" % (root, root))
        out.append("%s .ftr{border-top-color:var(--line)}" % root)
        out.append("%s .hero .phone{box-shadow:0 0 0 1px var(--line-2),0 34px 60px -34px rgba(0,0,0,.9)}" % root)
    # the check mark inside a chosen form option follows the text-on-accent color
    tick = t["on-accent"].replace("#", "%23")
    out.append("%s #quote .form-choice--selected::before{background-image:url(\"data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%%3E%%3Cpath d='M4 8.5l2.5 2.5L12 5.5' fill='none' stroke='%s' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'/%%3E%%3C/svg%%3E\")}" % (root, tick))
    return "\n".join(out)



# ---- contrast (WCAG 2.x relative luminance) ----
def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check(th):
    t = th["t"]
    rows = []
    for fg, need in (("ink", 7.0), ("muted", 4.5), ("accent", 4.5)):
        for bgk in ("bg", "band", "surface"):
            rows.append(("%s on %s" % (fg, bgk), ratio(t[fg], t[bgk]), need))
    rows.append(("on-accent on accent", ratio(t["on-accent"], t["accent"]), 4.5))
    rows.append(("on-accent on accent-hover", ratio(t["on-accent"], t["accent-hover"]), 4.5))
    rows.append(("ink on field", ratio(t["ink"], t["field"]), 7.0))
    rows.append(("muted (placeholder) on field", ratio(t["muted"], t["field"]), 4.5))
    if th.get("frame"):
        f = th["frame"]
        for fg, need in (("ink", 7.0), ("muted", 4.5), ("accent", 4.5)):
            for bgk in ("bg", "band", "surface"):
                rows.append(("frame %s on %s" % (fg, bgk), ratio(f[fg], f[bgk]), need))
        rows.append(("frame on-accent on accent", ratio(f["on-accent"], f["accent"]), 4.5))
    info = [("field border vs field", ratio(t["line-2"], t["field"])), ("field border vs surface", ratio(t["line-2"], t["surface"])),
            ("button vs page", ratio(t["accent"], t["bg"]))]
    return rows, info



# ---- the switcher added to the preview copy ----
NOW = ("", "Now", "Graphite & Gold", "#151515")
LOOKS = [NOW] + [(t["id"], t["letter"], t["name"], (t.get("frame") or t["t"])["bg"]) for t in THEMES]

TOOL_CSS = """
/* preview tools: neutral on purpose, they are not part of the site */
.pv{background:#101010;color:#C9C9C6;font:600 13px/1.4 Montserrat,Arial,sans-serif;padding:10px 16px;display:grid;gap:8px;border-bottom:1px solid #2A2A2A}
.pv-row{display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center}
.pv b{color:#fff;font-weight:700}
.pv a{color:#fff;font-weight:600;text-underline-offset:3px}
.pv-looks{gap:4px}
.pv-looks button{min-width:38px;height:38px;padding:0 10px;border-radius:9px;border:1px solid #3A3A3A;background:transparent;color:#fff;font:700 13px/1 Montserrat,Arial,sans-serif;cursor:pointer}
.pv-looks button[aria-pressed=true]{background:#fff;color:#101010;border-color:#fff}
.lk{position:fixed;left:50%;bottom:calc(12px + env(safe-area-inset-bottom,0px));transform:translateX(-50%);z-index:55;display:flex;align-items:center;gap:2px;padding:4px;border-radius:999px;background:#101010;color:#fff;border:1px solid #3A3A3A;box-shadow:0 10px 30px -10px rgba(0,0,0,.6);font:700 13px/1 Montserrat,Arial,sans-serif}
.lk button{width:44px;height:44px;border-radius:50%;border:0;background:transparent;color:#fff;font:700 22px/1 Montserrat,Arial,sans-serif;cursor:pointer;padding:0 0 3px}
.lk button:hover{background:#2A2A2A}
.lk span{min-width:176px;text-align:center;white-space:nowrap;padding:0 4px}
@media print{.pv,.lk{display:none}}
"""


EARLY = ('<script>(function(){var v=null;try{v=localStorage.getItem("cg-look")}catch(e){}'
         'try{var q=new URLSearchParams(location.search).get("look");if(q!==null)v=q}catch(e){}'
         'if(/^[%s]$/.test(v||""))document.documentElement.setAttribute("data-look",v)})();</script>' % "".join(t["id"] for t in THEMES))

BAR = ('<div class="pv"><div class="pv-row"><b>Preview. Not live.</b>'
       '<a href="index.html?b=Aguilera%27s+Painters&amp;t=painting&amp;c=Bartlett&amp;p=1">Pitch link</a>'
       '<a href="es.html?b=Aguilera%27s+Painters&amp;t=painting&amp;c=Bartlett&amp;p=1">Espa&ntilde;ol</a></div>'
       '<div class="pv-row pv-looks" role="group" aria-label="Try a color option">' +
       "".join('<button type="button" data-look="%s" aria-pressed="false" aria-label="%s">%s</button>' % (
           i, ("Current colors, " if not i else "Option %s, " % l) + n.replace("&", "and"), l) for i, l, n, _ in LOOKS) +
       '</div></div>')

PILL = ('<div class="lk" role="group" aria-label="Flip through color options">'
        '<button type="button" id="lkPrev" aria-label="Previous color option">&lsaquo;</button>'
        '<span id="lkName" aria-live="polite"></span>'
        '<button type="button" id="lkNext" aria-label="Next color option">&rsaquo;</button></div>\n'
        '<script>(function(){var LOOKS=%s,root=document.documentElement;'
        'function at(){var c=root.getAttribute("data-look")||"";for(var i=0;i<LOOKS.length;i++)if(LOOKS[i][0]===c)return i;return 0}'
        'function paint(){var L=LOOKS[at()];document.getElementById("lkName").textContent=L[1]+": "+L[2];'
        '[].forEach.call(document.querySelectorAll(".pv-looks button"),function(b){b.setAttribute("aria-pressed",b.getAttribute("data-look")===L[0]?"true":"false")});'
        'var m=document.querySelector(\'meta[name="theme-color"]\');if(m)m.setAttribute("content",L[3])}'
        'function set(v){if(v)root.setAttribute("data-look",v);else root.removeAttribute("data-look");try{localStorage.setItem("cg-look",v)}catch(e){}paint()}'
        'document.querySelector(".pv-looks").addEventListener("click",function(e){var b=e.target.closest("button");if(b)set(b.getAttribute("data-look"))});'
        'document.getElementById("lkPrev").addEventListener("click",function(){set(LOOKS[(at()+LOOKS.length-1)%%LOOKS.length][0])});'
        'document.getElementById("lkNext").addEventListener("click",function(){set(LOOKS[(at()+1)%%LOOKS.length][0])});'
        'if(document.getElementById("est"))document.querySelector(".lk").style.bottom="78px";paint()})();</script>\n') % json.dumps([list(x) for x in LOOKS])


OLD_BAR = re.compile(r'<div style="background:#1E1E1E;border-bottom:1px solid #2E2C29;[^>]*>.*?</div>', re.S)
LINK = '<link rel="stylesheet" href="assets/styles.css">'


def add_to_preview():
    css_text = "/* Color options for the private preview. Not part of the site. */\n"
    css_text += "\n".join(css(t, 'html[data-look="%s"]' % t["id"]) for t in THEMES) + "\n" + TOOL_CSS
    open(os.path.join(PREVIEW, "assets", "looks.css"), "w", encoding="utf-8").write(css_text)
    n = 0
    for f in sorted(os.listdir(PREVIEW)):
        if not f.endswith(".html"):
            continue
        p = os.path.join(PREVIEW, f)
        t = open(p, encoding="utf-8").read()
        assert t.count(LINK) == 1 and len(OLD_BAR.findall(t)) == 1 and t.count("</body>") == 1, f
        t = t.replace(LINK, LINK + '\n<link rel="stylesheet" href="assets/looks.css">\n' + EARLY)
        t = OLD_BAR.sub(lambda m: BAR, t)
        t = t.replace("</body>", PILL + "</body>")
        open(p, "w", encoding="utf-8").write(t)
        n += 1
    print("color options added to", n, "preview pages:", " ".join(t["letter"] for t in THEMES))


if __name__ == "__main__":
    if "--check" in sys.argv:
        bad = 0
        for th in THEMES:
            rows, info = check(th)
            fails = [(n, r, need) for n, r, need in rows if r < need]
            bad += len(fails)
            print("%s %-18s lowest contrast %.2f  %s" % (th["letter"], th["name"], min(r for _, r, _ in rows),
                                                          "all pass" if not fails else "FAIL: " + ", ".join("%s %.2f<%.1f" % f for f in fails)))
        sys.exit(1 if bad else 0)
    add_to_preview()
