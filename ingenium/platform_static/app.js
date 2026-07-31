"use strict";
var current = null; // active workspace slug

function $(id) { return document.getElementById(id); }
function showError(id, msg) { var el = $(id); el.textContent = msg || ""; el.hidden = !msg; }

async function api(method, path, body) {
  var opts = { method: method, headers: {} };
  if (body !== undefined) { opts.headers["Content-Type"] = "application/json"; opts.body = JSON.stringify(body); }
  var res = await fetch(path, opts);
  var data = res.status === 204 ? {} : await res.json();
  if (!res.ok) throw new Error((data && data.error) || ("HTTP " + res.status));
  return data;
}

// -- workspace list ----------------------------------------------------------
async function loadWorkspaces() {
  var data = await api("GET", "/api/workspaces");
  var list = $("workspace-list");
  list.innerHTML = data.workspaces
    .map(function (w) {
      return '<li data-slug="' + w.slug + '"' + (w.slug === current ? ' class="active"' : "") +
        ">" + escapeHtml(w.name) + '<span class="badge">' + w.runs + " run" + (w.runs === 1 ? "" : "s") + "</span></li>";
    })
    .join("");
  Array.prototype.forEach.call(list.querySelectorAll("li"), function (li) {
    li.addEventListener("click", function () { selectWorkspace(li.dataset.slug); });
  });
}

async function createWorkspace() {
  var name = $("new-name").value.trim();
  if (!name) { showError("sidebar-error", "Enter a name."); return; }
  showError("sidebar-error", "");
  try {
    var meta = await api("POST", "/api/workspaces", { name: name, seed: $("new-seed").checked });
    $("new-name").value = "";
    await loadWorkspaces();
    selectWorkspace(meta.slug);
  } catch (e) { showError("sidebar-error", e.message); }
}

// -- edge editor <-> snapshot ------------------------------------------------
function fillEdge(edge) {
  var s = edge.strategy || {};
  $("e-positioning").value = s.positioning || "";
  $("e-priority").value = (s.priorities && s.priorities[0] && s.priorities[0].name) || "";
  var recs = (edge.customer_data && edge.customer_data.records) || [];
  $("e-customers").value = recs.map(function (r) { return r.email || r.id; }).filter(Boolean).join("\n");
  var goalNames = Object.keys(edge.goals || {});
  var g = goalNames.length ? edge.goals[goalNames[0]].goal : { name: "", current: "", target: "" };
  $("e-goal-name").value = g.name || goalNames[0] || "";
  $("e-goal-current").value = g.current != null ? g.current : "";
  $("e-goal-target").value = g.target != null ? g.target : "";
  var offers = (edge.knowledge && edge.knowledge.offers) || [];
  $("e-knowledge").value = offers[0] || "";
  var b = edge.brand || {};
  $("e-voice").value = b.voice || "";
  $("e-tone").value = (b.tone_words || []).join(", ");
}

function buildEdgeSnapshot() {
  var emails = $("e-customers").value.split("\n").map(function (x) { return x.trim(); }).filter(Boolean);
  var records = emails.map(function (email, i) { return { id: "cust-" + (i + 1), email: email, stage: "new" }; });
  var target = parseFloat($("e-goal-target").value) || 0;
  var current = parseFloat($("e-goal-current").value) || 0;
  var goalName = $("e-goal-name").value.trim();
  var goals = {};
  if (goalName) goals[goalName] = { goal: { name: goalName, target: target, current: current } };
  var priority = $("e-priority").value.trim();
  var offer = $("e-knowledge").value.trim();
  return {
    strategy: { positioning: $("e-positioning").value.trim(), priorities: priority ? [{ name: priority, rank: 1 }] : [] },
    customer_data: { total: records.length, records: records },
    goals: goals,
    knowledge: offer ? { offers: [offer] } : {},
    brand: {
      voice: $("e-voice").value.trim(),
      tone_words: $("e-tone").value.split(",").map(function (x) { return x.trim(); }).filter(Boolean),
      taboo_words: [],
    },
  };
}

async function saveEdge() {
  if (!current) return;
  showError("main-error", "");
  try {
    await api("PUT", "/api/workspaces/" + current + "/edge", { edge: buildEdgeSnapshot() });
  } catch (e) { showError("main-error", e.message); }
}

