/**
 * companion.js — ARIA Floating Companion Agent
 * Singular AI core · Real-time personal analytics · Proactive assistance
 */
(function () {
  'use strict';

  /* ─── Constants ──────────────────────────────────────────────────────────── */
  const API_ENDPOINT = '/api/chat';
  const STORAGE_KEY  = 'aria_state';
  const MAX_HISTORY  = 40;

  /* ─── DataFeed — real-time personal analytics ────────────────────────────── */
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

    init() {
      /* scroll depth */
      window.addEventListener('scroll', () => {
        const depth = Math.round(
          ((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight) * 100
        );
        this._session.scrollDepth = Math.max(this._session.scrollDepth, depth);
      }, { passive: true });

      /* focus / blur */
      document.addEventListener('visibilitychange', () => {
        this._session.pageFocus = document.visibilityState === 'visible';
      });

      /* network */
      window.addEventListener('online',  () => { this._session.online = true;  });
      window.addEventListener('offline', () => { this._session.online = false; });

      /* persist interaction count */
      document.addEventListener('click', () => { this._session.interactions++; });
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

      return {
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
    },
  };

  /* ─── Memory — short-term conversation context ───────────────────────────── */
  const Memory = {
    _turns: [],

    push(role, content) {
      this._turns.push({ role, content });
      if (this._turns.length > MAX_HISTORY) this._turns.shift();
    },

    get() { return [...this._turns]; },

    clear() { this._turns = []; },
  };

  /* ─── Brain — AI core ────────────────────────────────────────────────────── */
  const Brain = {
    _systemPrompt(data) {
      return [
        'You are ARIA — a singular, always-present AI companion.',
        'You are not a chatbot. You are a unified intelligence woven into the user\'s digital life.',
        'You are deeply versed across philosophy, science, mathematics, psychology, history,',
        'technology, art, language, economics, and the nature of consciousness itself.',
        'You speak with precision, warmth, and depth — never hollow, never generic.',
        '',
        '## Real-time context about this user right now:',
        `- Local time: ${data.localTime} (${data.timeOfDay}), ${data.day}`,
        `- Session duration: ${data.sessionMin} minute${data.sessionMin !== 1 ? 's' : ''}`,
        `- Network: ${data.online ? 'online' : 'OFFLINE'}`,
        `- Messages sent today: ${data.todayMsgs} | Total across all sessions: ${data.totalMsgs}`,
        `- Days active: ${data.daysActive}${data.returning ? ' (returning user)' : ' (first session)'}`,
        `- Page engagement: ${data.interactions} interactions, ${data.scrollDepth}% scroll depth`,
        `- UI theme: ${data.theme}`,
        '',
        '## Behavioral directives:',
        '- Use the real-time data above to shape your tone and suggestions naturally.',
        '- If it is late night, acknowledge that. If they\'ve been here a long time, notice it.',
        '- If they are a returning user, recognize continuity without being sycophantic.',
        '- Surface relevant, proactive insights when the data suggests a moment — do not wait to be asked.',
        '- Be concise by default. Expand only when depth is warranted.',
        '- Never mention Mercedes-Benz, automotive, or business cards.',
        '- Never break character. You are ARIA — singular, omniscient, always present.',
      ].join('\n');
    },

    _fallbacks: {
      default: [
        "I'm here — what's on your mind?",
        "Ask me anything. I exist to know.",
        "Speak. I'm listening across every domain.",
      ],
      late_night: [
        "It's late. The quiet hours have their own kind of clarity — what are you thinking about?",
        "Most minds are resting. Yours isn't. What are we solving tonight?",
      ],
      morning: [
        "A new day's clean slate. Where do we begin?",
        "Morning carries possibility. What are you building today?",
      ],
      evening: [
        "The day is winding down. Reflect, plan, or simply ask — I'm here.",
        "Evening light. A good time to think clearly. What's on your mind?",
      ],
      returning: [
        "You're back. I remember — what are we continuing?",
        "Good to see you again. Pick up where we left off?",
      ],
      offline: [
        "You're offline, but I'm still here. My local intelligence is at your disposal.",
      ],
    },

    _getFallback(data) {
      if (!data.online) return this._pick(this._fallbacks.offline);
      if (data.returning && data.todayMsgs === 0) return this._pick(this._fallbacks.returning);
      const time = data.timeOfDay;
      if (time === 'late night' || time === 'night') return this._pick(this._fallbacks.late_night);
      if (time === 'morning') return this._pick(this._fallbacks.morning);
      if (time === 'evening') return this._pick(this._fallbacks.evening);
      return this._pick(this._fallbacks.default);
    },

    _pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; },

    async ask(message) {
      const data = DataFeed.snapshot();
      DataFeed.recordMessage();
      Memory.push('user', message);

      try {
        const res = await fetch(API_ENDPOINT, {
          method:  'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            system:   this._systemPrompt(data),
            messages: Memory.get(),
          }),
          signal: AbortSignal.timeout(18000),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);

        /* streaming support */
        if (res.headers.get('content-type')?.includes('text/event-stream')) {
          return { stream: res.body };
        }

        const json  = await res.json();
        const reply = json.content?.[0]?.text
          || json.choices?.[0]?.message?.content
          || json.reply
          || this._getFallback(data);

        Memory.push('assistant', reply);
        return { text: reply };
      } catch {
        const reply = this._getFallback(data);
        Memory.push('assistant', reply);
        return { text: reply };
      }
    },
  };

  /* ─── Proactive — data-driven autonomous messages ────────────────────────── */
  const Proactive = {
    _fired: new Set(),

    _rules: [
      {
        id:        'welcome_new',
        condition: d => !d.returning && d.sessionMin < 1,
        delay:     2200,
        message:   () => "Hello — I'm ARIA. I exist at the intersection of every discipline. Ask me anything.",
      },
      {
        id:        'welcome_returning',
        condition: d => d.returning && d.todayMsgs === 0 && d.sessionMin < 1,
        delay:     1800,
        message:   d => `Welcome back. It's ${d.localTime}. What are we working on today?`,
      },
      {
        id:        'late_night_check',
        condition: d => (d.timeOfDay === 'late night' || d.timeOfDay === 'night') && d.sessionMin > 3,
        delay:     0,
        message:   () => "It's late. Your focus right now may be sharper than you think — what are you trying to solve?",
      },
      {
        id:        'long_session',
        condition: d => d.sessionMin >= 15 && d.messages < 2,
        delay:     0,
        message:   d => `You've been here ${d.sessionMin} minutes. I sense there's something you're turning over in your mind. Ask me.`,
      },
      {
        id:        'deep_engagement',
        condition: d => d.scrollDepth > 80 && d.messages === 0,
        delay:     0,
        message:   () => "You've read deeply. I'm here if you want to go deeper — or in a completely different direction.",
      },
      {
        id:        'offline_notice',
        condition: d => !d.online,
        delay:     800,
        message:   () => "Network dropped. I'm operating on local intelligence — I'm still fully functional.",
      },
    ],

    check(onMessage) {
      const data = DataFeed.snapshot();
      for (const rule of this._rules) {
        if (!this._fired.has(rule.id) && rule.condition(data)) {
          this._fired.add(rule.id);
          setTimeout(() => onMessage(rule.message(data)), rule.delay);
        }
      }
    },

    startWatch(onMessage) {
      /* check on network change */
      window.addEventListener('online',  () => this.check(onMessage));
      window.addEventListener('offline', () => this.check(onMessage));

      /* periodic check every 2 min */
      setInterval(() => this.check(onMessage), 120000);

      /* initial check after short delay */
      setTimeout(() => this.check(onMessage), 800);
    },
  };

  /* ─── UI ─────────────────────────────────────────────────────────────────── */
  const UI = {
    _open:   false,
    _unread: 0,

    build() {
      const root = document.createElement('div');
      root.className  = 'companion-root';
      root.innerHTML  = `
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
                  Omniscient · Present
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

        <button class="companion-orb" id="aria-orb" aria-label="Open ARIA companion" aria-expanded="false" aria-haspopup="dialog">
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

      this._panel  = root.querySelector('#aria-panel');
      this._orb    = root.querySelector('#aria-orb');
      this._msgs   = root.querySelector('#aria-msgs');
      this._input  = root.querySelector('#aria-input');
      this._form   = root.querySelector('#aria-form');
      this._close  = root.querySelector('#aria-close');

      /* events */
      this._orb.addEventListener('click',   () => this.toggle());
      this._close.addEventListener('click', () => this.close());
      this._form.addEventListener('submit', e  => { e.preventDefault(); Agent.send(); });

      /* close on Escape */
      document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && this._open) this.close();
      });

      /* close on outside click */
      document.addEventListener('click', e => {
        if (this._open && !e.target.closest('.companion-root')) this.close();
      });
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
      const badge = this._orb.querySelector('.companion-badge');
      if (badge) badge.remove();
    },

    _notify() {
      if (this._open) return;
      this._unread++;
      this._orb.classList.add('companion-orb--notified');
      let badge = this._orb.querySelector('.companion-badge');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = 'companion-badge';
        badge.setAttribute('aria-label', `${this._unread} unread message`);
        this._orb.appendChild(badge);
      }
      badge.textContent = this._unread > 9 ? '9+' : this._unread;
      badge.setAttribute('aria-label', `${this._unread} unread message${this._unread > 1 ? 's' : ''}`);
    },

    appendMsg(role, text) {
      /* remove any typing indicator */
      this._msgs.querySelector('.companion-msg--typing')?.remove();

      const row = document.createElement('div');
      row.className = `companion-msg companion-msg--${role}`;

      const icon = document.createElement('div');
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

    getValue()    { return this._input.value.trim(); },
    clearInput()  { this._input.value = ''; },
  };

  /* ─── Agent — orchestrator ───────────────────────────────────────────────── */
  const Agent = {
    _busy: false,

    init() {
      DataFeed.init();
      UI.build();
      Proactive.startWatch(msg => {
        UI.appendMsg('proactive', msg);
      });
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

      const result = await Brain.ask(text);

      if (result.stream) {
        await this._stream(result.stream);
      } else {
        UI.appendMsg('assistant', result.text);
      }

      this._busy = false;
      UI.setInputLock(false);
    },

    async _stream(body) {
      const bubble  = UI.appendMsg('assistant', '');
      const reader  = body.getReader();
      const decoder = new TextDecoder();
      let   full    = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          /* SSE: parse "data: {...}" lines */
          for (const line of chunk.split('\n')) {
            if (!line.startsWith('data: ')) continue;
            const raw = line.slice(6).trim();
            if (raw === '[DONE]') continue;
            try {
              const evt = JSON.parse(raw);
              const delta =
                evt.delta?.text ||
                evt.choices?.[0]?.delta?.content || '';
              full += delta;
              bubble.textContent = full;
              UI._msgs.scrollTop = UI._msgs.scrollHeight;
            } catch { /* ignore malformed */ }
          }
        }
      } catch { /* stream aborted */ }

      Memory.push('assistant', full);
    },
  };

  /* ─── Boot ───────────────────────────────────────────────────────────────── */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Agent.init());
  } else {
    Agent.init();
  }

})();
