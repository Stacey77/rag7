// 5-minute app test drives. Any element with data-demo="<app name>" opens one.
// Each app has its own script in drives/<slug>.json (loaded on demand): a few scenarios, each with
// inputs the visitor can change, the AI agents' steps, a result card and follow-up questions.
// Text can use {input_id} for an input's value and {=expression} for simple arithmetic on inputs.
// Everything runs in the browser on sample data. The test drive self-destructs after 5 minutes.
(function () {
  "use strict";
  var LIMIT = 300;                      // seconds: 5 minutes
  var COOLDOWN = 24 * 60 * 60 * 1000;   // one test drive per app per visitor per day
  var CAL = "https://cal.com/stacey-williams-5enqex/discovery-call";
  var INDEX = window.ND_DRIVES || {};   // app name -> { slug, url }
  var BASE = (function () {             // folder that holds drives/, next to demos.js
    var s = document.currentScript || document.querySelector('script[src$="demos.js"]');
    return s && s.src ? s.src.replace(/demos\.js(\?.*)?$/, "") : "";
  })();

  var css = "\
.nd-demo-btn{cursor:pointer}\
dialog.nd-demo{border:0;padding:0;border-radius:16px;width:min(720px,calc(100vw - 24px));max-height:calc(100vh - 24px);max-height:calc(100dvh - 24px);overflow:hidden;background:#0E1729;color:#E8EDF7;box-shadow:0 24px 60px rgba(8,14,30,.45);font-family:var(--body,system-ui,sans-serif)}\
dialog.nd-demo[open]{display:flex;flex-direction:column}\
dialog.nd-demo::backdrop{background:rgba(8,14,30,.6)}\
.nd-h,.nd-bar,.nd-f{flex:none}\
.nd-h{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;padding:18px 22px 12px;border-bottom:1px solid #22304D}\
.nd-h h3{margin:0;font-family:var(--display,system-ui,sans-serif);font-size:1.3rem;letter-spacing:-.01em;color:#fff}\
.nd-h p{margin:4px 0 0;color:#A9B6CF;font-size:.95rem}\
.nd-timer{flex:none;text-align:center;font-variant-numeric:tabular-nums}\
.nd-timer b{display:block;font-size:1.5rem;font-weight:700;color:#FFC861;line-height:1}\
.nd-timer span{font-size:.72rem;color:#A9B6CF;text-transform:uppercase;letter-spacing:.06em}\
.nd-timer.low b{color:#FF7A7A}\
.nd-bar{height:3px;background:#22304D}.nd-bar i{display:block;height:100%;background:#FFC861;width:100%;transition:width 1s linear}\
.nd-b{padding:16px 22px 8px;overflow:auto;flex:1 1 auto;min-height:160px}\
.nd-b:focus-visible{outline:2px solid #FFC861;outline-offset:-2px}\
.nd-kicker{font-size:.75rem;color:#7F8DA8;text-transform:uppercase;letter-spacing:.06em;margin:0 0 8px}\
.nd-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-bottom:14px}\
.nd-card{all:unset;box-sizing:border-box;cursor:pointer;display:block;background:#17233C;border:1px solid #2A3A5C;border-radius:12px;padding:12px 14px}\
.nd-card:hover,.nd-card:focus-visible{border-color:#7FA2FF;outline:none}\
.nd-card b{display:block;color:#fff;margin-bottom:4px}\
.nd-card span{font-size:.88rem;color:#A9B6CF}\
.nd-own textarea{width:100%;box-sizing:border-box;min-height:64px;background:#17233C;border:1px solid #2A3A5C;border-radius:10px;color:#E8EDF7;padding:10px 12px;font:inherit;resize:vertical}\
.nd-own .nd-row{margin-top:8px}\
.nd-ask{background:#17233C;border:1px solid #22304D;border-radius:10px;padding:10px 12px;margin-bottom:12px;font-size:.95rem}\
.nd-ask small{display:block;color:#7F8DA8;font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px}\
.nd-inputs{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:4px 0 14px}\
.nd-inputs label{display:block;font-size:.82rem;color:#A9B6CF;margin-bottom:4px}\
.nd-inputs output{float:right;color:#FFC861;font-weight:700}\
.nd-inputs input[type=range]{width:100%;accent-color:#7FA2FF}\
.nd-inputs select{width:100%;background:#17233C;color:#E8EDF7;border:1px solid #2A3A5C;border-radius:8px;padding:8px}\
.nd-step{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;padding:8px 0;border-bottom:1px dashed #22304D;animation:ndIn .35s ease both}\
.nd-step em{font-style:normal;font-size:.75rem;font-weight:700;color:#0E1729;background:#7FA2FF;border-radius:999px;padding:2px 8px;height:fit-content;white-space:nowrap;justify-self:start}\
.nd-res{margin:14px 0 4px;border:1px solid #2F5BEA;border-radius:12px;overflow:hidden;animation:ndIn .4s ease both}\
.nd-res h4{margin:0;padding:9px 12px;background:#2F5BEA;color:#fff;font-size:.95rem}\
.nd-res dl{display:grid;grid-template-columns:1fr 1fr;margin:0}\
.nd-res dl div{padding:9px 12px;border-top:1px solid #22304D}\
.nd-res dt{font-size:.75rem;color:#A9B6CF}.nd-res dd{margin:0;font-weight:600;color:#fff}\
.nd-chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 4px}\
.nd-chip{border:1px solid #3A4B6E;background:transparent;color:#E8EDF7;border-radius:999px;padding:7px 12px;font:500 .88rem var(--body,system-ui,sans-serif);cursor:pointer}\
.nd-chip:hover,.nd-chip:focus-visible{border-color:#7FA2FF;outline:none}\
.nd-qa{background:#17233C;border-left:3px solid #7FA2FF;border-radius:8px;padding:10px 12px;margin-top:10px;animation:ndIn .35s ease both}\
.nd-qa b{display:block;color:#fff;margin-bottom:4px}\
.nd-note{font-size:.82rem;color:#A9B6CF;margin:8px 0 0}\
.nd-dots::after{content:'';animation:ndDots 1.2s steps(4) infinite}\
.nd-f{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;padding:12px 22px 16px;border-top:1px solid #22304D}\
.nd-f small{color:#7F8DA8;font-size:.78rem}\
.nd-acts{display:flex;gap:8px;flex-wrap:wrap}\
.nd-btn{display:inline-block;border:0;border-radius:9px;padding:10px 16px;font:600 .95rem var(--body,system-ui,sans-serif);text-decoration:none;cursor:pointer;background:#2F5BEA;color:#fff}\
.nd-btn:hover{background:#1A3AAE}.nd-btn.ghost{background:transparent;color:#E8EDF7;border:1.5px solid #3A4B6E}.nd-btn.ghost:hover{background:#17233C}\
.nd-btn:focus-visible,.nd-chip:focus-visible{outline:2px solid #FFC861;outline-offset:2px}\
.nd-gone{text-align:center;padding:34px 10px 20px;animation:ndIn .5s ease both}\
.nd-gone b{display:block;font-family:var(--display,system-ui,sans-serif);font-size:1.4rem;color:#fff;margin-bottom:6px}\
.nd-gone p{color:#A9B6CF;margin:0 auto 18px;max-width:44ch}\
.nd-burn{animation:ndBurn 1.1s ease forwards}\
@keyframes ndIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}\
@keyframes ndDots{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}}\
@keyframes ndBurn{0%{filter:none;opacity:1}30%{filter:blur(1px) hue-rotate(60deg);transform:skewX(-4deg)}60%{filter:blur(4px) saturate(3);opacity:.6;transform:skewX(6deg) scale(.98)}100%{filter:blur(12px);opacity:0;transform:scale(.94)}}\
@media (prefers-reduced-motion:reduce){.nd-step,.nd-res,.nd-gone,.nd-qa{animation:none}.nd-burn{animation:none;opacity:0}.nd-bar i{transition:none}}\
@media (max-width:520px){.nd-step{grid-template-columns:1fr}.nd-h{padding:14px 16px 10px}.nd-h h3{font-size:1.1rem}.nd-h p{font-size:.88rem}.nd-b{padding:12px 16px 4px}.nd-f{padding:10px 16px 12px}.nd-f small{width:100%}.nd-btn{padding:9px 13px;font-size:.88rem}}";

  // ---------- tiny, safe arithmetic for {=expression} (numbers, + - * / ( ), and a few functions)
  var FN = {
    round: function (x, d) { var k = Math.pow(10, d || 0); return Math.round(x * k) / k; },
    ceil: Math.ceil, floor: Math.floor, min: Math.min, max: Math.max, abs: Math.abs
  };
  function evaluate(src, vars) {
    var s = String(src), i = 0;
    function ws() { while (s[i] === " ") i++; }
    function num() { var m = /^\d+(\.\d+)?/.exec(s.slice(i)); if (!m) throw 0; i += m[0].length; return parseFloat(m[0]); }
    function ident() { var m = /^[A-Za-z_][A-Za-z0-9_]*/.exec(s.slice(i)); if (!m) throw 0; i += m[0].length; return m[0]; }
    function atom() {
      ws();
      if (s[i] === "(") { i++; var v = expr(); ws(); if (s[i++] !== ")") throw 0; return v; }
      if (s[i] === "-") { i++; return -atom(); }
      if (/\d/.test(s[i])) return num();
      var id = ident(); ws();
      if (s[i] === "(") {
        i++; var args = []; ws();
        if (s[i] !== ")") { for (;;) { args.push(expr()); ws(); if (s[i] === ",") { i++; continue; } break; } }
        if (s[i++] !== ")" || !FN[id]) throw 0;
        return FN[id].apply(null, args);
      }
      if (!(id in vars)) throw 0;
      return +vars[id];
    }
    function term() { var v = atom(); for (;;) { ws(); if (s[i] === "*") { i++; v *= atom(); } else if (s[i] === "/") { i++; v /= atom(); } else return v; } }
    function expr() { var v = term(); for (;;) { ws(); if (s[i] === "+") { i++; v += term(); } else if (s[i] === "-") { i++; v -= term(); } else return v; } }
    try { var r = expr(); ws(); if (i !== s.length || !isFinite(r)) return null; return r; } catch (e) { return null; }
  }
  function fmt(n) { return (Math.round(n * 100) / 100).toLocaleString("en-US"); }
  function fill(text, sc) {
    var src = String(text || "");
    return src.replace(/\{(=?)([^{}]+)\}/g, function (all, isExpr, body, at) {
      if (isExpr) { var v = evaluate(body, sc.nums); return v == null ? "" : fmt(v); }
      if (!(body in sc.labels)) return all;
      // "{weeks} weeks" in a script shouldn't read "3 weeks weeks": drop the unit when the text already says it.
      var unit = sc.units[body], after = src.slice(at + all.length).toLowerCase();
      return unit && after.indexOf(" " + unit.toLowerCase()) === 0 ? sc.plain[body] : sc.labels[body];
    });
  }

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function bookUrl(name) { return CAL + "?app=" + encodeURIComponent(name); }
  function lastRun(name) { try { return +localStorage.getItem("nd-drive:" + name) || 0; } catch (e) { return 0; } }
  function markRun(name) { try { localStorage.setItem("nd-drive:" + name, String(Date.now())); } catch (e) {} }

  var cache = {};
  function load(name) {
    var inline = (window.ND_DRIVE_DATA || {})[name];
    if (inline) return Promise.resolve(inline);
    var meta = INDEX[name];
    if (!meta) return Promise.reject(new Error("no drive"));
    if (cache[name]) return cache[name];
    return (cache[name] = fetch(BASE + "drives/" + meta.slug + ".json").then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }));
  }

  var dlg, timers = [], state = null;
  function clearTimers() { timers.forEach(function (t) { clearTimeout(t); clearInterval(t); }); timers = []; }
  function later(fn, ms) { var t = setTimeout(fn, ms); timers.push(t); return t; }

  function ensureDialog() {
    if (dlg) return dlg;
    var st = el("style"); st.textContent = css; document.head.appendChild(st);
    dlg = el("dialog", "nd-demo");
    dlg.setAttribute("aria-labelledby", "nd-demo-title");
    dlg.addEventListener("close", function () { clearTimers(); state = null; });
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
    document.body.appendChild(dlg);
    return dlg;
  }

  function shell(name, d) {
    var url = (INDEX[name] && INDEX[name].url) || d.url || "";
    dlg.innerHTML =
      '<div class="nd-h"><div><h3 id="nd-demo-title">' + esc(name) + "</h3><p>" + esc(d.tag) + "</p></div>" +
      '<div class="nd-timer" aria-live="off"><b>5:00</b><span>self-destructs</span></div></div>' +
      '<div class="nd-bar"><i></i></div>' +
      '<div class="nd-b" tabindex="0" role="region" aria-live="polite" aria-label="Test drive of ' + esc(name) + '"></div>' +
      '<div class="nd-f"><small>5-minute test drive with sample data. Nothing you type leaves this page.</small><div class="nd-acts">' +
      (url ? '<a class="nd-btn ghost" href="' + esc(url) + '" target="_blank" rel="noopener">Try the full app</a>' : "") +
      '<a class="nd-btn" href="' + esc(bookUrl(name)) + '" target="_blank" rel="noopener">Book a demo on your data</a>' +
      '<button type="button" class="nd-btn ghost" data-nd-close>Close</button></div></div>';
    dlg.querySelector("[data-nd-close]").onclick = function () { dlg.close(); };
  }

  function body() { return dlg.querySelector(".nd-b"); }

  function gone(name, again) {
    var b = body();
    b.innerHTML = '<div class="nd-gone"><b>This test drive has self-destructed.</b><p>' +
      (again ? "You've already taken this one today. " : "") +
      "That was sample data. Book 30 minutes and see " + esc(name) + " work on your own projects, numbers and team.</p>" +
      '<a class="nd-btn" href="' + esc(bookUrl(name)) + '" target="_blank" rel="noopener">Book a demo on your data</a></div>';
    var t = dlg.querySelector(".nd-timer"); if (t) t.innerHTML = "<b>0:00</b><span>expired</span>";
    var bar = dlg.querySelector(".nd-bar i"); if (bar) bar.style.width = "0";
  }

  function startTimer(name) {
    var tEl = dlg.querySelector(".nd-timer"), bar = dlg.querySelector(".nd-bar i"), left = LIMIT;
    timers.push(setInterval(function () {
      left -= 1;
      var l = Math.max(left, 0);
      tEl.querySelector("b").textContent = Math.floor(l / 60) + ":" + String(l % 60).padStart(2, "0");
      bar.style.width = (l / LIMIT * 100) + "%";
      if (left <= 30) tEl.classList.add("low");
      if (left <= 0) {
        clearTimers();
        var b = body(); b.classList.add("nd-burn");
        setTimeout(function () { if (!dlg.open) return; b.classList.remove("nd-burn"); gone(name, false); }, 1100);
      }
    }, 1000));
  }

  // ---------- screens
  function pickScreen() {
    var d = state.d, b = body();
    b.innerHTML = '<p class="nd-kicker">Step 1 of 3 · Pick a situation</p>';
    var cards = el("div", "nd-cards");
    d.scenarios.forEach(function (sc, k) {
      var c = el("button", "nd-card", "<b>" + esc(sc.title) + "</b><span>" + esc(previewAsk(sc)) + "</span>");
      c.type = "button"; c.onclick = function () { setupScreen(k, null); };
      cards.appendChild(c);
    });
    b.appendChild(cards);
    var own = el("div", "nd-own",
      '<label class="nd-kicker" for="nd-own-text">Or describe your own situation</label>' +
      '<textarea id="nd-own-text" maxlength="400" placeholder="Example: ' + esc(previewAsk(d.scenarios[0])) + '"></textarea>' +
      '<div class="nd-row"><button type="button" class="nd-btn ghost">Use my situation</button></div>');
    own.querySelector("button").onclick = function () {
      var t = own.querySelector("textarea").value.trim();
      if (!t) { own.querySelector("textarea").focus(); return; }
      setupScreen(bestMatch(t), t);
    };
    b.appendChild(own);
    b.scrollTop = 0;
  }

  function previewAsk(sc) { return fill(sc.ask, values(sc, {})); }

  // Pick the scenario whose words overlap most with what the visitor typed.
  function bestMatch(text) {
    var words = text.toLowerCase().match(/[a-z]{4,}/g) || [], best = 0, top = -1;
    state.d.scenarios.forEach(function (sc, k) {
      var hay = (sc.title + " " + sc.ask).toLowerCase(), n = 0;
      words.forEach(function (w) { if (hay.indexOf(w) >= 0) n++; });
      if (n > top) { top = n; best = k; }
    });
    return best;
  }

  function values(sc, chosen) {
    var nums = {}, labels = {}, plain = {}, units = {};
    (sc.inputs || []).forEach(function (inp) {
      var v = inp.id in chosen ? chosen[inp.id] : inp.value;
      if (inp.type === "select") {
        var opt = inp.options.filter(function (o) { return o.label === v; })[0] || inp.options[0];
        labels[inp.id] = opt.label; nums[inp.id] = +opt.n || 0;
      } else { nums[inp.id] = +v; plain[inp.id] = fmt(+v); units[inp.id] = inp.unit || ""; labels[inp.id] = fmt(+v) + (inp.unit ? " " + inp.unit : ""); }
      if (!(inp.id in plain)) plain[inp.id] = labels[inp.id];
    });
    return { nums: nums, labels: labels, plain: plain, units: units };
  }

  function setupScreen(k, ownText) {
    var sc = state.d.scenarios[k], b = body();
    state.k = k; state.own = ownText; state.chosen = state.chosen && state.lastK === k ? state.chosen : {};
    state.lastK = k;
    b.innerHTML = '<p class="nd-kicker">Step 2 of 3 · Set it up</p>';
    var ask = el("div", "nd-ask", "<small>Your request</small><span></span>");
    b.appendChild(ask);
    var form = el("div", "nd-inputs");
    (sc.inputs || []).forEach(function (inp) {
      var id = "nd-in-" + inp.id, wrap = el("div"), v = inp.id in state.chosen ? state.chosen[inp.id] : inp.value;
      if (inp.type === "select") {
        wrap.innerHTML = '<label for="' + id + '">' + esc(inp.label) + '</label><select id="' + id + '">' +
          inp.options.map(function (o) { return "<option" + (o.label === v ? " selected" : "") + ">" + esc(o.label) + "</option>"; }).join("") + "</select>";
      } else {
        wrap.innerHTML = '<label for="' + id + '">' + esc(inp.label) + ' <output for="' + id + '"></output></label>' +
          '<input id="' + id + '" type="range" min="' + inp.min + '" max="' + inp.max + '" step="' + (inp.step || 1) + '" value="' + v + '">';
      }
      var ctl = wrap.querySelector("select,input");
      ctl.addEventListener("input", function () { state.chosen[inp.id] = inp.type === "select" ? ctl.value : +ctl.value; refresh(); });
      form.appendChild(wrap);
    });
    if ((sc.inputs || []).length) b.appendChild(form);
    if (ownText) b.appendChild(el("p", "nd-note", "We matched your situation to the closest example: “" + esc(sc.title) + "”. Adjust the settings to fit."));
    var row = el("div", "nd-acts");
    var run = el("button", "nd-btn", "Run it"); run.type = "button"; run.onclick = function () { runScreen(); };
    var back = el("button", "nd-btn ghost", "Pick another situation"); back.type = "button"; back.onclick = pickScreen;
    row.appendChild(run); row.appendChild(back); b.appendChild(row);
    function refresh() {
      var vals = values(sc, state.chosen);
      ask.querySelector("span").textContent = ownText ? ownText : fill(sc.ask, vals);
      form.querySelectorAll("output").forEach(function (o) {
        var inp = (sc.inputs || []).filter(function (x) { return "nd-in-" + x.id === o.htmlFor.value; })[0];
        if (inp) o.textContent = vals.labels[inp.id];
      });
    }
    refresh();
    b.scrollTop = 0;
  }

  function runScreen() {
    var sc = state.d.scenarios[state.k], vals = values(sc, state.chosen), b = body();
    b.innerHTML = '<p class="nd-kicker">Step 3 of 3 · Watch it work</p>';
    b.appendChild(el("div", "nd-ask", "<small>Request</small>" + esc(state.own || fill(sc.ask, vals))));
    var working = el("div", "nd-step", '<em>Working</em><span class="nd-dots">Agents are on it</span>');
    b.appendChild(working);
    sc.steps.forEach(function (s, k) {
      later(function () {
        working.remove();
        b.appendChild(el("div", "nd-step", "<em>" + esc(s[0]) + "</em><span>" + esc(fill(s[1], vals)) + "</span>"));
        if (k < sc.steps.length - 1) b.appendChild(working);
        b.scrollTop = b.scrollHeight;
      }, 900 + k * 1700);
    });
    later(function () {
      var r = sc.result;
      b.appendChild(el("div", "nd-res", "<h4>" + esc(fill(r.title, vals)) + "</h4><dl>" +
        r.rows.map(function (x) { return "<div><dt>" + esc(x[0]) + "</dt><dd>" + esc(fill(x[1], vals)) + "</dd></div>"; }).join("") + "</dl>"));
      var chips = el("div", "nd-chips");
      (sc.followups || []).forEach(function (f) {
        var c = el("button", "nd-chip", esc(f[0])); c.type = "button";
        c.onclick = function () {
          c.disabled = true;
          var qa = el("div", "nd-qa", "<b>" + esc(f[0]) + "</b>" + esc(fill(f[1], vals)));
          chips.parentNode.insertBefore(qa, more);
          b.scrollTop = b.scrollHeight;
        };
        chips.appendChild(c);
      });
      if ((sc.followups || []).length) { b.appendChild(el("p", "nd-kicker", "Ask a follow-up")); b.appendChild(chips); }
      var more = el("div", "nd-acts"); more.style.marginTop = "14px";
      var adj = el("button", "nd-btn", "Change the settings and re-run"); adj.type = "button"; adj.onclick = function () { setupScreen(state.k, state.own); };
      var other = el("button", "nd-btn ghost", "Try another situation"); other.type = "button"; other.onclick = function () { state.own = null; pickScreen(); };
      if ((sc.inputs || []).length) more.appendChild(adj);
      more.appendChild(other);
      b.appendChild(more);
      b.scrollTop = b.scrollHeight;
    }, 900 + sc.steps.length * 1700);
  }

  function open(name) {
    ensureDialog(); clearTimers();
    load(name).then(function (d) {
      shell(name, d);
      if (!dlg.open) dlg.showModal();
      var close = dlg.querySelector("[data-nd-close]"); if (close) close.focus();
      if (Date.now() - lastRun(name) < COOLDOWN) { gone(name, true); return; }
      markRun(name);
      state = { name: name, d: d, k: 0, chosen: {} };
      startTimer(name);
      if (d.scenarios.length === 1 && !(d.scenarios[0].inputs || []).length) { state.k = 0; runScreen(); }
      else pickScreen();
    }, function () { window.open(bookUrl(name), "_blank", "noopener"); });
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-demo]");
    if (!b) return;
    e.preventDefault(); open(b.getAttribute("data-demo"));
  });
  window.NDDemo = { open: open, evaluate: evaluate };
})();
