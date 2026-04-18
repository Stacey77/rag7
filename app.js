'use strict';

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

let toastTimer = null;
function showToast(message, durationMs = 2200) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add('toast--visible');
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('toast--visible'), durationMs);
}

const models = {
  carbon12: {
    label: 'Carbon-12 Atom',
    description: 'Stable isotope with 6 protons, 6 neutrons, and shell distribution 2 + 4.',
    metrics: [
      ['Nuclear Composition', '6p / 6n'],
      ['Electron Shells', 'K:2 L:4'],
      ['Engineering Context', 'Organic chemistry backbone'],
    ],
  },
  carbon13: {
    label: 'Carbon-13 Atom',
    description: 'Carbon isotope with one extra neutron used in ecological and dietary tracing.',
    metrics: [
      ['Nuclear Composition', '6p / 7n'],
      ['Electron Shells', 'K:2 L:4'],
      ['Engineering Context', 'Isotopic analysis marker'],
    ],
  },
  methane: {
    label: 'Methane Molecule (CH4)',
    description: 'Tetrahedral carbon-hydrogen structure showing carbon valence bonding in 3D.',
    metrics: [
      ['Atomic Composition', '1 C + 4 H'],
      ['Bond Geometry', 'Tetrahedral 109.5°'],
      ['Engineering Context', 'Combustion and fuel science'],
    ],
  },
  'gear-train': {
    label: 'Planetary Gear Train',
    description: 'Mechanical power transmission model with coupled rotational dynamics.',
    metrics: [
      ['Primary Components', 'Sun + 3 Planet + Ring'],
      ['Motion Ratio', 'Approx. 1:3 reduction'],
      ['Engineering Context', 'Automotive transmissions'],
    ],
  },
  turbine: {
    label: 'Axial Turbine Stage',
    description: 'Rotor-stator interaction model representing mechanical energy extraction from flow.',
    metrics: [
      ['Blade Count', 'Rotor: 14 / Stator: 12'],
      ['Flow Type', 'Axial with swirl'],
      ['Engineering Context', 'Power and propulsion systems'],
    ],
  },
};

const canvas = document.getElementById('science-model-canvas');
const modelSelect = document.getElementById('model-select');
const modelDescription = document.getElementById('model-description');
let currentModel = 'carbon12';
let startTime = performance.now();

function updateMetrics(modelKey) {
  const model = models[modelKey];
  if (!model) return;
  modelDescription.textContent = model.description;
  const [a, b, c] = model.metrics;
  document.getElementById('metric-a-label').textContent = a[0];
  document.getElementById('metric-a-value').textContent = a[1];
  document.getElementById('metric-b-label').textContent = b[0];
  document.getElementById('metric-b-value').textContent = b[1];
  document.getElementById('metric-c-label').textContent = c[0];
  document.getElementById('metric-c-value').textContent = c[1];
}

function resizeCanvas() {
  if (!canvas) return;
  const rect = canvas.getBoundingClientRect();
  const ratio = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.floor(rect.width * ratio));
  canvas.height = Math.max(1, Math.floor(rect.height * ratio));
}

