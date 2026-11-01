/**
 * dashboard.js – Interactivity for the service technician dashboard
 * Handles: theme sync, greeting, date display, sparkline chart
 */

'use strict';

// ─── Theme (shared with app.js logic) ────────────────────────────────────────

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

// ─── Greeting & Date ──────────────────────────────────────────────────────────

function initGreeting() {
  const hour = new Date().getHours();
  let timeOfDay = 'evening';
  if (hour >= 5 && hour < 12) timeOfDay = 'morning';
  else if (hour >= 12 && hour < 17) timeOfDay = 'afternoon';

  const todEl = document.getElementById('time-of-day');
  if (todEl) todEl.textContent = timeOfDay;

  const dateEl = document.getElementById('today-date');
  if (dateEl) {
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  }
}

// ─── Weekly Sparkline Chart ───────────────────────────────────────────────────

// Services completed per day Mon–Fri (most recent week, sample data)
const WEEKLY_DATA = [
  { label: 'Mon', value: 4 },
  { label: 'Tue', value: 3 },
  { label: 'Wed', value: 5 },
  { label: 'Thu', value: 2 },
  { label: 'Fri', value: 4 },
];

function buildSparkline() {
  const chart = document.getElementById('spark-chart');
  if (!chart) return;

  const max = Math.max(...WEEKLY_DATA.map(d => d.value));
  const CHART_HEIGHT = 70; // px – matches CSS height

  WEEKLY_DATA.forEach(day => {
    const bar = document.createElement('div');
    bar.className = 'spark-bar';
    const heightPx = Math.round((day.value / max) * CHART_HEIGHT);
    bar.style.height = '0px'; // start at 0 for animation
    bar.setAttribute('aria-label', `${day.label}: ${day.value} services`);
    chart.appendChild(bar);

    // Animate in after a paint frame so CSS transition fires
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        bar.style.height = `${heightPx}px`;
      });
    });
  });
}

// ─── Animate bars in on first intersection ────────────────────────────────────

function animateBars() {
  const fills = document.querySelectorAll('.breakdown-bar__fill');
  // Reset widths so the transition plays when they come into view
  fills.forEach(el => {
    el.style.width = '0%';
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const fill = entry.target;
          // Re-apply the CSS custom property width
          const targetWidth = fill.style.getPropertyValue('--fill-pct');
          requestAnimationFrame(() => {
            fill.style.width = targetWidth;
          });
          observer.unobserve(fill);
        }
      });
    }, { threshold: 0.1 });

    fills.forEach(el => observer.observe(el));
  } else {
    // Fallback: just set widths directly
    fills.forEach(el => {
      el.style.width = el.style.getPropertyValue('--fill-pct');
    });
  }
}

// ─── Init ─────────────────────────────────────────────────────────────────────

initTheme();
initGreeting();
buildSparkline();
animateBars();
