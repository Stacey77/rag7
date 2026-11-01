/**
 * app.js – Main interactivity for the digital business card PWA
 * Handles: clipboard copy, share, theme toggle, PWA install prompt
 */

'use strict';

// ─── Theme ───────────────────────────────────────────────────────────────────

const THEME_KEY = 'preferred-theme';

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const isDark = theme === 'dark';
  const iconDark = document.getElementById('theme-icon-dark');
  const iconLight = document.getElementById('theme-icon-light');
  if (iconDark && iconLight) {
    iconDark.style.display = isDark ? '' : 'none';
    iconLight.style.display = isDark ? 'none' : '';
  }
  localStorage.setItem(THEME_KEY, theme);
}

function initTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(saved || (prefersDark ? 'dark' : 'light'));
}

document.getElementById('theme-toggle').addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
});

// ─── Toast ────────────────────────────────────────────────────────────────────

let toastTimer = null;

function showToast(message, durationMs = 2500) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('toast--visible');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('toast--visible'), durationMs);
}

// ─── Clipboard Copy ───────────────────────────────────────────────────────────

async function copyToClipboard(text) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
    } else {
      // Fallback for non-HTTPS contexts
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }
    showToast('✅ Copied to clipboard!');
  } catch {
    showToast('❌ Could not copy. Please copy manually.');
  }
}

document.querySelectorAll('.copy-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const text = btn.dataset.copy;
    if (text) copyToClipboard(text);
  });
});

// ─── Share ────────────────────────────────────────────────────────────────────

document.getElementById('btn-share').addEventListener('click', async () => {
  const shareData = {
    title: 'Stacey Williams – Certified Service Technician',
    text: 'Mercedes-Benz of Collierville – Certified Service Technician',
    url: 'https://stacey77.github.io/rag7/',
  };
  if (navigator.share) {
    try {
      await navigator.share(shareData);
    } catch (err) {
      if (err.name !== 'AbortError') showToast('Share failed – link copied instead!');
    }
  } else {
    await copyToClipboard(shareData.url);
    showToast('🔗 Link copied to clipboard!');
  }
});

// ─── vCard Download ───────────────────────────────────────────────────────────

document.getElementById('btn-vcard').addEventListener('click', () => {
  if (typeof generateVCard === 'function') {
    generateVCard();
  } else {
    showToast('❌ vCard module not loaded.');
  }
});

// ─── PWA Install Prompt ───────────────────────────────────────────────────────

let deferredInstallPrompt = null;

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();
  deferredInstallPrompt = e;
  // Show both install buttons
  ['btn-install', 'btn-install-bottom'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.style.display = '';
  });
});

async function triggerInstall() {
  if (!deferredInstallPrompt) return;
  deferredInstallPrompt.prompt();
  const { outcome } = await deferredInstallPrompt.userChoice;
  if (outcome === 'accepted') {
    showToast('🎉 App installed successfully!');
    ['btn-install', 'btn-install-bottom'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
    deferredInstallPrompt = null;
  }
}

document.getElementById('btn-install').addEventListener('click', triggerInstall);
document.getElementById('btn-install-bottom').addEventListener('click', triggerInstall);

window.addEventListener('appinstalled', () => {
  showToast('✅ App installed!');
  deferredInstallPrompt = null;
});

// ─── Service Worker Registration ──────────────────────────────────────────────

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/rag7/sw.js')
      .catch(err => console.warn('SW registration failed:', err));
  });
}

// ─── Init ─────────────────────────────────────────────────────────────────────

initTheme();
