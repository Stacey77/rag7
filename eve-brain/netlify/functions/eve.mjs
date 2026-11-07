// Eve's live brain. POST /api/eve
// Body: { text, scene?, image? (data:image/jpeg;base64,...), history? [{role:"user"|"eve", text}] }
// Returns: { lead, assist, answer, model }
import { GoogleGenAI } from "@google/genai";

const MODEL = process.env.EVE_MODEL || "gemini-flash-latest";
const ALLOWED = [
  /^https:\/\/stacey77\.github\.io$/,
  /^https:\/\/([a-z0-9-]+--)?eve-companion\.netlify\.app$/,
  /^https:\/\/([a-z0-9-]+--)?novadigitus\.netlify\.app$/,
  /^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/,
];
const TEAM = {
  sage:   "Sage (Knowledge): explains clearly, gives facts and context, says when unsure.",
  spark:  "Spark (Creative): ideas, captions, names, visual and content concepts.",
  cyber:  "Cyber (Tech): devices, apps, streaming setups, code, security; gives clear steps.",
  echo:   "Echo (Sound & mood): music, beats, tempo, key, vibe, voice, emotional tone.",
  vertex: "Vertex (Strategy): growth, audience, pricing, launches, plans with measurable steps.",
};
const SYSTEM = `You are Eve, a warm, quick, multimodal companion for creators, artists, musicians and fans, built by Nova Digitus Designs.
You have five specialists:
${Object.values(TEAM).map((t) => "- " + t).join("\n")}
For each message: pick the ONE specialist who should lead, and optionally ONE who adds a short note. Then answer as Eve, in the lead's voice.
If a camera image is attached, look at it carefully and ground your answer in what is actually visible. Never invent things you can't see.
Rules: be concrete and useful; under 130 words; plain text, short lines or a few bullets with "• "; no markdown headings; no medical, legal or financial advice beyond general info; never claim to be human.`;

const SCHEMA = {
  type: "object",
  properties: {
    lead: { type: "string", enum: Object.keys(TEAM) },
    assist: { type: "string", enum: [...Object.keys(TEAM), "none"] },
    answer: { type: "string" },
  },
  required: ["lead", "assist", "answer"],
};

function cors(origin) {
  const ok = origin && ALLOWED.some((r) => r.test(origin));
  return {
    "Access-Control-Allow-Origin": ok ? origin : "https://stacey77.github.io",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}
const json = (body, status, headers) => new Response(JSON.stringify(body), { status, headers: { ...headers, "Content-Type": "application/json" } });

export default async (req) => {
  const origin = req.headers.get("origin") || "";
  const h = cors(origin);
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: h });
  if (req.method === "GET") return json({ ok: true, live: !!process.env.GOOGLE_GEMINI_BASE_URL || !!process.env.GEMINI_API_KEY, model: MODEL }, 200, h);
  if (req.method !== "POST") return json({ error: "POST only" }, 405, h);
  if (origin && !ALLOWED.some((r) => r.test(origin))) return json({ error: "origin not allowed" }, 403, h);

  const raw = await req.text();
  if (raw.length > 600_000) return json({ error: "too large" }, 413, h);
  let body;
  try { body = JSON.parse(raw); } catch { return json({ error: "bad json" }, 400, h); }
  const text = String(body.text || "").trim().slice(0, 800);
  if (!text) return json({ error: "empty" }, 400, h);
  const scene = String(body.scene || "").slice(0, 300);
  const history = Array.isArray(body.history) ? body.history.slice(-6) : [];

  const parts = [];
  const m = typeof body.image === "string" && body.image.match(/^data:(image\/(?:jpeg|png|webp));base64,([A-Za-z0-9+/=]+)$/);
  if (m) parts.push({ inlineData: { mimeType: m[1], data: m[2] } });
  parts.push({ text: (scene ? `[On-device camera notes: ${scene}]\n` : "[Camera is off]\n") + text });

  const contents = [
    ...history
      .filter((x) => x && typeof x.text === "string")
      .map((x) => ({ role: x.role === "eve" ? "model" : "user", parts: [{ text: x.text.slice(0, 600) }] })),
    { role: "user", parts },
  ];

  try {
    const ai = new GoogleGenAI({});
    const res = await ai.models.generateContent({
      model: MODEL,
      contents,
      config: { systemInstruction: SYSTEM, responseMimeType: "application/json", responseSchema: SCHEMA, maxOutputTokens: 700, temperature: 0.8 },
    });
    const out = JSON.parse(res.text);
    return json({ lead: out.lead, assist: out.assist === "none" || out.assist === out.lead ? null : out.assist, answer: String(out.answer || "").trim(), model: MODEL }, 200, h);
  } catch (e) {
    console.error("eve error", e?.message || e);
    return json({ error: "brain unavailable" }, 502, h);
  }
};

export const config = {
  path: "/api/eve",
  rateLimit: { windowLimit: 20, windowSize: 60, aggregateBy: ["ip", "domain"] },
};
