/* Ingenium — client-side campaign brain for the dashboard.
 * Runs entirely in the browser (no server). Ported from the Python package:
 * the think/connect/execute loop plus local campaign-asset generation.
 * Edits are saved to localStorage so they persist between visits.
 */
(function () {
  "use strict";

  var STORE_KEY = "ingenium.dashboard.v1";
  var FIELD_IDS = ["ai-positioning", "ai-offer", "ai-voice", "ai-customers"];
  var lastReport = null;

  function $(id) { return document.getElementById(id); }

  // ---- edge assembled from the form ---------------------------------------
  function buildEdge() {
    var emails = $("ai-customers").value.split("\n").map(function (s) { return s.trim(); }).filter(Boolean);
    var records = emails.map(function (email, i) { return { id: "cust-" + (i + 1), email: email }; });
    var offer = $("ai-offer").value.trim();
    return {
      positioning: $("ai-positioning").value.trim(),
      offer: offer,
      voice: $("ai-voice").value.trim(),
      records: records,
    };
  }

  // ---- the execute() loop (mirrors ingenium/core + agent stages) ----------
  function execute(objective, edge) {
    var sent = edge.records.map(function (r) { return { to: r.email, subject: objective }; });
    var scheduled = sent.map(function (m) { return { title: "Follow up: " + objective, attendees: [m.to] }; });
    var recommendation = sent.length ? "scale" : "insufficient_data";
    return {
      objective: objective,
      edge: edge,
      pipeline: {
        research: { targetSegment: edge.records.length },
        create: { slug: slug(objective), title: objective },
        outreach: { sent: sent },
        followUp: { scheduled: scheduled },
        optimize: { recommendation: recommendation, reached: sent.length },
      },
    };
  }

  function slug(text) {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60) || "campaign";
  }

  // ---- real campaign assets, generated locally ----------------------------
  function landingHtml(report) {
    var e = report.edge, esc = escapeHtml;
    var offer = e.offer ? '<p class="offer">' + esc(e.offer) + "</p>" : "";
    var css = "body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1a1d24;background:#f7f7f9}" +
      ".hero{max-width:720px;margin:0 auto;padding:4rem 1.5rem;text-align:center}h1{font-size:2.4rem;margin-bottom:.5rem}" +
      ".sub{color:#5b6270;font-size:1.1rem}.offer{display:inline-block;margin:1.5rem 0;padding:.6rem 1rem;background:#eef;border-radius:8px;font-weight:600}" +
      ".cta{display:inline-block;margin-top:1rem;padding:.8rem 1.6rem;background:#5b5bf0;color:#fff;text-decoration:none;border-radius:8px}";
    return [
      "<!doctype html>",
      '<html lang="en"><head><meta charset="utf-8">',
      '<meta name="viewport" content="width=device-width, initial-scale=1">',
      "<title>" + esc(report.objective) + "</title>",
      "<style>" + css + "</style></head>",
      '<body><main class="hero">',
      "<h1>" + esc(report.objective) + "</h1>",
      '<p class="sub">' + esc(e.positioning) + "</p>",
      offer,
      '<div><a class="cta" href="#contact">Get started</a></div>',
      "</main></body></html>",
      "",
    ].join("\n");
  }

  function emailText(report) {
    var e = report.edge;
    var out = [];
    report.pipeline.outreach.sent.forEach(function (m) {
      var body = ["Hi there,", ""];
      body.push((e.positioning ? "We're " + e.positioning + ". " : "") + report.objective + " — and we wanted you to be first to know.");
      if (e.offer) body.push("", "This month: " + e.offer + ".");
      body.push("", "Reply to this email or give us a call to lock it in.", "", "Talk soon,", "The team");
      out.push("To: " + m.to + "\nSubject: " + report.objective + "\n\n" + body.join("\n") + "\n");
    });
    return out.join("\n----------------------------------------\n\n");
  }

  function icsText(report) {
    function pad(n) { return String(n).padStart(2, "0"); }
    var now = new Date();
    var when = new Date(now.getTime() + 3 * 24 * 3600 * 1000);
    function fmt(d) {
      return d.getUTCFullYear() + pad(d.getUTCMonth() + 1) + pad(d.getUTCDate()) + "T" +
        pad(d.getUTCHours()) + pad(d.getUTCMinutes()) + pad(d.getUTCSeconds()) + "Z";
    }
    var lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Ingenium//Campaign//EN", "CALSCALE:GREGORIAN"];
    report.pipeline.followUp.scheduled.forEach(function (ev, i) {
      lines.push("BEGIN:VEVENT", "UID:ingenium-" + fmt(now) + "-" + (i + 1) + "@campaign",
        "DTSTAMP:" + fmt(now), "DTSTART:" + fmt(when), "DURATION:PT30M",
        "SUMMARY:Follow up: " + report.objective, "DESCRIPTION:Follow up with " + (ev.attendees[0] || ""), "END:VEVENT");
    });
    lines.push("END:VCALENDAR");
    return lines.join("\r\n") + "\r\n";
  }

  function csvText(report) {
    var rows = [["recipient", "objective", "subject", "status"]];
    report.pipeline.outreach.sent.forEach(function (m) { rows.push([m.to, report.objective, m.subject, "drafted"]); });
    return rows.map(function (r) {
      return r.map(function (c) { return /[",\n]/.test(c) ? '"' + c.replace(/"/g, '""') + '"' : c; }).join(",");
    }).join("\n") + "\n";
  }

  function download(filename, text, type) {
    var blob = new Blob([text], { type: type || "text/plain" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  // ---- rendering ----------------------------------------------------------
  function renderReport(report) {
    var p = report.pipeline;
    var stages = [
      ["Research", "Sized up " + p.research.targetSegment + " customer(s)"],
      ["Create", 'Landing page "' + report.objective + '" ready'],
      ["Outreach", p.outreach.sent.length ? p.outreach.sent.length + " email(s) drafted" : "No customers yet"],
      ["Follow-up", p.followUp.scheduled.length + " follow-up(s) scheduled"],
      ["Optimize", "Recommendation: " + p.optimize.recommendation.replace("_", " ")],
    ];
    $("ai-stages").innerHTML = stages.map(function (s) {
      return '<li class="ai-stage"><span class="ai-stage__name">' + s[0] + "</span>" +
        '<span class="ai-stage__detail">' + escapeHtml(s[1]) + "</span></li>";
    }).join("");
    $("ai-output").hidden = false;
    var rec = p.optimize.recommendation;
    var badge = $("ai-rec");
    badge.textContent = rec === "scale" ? "Ready to scale" : "Add customers to act";
    badge.className = "ai-rec ai-rec--" + rec;
    $("ai-downloads").hidden = p.outreach.sent.length === 0 && rec !== "scale";
  }

  // ---- persistence --------------------------------------------------------
  function saveFields() {
    var data = {};
    FIELD_IDS.forEach(function (id) { data[id] = $(id).value; });
    try { localStorage.setItem(STORE_KEY, JSON.stringify(data)); } catch (e) { /* ignore */ }
  }
  function loadFields() {
    var raw;
    try { raw = localStorage.getItem(STORE_KEY); } catch (e) { return; }
    if (!raw) return;
    var data; try { data = JSON.parse(raw); } catch (e) { return; }
    FIELD_IDS.forEach(function (id) { if (typeof data[id] === "string") $(id).value = data[id]; });
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---- wire up ------------------------------------------------------------
  function run() {
    var objective = $("ai-objective").value.trim();
    if (!objective) return;
    saveFields();
    lastReport = execute(objective, buildEdge());
    renderReport(lastReport);
  }

  function init() {
    if (!$("ai-campaign")) return; // section not present
    loadFields();
    $("ai-run").addEventListener("click", run);
    $("ai-objective").addEventListener("keydown", function (e) { if (e.key === "Enter") run(); });
    FIELD_IDS.forEach(function (id) { $(id).addEventListener("change", saveFields); });
    $("dl-landing").addEventListener("click", function () { if (lastReport) download("landing.html", landingHtml(lastReport), "text/html"); });
    $("dl-emails").addEventListener("click", function () { if (lastReport) download("emails.txt", emailText(lastReport)); });
    $("dl-ics").addEventListener("click", function () { if (lastReport) download("followups.ics", icsText(lastReport), "text/calendar"); });
    $("dl-csv").addEventListener("click", function () { if (lastReport) download("outreach.csv", csvText(lastReport), "text/csv"); });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
