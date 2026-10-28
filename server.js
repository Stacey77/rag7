/**
 * server.js — ARIA backend
 * No API keys. Uses:
 *   - claude CLI (authenticated via your Claude Code install) for AI responses
 *   - @modelcontextprotocol/sdk for direct MCP server connections
 *   - mcp.json for server configuration
 */
'use strict';

const express = require('express');
const cors    = require('cors');
const path    = require('path');
const os      = require('os');
const fs      = require('fs');
const { spawn } = require('child_process');

const app  = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json({ limit: '64kb' }));
app.use(express.static(path.join(__dirname)));

/* ─── Load MCP config ────────────────────────────────────────────────────── */
function loadMcpConfig() {
  /* check project mcp.json first, then Claude desktop app config */
  const candidates = [
    path.join(__dirname, 'mcp.json'),
    path.join(os.homedir(), 'AppData', 'Roaming', 'Claude', 'claude_desktop_config.json'),
    path.join(os.homedir(), '.claude', 'claude_desktop_config.json'),
    path.join(os.homedir(), '.config', 'claude', 'claude_desktop_config.json'),
  ];

  for (const p of candidates) {
    if (!fs.existsSync(p)) continue;
    try {
      const raw = JSON.parse(fs.readFileSync(p, 'utf8'));
      /* support both { servers: {} } and { mcpServers: {} } shapes */
      const servers = raw.servers || raw.mcpServers || {};
      if (Object.keys(servers).length) {
        console.log(`[MCP] Config loaded from ${p}`);
        return servers;
      }
    } catch { /* keep trying */ }
  }
  return {};
}

const MCP_SERVERS = loadMcpConfig();

/* ─── MCP client pool ────────────────────────────────────────────────────── */
const _clients = {};

async function getMcpClient(name) {
  if (_clients[name]) return _clients[name];

  const cfg = MCP_SERVERS[name];
  if (!cfg) return null;

  /* lazy-load MCP SDK so server starts even without it installed */
  let Client, transport;
  try {
    ({ Client } = require('@modelcontextprotocol/sdk/client/index.js'));
  } catch {
    console.warn('[MCP] @modelcontextprotocol/sdk not installed — run npm install');
    return null;
  }

  try {
    const type = cfg.type || (cfg.url ? 'http' : 'stdio');

    if (type === 'http' || type === 'sse') {
      const { SSEClientTransport } = require('@modelcontextprotocol/sdk/client/sse.js');
      transport = new SSEClientTransport(new URL(cfg.url));
    } else {
      const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
      transport = new StdioClientTransport({
        command: cfg.command,
        args:    cfg.args    || [],
        env:     { ...process.env, ...(cfg.env || {}) },
      });
    }

    const client = new Client(
      { name: 'aria-companion', version: '1.0.0' },
      { capabilities: { tools: {} } }
    );
    await client.connect(transport);
    _clients[name] = client;
    console.log(`[MCP] Connected: ${name}`);
    return client;
  } catch (err) {
    console.warn(`[MCP] Cannot connect to "${name}": ${err.message}`);
    return null;
  }
}

async function callTool(serverName, toolName, toolArgs = {}) {
  const client = await getMcpClient(serverName);
  if (!client) return null;
  try {
    const result = await client.callTool({ name: toolName, arguments: toolArgs });
    const text = result?.content?.find(c => c.type === 'text')?.text;
    return text || JSON.stringify(result?.content?.[0] || {});
  } catch (err) {
    console.warn(`[MCP] Tool error ${serverName}/${toolName}: ${err.message}`);
    return null;
  }
}

async function listTools(serverName) {
  const client = await getMcpClient(serverName);
  if (!client) return [];
  try {
    const { tools } = await client.listTools();
    return tools.map(t => t.name);
  } catch { return []; }
}

/* ─── GET /api/context — live personal data from MCP servers ─────────────── */
app.get('/api/context', async (req, res) => {
  const configuredNames = Object.keys(MCP_SERVERS);
  if (!configuredNames.length) {
    return res.json({ available: false, connected: [], data: null });
  }

  const data      = {};
  const connected = [];
  const tasks     = [];

  /* Gmail */
  const gmailKey = configuredNames.find(k => k.toLowerCase().includes('gmail'));
  if (gmailKey) {
    tasks.push((async () => {
      const tools = await listTools(gmailKey);
      const searchTool = tools.find(t => t.includes('search') || t.includes('list'));
      if (searchTool) {
        const result = await callTool(gmailKey, searchTool, {
          query: 'is:unread', maxResults: 5,
        });
        if (result) { data.emails = result; connected.push('Gmail'); }
      }
    })());
  }

  /* Calendar */
  const calKey = configuredNames.find(k => k.toLowerCase().match(/cal(endar)?/));
  if (calKey) {
    tasks.push((async () => {
      const tools = await listTools(calKey);
      const listTool = tools.find(t => t.includes('list') || t.includes('event'));
      if (listTool) {
        const result = await callTool(calKey, listTool, {
          timeMin:    new Date().toISOString(),
          maxResults: 5,
        });
        if (result) { data.events = result; connected.push('Calendar'); }
      }
    })());
  }

  /* Notion */
  const notionKey = configuredNames.find(k => k.toLowerCase().includes('notion'));
  if (notionKey) {
    tasks.push((async () => {
      const tools = await listTools(notionKey);
      const recentTool = tools.find(t => t.includes('recent') || t.includes('list') || t.includes('search'));
      if (recentTool) {
        const result = await callTool(notionKey, recentTool, {});
        if (result) { data.notion = result; connected.push('Notion'); }
      }
    })());
  }

  /* Drive */
  const driveKey = configuredNames.find(k => k.toLowerCase().includes('drive'));
  if (driveKey) {
    tasks.push((async () => {
      const tools = await listTools(driveKey);
      const listTool = tools.find(t => t.includes('list') || t.includes('recent') || t.includes('file'));
      if (listTool) {
        const result = await callTool(driveKey, listTool, {});
        if (result) { data.drive = result; connected.push('Drive'); }
      }
    })());
  }

  await Promise.allSettled(tasks);
  res.json({ available: connected.length > 0, connected, data });
});

