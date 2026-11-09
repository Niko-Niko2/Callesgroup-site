/* Calles Group site script. Everything here is an enhancement: pages read fine without it. */
(function () {
  var d = document, de = d.documentElement;
  de.classList.add("js");
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Old one-page links (/#pricing) go to the real page.
  var old = { pricing: "/pricing.html", faq: "/faq.html", contact: "/contact.html",
    "bundle-launch": "/launch-bundle.html", "bundle-growth": "/growth-bundle.html", "bundle-premium": "/premium-bundle.html",
    websites: "/pricing.html", bundles: "/pricing.html#bundles", branding: "/pricing.html#extras",
    addons: "/pricing.html#extras", care: "/care-plans.html" };
  var h = location.hash.slice(1);
  if ((location.pathname === "/" || location.pathname === "/index.html") && old[h]) { location.replace(old[h]); return; }

  // Header hairline after 8px of scroll.
  var hdr = d.querySelector(".hdr");
  if (hdr) {
    var onScroll = function () { hdr.classList.toggle("scrolled", scrollY > 8); };
    addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  // Full-height menu panel below 1100px.
  var nav = d.getElementById("nav"), mb = d.getElementById("menuBtn");
  if (nav && mb) {
    var setMenu = function (open) {
      nav.classList.toggle("open", open); mb.setAttribute("aria-expanded", open);
      d.body.style.overflow = open ? "hidden" : "";
      if (open) { var c = nav.querySelector(".nav-close"); c && c.focus(); } else mb.focus();
    };
    mb.addEventListener("click", function (e) { e.preventDefault(); setMenu(true); });
    nav.addEventListener("click", function (e) { if (e.target.closest(".nav-close")) setMenu(false); });
    d.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("open")) setMenu(false); });
  }

  // Segmented switches: <div class="seg" data-switch="name"> with buttons carrying data-value.
  // Elements with data-<name>-<value> attributes swap their text; .roll wrappers animate the change.
  function rollTo(el, text) {
    if (el.textContent === text) return;
    if (reduce || !el.classList.contains("roll")) { el.textContent = text; return; }
    var cur = el.firstElementChild || el;
    var next = d.createElement("span"); next.textContent = text; next.className = "in";
    if (cur === el) { el.textContent = ""; cur = d.createElement("span"); el.appendChild(cur); }
    el.appendChild(next);
    requestAnimationFrame(function () { cur.className = "out"; next.className = ""; });
    setTimeout(function () { cur.remove(); }, 360);
  }
  function placePill(seg) {
    var pill = seg.querySelector(".seg-pill"), on = seg.querySelector("[aria-pressed=true]");
    if (!pill || !on) return;
    pill.style.width = on.offsetWidth + "px";
    pill.style.transform = "translateX(" + (on.offsetLeft - 4) + "px)";
  }
  function applySwitch(seg, b, animate) {
    var name = seg.dataset.switch, v = b.dataset.value, attr = "data-" + name + "-" + v;
    seg.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); });
    placePill(seg);
    d.querySelectorAll("[" + attr + "]").forEach(function (el) {
      var t = el.getAttribute(attr);
      animate ? rollTo(el, t) : (el.textContent = t);
    });
    d.querySelectorAll("[data-" + name + "-href-" + v + "]").forEach(function (el) { el.href = el.getAttribute("data-" + name + "-href-" + v); });
    d.querySelectorAll("[data-" + name + "-show]").forEach(function (el) { el.hidden = el.getAttribute("data-" + name + "-show") !== v; });
  }
  d.querySelectorAll(".seg").forEach(function (seg) {
    var pill = d.createElement("span"); pill.className = "seg-pill"; pill.setAttribute("aria-hidden", "true");
    seg.prepend(pill);
    // A button with data-hash="bundles" is chosen when the page opens at #bundles.
    var start = (location.hash && seg.querySelector('[data-hash="' + location.hash.slice(1) + '"]')) || seg.querySelector("[aria-pressed=true]");
    applySwitch(seg, start, false);
    seg.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b || b.getAttribute("aria-pressed") === "true") return;
      applySwitch(seg, b, true);
    });
  });
  // A link to #book or #details on the same page flips the matching switch.
  addEventListener("hashchange", function () {
    var b = location.hash && d.querySelector('.seg [data-hash="' + location.hash.slice(1) + '"]');
    if (b) applySwitch(b.closest(".seg"), b, true);
  });
  addEventListener("resize", function () { d.querySelectorAll(".seg").forEach(placePill); });
  if (d.fonts) d.fonts.ready.then(function () { d.querySelectorAll(".seg").forEach(placePill); });

  // Before / after slider. A real range input drives it, so keyboards and screen readers work too.
  d.querySelectorAll(".ba").forEach(function (ba) {
    var r = ba.querySelector("input");
    var set = function (v) { ba.style.setProperty("--cut", v + "%"); };
    r.addEventListener("input", function () { ba.classList.remove("nudge"); set(r.value); });
    if (reduce) return;
    // One nudge on load to show it can be dragged.
    setTimeout(function () {
      ba.classList.add("nudge"); set(38);
      setTimeout(function () { set(50); setTimeout(function () { ba.classList.remove("nudge"); }, 460); }, 460);
    }, 700);
  });

  // Accordions and See-everything expanders. Inside .open-desktop they start open on wide screens.
  var wide = matchMedia("(min-width:760px)").matches;
  d.querySelectorAll(".acc-item").forEach(function (it) {
    var b = it.querySelector(".acc-btn");
    if (wide && it.closest(".open-desktop")) { it.classList.add("open"); b.setAttribute("aria-expanded", "true"); }
    b.addEventListener("click", function () {
      var o = it.classList.toggle("open"); b.setAttribute("aria-expanded", o);
    });
  });

  // Swipe rows: dots follow the card in view; the active dot grows into a pill.
  d.querySelectorAll(".swipe").forEach(function (row) {
    var cards = [].slice.call(row.children), dots = row.nextElementSibling;
    if (!dots || !dots.classList.contains("dots")) return;
    var mark = function () {
      var best = 0, bd = 1e9, left = row.getBoundingClientRect().left;
      cards.forEach(function (c, i) { var dd = Math.abs(c.getBoundingClientRect().left - left - 16); if (dd < bd) { bd = dd; best = i; } });
      [].forEach.call(dots.children, function (x, i) { x.classList.toggle("on", i === best); });
    };
    row.addEventListener("scroll", function () { requestAnimationFrame(mark); }, { passive: true });
    row.scrollToCard = function (i) { row.scrollLeft = cards[i].offsetLeft - row.offsetLeft - 16; mark(); };
    mark();
  });

  // Fade sections up once as they enter the viewport. Cards stagger by 60ms.
  var rv = d.querySelectorAll(".rv");
  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    rv.forEach(function (el) {
      var p = el.parentElement, sib = p ? [].filter.call(p.children, function (c) { return c.classList.contains("rv"); }) : [];
      if (sib.length > 1) el.style.transitionDelay = (sib.indexOf(el) * 60) + "ms";
      io.observe(el);
    });
  } else rv.forEach(function (el) { el.classList.add("in"); });

  de.classList.add("ready");
  var yr = d.getElementById("yr"); if (yr) yr.textContent = new Date().getFullYear();
})();
