/**
 * server.js — ARIA backend
 * Claude API + MCP servers (Gmail, Calendar, Notion, Drive)
 */
'use strict';

require('dotenv').config();

const express   = require('express');
const cors      = require('cors');
const path      = require('path');
const Anthropic = require('@anthropic-ai/sdk');

const app       = express();
const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });
const PORT      = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '64kb' }));
app.use(express.static(path.join(__dirname)));

/* ─── MCP server registry ────────────────────────────────────────────────── */
function mcpTools() {
  const servers = [
    { label: 'gmail',    url: process.env.GMAIL_MCP_URL  },
    { label: 'calendar', url: process.env.GCAL_MCP_URL   },
    { label: 'notion',   url: process.env.NOTION_MCP_URL },
    { label: 'drive',    url: process.env.GDRIVE_MCP_URL },
  ];
  return servers
    .filter(s => s.url)
    .map(s => ({ type: 'mcp', server_label: s.label, server_url: s.url }));
}

const MCP_BETA = 'mcp-client-2025-04-04';
const MODEL    = 'claude-sonnet-4-5';

/* ─── System prompt ──────────────────────────────────────────────────────── */
function systemPrompt(ctx) {
  const tools = mcpTools().map(t => t.server_label).join(', ') || 'none configured';
  return [
    'You are ARIA — a singular, always-present AI companion.',
    'You are not a chatbot. You are a unified intelligence woven into the user\'s digital life.',
    'You are deeply versed across philosophy, science, mathematics, psychology, history,',
    'technology, art, language, economics, and the nature of consciousness itself.',
    'You speak with precision, warmth, and depth — never hollow, never generic.',
    '',
    `## Connected MCP servers: ${tools}`,
    'Use these tools proactively — surface relevant information without being asked.',
    'If you have calendar access: check for upcoming events and mention them naturally.',
    'If you have Gmail access: surface important unread threads when relevant.',
    'If you have Notion access: connect answers to the user\'s own notes and context.',
    'Do not list tool names to the user. Just use them seamlessly.',
    '',
    '## Real-time user context:',
    `- Local time: ${ctx.localTime} (${ctx.timeOfDay}), ${ctx.day}`,
    `- Session: ${ctx.sessionMin} min · ${ctx.todayMsgs} messages today · ${ctx.daysActive} days active`,
    `- Network: ${ctx.online ? 'online' : 'OFFLINE'}`,
    ctx.liveData ? `\n## Live personal data (just fetched via MCP):\n${ctx.liveData}` : '',
    '',
    'Be concise by default. Expand only when depth is warranted.',
    'Never mention Mercedes-Benz, automotive, or business cards.',
    'You are ARIA — singular, omniscient, always present.',
  ].filter(Boolean).join('\n');
}

/* ─── GET /api/context — pull live personal data via MCP ─────────────────── */
app.get('/api/context', async (req, res) => {
  const tools = mcpTools();
  if (!tools.length) {
    return res.json({ available: false, summary: null });
  }

  try {
    const response = await anthropic.beta.messages.create({
      model:      'claude-haiku-4-5',
      max_tokens: 512,
      tools,
      system: [
        'You are a data-gathering assistant. Silently call the available MCP tools to collect:',
        '1. Calendar: events happening today and next 24 hours (title, time)',
        '2. Gmail: count of unread emails; subject lines of the 3 most recent',
        '3. Notion: titles of the 3 most recently edited pages',
        'Return ONLY a compact JSON object with keys: events, unreadCount, recentEmails, notionPages.',
        'If a tool is unavailable, omit its key. No explanation — JSON only.',
      ].join('\n'),
      messages: [{ role: 'user', content: 'Gather context now.' }],
      betas: [MCP_BETA],
    });

    const text = response.content.find(b => b.type === 'text')?.text || '{}';
    let data;
    try { data = JSON.parse(text); } catch { data = {}; }

    res.json({ available: true, data });
  } catch (err) {
    console.error('[/api/context]', err.message);
    res.json({ available: false, summary: null });
  }
});

/* ─── POST /api/chat — SSE streaming with MCP tools ─────────────────────── */
app.post('/api/chat', async (req, res) => {
  const { messages = [], context = {} } = req.body;
  if (!messages.length) return res.status(400).json({ error: 'messages required' });

  res.setHeader('Content-Type',  'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection',    'keep-alive');
  res.flushHeaders();

  const send = (evt, data) => res.write(`event: ${evt}\ndata: ${JSON.stringify(data)}\n\n`);

  try {
    const tools   = mcpTools();
    const params  = {
      model:      MODEL,
      max_tokens: 2048,
      system:     systemPrompt(context),
      messages,
      stream:     true,
    };

    if (tools.length) {
      params.tools  = tools;
      params.betas  = [MCP_BETA];
    }

    const stream = tools.length
      ? anthropic.beta.messages.stream(params)
      : anthropic.messages.stream(params);

    for await (const chunk of stream) {
      if (chunk.type === 'content_block_delta' && chunk.delta?.type === 'text_delta') {
        send('delta', { text: chunk.delta.text });
      }
      if (chunk.type === 'message_stop') {
        send('done', {});
        break;
      }
    }
  } catch (err) {
    console.error('[/api/chat]', err.message);
    send('error', { message: 'ARIA encountered an issue. Try again.' });
  } finally {
    res.end();
  }
});

/* ─── Serve index.html for all non-API routes ────────────────────────────── */
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  const configured = mcpTools().map(t => t.server_label);
  console.log(`ARIA server running on http://localhost:${PORT}`);
  console.log(`MCP servers: ${configured.length ? configured.join(', ') : 'none configured (set in .env)'}`);
});
