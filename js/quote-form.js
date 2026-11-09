// Quote request form. Same 3 steps and questions as the old Wix form.
// Sends each request to Web3Forms, which emails it to andrew@callesgroup.com. No Wix needed.
// The access key is public by design (it can only send to the inbox it was made for).
export const ACCESS_KEY = "WEB3FORMS_ACCESS_KEY";

const STEPS = [
  { title: "What can we help with?", fields: [
    { name: "need", label: "What do you need?", type: "checks", required: true,
      options: ["Website", "Logo or branding", "Care plan", "Not sure yet"] },
    { name: "budget", label: "What's your budget?", type: "radio",
      options: ["Under $1,000", "$1,000 to $2,500", "$2,500 to $4,000", "$4,000+", "Not sure yet"] },
  ] },
  { title: "About your business", fields: [
    { name: "business_type", label: "What kind of business?", type: "radio",
      options: ["Contractor or trades", "Restaurant or food", "Salon, beauty or wellness", "Shop or retail", "Professional services", "Something else"] },
    { name: "current_website", label: "Do you have a website now?", type: "radio",
      options: ["Yes, but it needs work", "Yes, and it's fine", "Not yet"] },
    { name: "have_logo", label: "Do you have a logo?", type: "radio",
      options: ["Yes", "Yes, but it needs a refresh", "Not yet"] },
  ] },
  { title: "Where should we reply?", fields: [
    { name: "name", label: "Name", type: "text", required: true, auto: "name" },
    { name: "business_name", label: "Business name", type: "text", auto: "organization" },
    { name: "email", label: "Email", type: "email", required: true, auto: "email" },
    { name: "phone", label: "Phone", type: "tel", auto: "tel", placeholder: "(847) 555-1234" },
    { name: "message", label: "Anything else we should know?", type: "textarea",
      placeholder: "Optional. When you'd like to start, a deadline, ideas you like..." },
  ] },
];

const h = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null && v !== false) n.setAttribute(k, v === true ? "" : v);
  n.append(...kids.filter((k) => k != null));
  return n;
};

const usPhone = (v) => {
  const d = String(v).replace(/\D/g, "");
  if (d.length === 10) return `(${d.slice(0, 3)}) ${d.slice(3, 6)}-${d.slice(6)}`;
  if (d.length === 11 && d[0] === "1") return usPhone(d.slice(1));
  return String(v).trim();
};

