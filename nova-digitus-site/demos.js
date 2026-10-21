window.ND_DEMOS={"Engineering Orchestrator": {"tag": "Keeps engineering projects moving and flags blocked work before deadlines slip.", "ask": "Plan the bracket redesign for the Line 3 conveyor. Four engineers, ship in 3 weeks.", "steps": [["Planner", "Split the job into 14 tasks across CAD, FEA, drawings and supplier quote."], ["Scheduler", "Assigned owners by skill and load. Critical path: FEA, then drawings, then supplier."], ["3D analysis", "Load check on the new bracket: max stress 61% of yield at 2x rated load."], ["Watcher", "Supplier quote has no owner and blocks day 12. Flagged to the lead."]], "result": {"title": "Project plan ready", "rows": [["Tasks", "14"], ["Critical path", "16 working days"], ["Risks flagged", "1 blocked handoff"], ["Buffer", "2 days"]]}, "url": "https://nova-digitus-engineering-orchestrator.ai.studio"}, "AI Swarm Problem Solver": {"tag": "A team of AI agents takes a business problem apart and ranks fixes.", "ask": "Our warehouse ships 9% of orders late. Why, and what should we fix first?", "steps": [["Data agent", "Read 4,812 sample orders. Late orders cluster on Mondays and on multi-item picks."], ["Hypothesis agent", "Tested 5 explanations. Weekend backlog and pick-path length explain 78% of delays."], ["Critic agent", "Rejected 'carrier delays': on-time rate is the same across carriers."], ["Planner", "Ranked fixes by impact and effort."]], "result": {"title": "Top fix", "rows": [["Fix", "Saturday half-shift for pick backlog"], ["Expected late rate", "9% to 4%"], ["Effort", "Low"], ["Next best", "Re-slot top 50 SKUs near packing"]]}, "url": ""}, "Digital vCard": {"tag": "A phone-first business card your team shares by link or QR.", "ask": "Make cards for our three-person sales team with our logo and colors.", "steps": [["Designer", "Pulled brand colors and logo. Built one card layout for the team."], ["Builder", "Created 3 cards with one-tap call, email, text and save-to-contacts."], ["QR", "Generated a QR code and short link for each person."], ["Tracker", "Turned on view and save counts for each card."]], "result": {"title": "Team cards live", "rows": [["Cards", "3"], ["Share options", "Link, QR, NFC tag"], ["App needed", "None"], ["Sample week", "41 views, 17 contacts saved"]]}, "url": ""}, "Robot Agent Layer": {"tag": "Plans robot tasks and knows when to hand off to a person.", "ask": "Hotel floor 4: deliver towels to 412 and 418, then check the ice machine.", "steps": [["Task planner", "Built a route: linen room, 412, 418, ice machine. 6 minutes."], ["Safety", "Hallway cleaning cart detected near 415. Rerouted around it."], ["Robot", "Delivered to 412 and 418. Guests confirmed on the door screen."], ["Handoff", "Ice machine shows a fault code the robot can't clear. Paged maintenance."]], "result": {"title": "Run complete", "rows": [["Tasks done", "3 of 4"], ["Handed to staff", "1 (ice machine fault)"], ["Time", "6 min 40 s"], ["Incidents", "0"]]}, "url": ""}, "TerraFleet Autonomous Garden Robotics": {"tag": "Coordinates robots that tend gardens and growing beds.", "ask": "Tend beds 1 to 6 today. Rain is forecast tomorrow.", "steps": [["Sensors", "Soil moisture low in beds 2 and 5. Beds 1, 3, 4, 6 fine."], ["Planner", "Skip full watering because of rain. Light top-up for beds 2 and 5 only."], ["Weeder bot", "Cleared weeds in beds 3 and 4. 212 weeds removed."], ["Scout bot", "Aphids spotted on bed 6 kale. Photo sent for review."]], "result": {"title": "Garden report", "rows": [["Water saved", "68% vs full schedule"], ["Beds weeded", "2"], ["Alerts", "Aphids on bed 6"], ["Robot time", "54 min"]]}, "url": ""}, "Autarkic Field Engineering & Telemetry Suite": {"tag": "Design and monitor off-grid water, power and storage systems.", "ask": "Size a solar and battery system for a 4-person off-grid cabin.", "steps": [["Load model", "Estimated 9.2 kWh a day, peak 3.1 kW, from typical appliances."], ["Sizing", "Chose 5.4 kW of panels and 20 kWh of battery for 2 cloudy days."], ["Water", "Added a ram pump from the creek: 1,100 litres a day, no electricity."], ["Telemetry", "Set phone alerts for battery under 30% and pump stalls."]], "result": {"title": "System design", "rows": [["Solar", "5.4 kW"], ["Battery", "20 kWh"], ["Autonomy", "2.2 cloudy days"], ["Water", "1,100 L/day by ram pump"]]}, "url": ""}, "OmniNet AI: Network Diagnostics & Self-Healing": {"tag": "Finds network faults, predicts failures and fixes common problems.", "ask": "Staff say Wi-Fi drops every afternoon in the back office.", "steps": [["Scanner", "Found 38 devices. Access point AP-3 restarts around 2 pm daily."], ["Diagnostics", "AP-3 shares channel 6 with two neighbor networks. Interference peaks at 2 pm."], ["Predictor", "Switch port 14 shows rising errors. Likely to fail within 30 days."], ["Fixer", "Moved AP-3 to channel 11 and scheduled a check tomorrow at 2 pm."]], "result": {"title": "Diagnosis", "rows": [["Root cause", "Channel interference on AP-3"], ["Fixed automatically", "Yes"], ["Predicted failure", "Switch port 14"], ["Downtime avoided", "About 40 min a day"]]}, "url": ""}, "Stratum MCP: Cloud Resource Control Plane": {"tag": "Control cloud resources from one AI-ready control plane.", "ask": "Why did our cloud bill jump this month?", "steps": [["Inventory", "Read 3 accounts: 126 resources across compute, storage and databases."], ["Cost agent", "Bill up 31%. Most of it is 4 test servers left running since the 3rd."], ["Policy", "Those servers have no owner tag, which breaks your tagging rule."], ["Action", "Prepared a shutdown plan. Waiting for your approval before anything changes."]], "result": {"title": "Savings found", "rows": [["Monthly waste", "$1,840"], ["Resources to stop", "4"], ["Policy breaks", "4 untagged"], ["Changes made", "None until you approve"]]}, "url": ""}, "AI Governance & Guardrails Platform": {"tag": "Track AI use, vet AI vendors and stay inside your rules.", "ask": "Which AI tools are our teams using, and are any a risk?", "steps": [["Discovery", "Found 11 AI tools in use across 6 teams."], ["Vendor check", "Scored each vendor on data retention, training on your data, and access controls."], ["Policy", "2 tools allow training on your data, which your policy forbids."], ["Report", "Drafted a one-page summary for leadership with fixes."]], "result": {"title": "AI risk summary", "rows": [["Tools found", "11"], ["Approved", "7"], ["Need review", "2"], ["Against policy", "2"]]}, "url": ""}, "AgentForge: GenAI Studio": {"tag": "Build multi-agent workflows with retrieval, tools and monitoring.", "ask": "Build an agent that answers HR policy questions from our handbook.", "steps": [["Ingest", "Indexed the 84-page handbook into 412 searchable passages."], ["Builder", "Created an answer agent and a checker agent that verifies every citation."], ["Test", "Ran 25 sample questions. 24 correct with page citations, 1 sent to HR."], ["Deploy", "Generated a deployment blueprint with logging and a monthly accuracy report."]], "result": {"title": "Agent ready", "rows": [["Accuracy on test set", "96%"], ["Citations", "Every answer"], ["Hand-offs to HR", "Unclear questions only"], ["Setup time", "Under an hour"]]}, "url": ""}, "OmniAgent Enterprise Platform": {"tag": "Deploy secure AI agents with human oversight built in.", "ask": "Let an agent draft supplier emails, but a person approves before sending.", "steps": [["Setup", "Connected the agent to your inbox and supplier list through MCP."], ["Guardrails", "Agent can draft only. Sending needs a manager's approval."], ["Run", "Drafted 6 follow-ups for overdue purchase orders."], ["Oversight", "Manager approved 5, edited 1. Every action logged."]], "result": {"title": "Today's run", "rows": [["Drafts", "6"], ["Approved", "5"], ["Edited by a person", "1"], ["Sent without approval", "0"]]}, "url": ""}, "AI Business Operations Orchestrator": {"tag": "A team of AI agents that runs the busywork of a small business.", "ask": "Get next week ready: posts, follow-ups, invoices and my calendar.", "steps": [["Marketing agent", "Drafted 5 social posts and scheduled them for best times."], ["Outreach agent", "Wrote follow-ups to 8 leads who went quiet."], ["Finance agent", "Found 3 unpaid invoices over 30 days and drafted reminders."], ["Scheduler", "Blocked focus time and moved 2 meetings that clashed."]], "result": {"title": "Week prepared", "rows": [["Posts scheduled", "5"], ["Follow-ups drafted", "8"], ["Overdue invoices", "3 ($6,420)"], ["Hours saved", "About 6"]]}, "url": ""}, "Nova Digitus Conversational AI": {"tag": "Voice and chat assistant for customer conversations, with guardrails.", "ask": "Customer: 'My order hasn't arrived and I want a refund.'", "steps": [["Intent", "Detected: late delivery, refund request. Tone: frustrated."], ["Lookup", "Order #20417 is with the carrier, due tomorrow."], ["Guardrail", "Refunds over $200 need a person. This one is $89, inside policy."], ["Reply", "Apologized, shared tracking, and offered a refund or 15% off if it arrives."]], "result": {"title": "Conversation handled", "rows": [["Resolved without staff", "Yes"], ["Policy checks", "Passed"], ["Time to answer", "4 seconds"], ["Customer choice", "Kept order, took 15% off"]]}, "url": ""}, "Problem Crusher": {"tag": "Turns a messy manual process into AI agents that run it.", "ask": "We copy web form leads into a spreadsheet and email each one by hand.", "steps": [["Mapper", "Mapped the process: 6 manual steps, about 12 minutes per lead."], ["Designer", "Proposed 3 agents: capture, qualify, reply."], ["Builder", "Capture agent files each lead. Qualify agent scores it. Reply agent drafts the email."], ["Test", "Ran 20 past leads through it. Matched your manual decisions 19 times."]], "result": {"title": "Process automated", "rows": [["Manual steps removed", "5 of 6"], ["Time per lead", "12 min to under 1"], ["Agreement with you", "95%"], ["Still yours", "Final send"]]}, "url": ""}, "AI CMO Platform": {"tag": "A full AI marketing team for founders, in one dashboard.", "ask": "Launch plan for our new $49 meal-prep subscription in Atlanta.", "steps": [["Strategist", "Target: busy professionals 28 to 45 within 10 miles of Midtown."], ["Copy agent", "Wrote 3 ad angles: time saved, eating healthy, no grocery runs."], ["Channel agent", "Split budget: 50% Instagram, 30% Google, 20% local creators."], ["Analyst", "Set targets: $18 per sign-up, 400 sign-ups in 60 days."]], "result": {"title": "Launch plan", "rows": [["Audience", "Midtown professionals"], ["Ad angles", "3"], ["Target cost per sign-up", "$18"], ["60-day goal", "400 subscribers"]]}, "url": ""}, "AI SDR Agent Fleet": {"tag": "AI sales team that prospects, writes outreach and qualifies leads.", "ask": "Find 50 logistics companies in Texas that need route planning.", "steps": [["Prospector", "Found 50 companies with 20 to 200 trucks and a recent hiring push."], ["Researcher", "Pulled one relevant fact per company for a personal opener."], ["Writer", "Drafted a 3-email sequence for each, in your voice."], ["Qualifier", "Ranked by fit. Top 12 marked call-first."]], "result": {"title": "Pipeline built", "rows": [["Prospects", "50"], ["Personal openers", "50"], ["Emails drafted", "150"], ["Call-first", "12"]]}, "url": ""}, "Sovereign Equity & Overage Recovery Engine": {"tag": "Find and document unclaimed tax-sale and foreclosure surplus funds.", "ask": "Show surplus funds from tax sales in one sample county.", "steps": [["Records agent", "Read 312 sample tax-sale results from the last 3 years."], ["Matcher", "38 sales left a surplus over $5,000 after the debt was paid."], ["Verifier", "Checked claim deadlines. 29 are still open."], ["Docs agent", "Prepared a claim packet checklist for each open case."]], "result": {"title": "Sample county", "rows": [["Sales reviewed", "312"], ["Surplus over $5k", "38"], ["Still claimable", "29"], ["Sample total", "$1.2M"]]}, "url": ""}, "Wealth Strategy Playbook": {"tag": "Plan the buy, borrow, die strategy with holding-company structures.", "ask": "Show how a $400k rental portfolio could fund living costs without selling.", "steps": [["Model", "Sample portfolio: $400k value, $120k owed, rising 4% a year."], ["Borrow", "Line of credit at 55% loan-to-value releases about $100k over 5 years."], ["Stress test", "Checked a 20% price drop. Still under the lender's limit."], ["Structure", "Showed how a holding company separates the properties from personal assets."]], "result": {"title": "Illustration only", "rows": [["Cash released", "About $100k over 5 years"], ["Properties sold", "0"], ["Worst-case LTV", "62%"], ["Next step", "Review with your CPA and attorney"]]}, "url": ""}, "Wealth in Health: Sound Healing": {"tag": "Guided sound sessions with Solfeggio tones and cymatic visuals.", "ask": "A 10-minute wind-down session before sleep.", "steps": [["Mood check", "You chose: wired and tired. Goal: fall asleep."], ["Composer", "Built a session: 432 Hz base, slowing binaural beat from 10 Hz to 4 Hz."], ["Visuals", "Cymatic pattern slows with the sound, dimming over 10 minutes."], ["Journal", "Session saved so you can see which ones help most."]], "result": {"title": "Session ready", "rows": [["Length", "10 minutes"], ["Tones", "432 Hz with binaural beat"], ["Visuals", "Cymatic, dimming"], ["Best with", "Headphones"]]}, "url": ""}, "Wealth in Health Index": {"tag": "Links daily wellness habits to healthcare savings and investment growth.", "ask": "What is walking 30 minutes a day worth to me financially?", "steps": [["Habits", "Sample person: 42, walks 3 days a week now, wants 7."], ["Health model", "Uses published research on activity and healthcare costs."], ["Savings", "Estimated lower yearly healthcare spending, shown as a range."], ["Growth", "Shows that saving invested at 6% for 20 years."]], "result": {"title": "Sample estimate", "rows": [["Yearly savings range", "$600 to $1,500"], ["Invested 20 years at 6%", "$22k to $55k"], ["Habit streak", "Tracked daily"], ["Note", "Estimates, not medical advice"]]}, "url": ""}, "Monument: Archive of Black Innovation": {"tag": "Interactive museum and patent archive of Black inventors.", "ask": "Show inventors whose work shaped modern traffic and transport.", "steps": [["Search", "Found inventors and patents connected to transport and road safety."], ["Curator", "Opened a gallery on Garrett Morgan's traffic signal patent of 1923."], ["Timeline", "Placed related patents on a timeline from 1890 to today."], ["Lesson", "Built a 5-question classroom quiz from the gallery."]], "result": {"title": "Gallery ready", "rows": [["Featured inventor", "Garrett Morgan"], ["Patents linked", "Shown on a timeline"], ["Format", "3D gallery and timeline"], ["Classroom", "Quiz included"]]}, "url": ""}, "Tree of Life Interactive Map": {"tag": "A seven-level 3D Tree of Life with an AI guide and audio.", "ask": "Walk me through the first level and what it teaches.", "steps": [["Map", "Opened level one in 3D and lit its path to level two."], ["Guide", "Explained the level through Kemet, Kush and Kabbalah side by side."], ["Audio", "Started the matching binaural track for reflection."], ["Practice", "Suggested a 5-minute journaling prompt for the day."]], "result": {"title": "Level one", "rows": [["Traditions compared", "3"], ["Audio", "Binaural, 7 minutes"], ["Practice", "Daily journal prompt"], ["Next", "Level two unlocks"]]}, "url": ""}, "AI Agentic Brain: Digital Illustration Platform": {"tag": "Illustration studio with AI design agents and a color harmony engine.", "ask": "Children's book cover: a fox reading under a tree at dusk.", "steps": [["Concept agent", "Drew 3 thumbnail layouts on the shared sketchpad."], ["Color engine", "Built a dusk palette: deep teal, amber, soft violet."], ["Illustrator agent", "Refined layout 2 with clear space for the title."], ["Review", "Checked contrast so the title stays readable on shelves."]], "result": {"title": "Cover draft", "rows": [["Thumbnails", "3"], ["Palette", "5 colors, dusk"], ["Chosen layout", "2"], ["Ready for", "Your edits"]]}, "url": ""}, "AuraDJ": {"tag": "An AI DJ that reads your mood and builds sets that grow with you.", "ask": "Focus music for a 90-minute work block.", "steps": [["Mood", "You picked: focused, slightly tired."], ["Taste", "Learned you skip vocals during work and like lo-fi and soft house."], ["Builder", "Built a 90-minute set that starts at 80 BPM and lifts to 110."], ["Learning", "Skips and replays tune your next set."]], "result": {"title": "Set ready", "rows": [["Length", "90 minutes"], ["Tempo", "80 to 110 BPM"], ["Vocals", "None"], ["Gets better", "Every time you listen"]]}, "url": ""}};
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
