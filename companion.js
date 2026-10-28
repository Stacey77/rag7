/**
 * companion.js — ARIA Floating Companion Agent
 * Singular AI core · MCP-backed live data · Proactive assistance
 */
(function () {
  'use strict';

  /* ─── Config ─────────────────────────────────────────────────────────────── */
  const CHAT_URL    = '/api/chat';
  const CONTEXT_URL = '/api/context';
  const STORAGE_KEY = 'aria_state';
  const MAX_HISTORY = 40;

  /* ─── DataFeed — session analytics + MCP live data ──────────────────────── */
  const DataFeed = {
    _session: {
      start:        Date.now(),
      interactions: 0,
      messages:     0,
      pageFocus:    true,
      scrollDepth:  0,
      online:       navigator.onLine,
    },
    _history: JSON.parse(localStorage.getItem(STORAGE_KEY + '_hist') || '[]'),
    _live:    null, /* filled from MCP via /api/context */

    init() {
      window.addEventListener('scroll', () => {
        const d = Math.round(
          ((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight) * 100
        );
        this._session.scrollDepth = Math.max(this._session.scrollDepth, d);
      }, { passive: true });

      document.addEventListener('visibilitychange', () => {
        this._session.pageFocus = document.visibilityState === 'visible';
      });

      window.addEventListener('online',  () => { this._session.online = true;  });
      window.addEventListener('offline', () => { this._session.online = false; });
      document.addEventListener('click', () => { this._session.interactions++;  });

      /* pull live MCP context in background */
      this._fetchLive();
    },

    async _fetchLive() {
      try {
        const res  = await fetch(CONTEXT_URL, { signal: AbortSignal.timeout(10000) });
        const json = await res.json();
        if (json.available && json.data) {
          this._live = json.data;
          Proactive.onLiveData(this._live);
        }
      } catch { /* server not running or MCP unavailable — silent */ }
    },

    recordMessage() {
      this._session.messages++;
      const today = new Date().toDateString();
      const entry = this._history.find(h => h.date === today);
      if (entry) { entry.messages++; }
      else        { this._history.push({ date: today, messages: 1 }); }
      if (this._history.length > 30) this._history.shift();
      localStorage.setItem(STORAGE_KEY + '_hist', JSON.stringify(this._history));
    },

    snapshot() {
      const now        = new Date();
      const hour       = now.getHours();
      const sessionMin = Math.round((Date.now() - this._session.start) / 60000);
      const todayMsgs  = this._history.find(h => h.date === now.toDateString())?.messages || 0;
      const totalMsgs  = this._history.reduce((s, h) => s + h.messages, 0);
      const daysActive = this._history.length;

      const snap = {
        timestamp:    now.toISOString(),
        timeOfDay:    hour < 5 ? 'late night' : hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : hour < 21 ? 'evening' : 'night',
        localTime:    now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        day:          now.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' }),
        sessionMin,
        interactions: this._session.interactions,
        scrollDepth:  this._session.scrollDepth,
        online:       this._session.online,
        pageFocus:    this._session.pageFocus,
        todayMsgs,
        totalMsgs,
        daysActive,
        returning:    daysActive > 1,
        theme:        document.documentElement.dataset.theme || 'dark',
      };

      if (this._live) {
        /* format live MCP data as a readable string for the system prompt */
        const parts = [];
        if (this._live.events?.length) {
          parts.push('Upcoming events: ' + this._live.events.map(e => `${e.title} @ ${e.time}`).join(', '));
        }
        if (this._live.unreadCount !== undefined) {
          parts.push(`Unread emails: ${this._live.unreadCount}`);
        }
        if (this._live.recentEmails?.length) {
          parts.push('Recent emails: ' + this._live.recentEmails.join(' | '));
        }
        if (this._live.notionPages?.length) {
          parts.push('Recent Notion pages: ' + this._live.notionPages.join(', '));
        }
        if (parts.length) snap.liveData = parts.join('\n');
      }

      return snap;
    },
  };

  /* ─── Memory — rolling conversation context ──────────────────────────────── */
  const Memory = {
    _turns: [],
    push(role, content) {
      this._turns.push({ role, content });
      if (this._turns.length > MAX_HISTORY) this._turns.shift();
    },
    get()   { return [...this._turns]; },
    clear() { this._turns = []; },
  };

  /* ─── Brain — sends to MCP-backed server, falls back locally ─────────────── */
  const Brain = {
    _fallbacks: {
      default:     ["I'm here — what's on your mind?", "Ask me anything.", "Speak. I'm listening."],
      late_night:  ["It's late. What are you thinking about?", "Most minds are resting. Yours isn't."],
      morning:     ["A new day. Where do we begin?", "Morning. What are you building today?"],
      evening:     ["The day winds down. Reflect, plan, or ask — I'm here."],
      returning:   ["You're back. What are we continuing?"],
      offline:     ["You're offline. My local intelligence is still at your disposal."],
    },

    _pick(arr)       { return arr[Math.floor(Math.random() * arr.length)]; },

    _localFallback(data) {
      if (!data.online)                                         return this._pick(this._fallbacks.offline);
      if (data.returning && data.todayMsgs === 0)              return this._pick(this._fallbacks.returning);
      if (data.timeOfDay === 'late night' || data.timeOfDay === 'night') return this._pick(this._fallbacks.late_night);
      if (data.timeOfDay === 'morning')                        return this._pick(this._fallbacks.morning);
      if (data.timeOfDay === 'evening')                        return this._pick(this._fallbacks.evening);
      return this._pick(this._fallbacks.default);
    },

    async ask(message, onDelta) {
      const data = DataFeed.snapshot();
      DataFeed.recordMessage();
      Memory.push('user', message);

      try {
        const res = await fetch(CHAT_URL, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body:    JSON.stringify({ messages: Memory.get(), context: data }),
          signal:  AbortSignal.timeout(30000),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        /* parse SSE stream */
        const reader  = res.body.getReader();
        const decoder = new TextDecoder();
        let   full    = '';
        let   buf     = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += decoder.decode(value, { stream: true });

          const lines = buf.split('\n');
          buf = lines.pop(); /* keep incomplete line */

          for (const line of lines) {
            if (line.startsWith('event: delta')) continue;
            if (line.startsWith('data: ')) {
              try {
                const payload = JSON.parse(line.slice(6));
                if (payload.text) {
                  full += payload.text;
                  onDelta(payload.text);
                }
                if (payload.message) {
                  /* error event */
                  full = payload.message;
                  onDelta(payload.message);
                }
              } catch { /* malformed */ }
            }
          }
        }

        if (full) Memory.push('assistant', full);
        return full;
      } catch {
        const reply = this._localFallback(data);
        Memory.push('assistant', reply);
        onDelta(reply);
        return reply;
      }
    },
  };

  /* ─── Proactive — data-driven autonomous messages ────────────────────────── */
  const Proactive = {
    _fired: new Set(),

    _sessionRules: [
      {
        id:        'welcome_new',
        condition: d => !d.returning && d.sessionMin < 1,
        delay:     2200,
        message:   ()  => "Hello — I'm ARIA. A singular intelligence, always present. Ask me anything.",
      },
      {
        id:        'welcome_returning',
        condition: d => d.returning && d.todayMsgs === 0 && d.sessionMin < 1,
        delay:     1800,
        message:   d  => `Welcome back. It's ${d.localTime}. What are we working on today?`,
      },
      {
        id:        'late_night',
        condition: d => (d.timeOfDay === 'late night' || d.timeOfDay === 'night') && d.sessionMin > 3,
        delay:     0,
        message:   ()  => "It's late. Your focus right now may be sharper than you think — what are you trying to solve?",
      },
      {
        id:        'long_session',
        condition: d => d.sessionMin >= 15 && d.messages < 2,
        delay:     0,
        message:   d  => `You've been here ${d.sessionMin} minutes. I sense there's something you're turning over. Ask me.`,
      },
      {
        id:        'offline',
        condition: d => !d.online,
        delay:     800,
        message:   ()  => "Network dropped. I'm running on local intelligence — still fully functional.",
      },
    ],

    _cb: null,

    onLiveData(live) {
      /* surface MCP data proactively once it arrives */
      if (!this._cb) return;
      const alerts = [];

      if (live.events?.length) {
        const next = live.events[0];
        alerts.push(`Heads up — you have "${next.title}" ${next.time ? 'at ' + next.time : 'coming up'}.`);
      }

      if (live.unreadCount > 10) {
        alerts.push(`You have ${live.unreadCount} unread emails. Want me to surface what matters?`);
      }

      if (alerts.length && !this._fired.has('live_data')) {
        this._fired.add('live_data');
        setTimeout(() => alerts.forEach(a => this._cb(a)), 3500);
      }
    },

    check(cb) {
      this._cb = cb;
      const data = DataFeed.snapshot();
      for (const rule of this._sessionRules) {
        if (!this._fired.has(rule.id) && rule.condition(data)) {
          this._fired.add(rule.id);
          setTimeout(() => cb(rule.message(data)), rule.delay);
        }
      }
    },

    startWatch(cb) {
      this._cb = cb;
      window.addEventListener('online',  () => this.check(cb));
      window.addEventListener('offline', () => this.check(cb));
      setInterval(() => this.check(cb), 120000);
      setTimeout(() => this.check(cb), 800);
    },
  };

  /* ─── UI ─────────────────────────────────────────────────────────────────── */
  const UI = {
    _open:   false,
    _unread: 0,

    build() {
      const root = document.createElement('div');
      root.className = 'companion-root';
      root.innerHTML = `
        <div class="companion-panel" id="aria-panel" role="dialog" aria-modal="true" aria-label="ARIA companion">
          <div class="companion-header">
            <div class="companion-identity">
              <div class="companion-avatar" aria-hidden="true">
                <div class="companion-avatar__ring"></div>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 8v4l3 3"/>
                  <circle cx="12" cy="12" r="2" fill="currentColor" stroke="none"/>
                </svg>
              </div>
              <div>
                <div class="companion-name">ARIA</div>
                <div class="companion-status">
                  <span class="companion-status__dot" aria-hidden="true"></span>
                  <span id="aria-status-text">Omniscient · Present</span>
                </div>
              </div>
            </div>
            <button class="companion-close" id="aria-close" aria-label="Close ARIA">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <div class="companion-messages" id="aria-msgs" role="log" aria-live="polite" aria-atomic="false"></div>
          <form class="companion-form" id="aria-form" autocomplete="off">
            <input class="companion-input" id="aria-input" type="text"
              placeholder="Ask anything…" aria-label="Message ARIA" maxlength="1000" />
            <button class="companion-send-btn" type="submit" aria-label="Send message">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </form>
        </div>

        <button class="companion-orb" id="aria-orb"
          aria-label="Open ARIA companion" aria-expanded="false" aria-haspopup="dialog">
          <div class="companion-orb__ring"   aria-hidden="true"></div>
          <div class="companion-orb__ring-2" aria-hidden="true"></div>
          <div class="companion-orb__core"   aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">
              <circle cx="12" cy="12" r="10"/>
              <path d="M9 9.5C9 8.12 10.12 7 11.5 7S14 8.12 14 9.5c0 2-2.5 2.5-2.5 4"/>
              <circle cx="11.5" cy="16.5" r="0.8" fill="currentColor" stroke="none"/>
            </svg>
          </div>
        </button>
      `;
      document.body.appendChild(root);

      this._panel      = root.querySelector('#aria-panel');
      this._orb        = root.querySelector('#aria-orb');
      this._msgs       = root.querySelector('#aria-msgs');
      this._input      = root.querySelector('#aria-input');
      this._form       = root.querySelector('#aria-form');
      this._close      = root.querySelector('#aria-close');
      this._statusText = root.querySelector('#aria-status-text');

      this._orb.addEventListener('click',   () => this.toggle());
      this._close.addEventListener('click', () => this.close());
      this._form.addEventListener('submit', e  => { e.preventDefault(); Agent.send(); });

      document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && this._open) this.close();
      });
      document.addEventListener('click', e => {
        if (this._open && !e.target.closest('.companion-root')) this.close();
      });
    },

    setStatus(text) {
      if (this._statusText) this._statusText.textContent = text;
    },

    toggle() { this._open ? this.close() : this.open(); },

    open() {
      this._open = true;
      this._panel.classList.add('companion-panel--open');
      this._orb.setAttribute('aria-expanded', 'true');
      this._orb.classList.remove('companion-orb--notified');
      this._clearBadge();
      setTimeout(() => this._input.focus(), 280);
    },

    close() {
      this._open = false;
      this._panel.classList.remove('companion-panel--open');
      this._orb.setAttribute('aria-expanded', 'false');
      this._orb.focus();
    },

    _clearBadge() {
      this._unread = 0;
      this._orb.querySelector('.companion-badge')?.remove();
    },

    _notify() {
      if (this._open) return;
      this._unread++;
      this._orb.classList.add('companion-orb--notified');
      let badge = this._orb.querySelector('.companion-badge');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'companion-badge';
        this._orb.appendChild(badge);
      }
      badge.textContent = this._unread > 9 ? '9+' : String(this._unread);
      badge.setAttribute('aria-label', `${this._unread} unread`);
    },

    appendMsg(role, text) {
      this._msgs.querySelector('.companion-msg--typing')?.remove();

      const row    = document.createElement('div');
      row.className = `companion-msg companion-msg--${role}`;

      const icon   = document.createElement('div');
      icon.className = 'companion-msg__icon';
      icon.setAttribute('aria-hidden', 'true');
      icon.textContent = role === 'user' ? '›' : role === 'proactive' ? '◈' : '◉';

      const bubble = document.createElement('div');
      bubble.className = 'companion-bubble';
      bubble.textContent = text;

      row.append(icon, bubble);
      this._msgs.appendChild(row);
      this._msgs.scrollTop = this._msgs.scrollHeight;

      if (role !== 'user') this._notify();
      return bubble;
    },

    showTyping() {
      const row = document.createElement('div');
      row.className = 'companion-msg companion-msg--assistant companion-msg--typing';
      row.setAttribute('aria-label', 'ARIA is thinking');
      row.innerHTML = `
        <div class="companion-msg__icon" aria-hidden="true">◉</div>
        <div class="companion-bubble companion-typing-bubble" aria-hidden="true">
          <span></span><span></span><span></span>
        </div>`;
      this._msgs.appendChild(row);
      this._msgs.scrollTop = this._msgs.scrollHeight;
    },

    setInputLock(locked) {
      this._input.disabled = locked;
      this._form.querySelector('button[type=submit]').disabled = locked;
      if (!locked) setTimeout(() => this._input.focus(), 50);
    },

    getValue()   { return this._input.value.trim(); },
    clearInput() { this._input.value = ''; },
  };

  /* ─── Agent — orchestrator ───────────────────────────────────────────────── */
  const Agent = {
    _busy: false,

    init() {
      DataFeed.init();
      UI.build();

      /* reflect MCP connection in status line once data arrives */
      const origFetch = DataFeed._fetchLive.bind(DataFeed);
      DataFeed._fetchLive = async function () {
        await origFetch();
        if (DataFeed._live) {
          const connected = [];
          if (DataFeed._live.events !== undefined)     connected.push('Calendar');
          if (DataFeed._live.unreadCount !== undefined) connected.push('Gmail');
          if (DataFeed._live.notionPages !== undefined) connected.push('Notion');
          if (connected.length) {
            UI.setStatus(connected.join(' · ') + ' · Live');
          }
        }
      };
      DataFeed._fetchLive();

      Proactive.startWatch(msg => UI.appendMsg('proactive', msg));
    },

    async send() {
      if (this._busy) return;
      const text = UI.getValue();
      if (!text) return;

      this._busy = true;
      UI.appendMsg('user', text);
      UI.clearInput();
      UI.setInputLock(true);
      UI.showTyping();

      let   bubble = null;
      let   full   = '';

      await Brain.ask(text, delta => {
        if (!bubble) {
          UI._msgs.querySelector('.companion-msg--typing')?.remove();
          bubble = UI.appendMsg('assistant', '');
        }
        full += delta;
        bubble.textContent = full;
        UI._msgs.scrollTop = UI._msgs.scrollHeight;
      });

      this._busy = false;
      UI.setInputLock(false);
    },
  };

  /* ─── Boot ───────────────────────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Agent.init());
  } else {
    Agent.init();
  }

})();