// -- selection + rendering ---------------------------------------------------
async function selectWorkspace(slug) {
  current = slug;
  var ws = await api("GET", "/api/workspaces/" + slug);
  $("main").hidden = false;
  $("ws-name").textContent = ws.name;
  $("ws-runs").textContent = ws.runs + " run" + (ws.runs === 1 ? "" : "s");
  fillEdge(ws.edge);
  resetStages();
  renderHistory(ws.history);
  await loadWorkspaces();
}

function resetStages() {
  ["research", "create", "outreach", "follow_up", "optimize"].forEach(function (s) {
    var card = $("stage-" + s); card.classList.remove("done");
    card.querySelector(".body").textContent = "Not run yet";
  });
  Array.prototype.forEach.call(document.querySelectorAll(".integration"), function (el) { el.classList.remove("connected"); });
}

function markDone(id, html) { var c = $(id); c.classList.add("done"); c.querySelector(".body").innerHTML = html; }

function renderPipeline(p) {
  markDone("stage-research", "<p>Target segment: " + p.research.findings.target_segment + " customer(s)</p>" +
    "<p>Priorities considered: " + p.research.findings.priorities.length + "</p>");
  markDone("stage-create", '<p>Published "' + escapeHtml(p.create.asset.content.title) + '"</p>' +
    '<span class="chip">' + p.create.asset.slug + "</span>");
  markDone("stage-outreach", p.outreach.sent.length
    ? p.outreach.sent.map(function (m) { return '<span class="chip">' + escapeHtml(m.to) + "</span>"; }).join("") +
      "<p>" + p.outreach.sent.length + " email(s) sent</p>"
    : "No customers to reach yet.");
  markDone("stage-follow_up", p.follow_up.scheduled.length
    ? "<p>" + p.follow_up.scheduled.length + " follow-up(s) scheduled</p>" : "Nothing scheduled.");
  markDone("stage-optimize", '<p class="recommendation ' + p.optimize.recommendation + '">' +
    p.optimize.recommendation.replace("_", " ") + "</p><p>Outreach tracked: " + (p.optimize.report.outreach_sent || 0) + "</p>");
}

function updateIntegrations(integrations) {
  Array.prototype.forEach.call(document.querySelectorAll(".integration"), function (el) {
    var s = integrations[el.dataset.name];
    el.classList.toggle("connected", !!(s && s.connected));
  });
}

function renderHistory(runs) {
  var section = $("history-section"), list = $("history-list");
  if (!runs || !runs.length) { section.hidden = true; return; }
  list.innerHTML = runs.map(function (r) {
    return "<li>" + escapeHtml(r.objective) + '<span class="rec ' + r.recommendation + '">' +
      r.recommendation.replace("_", " ") + " · " + r.reached + " reached</span></li>";
  }).join("");
  section.hidden = false;
}

async function run() {
  if (!current) return;
  var objective = $("objective").value.trim();
  if (!objective) { showError("main-error", "Enter an objective."); return; }
  showError("main-error", "");
  var btn = $("run-btn"); btn.disabled = true; btn.textContent = "Running…";
  try {
    await saveEdge();
    var report = await api("POST", "/api/workspaces/" + current + "/execute", { objective: objective });
    updateIntegrations(report.integrations);
    renderPipeline(report.pipeline);
    var ws = await api("GET", "/api/workspaces/" + current);
    renderHistory(ws.history);
    $("ws-runs").textContent = ws.runs + " run" + (ws.runs === 1 ? "" : "s");
    await loadWorkspaces();
  } catch (e) { showError("main-error", e.message); }
  finally { btn.disabled = false; btn.textContent = "Run"; }
}

async function exportKit() {
  if (!current) return;
  var objective = $("objective").value.trim();
  if (!objective) { showError("main-error", "Enter an objective to export a kit for."); return; }
  showError("main-error", "");
  // save the edge first so the kit reflects the latest fields
  await saveEdge();
  window.location = "/api/workspaces/" + current + "/campaign.zip?objective=" + encodeURIComponent(objective);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

$("create-btn").addEventListener("click", createWorkspace);
$("new-name").addEventListener("keydown", function (e) { if (e.key === "Enter") createWorkspace(); });
$("save-edge-btn").addEventListener("click", saveEdge);
$("run-btn").addEventListener("click", run);
$("export-btn").addEventListener("click", exportKit);
$("objective").addEventListener("keydown", function (e) { if (e.key === "Enter") run(); });

loadWorkspaces();
