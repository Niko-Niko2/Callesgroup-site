/* Calles Group selling tools: the live sample site, the what-if calculator, pitch links and the call request.
   Everything runs in the visitor's browser. Nothing typed here is sent anywhere unless they tap a text or call button.

   Pitch links: add these to the home page address to open it already filled in for one owner.
     ?b=Business+Name   &t=roofing   &c=Elgin   &p=0..3 (sample colors)
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
    pay: function (n, p, t, k) { return "Un sitio " + n + " de " + p + " se pagaría en <b>" + t + "</b> a ese ritmo. Eso es " + k + (k === 1 ? " trabajo." : " trabajos."); },
    payNone: "Suba las llamadas o el valor del trabajo para ver en cuánto tiempo se paga.",
    dur: function (x) {
      if (x <= 1.5) return "más o menos un día"; if (x < 14) return "unos " + Math.round(x) + " días";
      if (x < 60) return "unas " + Math.round(x / 7) + " semanas"; if (x < 1100) return "unos " + Math.round(x / 30) + " meses"; return "más de 3 años";
    },
    smsDemo: function (s) { return s.biz ? "Hola Andrew, soy de " + s.biz + ". Vi la muestra del sitio para mi negocio de " + s.trade.toLowerCase() + " en " + s.town + ". Quiero una llamada gratis." : "Hola Andrew, vi la muestra en callesgroup.com. Quiero una llamada gratis para mi negocio."; },
    smsCalc: function (s, r) { return "Hola Andrew" + (s.biz ? ", soy de " + s.biz : "") + ". Hice las cuentas en su sitio: " + s.trade.toLowerCase() + ", trabajo promedio de " + r.job + ", " + r.calls + " llamadas extra al mes, como " + r.yr + " al año. Hablemos."; },
    smsBook: function (s, when) { return "Hola Andrew" + (s.biz ? ", soy de " + s.biz : "") + ". Quiero una llamada gratis el " + when + "."; },
    note: function (s, when) { return "Favor de llamarme: " + when + "." + (s.biz ? " Negocio: " + s.biz + "." : ""); },
    loc: "es-US"
  } : {
    biz: "Your Business Name", kick: function (t, c) { return t + " in " + c; }, call: "Call now", quote: "Free estimate",
    photo: "Your job photos go here", rev: "Your Google reviews show here", foot: function (c) { return "Serving " + c + " and nearby towns"; },
    hello: function (b) { return b + ", this sample is for you."; },
    jobHint: function (t) { return "A starting guess for " + t.toLowerCase() + ". Put in your real number."; },
    callsHint: function (n) { return n === 1 ? "Just one more call a month." : n + " a month is about " + (n / 4.33 < 1.5 ? "one a week." : Math.round(n / 4.33) + " a week."); },
    pay: function (n, p, t, k) { return "A " + n + " site at " + p + " would be paid back in <b>" + t + "</b> at that pace. That is " + k + (k === 1 ? " job." : " jobs."); },
    payNone: "Raise the calls or the job value to see how fast a site pays for itself.",
    dur: function (x) {
      if (x <= 1.5) return "about a day"; if (x < 14) return "about " + Math.round(x) + " days";
      if (x < 60) return "about " + Math.round(x / 7) + " weeks"; if (x < 1100) return "about " + Math.round(x / 30) + " months"; return "more than 3 years";
    },
    smsDemo: function (s) { return s.biz ? "Hi Andrew, it's " + s.biz + ". I saw the sample site for my " + s.trade.toLowerCase() + " business in " + s.town + ". I'd like a free quote call." : "Hi Andrew, I saw the sample site on callesgroup.com. I'd like a free quote call for my business."; },
    smsCalc: function (s, r) { return "Hi Andrew" + (s.biz ? ", it's " + s.biz : "") + ". I ran the numbers on your site: " + s.trade.toLowerCase() + ", average job " + r.job + ", " + r.calls + " extra calls a month, about " + r.yr + " a year. Let's talk."; },
    smsBook: function (s, when) { return "Hi Andrew" + (s.biz ? ", it's " + s.biz : "") + ". I'd like a free quote call " + when + "."; },
    note: function (s, when) { return "Please call me: " + when + "." + (s.biz ? " Business: " + s.biz + "." : ""); },
    loc: "en-US"
  };

  function clean(v, n) { return String(v == null ? "" : v).replace(/[<>\u0000-\u001f]/g, "").replace(/\s+/g, " ").trim().slice(0, n); }
  function money(n) { return "$" + Math.round(n).toLocaleString("en-US"); }
  function sms(body) { return "sms:" + PHONE + "?&body=" + encodeURIComponent(body); }
  function trade(k) { for (var i = 0; i < TRADES.length; i++) if (TRADES[i].k === k) return TRADES[i]; return null; }
  function press(group, btn) { [].forEach.call(group.querySelectorAll("button"), function (b) { b.setAttribute("aria-pressed", b === btn); }); }

  // What we know about this visitor: from a pitch link first, then from earlier in this visit.
  var S = { biz: "", tk: "roofing", town: "Elgin", pal: 0 };
  try { var saved = JSON.parse(sessionStorage.getItem("cg") || "null"); if (saved) for (var key in S) if (saved[key] != null) S[key] = saved[key]; } catch (e) {}
  var q = new URLSearchParams(location.search), linked = !!clean(q.get("b"), 40);
  if (linked) S.biz = clean(q.get("b"), 40);
  if (trade(q.get("t"))) S.tk = q.get("t");
  if (clean(q.get("c"), 28)) S.town = clean(q.get("c"), 28);
  if (/^[0-3]$/.test(q.get("p") || "")) S.pal = +q.get("p");
  if (!trade(S.tk)) S.tk = "roofing";
  S.biz = clean(S.biz, 40); S.town = clean(S.town, 28) || "Elgin"; S.pal = +S.pal || 0;
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
      [].forEach.call(d.querySelectorAll(".sw"), function (b) { b.setAttribute("aria-pressed", +b.dataset.pal === S.pal); });
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
    var dt = $("estDate");
    if (dt) dt.textContent = new Date().toLocaleDateString(T.loc, { month: "short", day: "numeric", year: "numeric" });
    paint(false);
    // Keep the chosen trade in view inside the row of trade buttons.
    var on = chips.querySelector('[aria-pressed="true"]');
    if (on) chips.scrollLeft = Math.max(0, on.getBoundingClientRect().left - chips.getBoundingClientRect().left + chips.scrollLeft - 40);
    // Opened from a pitch link: greet the owner by name, written in by hand.
    var hello = $("hello");
    if (hello && linked) {
      hello.textContent = T.hello(S.biz); hello.hidden = false; hello.classList.add("write");
      requestAnimationFrame(function () { requestAnimationFrame(function () { hello.classList.add("go"); }); });
    }
  }

  /* ---------- 2. The what-if calculator ---------- */
  var calc = $("calc");
  if (calc) {
    var job = $("cJob"), jobR = $("cJobR"), winO = $("cWin"), calls = $("cCalls"), pk = $("cPkgs");
    var pkgs = []; try { pkgs = JSON.parse(calc.dataset.pkgs); } catch (e) {}
    var win = 3, pick = pkgs[0], touched = false, shown = null, raf;
    pkgs.forEach(function (p, i) {
      var b = d.createElement("button"); b.type = "button"; b.className = "pick"; b.textContent = p.n + " " + money(p.p);
      b.setAttribute("aria-pressed", i === 0); b.dataset.i = i; pk.appendChild(b);
    });
    pk.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; pick = pkgs[+b.dataset.i]; press(pk, b); run(false); });
    var count = function (el, to) {
      cancelAnimationFrame(raf);
      if (reduce || shown == null) { shown = to; el.textContent = money(to); return; }
      var from = shown, t0 = performance.now();
      var step = function (t) { var k = Math.min(1, (t - t0) / 380), e = 1 - Math.pow(1 - k, 3); shown = from + (to - from) * e; el.textContent = money(shown); if (k < 1) raf = requestAnimationFrame(step); };
      raf = requestAnimationFrame(step);
    };
    var run = function () {
      var j = Math.max(0, Math.min(1000000, +job.value || 0)), c = +calls.value, jobs = c * win / 10, mo = jobs * j, yr = mo * 12;
      winO.textContent = win; $("cCallsV").textContent = c; $("cCallsHint").textContent = T.callsHint(c);
      $("cJobHint").textContent = T.jobHint(trade(S.tk).n[L]);
      count($("cYear"), yr); $("cMonth").textContent = money(mo);
      $("cJobs").textContent = jobs < 10 ? (Math.round(jobs * 10) / 10).toLocaleString(T.loc) : Math.round(jobs);
      var pay = $("cPay");
      if (pick && mo > 0 && j > 0) pay.innerHTML = T.pay(pick.n, money(pick.p), T.dur(pick.p / (mo / 30)), Math.max(1, Math.ceil(pick.p / j)));
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

  /* ---------- 3. Ask for a call time ---------- */
  [].forEach.call(d.querySelectorAll("[data-bk]"), function (bk) {
    var days = bk.querySelector("[data-bk-days]"), times = bk.querySelector("[data-bk-times]"), biz = bk.querySelector("#bkBiz");
    var sum = bk.querySelector("[data-bk-sum]"), text = bk.querySelector("[data-bk-text]"), form = bk.querySelector("[data-bk-form]");
    var now = new Date();
    for (var i = 1; i <= 6; i++) {
      var day = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i);
      var b = d.createElement("button"); b.type = "button"; b.className = "pick";
      b.textContent = day.toLocaleDateString(T.loc, { weekday: "short", month: "short", day: "numeric" });
      b.setAttribute("aria-pressed", i === 1); days.appendChild(b);
    }
    if (biz) biz.value = S.biz;
    var when = function () {
      var dd = days.querySelector('[aria-pressed="true"]'), tt = times.querySelector('[aria-pressed="true"]');
      return (dd ? dd.textContent : "") + ", " + (tt ? tt.textContent.toLowerCase() : "");
    };
    var paint = function () {
      var w = when(); sum.textContent = w;
      text.href = sms(T.smsBook(view(), w));
    };
    [days, times].forEach(function (g) { g.addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b) return; press(g, b); paint(); }); });
    if (biz) biz.addEventListener("input", function () { S.biz = clean(biz.value, 40); save(); paint(); });
    // "Have Andrew call me": carry the chosen time into the quote form's message box.
    if (form) form.addEventListener("click", function () { window.CG_CALL_NOTE = T.note(view(), when()); if (window.cgSetNote) window.cgSetNote(); });
    paint();
  });
})();