function drawNucleus(ctx, x, y, radius, protonCount, neutronCount) {
  const grad = ctx.createRadialGradient(x - radius * 0.3, y - radius * 0.3, radius * 0.2, x, y, radius);
  grad.addColorStop(0, '#9dd7ff');
  grad.addColorStop(1, '#1f5a83');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = 'rgba(255,255,255,0.9)';
  ctx.font = `${Math.max(12, Math.floor(radius * 0.35))}px Inter, sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText(`${protonCount}p ${neutronCount}n`, x, y + 5);
}

function drawAtom(ctx, w, h, time, neutronCount) {
  const centerX = w * 0.52;
  const centerY = h * 0.52;
  const ratio = canvas.width / w;

  drawNucleus(ctx, centerX, centerY, 34 * ratio, 6, neutronCount);

  const shells = [
    { radius: 86 * ratio, electrons: 2, speed: 0.6 },
    { radius: 140 * ratio, electrons: 4, speed: -0.4 },
  ];

  shells.forEach(shell => {
    ctx.strokeStyle = 'rgba(130, 184, 255, 0.35)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.ellipse(centerX, centerY, shell.radius, shell.radius * 0.45, 0.15, 0, Math.PI * 2);
    ctx.stroke();

    for (let i = 0; i < shell.electrons; i++) {
      const theta = (time * shell.speed) + (i * (Math.PI * 2 / shell.electrons));
      const ex = centerX + Math.cos(theta) * shell.radius;
      const ey = centerY + Math.sin(theta) * shell.radius * 0.45;
      ctx.fillStyle = '#e8f3ff';
      ctx.beginPath();
      ctx.arc(ex, ey, 7 * ratio, 0, Math.PI * 2);
      ctx.fill();
    }
  });
}

function drawMethane(ctx, w, h, time) {
  const cx = w * 0.52;
  const cy = h * 0.52;
  const ratio = canvas.width / w;
  const r = 120 * ratio;
  const wobble = Math.sin(time * 0.8) * 0.22;

  const points = [
    [Math.cos(time) * r * 0.2, -r * 0.65],
    [r * 0.75, r * 0.2],
    [-r * 0.75, r * 0.18],
    [Math.sin(time * 0.6) * r * 0.35, r * 0.75],
  ];

  points.forEach((p, i) => {
    const x = cx + p[0] * (1 + (i % 2 ? wobble : -wobble));
    const y = cy + p[1] * (1 - wobble * 0.5);
    ctx.strokeStyle = 'rgba(180, 210, 255, 0.7)';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(x, y);
    ctx.stroke();

    ctx.fillStyle = '#f6fbff';
    ctx.beginPath();
    ctx.arc(x, y, 14 * ratio, 0, Math.PI * 2);
    ctx.fill();
  });

  drawNucleus(ctx, cx, cy, 26 * ratio, 6, 6);
}

function drawGear(ctx, x, y, radius, teeth, angle, color, inner = radius * 0.38) {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);

  ctx.fillStyle = color;
  ctx.beginPath();
  for (let i = 0; i < teeth; i++) {
    const a = (i / teeth) * Math.PI * 2;
    const outer = radius + (i % 2 ? radius * 0.07 : radius * 0.16);
    ctx.lineTo(Math.cos(a) * outer, Math.sin(a) * outer);
  }
  ctx.closePath();
  ctx.fill();

  ctx.globalCompositeOperation = 'destination-out';
  ctx.beginPath();
  ctx.arc(0, 0, inner, 0, Math.PI * 2);
  ctx.fill();
  ctx.globalCompositeOperation = 'source-over';

  ctx.strokeStyle = 'rgba(255,255,255,0.55)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(0, 0, radius * 0.55, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();
}

function drawGearTrain(ctx, w, h, time) {
  const cx = w * 0.52;
  const cy = h * 0.52;
  const ratio = canvas.width / w;
  const big = 86 * ratio;
  const medium = 58 * ratio;

  drawGear(ctx, cx, cy, big, 26, time * 0.55, '#3e7cc5');
  drawGear(ctx, cx - 130 * ratio, cy + 70 * ratio, medium, 18, -time * 0.95, '#5fa1f3');
  drawGear(ctx, cx + 130 * ratio, cy + 70 * ratio, medium, 18, -time * 0.95, '#5fa1f3');
  drawGear(ctx, cx, cy - 145 * ratio, medium, 18, -time * 0.95, '#5fa1f3');
}

function drawTurbine(ctx, w, h, time) {
  const cx = w * 0.52;
  const cy = h * 0.52;
  const ratio = canvas.width / w;

  ctx.strokeStyle = 'rgba(166, 210, 255, 0.4)';
  for (let i = -2; i <= 2; i++) {
    ctx.beginPath();
    ctx.moveTo(cx - 260 * ratio, cy + i * 38 * ratio);
    ctx.quadraticCurveTo(cx, cy + Math.sin(time + i) * 42 * ratio, cx + 260 * ratio, cy + i * 38 * ratio);
    ctx.stroke();
  }

  const blades = 14;
  const rotorRadius = 102 * ratio;
  for (let i = 0; i < blades; i++) {
    const a = (i / blades) * Math.PI * 2 + time * 1.4;
    const x = cx + Math.cos(a) * rotorRadius;
    const y = cy + Math.sin(a) * rotorRadius * 0.6;
    const size = 26 * ratio;

    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(a + Math.PI / 2);
    ctx.fillStyle = '#76b6ff';
    ctx.beginPath();
    ctx.moveTo(0, -size * 0.3);
    ctx.quadraticCurveTo(size, 0, 0, size * 0.3);
    ctx.quadraticCurveTo(-size * 0.18, 0, 0, -size * 0.3);
    ctx.fill();
    ctx.restore();
  }

  drawNucleus(ctx, cx, cy, 22 * ratio, 14, 14);
}

function drawFrame(now) {
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const dpr = window.devicePixelRatio || 1;
  const w = canvas.width / dpr;
  const h = canvas.height / dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);

  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, 'rgba(10, 20, 40, 0.92)');
  g.addColorStop(1, 'rgba(10, 35, 65, 0.92)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);

  const time = (now - startTime) / 1000;
  if (currentModel === 'carbon12') drawAtom(ctx, w, h, time, 6);
  if (currentModel === 'carbon13') drawAtom(ctx, w, h, time, 7);
  if (currentModel === 'methane') drawMethane(ctx, w, h, time);
  if (currentModel === 'gear-train') drawGearTrain(ctx, w, h, time);
  if (currentModel === 'turbine') drawTurbine(ctx, w, h, time);

  requestAnimationFrame(drawFrame);
}

function switchModel(modelKey, silent = false) {
  if (!models[modelKey]) return;
  currentModel = modelKey;
  if (modelSelect) modelSelect.value = modelKey;
  updateMetrics(modelKey);
  if (!silent) showToast(`Loaded ${models[modelKey].label}`);
}

function initModelControls() {
  if (!canvas || !modelSelect) return;
  resizeCanvas();
  updateMetrics(currentModel);

  modelSelect.addEventListener('change', event => {
    switchModel(event.target.value);
  });

  document.querySelectorAll('[data-model]').forEach(btn => {
    btn.addEventListener('click', () => switchModel(btn.dataset.model));
  });

  window.addEventListener('resize', resizeCanvas);
  requestAnimationFrame(drawFrame);
}

const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/rag7/sw.js')
      .catch(err => console.warn('SW registration failed:', err));
  });
}

initTheme();
initModelControls();
