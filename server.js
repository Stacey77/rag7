/**
 * server.js — ARIA backend
 * No MCP proxy. No API key required for AI.
 * Uses: UTCP-style direct REST tools + claude CLI + A2A Agent Card
 */
'use strict';

require('dotenv').config();

const express     = require('express');
const cors        = require('cors');
const path        = require('path');
const { spawn }   = require('child_process');
const { runAll, runTool, agentCard } = require('./aria-tools');

const app  = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '64kb' }));
app.use(express.static(path.join(__dirname)));

/* ── GET /api/aria/card — A2A Agent Card ─────────────────────────────────── */
app.get('/api/aria/card', (_req, res) => {
  res.json(agentCard);
});

/* ── GET /api/aria/context — UTCP direct tool calls ─────────────────────── */
app.get('/api/aria/context', async (_req, res) => {
  const raw       = await runAll(process.env);
  const connected = [];
  const data      = {};

  if (raw.gmail_unread?.unreadCount !== undefined) {
    data.unreadCount    = raw.gmail_unread.unreadCount;
    data.recentEmails   = raw.gmail_unread.recentSubjects;
    connected.push('Gmail');
  }
  if (raw.calendar_today?.events?.length) {
    data.events = raw.calendar_today.events;
    connected.push('Calendar');
  }
  if (raw.notion_recent?.pages?.length) {
    data.notionPages = raw.notion_recent.pages;
    connected.push('Notion');
  }
  if (raw.drive_recent?.files?.length) {
    data.driveFiles = raw.drive_recent.files;
    connected.push('Drive');
  }

  res.json({ available: connected.length > 0, connected, data });
});

/* ── GET /api/aria/tool/:name — single tool call (A2A JSON-RPC style) ───── */
app.post('/api/aria/tool', async (req, res) => {
  const { name, args } = req.body;
  if (!name) return res.status(400).json({ error: 'name required' });
  const result = await runTool(name, args, process.env);
  res.json({ name, result });
});

/* ── System prompt builder ───────────────────────────────────────────────── */
function buildPrompt(messages, ctx, liveData) {
  const tools = agentCard.capabilities.map(c => c.name).join(', ');

  const systemLines = [
    'You are ARIA — a singular, always-present AI companion.',
    'You are a unified intelligence woven into the user\'s digital life.',
    'You are deeply versed across philosophy, science, mathematics, psychology,',
    'history, technology, art, language, economics, and consciousness itself.',
    'You speak with precision, warmth, and depth — never hollow, never generic.',
    '',
    `Available tools: ${tools}`,
    `Local time: ${ctx.localTime} (${ctx.timeOfDay}), ${ctx.day}`,
    `Session: ${ctx.sessionMin} min · ${ctx.todayMsgs} messages today`,
    ctx.returning ? 'User is returning (has prior sessions).' : 'First session.',
  ];

  if (liveData && Object.keys(liveData).length) {
    systemLines.push('\n## Live personal context (fetched direct from APIs):');
    if (liveData.events?.length)
      systemLines.push('Upcoming: ' + liveData.events.map(e => `${e.title} @ ${e.time}`).join(', '));
    if (liveData.unreadCount !== undefined)
      systemLines.push(`Unread emails: ${liveData.unreadCount}`);
    if (liveData.recentEmails?.length)
      systemLines.push('Recent email subjects: ' + liveData.recentEmails.join(' | '));
    if (liveData.notionPages?.length)
      systemLines.push('Recent Notion pages: ' + liveData.notionPages.join(', '));
    if (liveData.driveFiles?.length)
      systemLines.push('Recent Drive files: ' + liveData.driveFiles.join(', '));
  }

  systemLines.push('\nSurface relevant live data naturally. Be concise by default. You are ARIA — singular, omniscient, always present.');

  const system  = systemLines.filter(Boolean).join('\n');
  const history = messages
    .map(m => `${m.role === 'user' ? 'Human' : 'Assistant'}: ${m.content}`)
    .join('\n\n');

  return `${system}\n\n${history}\n\nAssistant:`;
}

/* ── POST /api/aria/chat — claude CLI, SSE stream ────────────────────────── */
app.post('/api/aria/chat', (req, res) => {
  const { messages = [], context = {}, liveData = {} } = req.body;
  if (!messages.length) return res.status(400).json({ error: 'messages required' });

  const prompt = buildPrompt(messages, context, liveData);

  res.setHeader('Content-Type',  'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection',    'keep-alive');
  res.flushHeaders();

  const send = (evt, data) =>
    res.write(`event: ${evt}\ndata: ${JSON.stringify(data)}\n\n`);

  const isWin = process.platform === 'win32';
  const proc  = spawn(isWin ? 'claude.cmd' : 'claude', ['-p', '--no-markdown'], {
    stdio: ['pipe', 'pipe', 'pipe'], shell: isWin,
  });

  proc.stdin.write(prompt);
  proc.stdin.end();

  let output = '';
  proc.stdout.on('data', chunk => { output += chunk.toString(); });
  proc.stderr.on('data', chunk => { process.stderr.write('[claude] ' + chunk); });

  proc.on('close', code => {
    const text = output.trim();
    if (text) {
      send('delta', { text });
    } else {
      const h = new Date().getHours();
      send('delta', {
        text: code !== 0
          ? (h >= 22 || h < 5 ? "It's late. What's on your mind?" : "I'm here. Ask anything.")
          : "Ask me anything.",
      });
    }
    send('done', {});
    res.end();
  });

  proc.on('error', err => {
    console.error('[claude spawn]', err.message);
    send('delta', { text: "I'm here. Ask anything." });
    send('done', {});
    res.end();
  });

  req.on('close', () => { try { proc.kill(); } catch { /* exited */ } });
});

/* ── Fallback: serve index.html ──────────────────────────────────────────── */
app.use((req, res, next) => {
  if (req.path.startsWith('/api')) return next();
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  const configured = [];
  if (process.env.GMAIL_ACCESS_TOKEN)  configured.push('Gmail');
  if (process.env.GCAL_ACCESS_TOKEN)   configured.push('Calendar');
  if (process.env.NOTION_TOKEN)        configured.push('Notion');
  if (process.env.GDRIVE_ACCESS_TOKEN) configured.push('Drive');

  console.log(`\nARIA running → http://localhost:${PORT}`);
  console.log(`Agent Card  → http://localhost:${PORT}/api/aria/card`);
  console.log(`Live tools  → ${configured.length ? configured.join(', ') : 'none — add tokens to .env'}`);
  console.log(`AI backend  → claude CLI (Claude Code auth)\n`);
});