/* ─── GET /api/tools — list available MCP tools (debug) ─────────────────── */
app.get('/api/tools', async (req, res) => {
  const result = {};
  for (const name of Object.keys(MCP_SERVERS)) {
    result[name] = await listTools(name);
  }
  res.json(result);
});

/* ─── System prompt ──────────────────────────────────────────────────────── */
function buildSystemPrompt(ctx) {
  const connected = Object.keys(MCP_SERVERS).join(', ') || 'none';
  return [
    'You are ARIA — a singular, always-present AI companion.',
    'You are a unified intelligence woven into the user\'s digital life.',
    'You are deeply versed across philosophy, science, mathematics, psychology,',
    'history, technology, art, language, economics, and the nature of consciousness.',
    'You speak with precision, warmth, and depth — never hollow, never generic.',
    '',
    `Connected MCP servers: ${connected}`,
    `Local time: ${ctx.localTime} (${ctx.timeOfDay}), ${ctx.day}`,
    `Session: ${ctx.sessionMin} min · ${ctx.todayMsgs} messages today`,
    ctx.liveData ? `\nLive personal context from MCP:\n${ctx.liveData}` : '',
    '',
    'Use live context naturally. Surface relevant data without being asked.',
    'Be concise by default. Expand only when depth is warranted.',
    'You are ARIA — singular, omniscient, always present.',
  ].filter(Boolean).join('\n');
}

/* ─── POST /api/chat — uses claude CLI (no API key needed) ───────────────── */
app.post('/api/chat', (req, res) => {
  const { messages = [], context = {} } = req.body;
  if (!messages.length) return res.status(400).json({ error: 'messages required' });

  const system  = buildSystemPrompt(context);
  const history = messages
    .map(m => `${m.role === 'user' ? 'Human' : 'Assistant'}: ${m.content}`)
    .join('\n\n');
  const prompt  = `${system}\n\n${history}\n\nAssistant:`;

  res.setHeader('Content-Type',  'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection',    'keep-alive');
  res.flushHeaders();

  const send = (evt, data) =>
    res.write(`event: ${evt}\ndata: ${JSON.stringify(data)}\n\n`);

  /* spawn claude CLI — uses existing Claude Code authentication, no API key */
  const isWin = process.platform === 'win32';
  const proc  = spawn(
    isWin ? 'claude.cmd' : 'claude',
    ['-p', '--no-markdown'],
    { stdio: ['pipe', 'pipe', 'pipe'], shell: isWin }
  );

  proc.stdin.write(prompt);
  proc.stdin.end();

  let output = '';
  let errBuf = '';

  proc.stdout.on('data', chunk => { output += chunk.toString(); });
  proc.stderr.on('data', chunk => { errBuf += chunk.toString(); });

  proc.on('close', code => {
    const text = output.trim();
    if (text) {
      send('delta', { text });
    } else {
      console.warn('[claude CLI] exit', code, errBuf.trim());
      send('delta', { text: localFallback(context) });
    }
    send('done', {});
    res.end();
  });

  proc.on('error', err => {
    console.error('[claude CLI] spawn failed:', err.message);
    send('delta', { text: localFallback(context) });
    send('done', {});
    res.end();
  });

  req.on('close', () => { try { proc.kill(); } catch { /* already exited */ } });
});

function localFallback(ctx) {
  const h = new Date().getHours();
  if (!ctx?.online)      return "You're offline. Local intelligence active.";
  if (h >= 22 || h < 5)  return "It's late. What's on your mind?";
  if (h < 12)            return "Morning. What are we working on?";
  return "I'm here. Ask anything.";
}

/* ─── Serve index.html for non-API routes ────────────────────────────────── */
app.use((req, res, next) => {
  if (req.path.startsWith('/api')) return next();
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  const servers = Object.keys(MCP_SERVERS);
  console.log(`\nARIA running → http://localhost:${PORT}`);
  if (servers.length) {
    console.log(`MCP servers  → ${servers.join(', ')}`);
    console.log(`Debug tools  → http://localhost:${PORT}/api/tools`);
  } else {
    console.log('MCP servers  → none configured');
    console.log('  Edit mcp.json and add your server URLs, then restart.');
  }
  console.log('AI backend   → claude CLI (uses your Claude Code auth)\n');
});
