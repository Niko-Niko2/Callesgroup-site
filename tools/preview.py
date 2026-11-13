#!/usr/bin/env python3
"""Makes a copy of the built site that works from any folder, for private previews.

  python3 tools/build.py && python3 tools/preview.py

Output: _preview/ (not committed, not published). Differences from the real site:
  - every /root link becomes a relative link, so the copy works without a web server at the domain root
  - every page is marked noindex and carries a "Preview. Not live." bar with two sample pitch links
  - the Wix quote form is replaced by a note, because it only loads on the real domain
"""
import os
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_preview")
BAR = ('<div style="background:#1E1E1E;border-bottom:1px solid #2E2C29;padding:9px 16px;font:600 13px/1.4 Montserrat,Arial,sans-serif;color:#A8A49E;display:flex;flex-wrap:wrap;gap:6px 18px;align-items:center">'
       '<span>Preview. Not live.</span>'
       '<a href="index.html?b=Aguilera%27s+Painters&amp;t=painting&amp;c=Bartlett&amp;p=1" style="color:#C9A962">Open as a pitch link</a>'
       '<a href="es.html?b=Aguilera%27s+Painters&amp;t=painting&amp;c=Bartlett&amp;p=1" style="color:#C9A962">En espa&ntilde;ol</a></div>')
NOTE = ('<script>document.getElementById("quote").innerHTML=\'<p style="padding:8px 0 24px"><b>The quote form loads here on the real site.</b> '
        'It is the same Wix form that is live today, so leads keep landing in Wix.</p>\';</script>')


def rel(m):
    attr, url = m.group(1), m.group(2)
    if url == "/":
        return '%s="index.html"' % attr
    if url.startswith("/#"):
        return '%s="index.html%s"' % (attr, url[1:])
    return '%s="%s"' % (attr, url[1:])


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(os.path.join(OUT, "assets", "fonts"))
    n = 0
    for f in sorted(os.listdir(ROOT)):
        if not f.endswith(".html") or f == "palette-preview.html" or f.endswith("-bundle.html"):
            continue
        t = open(os.path.join(ROOT, f), encoding="utf-8").read()
        t = re.sub(r'\b(href|src)="(/[^"/][^"]*|/#[^"]*|/)"', rel, t)
        t = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex, nofollow">', t)
        t = re.sub(r'<link rel="(canonical|alternate)"[^>]*>\n', "", t)
        t = t.replace('location.assign("/thank-you.html")', 'location.assign("thank-you.html")')
        t = re.sub(r'<script type="module">[\s\S]*?</script>', NOTE, t)
        t = re.sub(r"(<body>\n)", r"\1" + BAR.replace("\\", "\\\\") + "\n", t, count=1)
        if f == "index.html":  # the preview gets its own name so it is easy to tell from the real site
            t = re.sub(r"<title>.*?</title>", "<title>Calles Group Site Preview</title>", t, count=1)
        open(os.path.join(OUT, f), "w", encoding="utf-8").write(t)
        n += 1
    css = open(os.path.join(ROOT, "assets", "styles.css"), encoding="utf-8").read().replace("url(/assets/fonts/", "url(fonts/")
    open(os.path.join(OUT, "assets", "styles.css"), "w", encoding="utf-8").write(css)
    for f in ("site.js", "tools.js"):
        shutil.copy(os.path.join(ROOT, "assets", f), os.path.join(OUT, "assets", f))
    for f in os.listdir(os.path.join(ROOT, "assets", "fonts")):
        shutil.copy(os.path.join(ROOT, "assets", "fonts", f), os.path.join(OUT, "assets", "fonts", f))
    for f in ("favicon.svg", "og-image.png"):
        shutil.copy(os.path.join(ROOT, f), os.path.join(OUT, f))
    print("preview copy:", n, "pages in", OUT)


if __name__ == "__main__":
    main()