export function renderQuoteForm(mount, { need, onStep, onDone } = {}) {
  let step = 0;
  const form = h("form", { class: "form", novalidate: true, "data-state": "ready" });
  const head = h("div", { class: "form-step" });
  const title = h("h3", { class: "form-step-title" });
  const count = h("p", { class: "form-step-count" });
  head.append(title, count);
  const error = h("p", { class: "form-form-error", role: "alert", hidden: true });
  const back = h("button", { class: "form-back", type: "button" }, "Back");
  const next = h("button", { class: "form-next", type: "button" }, "Continue");
  const submit = h("button", { class: "form-submit", type: "submit" }, "Send my request");
  const actions = h("div", { class: "form-actions" }, back, next, submit);
  // Honeypot: real people never see or fill this.
  const trap = h("input", { type: "checkbox", name: "botcheck", tabindex: "-1", autocomplete: "off", style: "display:none" });

  const boxes = STEPS.map((s) => {
    const fs = h("fieldset", { class: "form-fields" });
    for (const f of s.fields) fs.append(field(f));
    return fs;
  });
  form.append(head, ...boxes, error, actions, trap);
  mount.replaceChildren(form);

  function field(f) {
    const id = `q-${f.name}`;
    const req = f.required ? h("span", { class: "form-required", "aria-hidden": "true" }, " *") : null;
    const err = h("p", { class: "form-error", id: `${id}-err`, role: "alert", hidden: true });
    if (f.type === "checks" || f.type === "radio") {
      const multi = f.type === "checks";
      const wrap = h("div", { class: `form-field form-field--${multi ? "checkboxGroup" : "radioGroup"}`, role: multi ? "group" : "radiogroup", "aria-labelledby": `${id}-l`, "data-name": f.name });
      const choices = h("div", { class: "form-choices" });
      f.options.forEach((o, i) => {
        const input = h("input", { type: multi ? "checkbox" : "radio", name: f.name, value: o, id: `${id}-${i}` });
        const lab = h("label", { class: "form-choice", for: `${id}-${i}` }, input, h("span", { class: "form-choice-label" }, o));
        input.addEventListener("change", () => {
          wrap.querySelectorAll(".form-choice").forEach((c) => c.classList.toggle("form-choice--selected", c.querySelector("input").checked));
          err.hidden = true;
        });
        choices.append(lab);
      });
      wrap.append(h("p", { class: "form-label", id: `${id}-l` }, f.label, req), choices, err);
      return wrap;
    }
    const wrap = h("div", { class: `form-field form-field--${f.type}`, "data-name": f.name });
    const ctrl = f.type === "textarea"
      ? h("textarea", { class: "form-control", name: f.name, id, rows: "4", placeholder: f.placeholder })
      : h("input", { class: "form-control", name: f.name, id, type: f.type, autocomplete: f.auto, placeholder: f.placeholder, required: f.required, "aria-describedby": `${id}-err` });
    ctrl.addEventListener("input", () => { err.hidden = true; });
    wrap.append(h("label", { class: "form-label", for: id }, f.label, req), ctrl, err);
    return wrap;
  }

  function values() {
    const fd = new FormData(form);
    const out = {};
    for (const s of STEPS) for (const f of s.fields) {
      out[f.name] = f.type === "checks" ? fd.getAll(f.name) : (fd.get(f.name) || "").toString().trim();
    }
    return out;
  }

  function check(i) {
    const v = values();
    let ok = true, first = null;
    for (const f of STEPS[i].fields) {
      const box = form.querySelector(`[data-name="${f.name}"]`), err = box.querySelector(".form-error");
      let msg = "";
      const val = v[f.name];
      if (f.required && (Array.isArray(val) ? !val.length : !val)) msg = f.type === "checks" ? "Pick at least one." : "Please fill this in.";
      else if (f.type === "email" && val && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) msg = "Please enter a valid email.";
      else if (f.type === "tel" && val && val.replace(/\D/g, "").length < 10) msg = "Please enter a 10-digit phone number.";
      err.textContent = msg; err.hidden = !msg;
      if (msg) { ok = false; first = first || box.querySelector("input,textarea"); }
    }
    if (first) first.focus();
    return ok;
  }

  function show(i) {
    step = i;
    boxes.forEach((b, n) => { b.hidden = n !== i; });
    title.textContent = STEPS[i].title;
    count.textContent = `Step ${i + 1} of ${STEPS.length}`;
    back.hidden = i === 0;
    next.hidden = i === STEPS.length - 1;
    submit.hidden = i !== STEPS.length - 1;
    error.hidden = true;
    onStep && onStep(i + 1, STEPS.length, boxes[i]);
  }

  back.addEventListener("click", () => show(step - 1));
  next.addEventListener("click", () => { if (check(step)) show(step + 1); });
  form.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && e.target.tagName === "INPUT" && step < STEPS.length - 1) { e.preventDefault(); next.click(); }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!check(step)) return;
    if (trap.checked) return;
    const v = values();
    const payload = {
      access_key: ACCESS_KEY,
      subject: `New quote request: ${v.name}${v.business_name ? ` (${v.business_name})` : ""}`,
      from_name: "callesgroup.com quote form",
      replyto: v.email,
      "What do you need?": v.need.join(", "),
      "Budget": v.budget || "-",
      "Kind of business": v.business_type || "-",
      "Has a website": v.current_website || "-",
      "Has a logo": v.have_logo || "-",
      "Name": v.name,
      "Business name": v.business_name || "-",
      "Email": v.email,
      "Phone": v.phone ? usPhone(v.phone) : "-",
      "Message": v.message || "-",
      "Page": location.href,
    };
    submit.disabled = back.disabled = true;
    submit.textContent = "Sending…";
    form.dataset.state = "sending";
    try {
      const res = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || data.success === false) throw new Error(data.message || res.status);
      form.dataset.state = "done";
      onDone && onDone();
    } catch (err) {
      form.dataset.state = "ready";
      submit.disabled = back.disabled = false;
      submit.textContent = "Send my request";
      error.innerHTML = 'Sorry, that didn\'t send. Please try again, or call or text <a href="tel:+13126000590">312-600-0590</a> or email <a href="mailto:andrew@callesgroup.com">andrew@callesgroup.com</a>.';
      error.hidden = false;
    }
  });

  // ?need=<key>: tick the matching boxes and start the message.
  if (need) {
    form.querySelectorAll('input[name="need"]').forEach((i) => {
      if (need.checks.includes(i.value)) { i.checked = true; i.dispatchEvent(new Event("change")); }
    });
    if (need.note) form.querySelector('[name="message"]').value = need.note;
  }

  show(0);
  return form;
}
