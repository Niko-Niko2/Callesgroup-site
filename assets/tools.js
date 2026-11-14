/* Calles Group selling tools: the live sample site, the missed-calls calculator, the estimate, pitch links and the call request.
   Everything runs in the visitor's browser. Nothing typed here is sent anywhere unless they tap a text or call button.

   Pitch links: add these to the home page address to open it already filled in for one owner.
     ?b=Business+Name   &t=roofing   &c=Elgin   &p=0..5 (sample colors, in the order of the buttons: Daylight, Ember, Evergreen, Barn red, Harbor, Glacier)
   Trade keys: roofing hvac plumbing remodeling electrical landscaping painting concrete detailing washing other */
(function () {
  var d = document, es = d.documentElement.lang === "es";
  var $ = function (id) { return d.getElementById(id); };
  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var PHONE = "+13126000590";

  // Average job values are starting guesses only. The page tells the visitor to replace them.
  var TRADES = [
    { k: "roofing", n: ["Roofing", "Techos"], job: 12000,
      h: ["Roof repair and replacement, done right the first time.", "Reparación y cambio de techos, bien hechos a la primera."],
      s: [["Roof replacement", "Storm damage repair", "Gutters and siding"], ["Cambio de techo", "Daños por tormenta", "Canaletas y siding"]] },
    { k: "hvac", n: ["Heating and cooling", "Calefacción y aire"], job: 6500,
      h: ["Heating and cooling you can count on.", "Calefacción y aire en los que puede confiar."],
      s: [["Furnace repair", "AC installation", "Seasonal tune-ups"], ["Reparación de calefacción", "Instalación de aire", "Mantenimiento de temporada"]] },
    { k: "plumbing", n: ["Plumbing", "Plomería"], job: 900,
      h: ["Plumbing fixed fast, priced up front.", "Plomería rápida, con precio claro."],
      s: [["Leak repair", "Water heaters", "Drain cleaning"], ["Reparación de fugas", "Calentadores de agua", "Destape de drenajes"]] },
    { k: "remodeling", n: ["Remodeling", "Remodelación"], job: 25000,
      h: ["Kitchens, baths and basements built to last.", "Cocinas, baños y sótanos hechos para durar."],
      s: [["Kitchen remodels", "Bathroom remodels", "Basement finishing"], ["Cocinas", "Baños", "Sótanos terminados"]] },
    { k: "electrical", n: ["Electrical", "Electricidad"], job: 1200,
      h: ["Safe, clean electrical work.", "Trabajo eléctrico seguro y limpio."],
      s: [["Panel upgrades", "Lighting", "EV chargers"], ["Cambio de paneles", "Iluminación", "Cargadores para autos eléctricos"]] },
    { k: "landscaping", n: ["Landscaping", "Jardinería"], job: 4000,
      h: ["Yards that make the neighbors look twice.", "Jardines que hacen voltear a los vecinos."],
      s: [["Lawn care", "Patios and pavers", "Seasonal cleanups"], ["Corte de césped", "Patios y adoquines", "Limpiezas de temporada"]] },
    { k: "painting", n: ["Painting", "Pintura"], job: 3500,
      h: ["Clean lines. Clean job sites.", "Líneas limpias. Trabajo limpio."],
      s: [["Interior painting", "Exterior painting", "Cabinet refinishing"], ["Pintura interior", "Pintura exterior", "Gabinetes"]] },
    { k: "concrete", n: ["Concrete", "Concreto"], job: 6000,
      h: ["Driveways, patios and flatwork that last.", "Entradas, patios y pisos que duran."],
      s: [["Driveways", "Patios", "Stamped concrete"], ["Entradas", "Patios", "Concreto estampado"]] },
    { k: "detailing", n: ["Auto detailing", "Detallado de autos"], job: 250,
      h: ["Your car, back to showroom clean.", "Su auto, como recién salido de agencia."],
      s: [["Interior detail", "Paint correction", "Ceramic coating"], ["Detallado interior", "Corrección de pintura", "Recubrimiento cerámico"]] },
    { k: "washing", n: ["Pressure washing", "Lavado a presión"], job: 400,
      h: ["Years of grime gone in an afternoon.", "Años de mugre fuera en una tarde."],
      s: [["House washing", "Driveways", "Decks and fences"], ["Lavado de casas", "Entradas", "Terrazas y cercas"]] },
    { k: "other", n: ["Something else", "Otro"], job: 2500,
      h: ["Quality work, done right.", "Trabajo de calidad, bien hecho."],
      s: [["Your main service", "Your second service", "Your third service"], ["Su servicio principal", "Su segundo servicio", "Su tercer servicio"]] }
  ];
  var L = es ? 1 : 0;
  var T = es ? {
    biz: "El nombre de su negocio", kick: function (t, c) { return t + " en " + c; }, call: "Llamar ahora", quote: "Presupuesto gratis",
    photo: "Aquí van las fotos de sus trabajos", rev: "Aquí se ven sus reseñas de Google", foot: function (c) { return "Servicio en " + c + " y alrededores"; },
    hello: function (b) { return "Hola, " + b + ". Esta muestra es para usted."; },
    jobHint: function (t) { return "Un número inicial para " + t.toLowerCase() + ". Ponga su número real."; },
    callsHint: function (n) { return n === 1 ? "Una sola llamada más al mes." : n + " al mes es como " + (n / 4.33 < 1.5 ? "una por semana." : Math.round(n / 4.33) + " por semana."); },
    pay: function (t, k) { return "A ese ritmo se paga solo en <b>" + t + "</b>. Eso es " + k + (k === 1 ? " trabajo." : " trabajos."); },
    payNone: "Suba las llamadas o el valor del trabajo para ver en cuánto tiempo se paga.",
    siteBar: function (n) { return "Un sitio " + n + ", un solo pago"; },
    dur: function (x) {
      if (x <= 1.5) return "más o menos un día"; if (x < 14) return "unos " + Math.round(x) + " días";
      if (x < 60) return "unas " + Math.round(x / 7) + " semanas"; if (x < 1100) return "unos " + Math.round(x / 30) + " meses"; return "más de 3 años";
    },
    smsDemo: function (s) { return s.biz ? "Hola Andrew, soy de " + s.biz + ". Vi la muestra del sitio para mi negocio de " + s.trade.toLowerCase() + " en " + s.town + ". Quiero una llamada gratis." : "Hola Andrew, vi la muestra en callesgroup.com. Quiero una llamada gratis para mi negocio."; },
    smsCalc: function (s, r) { return "Hola Andrew" + (s.biz ? ", soy de " + s.biz : "") + ". Hice las cuentas en su sitio: " + s.trade.toLowerCase() + ", trabajo promedio de " + r.job + ", unas " + r.calls + " llamadas perdidas al mes. Son como " + r.yr + " al año. Hablemos."; },
    smsBook: function (s, when) { return "Hola Andrew" + (s.biz ? ", soy de " + s.biz : "") + ". Quiero una llamada gratis " + when + "."; },
    note: function (s, when) { return "Favor de llamarme " + when + "." + (s.biz ? " Negocio: " + s.biz + "." : ""); },
    today: "Hoy", when: function (day, time, isToday) { return (isToday ? "hoy" : "el " + day) + " a las " + time; },
    loc: "es-US"
  } : {
    biz: "Your Business Name", kick: function (t, c) { return t + " in " + c; }, call: "Call now", quote: "Free estimate",
    photo: "Your job photos go here", rev: "Your Google reviews show here", foot: function (c) { return "Serving " + c + " and nearby towns"; },
    hello: function (b) { return b + ", this sample is for you."; },
    jobHint: function (t) { return "A starting guess for " + t.toLowerCase() + ". Put in your real number."; },
    callsHint: function (n) { return n === 1 ? "Just one more call a month." : n + " a month is about " + (n / 4.33 < 1.5 ? "one a week." : Math.round(n / 4.33) + " a week."); },
    pay: function (t, k) { return "At that pace it pays for itself in <b>" + t + "</b>. That is " + k + (k === 1 ? " job." : " jobs."); },
    payNone: "Raise the calls or the job value to see how fast a site pays for itself.",
    siteBar: function (n) { return "A " + n + " website, paid once"; },
    dur: function (x) {
      if (x <= 1.5) return "about a day"; if (x < 14) return "about " + Math.round(x) + " days";
      if (x < 60) return "about " + Math.round(x / 7) + " weeks"; if (x < 1100) return "about " + Math.round(x / 30) + " months"; return "more than 3 years";
    },
    smsDemo: function (s) { return s.biz ? "Hi Andrew, it's " + s.biz + ". I saw the sample site for my " + s.trade.toLowerCase() + " business in " + s.town + ". I'd like a free quote call." : "Hi Andrew, I saw the sample site on callesgroup.com. I'd like a free quote call for my business."; },
    smsCalc: function (s, r) { return "Hi Andrew" + (s.biz ? ", it's " + s.biz : "") + ". I ran the numbers on your site: " + s.trade.toLowerCase() + ", average job " + r.job + ", about " + r.calls + " missed calls a month. That is about " + r.yr + " a year. Let's talk."; },
    smsBook: function (s, when) { return "Hi Andrew" + (s.biz ? ", it's " + s.biz : "") + ". I'd like a free quote call " + when + "."; },
    note: function (s, when) { return "Please call me " + when + "." + (s.biz ? " Business: " + s.biz + "." : ""); },
    today: "Today", when: function (day, time, isToday) { return (isToday ? "today" : day) + " at " + time; },
    loc: "en-US"
  };

  function clean(v, n) { return String(v == null ? "" : v).replace(/[<>\u0000-\u001f]/g, "").replace(/\s+/g, " ").trim().slice(0, n); }
  function money(n) { return "$" + Math.round(n).toLocaleString("en-US"); }
  function sms(body) { return "sms:" + PHONE + "?&body=" + encodeURIComponent(body); }
  function trade(k) { for (var i = 0; i < TRADES.length; i++) if (TRADES[i].k === k) return TRADES[i]; return null; }
  // Ease a dollar figure to its new value. Each element remembers what it is showing.
  function count(el, to) {
    cancelAnimationFrame(el._raf);
    if (reduce || el._v == null) { el._v = to; el.textContent = money(to); return; }
    var from = el._v, t0 = performance.now();
    var step = function (t) { var k = Math.min(1, (t - t0) / 380), e = 1 - Math.pow(1 - k, 3); el._v = from + (to - from) * e; el.textContent = money(el._v); if (k < 1) el._raf = requestAnimationFrame(step); };
    el._raf = requestAnimationFrame(step);
  }
  function press(group, btn) { [].forEach.call(group.querySelectorAll("button"), function (b) { b.setAttribute("aria-pressed", b === btn); }); }

  // What we know about this visitor: from a pitch link first, then from earlier in this visit.
  var S = { biz: "", tk: "roofing", town: "Elgin", pal: 0 };
  try { var saved = JSON.parse(sessionStorage.getItem("cg") || "null"); if (saved) for (var key in S) if (saved[key] != null) S[key] = saved[key]; } catch (e) {}
  var q = new URLSearchParams(location.search), linked = !!clean(q.get("b"), 40);
  if (linked) S.biz = clean(q.get("b"), 40);
  if (trade(q.get("t"))) S.tk = q.get("t");
  if (clean(q.get("c"), 28)) S.town = clean(q.get("c"), 28);
  if (/^[0-5]$/.test(q.get("p") || "")) S.pal = +q.get("p");
  if (!trade(S.tk)) S.tk = "roofing";
  S.biz = clean(S.biz, 40); S.town = clean(S.town, 28) || "Elgin"; S.pal = +S.pal >= 0 && +S.pal <= 5 ? Math.floor(+S.pal) : 0;
  function save() { try { sessionStorage.setItem("cg", JSON.stringify(S)); } catch (e) {} }
  function view() { var t = trade(S.tk); return { biz: S.biz, trade: t.n[L], town: S.town }; }
  var listeners = [];
  function changed() { save(); listeners.forEach(function (fn) { fn(); }); }

  /* ---------- 1. The sample site in the phone ---------- */
  var ps = $("ps");
  if (ps) {
    var bizIn = $("dBiz"), townIn = $("dTown"), chips = $("dTrades"), swapT;
    TRADES.forEach(function (t) {
      var b = d.createElement("button"); b.type = "button"; b.className = "pick"; b.textContent = t.n[L];
      b.dataset.k = t.k; b.setAttribute("aria-pressed", t.k === S.tk); chips.appendChild(b);
    });
    var paint = function (animate) {
      var t = trade(S.tk);
      $("psName").textContent = S.biz || T.biz;
      $("psKick").textContent = T.kick(t.n[L], S.town + ", IL");
      $("psHead").textContent = t.h[L];
      $("psS1").textContent = t.s[L][0]; $("psS2").textContent = t.s[L][1]; $("psS3").textContent = t.s[L][2];
      $("psCall").textContent = T.call; $("psQuote").textContent = T.quote; $("psPhoto").textContent = T.photo; $("psRev").textContent = T.rev;
      $("psFoot").textContent = T.foot(S.town);
      ps.dataset.pal = S.pal;
      [].forEach.call(d.querySelectorAll(".sw"), function (b) {
        b.setAttribute("aria-pressed", +b.dataset.pal === S.pal);
        if (+b.dataset.pal === S.pal && $("swName")) $("swName").textContent = b.dataset.name;
      });
      var tx = $("demoText"); if (tx) tx.href = sms(T.smsDemo(view()));
      if (animate && !reduce) { ps.classList.remove("swap"); void ps.offsetWidth; ps.classList.add("swap"); clearTimeout(swapT); swapT = setTimeout(function () { ps.classList.remove("swap"); }, 600); }
    };
    bizIn.value = S.biz; townIn.value = S.town;
    bizIn.addEventListener("input", function () { S.biz = clean(bizIn.value, 40); paint(false); changed(); });
    townIn.addEventListener("input", function () { S.town = clean(townIn.value, 28) || "Elgin"; paint(false); changed(); });
    chips.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      S.tk = b.dataset.k; press(chips, b); paint(true); changed();
    });
    d.querySelector(".swatches").addEventListener("click", function (e) {
      var b = e.target.closest(".sw"); if (!b) return; S.pal = +b.dataset.pal; paint(false); save();
    });
    // On a phone the sample sits below the form: bring it into view once they finish typing their name.
    var show = function () { if (S.biz && innerWidth < 940) $("demo").scrollIntoView({ block: "center", behavior: reduce ? "auto" : "smooth" }); };
    bizIn.addEventListener("change", show);
    $("demoForm").addEventListener("submit", function (e) { e.preventDefault(); bizIn.blur(); townIn.blur(); });
    paint(false);
    // Keep the chosen trade in view inside the row of trade buttons.
    var on = chips.querySelector('[aria-pressed="true"]');
    if (on) chips.scrollLeft = Math.max(0, on.getBoundingClientRect().left - chips.getBoundingClientRect().left + chips.scrollLeft - 40);
    // Opened from a pitch link: greet the owner by name.
    var hello = $("hello");
    if (hello && linked) { hello.textContent = T.hello(S.biz); hello.hidden = false; }
  }

  /* ---------- 2. The missed-calls calculator ---------- */
  // Missed calls a month x wins out of 10 x what one job is worth. Two bars put a year of that next to a website's price.
  var calc = $("calc");
  if (calc) {
    var job = $("cJob"), jobR = $("cJobR"), winO = $("cWin"), calls = $("cCalls"), pk = $("cPkgs");
    var pkgs = []; try { pkgs = JSON.parse(calc.dataset.pkgs); } catch (e) {}
    var win = 3, pick = pkgs[0], touched = false;
    pkgs.forEach(function (p, i) {
      var b = d.createElement("button"); b.type = "button"; b.className = "pick"; b.textContent = p.n + " " + money(p.p);
      b.setAttribute("aria-pressed", i === 0); b.dataset.i = i; pk.appendChild(b);
    });
    pk.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; pick = pkgs[+b.dataset.i]; press(pk, b); run(); });
    var run = function () {
      var j = Math.max(0, Math.min(1000000, +job.value || 0)), c = +calls.value, jobs = c * win / 10, mo = jobs * j, yr = mo * 12;
      winO.textContent = win; $("cCallsV").textContent = c; $("cCallsHint").textContent = T.callsHint(c);
      $("cJobHint").textContent = T.jobHint(trade(S.tk).n[L]);
      count($("cYear"), yr); $("cMonth").textContent = money(mo);
      $("cJobs").textContent = jobs < 10 ? (Math.round(jobs * 10) / 10).toLocaleString(T.loc) : Math.round(jobs);
      var pay = $("cPay");
      if (pick) {
        // Both bars share one scale, so the website's bar is as small next to the year as it really is.
        var top = Math.max(yr, pick.p, 1);
        $("cBarLoss").style.width = (yr / top * 100) + "%"; $("cBarSite").style.width = (pick.p / top * 100) + "%";
        $("cBarLossV").textContent = money(yr); $("cBarSiteV").textContent = money(pick.p); $("cBarSiteL").textContent = T.siteBar(pick.n);
      }
      if (pick && mo > 0 && j > 0) pay.innerHTML = T.pay(T.dur(pick.p / (mo / 30)), Math.max(1, Math.ceil(pick.p / j)));
      else pay.textContent = T.payNone;
      $("cText").href = sms(T.smsCalc(view(), { job: money(j), calls: c, yr: money(yr) }));
    };
    var setJob = function (v) { job.value = v; jobR.value = Math.min(+jobR.max, Math.max(+jobR.min, v)); };
    job.addEventListener("input", function () { touched = true; jobR.value = Math.min(+jobR.max, Math.max(+jobR.min, +job.value || 0)); run(); });
    jobR.addEventListener("input", function () { touched = true; job.value = jobR.value; run(); });
    calls.addEventListener("input", run);
    $("cWinDn").addEventListener("click", function () { win = Math.max(1, win - 1); run(); });
    $("cWinUp").addEventListener("click", function () { win = Math.min(10, win + 1); run(); });
    // The trade picked in the sample sets the starting job value, until the visitor types their own.
    listeners.push(function () { if (!touched) setJob(trade(S.tk).job); run(); });
    setJob(trade(S.tk).job); run();
  }

  /* ---------- 3. The estimate on the price list ---------- */
  // Tap a website, tick any extras, and the last box adds it up. Every price and rule arrives in data-est from offers.json:
  // the Brand Kit covers the logo, Premium already comes with the photo shoot, and care is a monthly line of its own.
  var est = $("est");
  if (est) {
    var E = null; try { E = JSON.parse(est.dataset.est); } catch (e) {}
    var rows = {}; [].forEach.call(est.querySelectorAll("label[data-k]"), function (l) { rows[l.dataset.k] = l; });
    var boxes = [].slice.call(est.querySelectorAll(".pk")), barEl = $("estBar");
    var put = function (tpl) { var a = arguments, i = 1; return tpl.replace(/%s/g, function () { return a[i++]; }); };
    var sum = function () {
      var inp = est.querySelector('input[name="est-site"]:checked'), site = null, total = 0, items = [], on = {};
      E.sites.forEach(function (x) { if (inp && x.k === inp.value) site = x; });
      boxes.forEach(function (b) { b.classList.toggle("on", !!site && b.dataset.k === site.k); });
      if (site) { total += site.p; items.push([put(E.t.site, site.n), money(site.p)]); }
      E.adds.forEach(function (a) { on[a.k] = rows[a.k].querySelector("input").checked; });
      E.adds.forEach(function (a) {
        var row = rows[a.k], box = row.querySelector("input"), price = row.querySelector(".item-p"), why = "";
        E.adds.forEach(function (o) { if (o.covers && o.covers.indexOf(a.k) >= 0 && on[o.k]) why = E.t.inKit; });
        if (a.inside && site && a.inside.indexOf(site.k) >= 0) why = E.t.inPremium;
        if (price._own == null) price._own = price.innerHTML;
        if (why) { price.textContent = ""; var sm = d.createElement("small"); sm.textContent = why; price.appendChild(sm); }
        else if (row.classList.contains("covered")) price.innerHTML = price._own;
        row.classList.toggle("covered", !!why); box.disabled = !!why;
        if (box.checked && !why) { total += a.p; items.push([a.n, money(a.p)]); }
      });
      var care = rows.care.querySelector("input").checked;
      $("estCare").hidden = !care;
      var list = $("estLines"); list.textContent = "";
      items.forEach(function (it) { var li = d.createElement("li"), n = d.createElement("span"), v = d.createElement("b"); n.textContent = it[0]; v.textContent = it[1]; li.appendChild(n); li.appendChild(v); list.appendChild(li); });
      count($("estTotal"), total); count($("estBarN"), total); $("estDep").textContent = money(Math.round(total / 2));
      var f = E.founding, payLine = total > 2500 ? E.pay[1] : E.pay[0];
      if (site && f && f.left > 0 && site.k === f.k) payLine += " " + put(E.t.founding, site.n, money(f.p)) + " " + E.spots + ".";
      $("estPay").textContent = payLine;
      $("estText").href = sms(put(E.t.sms, S.biz ? put(E.t.smsMe, S.biz) : "", items.map(function (it) { return it[0] + " " + it[1]; }).join(", "), money(total), care ? E.t.smsCare : ""));
    };
    if (E) {
      est.addEventListener("change", sum); listeners.push(sum); sum();
      // The riding bar shows while the choices are on screen and steps aside once the estimate itself is in view.
      barEl.hidden = false;
      if ("IntersectionObserver" in window) new IntersectionObserver(function (es) { barEl.classList.toggle("off", es[0].isIntersecting); }, { threshold: 0.35 }).observe($("estSum"));
    }
  }

  /* ---------- 4. Ask for a call time ---------- */
  // The times offered are Andrew's call hours, set in data/offers.json and passed in on the element.
  [].forEach.call(d.querySelectorAll("[data-bk]"), function (bk) {
    var days = bk.querySelector("[data-bk-days]"), times = bk.querySelector("[data-bk-times]"), biz = bk.querySelector("#bkBiz");
    var sum = bk.querySelector("[data-bk-sum]"), text = bk.querySelector("[data-bk-text]"), form = bk.querySelector("[data-bk-form]");
    var nums = function (v, fallback) { var a = String(v || "").split(",").map(Number).filter(function (n) { return n >= 0 && n < 24; }); return a.length ? a : fallback; };
    var hours = { wd: nums(bk.dataset.weekday, [18, 19, 20]), we: nums(bk.dataset.weekend, [15, 16, 17, 18]) };
    var now = new Date(), list = [], cur = 0;
    // Today is offered only while a call time is still at least an hour or so away.
    for (var i = 0; list.length < 6 && i < 12; i++) {
      var day = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i);
      var hrs = (day.getDay() === 0 || day.getDay() === 6) ? hours.we : hours.wd;
      if (i === 0) hrs = hrs.filter(function (h) { return h >= now.getHours() + 2; });
      if (hrs.length) list.push({ label: day.toLocaleDateString(T.loc, { weekday: "short", month: "short", day: "numeric" }), hrs: hrs, today: i === 0 });
    }
    var button = function (label, on) { var b = d.createElement("button"); b.type = "button"; b.className = "pick"; b.textContent = label; b.setAttribute("aria-pressed", on); return b; };
    var clock = function (h) { return new Date(2000, 0, 1, h).toLocaleTimeString(T.loc, { hour: "numeric", minute: "2-digit" }); };
    list.forEach(function (it, i) { var b = button(it.today ? T.today : it.label, i === 0); b.dataset.i = i; days.appendChild(b); });
    var fillTimes = function () { times.textContent = ""; list[cur].hrs.forEach(function (h, j) { times.appendChild(button(clock(h), j === 0)); }); };
    if (biz) biz.value = S.biz;
    var when = function () { var it = list[cur], tt = times.querySelector('[aria-pressed="true"]'); return T.when(it.label, tt ? tt.textContent : "", it.today); };
    var paint = function () { var w = when(); sum.textContent = w.charAt(0).toUpperCase() + w.slice(1); text.href = sms(T.smsBook(view(), w)); };
    days.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; cur = +b.dataset.i; press(days, b); fillTimes(); paint(); });
    times.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; press(times, b); paint(); });
    if (biz) biz.addEventListener("input", function () { S.biz = clean(biz.value, 40); save(); paint(); });
    // "Have Andrew call me": carry the chosen time into the quote form's message box.
    if (form) form.addEventListener("click", function () { window.CG_CALL_NOTE = T.note(view(), when()); if (window.cgSetNote) window.cgSetNote(); });
    fillTimes(); paint();
  });
})();
