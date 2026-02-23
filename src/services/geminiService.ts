/**
 * Gemini API service with:
 * - Typed error handling (AIError)
 * - Exponential backoff + jitter for transient errors
 * - No retry on quota / invalid-key errors
 * - Response caching via aiCache
 * - AI Studio key selection support (window.aistudio)
 */

import type { BudgetData } from '../types/budget';
import { classifyHttpError, classifyNetworkError, type AIError } from './aiErrors';
import { cacheGet, cacheSet, buildFingerprint } from './aiCache';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type AIResult<T> =
  | { ok: true; value: T; fromCache: boolean }
  | { ok: false; error: AIError };

export interface RetryOptions {
  maxAttempts: number;
  baseDelayMs: number;
  maxDelayMs: number;
}

const DEFAULT_RETRY: RetryOptions = {
  maxAttempts: 3,
  baseDelayMs: 500,
  maxDelayMs: 8000,
};

// Gemini model
const MODEL = 'gemini-2.0-flash';

// ---------------------------------------------------------------------------
// Core fetch helper with retry
// ---------------------------------------------------------------------------

async function fetchGemini(
  apiKey: string,
  prompt: string,
  retryOpts: RetryOptions = DEFAULT_RETRY,
): Promise<AIResult<string>> {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${apiKey}`;
  const body = JSON.stringify({
    contents: [{ parts: [{ text: prompt }] }],
  });

  let lastError: AIError | null = null;

  for (let attempt = 1; attempt <= retryOpts.maxAttempts; attempt++) {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      });

      if (!response.ok) {
        let parsedBody: unknown = null;
        try {
          parsedBody = await response.json();
        } catch {
          // ignore parse error
        }
        const err = classifyHttpError(response.status, parsedBody);
        // Don't retry quota / invalid-key errors
        if (err.kind === 'quota' || err.kind === 'invalid_key') {
          return { ok: false, error: err };
        }
        lastError = err;
        // Retry server errors
        if (attempt < retryOpts.maxAttempts) {
          await sleep(backoffDelay(attempt, retryOpts));
          continue;
        }
        return { ok: false, error: err };
      }

      const data = await response.json() as GeminiResponse;
      const text = data.candidates?.[0]?.content?.parts?.[0]?.text ?? '';
      return { ok: true, value: text, fromCache: false };
    } catch (err) {
      const aiErr = classifyNetworkError(err);
      lastError = aiErr;
      if (attempt < retryOpts.maxAttempts) {
        await sleep(backoffDelay(attempt, retryOpts));
        continue;
      }
    }
  }

  return {
    ok: false,
    error: lastError ?? {
      kind: 'unknown',
      message: 'An unexpected error occurred.',
    },
  };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Get AI-generated financial insights for the Dashboard.
 * Results are cached for 12 h keyed by a fingerprint of the budget data.
 */
export async function getDashboardInsights(
  apiKey: string,
  data: BudgetData,
): Promise<AIResult<string>> {
  const fingerprint = buildFingerprint({
    type: 'dashboard',
    transactions: data.transactions.slice(-20),
    bills: data.bills,
    goals: data.goals,
    income: data.monthlyIncome,
  });

  const cached = cacheGet<string>('dashboard-insights', fingerprint);
  if (cached !== null) {
    return { ok: true, value: cached, fromCache: true };
  }

  const prompt = buildDashboardPrompt(data);
  const result = await fetchGemini(apiKey, prompt);

  if (result.ok) {
    cacheSet('dashboard-insights', fingerprint, result.value);
  }

  return result;
}

/**
 * Get AI-generated advice for the AI Advisor component.
 * Cached per unique question + financial snapshot.
 */
export async function getAdvisorResponse(
  apiKey: string,
  question: string,
  data: BudgetData,
): Promise<AIResult<string>> {
  const fingerprint = buildFingerprint({
    type: 'advisor',
    question,
    transactions: data.transactions.slice(-10),
    bills: data.bills,
    goals: data.goals,
    income: data.monthlyIncome,
  });

  const cacheKey = `advisor-${simpleKeyHash(question)}`;
  const cached = cacheGet<string>(cacheKey, fingerprint);
  if (cached !== null) {
    return { ok: true, value: cached, fromCache: true };
  }

  const prompt = buildAdvisorPrompt(question, data);
  const result = await fetchGemini(apiKey, prompt);

  if (result.ok) {
    cacheSet(cacheKey, fingerprint, result.value);
  }

  return result;
}

// ---------------------------------------------------------------------------
// AI Studio key helpers (guarded)
// ---------------------------------------------------------------------------

/** Returns true if running inside AI Studio with a selected key. */
export function hasAIStudioKey(): boolean {
  try {
    return !!(
      (window as AIStudioWindow).aistudio?.hasSelectedApiKey?.()
    );
  } catch {
    return false;
  }
}

/** Opens the AI Studio key selector (no-op if not available). */
export function openAIStudioKeySelector(): void {
  try {
    (window as AIStudioWindow).aistudio?.openSelectKey?.();
  } catch {
    // ignore
  }
}

// ---------------------------------------------------------------------------
// Prompt builders
// ---------------------------------------------------------------------------

function buildDashboardPrompt(data: BudgetData): string {
  const recent = data.transactions.slice(-20);
  const totalSpent = recent
    .filter((t) => t.amount < 0)
    .reduce((s, t) => s + Math.abs(t.amount), 0);
  const upcoming = data.bills.filter((b) => !b.isPaid);

  return `You are a helpful financial advisor. Based on the following financial data, provide 3-4 concise, actionable insights in plain English (no markdown headers, keep it friendly):

Monthly income: $${data.monthlyIncome.toFixed(2)}
Total spent (last 20 transactions): $${totalSpent.toFixed(2)}
Upcoming unpaid bills: ${upcoming.map((b) => `${b.name} $${b.amount}`).join(', ') || 'none'}
Financial goals: ${data.goals.map((g) => `${g.name} (${Math.round((g.currentAmount / g.targetAmount) * 100)}% funded)`).join(', ') || 'none'}

Provide brief, practical financial advice.`;
}

function buildAdvisorPrompt(question: string, data: BudgetData): string {
  return `You are a helpful financial advisor. Answer the following question based on the user's financial data.

User question: ${question}

Monthly income: $${data.monthlyIncome.toFixed(2)}
Recent transactions: ${data.transactions
    .slice(-5)
    .map((t) => `${t.description}: $${t.amount}`)
    .join(', ')}
Goals: ${data.goals
    .map((g) => `${g.name}: $${g.currentAmount}/$${g.targetAmount}`)
    .join(', ')}

Answer concisely and practically in 2-4 sentences.`;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function backoffDelay(attempt: number, opts: RetryOptions): number {
  const base = opts.baseDelayMs * Math.pow(2, attempt - 1);
  const jitter = Math.random() * base * 0.3;
  return Math.min(base + jitter, opts.maxDelayMs);
}

function simpleKeyHash(str: string): string {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (Math.imul(31, h) + str.charCodeAt(i)) | 0;
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}

// ---------------------------------------------------------------------------
// Internal types
// ---------------------------------------------------------------------------

interface GeminiResponse {
  candidates?: Array<{
    content?: {
      parts?: Array<{ text?: string }>;
    };
  }>;
}

interface AIStudioWindow extends Window {
  aistudio?: {
    hasSelectedApiKey?: () => boolean;
    openSelectKey?: () => void;
  };
}
