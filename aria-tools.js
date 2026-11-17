/**
 * aria-tools.js — UTCP-style direct tool registry
 * Single-hop REST calls to data sources. No MCP proxy, no agent relay.
 * Each tool: { name, description, schema, execute(args, env) }
 */
'use strict';

const https = require('https');

/* ── minimal fetch wrapper (Node < 18 fallback) ───────────────────────────── */
function apiFetch(url, opts = {}) {
  return new Promise((resolve, reject) => {
    const { hostname, pathname, search } = new URL(url);
    const options = {
      hostname, path: pathname + (search || ''),
      method:  opts.method  || 'GET',
      headers: opts.headers || {},
    };
    const req = https.request(options, res => {
      let data = '';
      res.on('data', c => { data += c; });
      res.on('end', () => {
        try { resolve({ ok: res.statusCode < 400, status: res.statusCode, json: () => JSON.parse(data), text: () => data }); }
        catch { resolve({ ok: false, status: res.statusCode, json: () => ({}), text: () => data }); }
      });
    });
    req.on('error', reject);
    if (opts.body) req.write(opts.body);
    req.end();
  });
}

/* ── Tool registry ────────────────────────────────────────────────────────── */
const tools = [

  /* ── Gmail ─────────────────────────────────────────────────────────────── */
  {
    name: 'gmail_unread',
    description: 'Count of unread emails and subjects of the 5 most recent',
    schema: { type: 'object', properties: {}, required: [] },
    async execute(_args, env) {
      const token = env.GMAIL_ACCESS_TOKEN;
      if (!token) return null;
      try {
        const list = await apiFetch(
          'https://gmail.googleapis.com/gmail/v1/users/me/messages?labelIds=INBOX&labelIds=UNREAD&maxResults=5',
          { headers: { Authorization: `Bearer ${token}` } }
        );
        const data = list.json();
        const unreadCount = data.resultSizeEstimate || 0;

        const subjects = await Promise.all(
          (data.messages || []).slice(0, 5).map(async m => {
            const msg = await apiFetch(
              `https://gmail.googleapis.com/gmail/v1/users/me/messages/${m.id}?format=metadata&metadataHeaders=Subject`,
              { headers: { Authorization: `Bearer ${token}` } }
            );
            const headers = msg.json().payload?.headers || [];
            return headers.find(h => h.name === 'Subject')?.value || '(no subject)';
          })
        );
        return { unreadCount, recentSubjects: subjects };
      } catch { return null; }
    },
  },

  /* ── Google Calendar ────────────────────────────────────────────────────── */
  {
    name: 'calendar_today',
    description: 'Events happening today and in the next 24 hours',
    schema: { type: 'object', properties: {}, required: [] },
    async execute(_args, env) {
      const token = env.GCAL_ACCESS_TOKEN;
      if (!token) return null;
      try {
        const now = new Date();
        const end = new Date(now.getTime() + 86400000);
        const url = `https://www.googleapis.com/calendar/v3/calendars/primary/events`
          + `?timeMin=${encodeURIComponent(now.toISOString())}`
          + `&timeMax=${encodeURIComponent(end.toISOString())}`
          + `&singleEvents=true&orderBy=startTime&maxResults=8`;
        const res  = await apiFetch(url, { headers: { Authorization: `Bearer ${token}` } });
        const data = res.json();
        const events = (data.items || []).map(e => ({
          title: e.summary || '(untitled)',
          time:  e.start?.dateTime
            ? new Date(e.start.dateTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            : 'all day',
        }));
        return { events };
      } catch { return null; }
    },
  },

  /* ── Notion ─────────────────────────────────────────────────────────────── */
  {
    name: 'notion_recent',
    description: 'Titles of the 5 most recently edited Notion pages',
    schema: { type: 'object', properties: {}, required: [] },
    async execute(_args, env) {
      const token = env.NOTION_TOKEN;
      if (!token) return null;
      try {
        const res  = await apiFetch('https://api.notion.com/v1/search', {
          method: 'POST',
          headers: {
            Authorization:    `Bearer ${token}`,
            'Notion-Version': '2022-06-28',
            'Content-Type':   'application/json',
          },
          body: JSON.stringify({ sort: { direction: 'descending', timestamp: 'last_edited_time' }, page_size: 5 }),
        });
        const data  = res.json();
        const pages = (data.results || []).map(p => {
          const title = p.properties?.title?.title?.[0]?.plain_text
            || p.properties?.Name?.title?.[0]?.plain_text
            || '(untitled)';
          return title;
        });
        return { pages };
      } catch { return null; }
    },
  },

  /* ── Google Drive ───────────────────────────────────────────────────────── */
  {
    name: 'drive_recent',
    description: 'Names of the 5 most recently modified Drive files',
    schema: { type: 'object', properties: {}, required: [] },
    async execute(_args, env) {
      const token = env.GDRIVE_ACCESS_TOKEN;
      if (!token) return null;
      try {
        const url = `https://www.googleapis.com/drive/v3/files`
          + `?orderBy=modifiedTime+desc&pageSize=5&fields=files(name,modifiedTime)`;
        const res  = await apiFetch(url, { headers: { Authorization: `Bearer ${token}` } });
        const data = res.json();
        const files = (data.files || []).map(f => f.name);
        return { files };
      } catch { return null; }
    },
  },

  /* ── System clock / local context ───────────────────────────────────────── */
  {
    name: 'local_context',
    description: 'Server time, day of week, and time-of-day classification',
    schema: { type: 'object', properties: {}, required: [] },
    async execute() {
      const now  = new Date();
      const hour = now.getHours();
      return {
        iso:       now.toISOString(),
        localTime: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        day:       now.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' }),
        timeOfDay: hour < 5 ? 'late night' : hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : hour < 21 ? 'evening' : 'night',
      };
    },
  },
];

/* ── Runner ───────────────────────────────────────────────────────────────── */
async function runTool(name, args, env) {
  const tool = tools.find(t => t.name === name);
  if (!tool) return { error: `Unknown tool: ${name}` };
  try {
    return await tool.execute(args || {}, env || process.env);
  } catch (err) {
    return { error: err.message };
  }
}

async function runAll(env) {
  const results = {};
  await Promise.allSettled(
    tools.map(t => t.execute({}, env || process.env).then(r => { results[t.name] = r; }).catch(() => {}))
  );
  return results;
}

/* ── A2A Agent Card ────────────────────────────────────────────────────────── */
const agentCard = {
  schemaVersion: '1.0',
  name:          'ARIA',
  description:   'Singular AI companion. All-knowing, always present. Real-time personal data + proactive assistance.',
  version:       '2.0.0',
  protocol:      'a2a-json-rpc-2.0',
  capabilities: tools.map(t => ({ name: t.name, description: t.description, inputSchema: t.schema })),
  endpoints: {
    chat:    '/api/aria/chat',
    context: '/api/aria/context',
    card:    '/api/aria/card',
  },
  auth: 'none',
};

module.exports = { tools, runTool, runAll, agentCard };
