(function () {
  // Old one-page links (/#pricing) go to the real page.
  var old = { pricing: "/pricing.html", faq: "/faq.html", contact: "/contact.html",
    "bundle-launch": "/launch-bundle.html", "bundle-growth": "/growth-bundle.html", "bundle-premium": "/premium-bundle.html",
    websites: "/pricing.html#websites", bundles: "/pricing.html#bundles", branding: "/pricing.html#branding",
    addons: "/pricing.html#addons", care: "/care-plans.html" };
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

  // Sticky phone button steps aside while the page's own hero or final buttons or the footer are on screen,
  // so it never sits on top of them.
  var mcta = document.getElementById("mcta");
  var ends = document.querySelectorAll("#heroBtns, #final, footer");
  if (mcta && ends.length && "IntersectionObserver" in window) {
    var seen = new Set();
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { e.isIntersecting ? seen.add(e.target) : seen.delete(e.target); });
      mcta.classList.toggle("mcta-off", seen.size > 0);
    });
    ends.forEach(function (el) { io.observe(el); });
  }
})();
