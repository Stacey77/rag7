/**
 * chat-ui.js – AI assistant chat panel
 *
 * Uses a local FAQ fallback when no server endpoint is configured.
 * If CHAT_ENDPOINT is set (via a meta tag or inline config), it posts
 * messages to the server-side proxy instead.
 *
 * Server endpoint URL resolution order:
 *   1. <meta name="chat-endpoint" content="https://…"> in index.html
 *   2. window.CHAT_ENDPOINT global variable
 *   3. null → use local FAQ fallback (safe default)
 */

'use strict';

// ─── Config ───────────────────────────────────────────────────────────────────

const CHAT_ENDPOINT = (() => {
  const meta = document.querySelector('meta[name="chat-endpoint"]');
  if (meta && meta.content && meta.content !== '') return meta.content;
  if (typeof window.CHAT_ENDPOINT === 'string' && window.CHAT_ENDPOINT !== '') {
    return window.CHAT_ENDPOINT;
  }
  return null;
})();

// ─── Local FAQ Fallback ───────────────────────────────────────────────────────

const FAQ = [
  {
    patterns: [/hours?|open|close|schedule|timing/i],
    reply: 'Our service department is open Monday–Friday 7 AM–6 PM and Saturday 8 AM–4 PM. Call (901) 494-3990 to confirm same-day availability.',
  },
  {
    patterns: [/appoint|book|schedul|reserv/i],
    reply: 'You can book a service appointment by calling (901) 494-3990 or visiting mbcollierville.com. Stacey will personally ensure your vehicle is well cared for!',
  },
  {
    patterns: [/loaner|rental|car while/i],
    reply: 'Loaner vehicles are available for qualifying services. Please mention this when you schedule your appointment so we can arrange it for you.',
  },
  {
    patterns: [/oil change|service a|service b|maintenance/i],
    reply: 'We perform all factory-scheduled maintenance (Service A & B), oil changes, brake service, tire rotations, and more using genuine Mercedes-Benz parts.',
  },
  {
    patterns: [/warranty|recall|tsb/i],
    reply: 'All warranty work and recall repairs are handled at no charge to you. Bring your vehicle in and we\'ll take care of everything through the factory.',
  },
  {
    patterns: [/price|cost|fee|how much/i],
    reply: 'Pricing depends on the service needed. Call (901) 494-3990 or email stacey.williams@mbcollierville.com for a detailed quote.',
  },
  {
    patterns: [/address|location|directions?|where/i],
    reply: 'We\'re located at 1088 W. Poplar Ave, Collierville, TN. Use the map link on the card for turn-by-turn directions.',
  },
  {
    patterns: [/email|contact|reach|talk/i],
    reply: 'You can reach Stacey directly at stacey.williams@mbcollierville.com or by phone at (901) 494-3990.',
  },
  {
    patterns: [/cert|qualif|train|expert/i],
    reply: 'Stacey is a factory-certified Mercedes-Benz technician with specialized training on all AMG, EQ, and standard model lines.',
  },
  {
    patterns: [/hi|hello|hey|good morning|good afternoon|sup/i],
    reply: 'Hello! How can I help you today? You can ask about services, appointments, hours, or how to contact Stacey.',
  },
  {
    patterns: [/thank|thanks|appreciate|great/i],
    reply: 'You\'re welcome! Don\'t hesitate to reach out if you need anything else. 😊',
  },
];

function localFallback(message) {
  const lower = message.toLowerCase();
  for (const entry of FAQ) {
    if (entry.patterns.some(p => p.test(lower))) {
      return entry.reply;
    }
  }
  return "I'm not sure about that one. For the most accurate answer, please call (901) 494-3990 or email stacey.williams@mbcollierville.com and Stacey will be happy to help!";
}

// ─── Chat History ─────────────────────────────────────────────────────────────

const chatHistory = [];

// ─── DOM Helpers ──────────────────────────────────────────────────────────────

function appendMessage(role, text) {
  const container = document.getElementById('chat-messages');
  const wrapper = document.createElement('div');
  wrapper.className = `chat-message ${role}`;
  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';
  bubble.textContent = text;
  wrapper.appendChild(bubble);
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

function showTyping() {
  const container = document.getElementById('chat-messages');
  const wrapper = document.createElement('div');
  wrapper.id = 'typing-indicator';
  wrapper.className = 'chat-message assistant';
  wrapper.setAttribute('aria-label', 'Assistant is typing');
  wrapper.innerHTML = '<div class="chat-bubble typing"><span></span><span></span><span></span></div>';
  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

function hideTyping() {
  const el = document.getElementById('typing-indicator');
  if (el) el.remove();
}

// ─── Send Message ─────────────────────────────────────────────────────────────

async function sendMessage(message) {
  chatHistory.push({ role: 'user', content: message });

  if (!CHAT_ENDPOINT) {
    // Local fallback – simulate slight delay for realism
    showTyping();
    await new Promise(r => setTimeout(r, 500 + Math.random() * 500));
    hideTyping();
    const reply = localFallback(message);
    chatHistory.push({ role: 'assistant', content: reply });
    appendMessage('assistant', reply);
    return;
  }

  // Server-side proxy request
  showTyping();
  try {
    const res = await fetch(CHAT_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history: chatHistory.slice(-10) }),
    });
    hideTyping();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    const reply = data.reply || 'Sorry, I received an empty response.';
    chatHistory.push({ role: 'assistant', content: reply });
    appendMessage('assistant', reply);
  } catch (err) {
    hideTyping();
    const fallbackReply = localFallback(message);
    chatHistory.push({ role: 'assistant', content: fallbackReply });
    appendMessage('assistant', fallbackReply);
    console.warn('Chat endpoint error, using local fallback:', err.message);
  }
}

// ─── Panel Toggle ─────────────────────────────────────────────────────────────

function openChat() {
  const panel = document.getElementById('chat-panel');
  const fab = document.getElementById('ai-fab');
  panel.classList.add('chat-panel--open');
  panel.setAttribute('aria-hidden', 'false');
  fab.setAttribute('aria-expanded', 'true');
  document.getElementById('chat-input').focus();
}

function closeChat() {
  const panel = document.getElementById('chat-panel');
  const fab = document.getElementById('ai-fab');
  panel.classList.remove('chat-panel--open');
  panel.setAttribute('aria-hidden', 'true');
  fab.setAttribute('aria-expanded', 'false');
  fab.focus();
}

document.getElementById('ai-fab').addEventListener('click', () => {
  const panel = document.getElementById('chat-panel');
  if (panel.classList.contains('chat-panel--open')) {
    closeChat();
  } else {
    openChat();
  }
});

document.getElementById('chat-close').addEventListener('click', closeChat);

// Close on Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    const panel = document.getElementById('chat-panel');
    if (panel.classList.contains('chat-panel--open')) closeChat();
  }
});

// ─── Form Submit ──────────────────────────────────────────────────────────────

document.getElementById('chat-form').addEventListener('submit', async e => {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;

  input.value = '';
  input.disabled = true;
  document.querySelector('.chat-send').disabled = true;

  appendMessage('user', message);
  await sendMessage(message);

  input.disabled = false;
  document.querySelector('.chat-send').disabled = false;
  input.focus();
});
