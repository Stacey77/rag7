// 60-second app teasers. Any element with data-demo="<app name>" opens one.
// Each demo is a simulated walkthrough with sample data. It plays once, then
// self-destructs when its timer runs out, and offers a booking link.
(function () {
  "use strict";
  var LIMIT = 60;                       // seconds before the demo self-destructs
  var COOLDOWN = 24 * 60 * 60 * 1000;   // one run per app per visitor per day
  var CAL = "https://cal.com/stacey-williams-5enqex/discovery-call";

  var css = "\
.nd-demo-btn{cursor:pointer}\
dialog.nd-demo{border:0;padding:0;border-radius:16px;width:min(640px,calc(100vw - 24px));max-height:calc(100vh - 24px);max-height:calc(100dvh - 24px);overflow:hidden;background:#0E1729;color:#E8EDF7;box-shadow:0 24px 60px rgba(8,14,30,.45);font-family:var(--body,system-ui,sans-serif)}\
dialog.nd-demo[open]{display:flex;flex-direction:column}\
dialog.nd-demo::backdrop{background:rgba(8,14,30,.6)}\
.nd-h,.nd-bar,.nd-f{flex:none}\
.nd-h{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;padding:20px 22px 14px;border-bottom:1px solid #22304D}\
.nd-h h3{margin:0;font-family:var(--display,system-ui,sans-serif);font-size:1.3rem;letter-spacing:-.01em;color:#fff}\
.nd-h p{margin:4px 0 0;color:#A9B6CF;font-size:.95rem}\
.nd-timer{flex:none;text-align:center;font-variant-numeric:tabular-nums}\
.nd-timer b{display:block;font-size:1.5rem;font-weight:700;color:#FFC861;line-height:1}\
.nd-timer span{font-size:.72rem;color:#A9B6CF;text-transform:uppercase;letter-spacing:.06em}\
.nd-timer.low b{color:#FF7A7A}\
.nd-bar{height:3px;background:#22304D}.nd-bar i{display:block;height:100%;background:#FFC861;width:100%;transition:width 1s linear}\
.nd-b{padding:16px 22px 6px;overflow:auto;flex:1 1 auto;min-height:120px}\
.nd-b:focus{outline:none}.nd-b:focus-visible{outline:2px solid #FFC861;outline-offset:-2px;border-radius:4px}\
.nd-ask{background:#17233C;border:1px solid #22304D;border-radius:10px;padding:10px 12px;margin-bottom:12px;font-size:.95rem}\
.nd-ask small{display:block;color:#7F8DA8;font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px}\
.nd-step{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;padding:8px 0;border-bottom:1px dashed #22304D;animation:ndIn .35s ease both}\
.nd-step em{font-style:normal;font-size:.75rem;font-weight:700;color:#0E1729;background:#7FA2FF;border-radius:999px;padding:2px 8px;height:fit-content;white-space:nowrap;justify-self:start}\
.nd-res{margin:14px 0 4px;border:1px solid #2F5BEA;border-radius:12px;overflow:hidden;animation:ndIn .4s ease both}\
.nd-res h4{margin:0;padding:9px 12px;background:#2F5BEA;color:#fff;font-size:.95rem}\
.nd-res dl{display:grid;grid-template-columns:1fr 1fr;margin:0}\
.nd-res dl div{padding:9px 12px;border-top:1px solid #22304D}\
.nd-res dt{font-size:.75rem;color:#A9B6CF}.nd-res dd{margin:0;font-weight:600;color:#fff}\
.nd-dots::after{content:'';animation:ndDots 1.2s steps(4) infinite}\
.nd-f{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;padding:14px 22px 18px;border-top:1px solid #22304D}\
.nd-f small{color:#7F8DA8;font-size:.78rem}\
.nd-f .nd-acts{display:flex;gap:8px;flex-wrap:wrap}\
.nd-btn{display:inline-block;border:0;border-radius:9px;padding:10px 16px;font:600 .95rem var(--body,system-ui,sans-serif);text-decoration:none;cursor:pointer;background:#2F5BEA;color:#fff}\
.nd-btn:hover{background:#1A3AAE}.nd-btn.ghost{background:transparent;color:#E8EDF7;border:1.5px solid #3A4B6E}.nd-btn.ghost:hover{background:#17233C}\
.nd-gone{text-align:center;padding:34px 10px 20px;animation:ndIn .5s ease both}\
.nd-gone b{display:block;font-family:var(--display,system-ui,sans-serif);font-size:1.4rem;color:#fff;margin-bottom:6px}\
.nd-gone p{color:#A9B6CF;margin:0 auto 18px;max-width:42ch}\
.nd-burn{animation:ndBurn 1.1s ease forwards}\
@keyframes ndIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}\
@keyframes ndDots{0%{content:''}25%{content:'.'}50%{content:'..'}75%{content:'...'}}\
@keyframes ndBurn{0%{filter:none;opacity:1}30%{filter:blur(1px) hue-rotate(60deg);transform:skewX(-4deg)}60%{filter:blur(4px) saturate(3);opacity:.6;transform:skewX(6deg) scale(.98)}100%{filter:blur(12px);opacity:0;transform:scale(.94)}}\
@media (prefers-reduced-motion:reduce){.nd-step,.nd-res,.nd-gone{animation:none}.nd-burn{animation:none;opacity:0}.nd-bar i{transition:none}}\
@media (max-width:520px){.nd-res dl{grid-template-columns:1fr 1fr}.nd-step{grid-template-columns:1fr}.nd-h{padding:16px 16px 12px}.nd-h h3{font-size:1.1rem}.nd-h p{font-size:.88rem}.nd-b{padding:12px 16px 4px}.nd-f{padding:12px 16px 14px}.nd-f small{width:100%}.nd-btn{padding:9px 13px;font-size:.88rem}}";

  function el(tag, cls, html) { var e = document.createElement(tag); if (cls) e.className = cls; if (html != null) e.innerHTML = html; return e; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function bookUrl(name) { return CAL + "?app=" + encodeURIComponent(name); }
  function lastRun(name) { try { return +localStorage.getItem("nd-demo:" + name) || 0; } catch (e) { return 0; } }
  function markRun(name) { try { localStorage.setItem("nd-demo:" + name, String(Date.now())); } catch (e) {} }

  var dlg, timers = [];
  function clearTimers() { timers.forEach(clearTimeout); timers.forEach(clearInterval); timers = []; }
  function later(fn, ms) { timers.push(setTimeout(fn, ms)); }

  function ensureDialog() {
    if (dlg) return dlg;
    var st = el("style"); st.textContent = css; document.head.appendChild(st);
    dlg = el("dialog", "nd-demo");
    dlg.setAttribute("aria-labelledby", "nd-demo-title");
    dlg.addEventListener("close", clearTimers);
    dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
    document.body.appendChild(dlg);
    return dlg;
  }

  function footer(name, d, note) {
    return '<div class="nd-f"><small>' + esc(note) + '</small><div class="nd-acts">' +
      (d.url ? '<a class="nd-btn ghost" href="' + esc(d.url) + '" target="_blank" rel="noopener">Try the full app</a>' : "") +
      '<a class="nd-btn" href="' + esc(bookUrl(name)) + '" target="_blank" rel="noopener">Book a demo on your data</a>' +
      '<button type="button" class="nd-btn ghost" data-nd-close>Close</button></div></div>';
  }

  function gone(name, d, again) {
    var body = dlg.querySelector(".nd-b");
    body.innerHTML = '<div class="nd-gone"><b>This demo has self-destructed.</b><p>' +
      (again ? "You've already watched this one today. " : "") +
      "That was sample data. Book 30 minutes and see " + esc(name) + " work on your own projects, numbers and team.</p>" +
      '<a class="nd-btn" href="' + esc(bookUrl(name)) + '" target="_blank" rel="noopener">Book a demo on your data</a></div>';
    var t = dlg.querySelector(".nd-timer"); if (t) t.innerHTML = "<b>0:00</b><span>expired</span>";
    var bar = dlg.querySelector(".nd-bar i"); if (bar) bar.style.width = "0";
  }

  function open(name) {
    var d = (window.ND_DEMOS || {})[name];
    if (!d) { window.open(bookUrl(name), "_blank", "noopener"); return; }
    ensureDialog(); clearTimers();
    var again = Date.now() - lastRun(name) < COOLDOWN;
    dlg.innerHTML =
      '<div class="nd-h"><div><h3 id="nd-demo-title">' + esc(name) + "</h3><p>" + esc(d.tag) + '</p></div>' +
      '<div class="nd-timer" aria-live="off"><b>1:00</b><span>self-destructs</span></div></div>' +
      '<div class="nd-bar"><i></i></div><div class="nd-b" tabindex="0" role="region" aria-label="Demo walkthrough for ' + esc(name) + '" aria-live="polite"></div>' +
      footer(name, d, "Simulated walkthrough with sample data.");
    var closeBtn = dlg.querySelector("[data-nd-close]");
    closeBtn.onclick = function () { dlg.close(); };
    if (!dlg.open) dlg.showModal();
    closeBtn.focus();                   // predictable start point; Esc and the backdrop also close
    if (again) { gone(name, d, true); return; }
    markRun(name);

    var body = dlg.querySelector(".nd-b"), tEl = dlg.querySelector(".nd-timer"), bar = dlg.querySelector(".nd-bar i");
    var left = LIMIT;
    timers.push(setInterval(function () {
      left -= 1;
      tEl.querySelector("b").textContent = "0:" + String(Math.max(left, 0)).padStart(2, "0");
      bar.style.width = (Math.max(left, 0) / LIMIT * 100) + "%";
      if (left <= 10) tEl.classList.add("low");
      if (left <= 0) {
        clearTimers();
        body.classList.add("nd-burn");
        later(function () { body.classList.remove("nd-burn"); gone(name, d, false); }, 1100);
      }
    }, 1000));

    var ask = el("div", "nd-ask", "<small>Request</small>");
    var askText = el("span"); ask.appendChild(askText); body.appendChild(ask);
    var i = 0, text = d.ask;
    (function type() { askText.textContent = text.slice(0, ++i); if (i < text.length) later(type, 18); else run(); })();

    function run() {
      var working = el("div", "nd-step", '<em>Working</em><span class="nd-dots">Agents are on it</span>');
      body.appendChild(working);
      d.steps.forEach(function (s, k) {
        later(function () {
          working.remove();
          body.appendChild(el("div", "nd-step", "<em>" + esc(s[0]) + "</em><span>" + esc(s[1]) + "</span>"));
          if (k < d.steps.length - 1) body.appendChild(working);
          body.scrollTop = body.scrollHeight;
        }, 1400 + k * 2200);
      });
      later(function () {
        var r = d.result;
        body.appendChild(el("div", "nd-res", "<h4>" + esc(r.title) + "</h4><dl>" +
          r.rows.map(function (x) { return "<div><dt>" + esc(x[0]) + "</dt><dd>" + esc(x[1]) + "</dd></div>"; }).join("") + "</dl>"));
        body.scrollTop = body.scrollHeight;
      }, 1400 + d.steps.length * 2200);
    }
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("[data-demo]");
    if (!b) return;
    e.preventDefault(); open(b.getAttribute("data-demo"));
  });
  window.NDDemo = { open: open };
})();
