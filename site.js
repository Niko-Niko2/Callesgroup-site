(function () {
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
