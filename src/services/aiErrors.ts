/**
 * Typed error structure for AI service failures.
 * Normalizes errors from Gemini API into a consistent shape.
 */

export type AIErrorKind =
  | 'quota'        // 429 / RESOURCE_EXHAUSTED – hard quota, do not retry
  | 'invalid_key'  // 400/401/403 – bad or missing API key
  | 'network'      // fetch failed / offline
  | 'server'       // 5xx – transient server error, safe to retry
  | 'unknown';     // anything else

export interface AIError {
  kind: AIErrorKind;
  message: string;
  statusCode?: number;
  raw?: unknown;
}

/** Type guard */
export function isAIError(value: unknown): value is AIError {
  return (
    typeof value === 'object' &&
    value !== null &&
    'kind' in value &&
    'message' in value
  );
}

/**
 * Classify an HTTP response + optional parsed body into an AIError.
 * Call after a non-ok fetch response.
 */
export function classifyHttpError(
  statusCode: number,
  body: unknown,
): AIError {
  // Check for Gemini RESOURCE_EXHAUSTED in the body
  if (isGeminiResourceExhausted(body)) {
    return {
      kind: 'quota',
      message:
        'You have exceeded your Gemini API quota. Please check your plan and billing, or connect a different API key.',
      statusCode,
      raw: body,
    };
  }

  if (statusCode === 429) {
    return {
      kind: 'quota',
      message: 'Rate limit exceeded. Too many requests to the Gemini API.',
      statusCode,
      raw: body,
    };
  }

  if (statusCode === 400 || statusCode === 401 || statusCode === 403) {
    return {
      kind: 'invalid_key',
      message: 'Invalid or missing API key. Please check your Gemini API key.',
      statusCode,
      raw: body,
    };
  }

  if (statusCode >= 500 && statusCode < 600) {
    return {
      kind: 'server',
      message: `Gemini API server error (${statusCode}). This is usually temporary – please try again.`,
      statusCode,
      raw: body,
    };
  }

  return {
    kind: 'unknown',
    message: `Unexpected error from Gemini API (HTTP ${statusCode}).`,
    statusCode,
    raw: body,
  };
}

/** Classify a network / fetch-level error (no HTTP response). */
export function classifyNetworkError(error: unknown): AIError {
  const message =
    error instanceof Error ? error.message : String(error);
  return {
    kind: 'network',
    message: `Network error: ${message}. Please check your internet connection.`,
    raw: error,
  };
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function isGeminiResourceExhausted(body: unknown): boolean {
  if (typeof body !== 'object' || body === null) return false;
  const b = body as Record<string, unknown>;
  const error = b['error'];
  if (typeof error !== 'object' || error === null) return false;
  const e = error as Record<string, unknown>;
  return (
    e['status'] === 'RESOURCE_EXHAUSTED' ||
    (typeof e['message'] === 'string' &&
      e['message'].toLowerCase().includes('quota'))
  );
}
