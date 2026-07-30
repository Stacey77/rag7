const errorEl = document.getElementById("error");
const runBtn = document.getElementById("run-btn");
const objectiveInput = document.getElementById("objective");

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = !message;
}

function setBody(cardId, html) {
  document.querySelector(`#${cardId} .body`).innerHTML = html;
}

function renderEdge(edge) {
  const strategy = edge.strategy || {};
  setBody(
    "edge-strategy",
    (strategy.positioning ? `<p>${strategy.positioning}</p>` : "") +
      (strategy.priorities || [])
        .map((p) => `<span class="chip">#${p.rank} ${p.name}</span>`)
        .join("") || "No strategy set yet."
  );

  const customers = edge.customer_data || { total: 0, records: [] };
  setBody(
    "edge-customer_data",
    `<p>${customers.total} customer record(s)</p>` +
      customers.records.map((r) => `<span class="chip">${r.email || r.id}</span>`).join("")
  );

  const goals = edge.goals || {};
  const goalNames = Object.keys(goals);
  setBody(
    "edge-goals",
    goalNames.length
      ? goalNames
          .map((name) => {
            const g = goals[name];
            return `<p>${name}: ${g.goal.current}/${g.goal.target} (${Math.round(g.completion_ratio * 100)}%)</p>`;
          })
          .join("")
      : "No goals set yet."
  );

  const knowledge = edge.knowledge || {};
  const topics = Object.keys(knowledge);
  setBody(
    "edge-knowledge",
    topics.length
      ? topics.map((topic) => `<p><strong>${topic}:</strong> ${knowledge[topic].join("; ")}</p>`).join("")
      : "No knowledge recorded yet."
  );

  const brand = edge.brand || {};
  setBody(
    "edge-brand",
    (brand.voice ? `<p>${brand.voice}</p>` : "No voice set yet.") +
      (brand.tone_words || []).map((w) => `<span class="chip">${w}</span>`).join("")
  );
}

function updateIntegrations(integrations) {
  document.querySelectorAll(".integration").forEach((el) => {
    const status = integrations[el.dataset.name];
    el.classList.toggle("connected", Boolean(status && status.connected));
  });
}

function markDone(cardId, html) {
  const card = document.getElementById(cardId);
  card.classList.add("done");
  setBody(cardId, html);
}

function renderPipeline(pipeline) {
  const research = pipeline.research.findings;
  markDone(
    "stage-research",
    `<p>Target segment: ${research.target_segment} customer(s)</p>` +
      `<p>Priorities considered: ${research.priorities.length}</p>`
  );

  const asset = pipeline.create.asset;
  markDone("stage-create", `<p>Published "${asset.content.title}"</p><span class="chip">${asset.slug}</span>`);

  const sent = pipeline.outreach.sent;
  markDone(
    "stage-outreach",
    sent.length
      ? sent.map((m) => `<span class="chip">${m.to}</span>`).join("") + `<p>${sent.length} email(s) sent</p>`
      : "No customers to reach yet."
  );

  const scheduled = pipeline.follow_up.scheduled;
  markDone(
    "stage-follow_up",
    scheduled.length ? `<p>${scheduled.length} follow-up(s) scheduled (${scheduled[0].when})</p>` : "Nothing scheduled."
  );

  const optimize = pipeline.optimize;
  markDone(
    "stage-optimize",
    `<p class="recommendation ${optimize.recommendation}">${optimize.recommendation.replace("_", " ")}</p>` +
      `<p>Outreach events tracked: ${optimize.report.outreach_sent || 0}</p>`
  );
}

async function loadEdge() {
  try {
    const response = await fetch("/api/edge");
    renderEdge(await response.json());
  } catch (err) {
    showError("Could not load company edge: " + err.message);
  }
}

async function execute() {
  const objective = objectiveInput.value.trim();
  if (!objective) {
    showError("Enter an objective first.");
    return;
  }
  showError("");
  runBtn.disabled = true;
  runBtn.textContent = "Thinking…";
  try {
    const response = await fetch("/api/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ objective }),
    });
    const report = await response.json();
    if (!response.ok) {
      showError(report.error || "Execution failed.");
      return;
    }
    renderEdge(report.edge);
    updateIntegrations(report.integrations);
    renderPipeline(report.pipeline);
  } catch (err) {
    showError("Execution failed: " + err.message);
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = "Think, connect, execute";
  }
}

runBtn.addEventListener("click", execute);
objectiveInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") execute();
});

loadEdge();
