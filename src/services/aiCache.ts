/**
 * AI response cache backed by localStorage.
 *
 * Keys are versioned and include an input fingerprint so that
 * materially different financial snapshots or prompt types produce
 * separate cache entries.
 *
 * TTL defaults to 12 hours (configurable per call-site).
 */

const CACHE_VERSION = 'v1';
const CACHE_PREFIX = `rag7:ai-cache:${CACHE_VERSION}:`;
const DEFAULT_TTL_MS = 12 * 60 * 60 * 1000; // 12 hours

export interface CacheEntry<T> {
  value: T;
  expiresAt: number; // epoch ms
  fingerprint: string;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/** Store a value. TTL is in milliseconds; defaults to 12 h. */
export function cacheSet<T>(
  key: string,
  fingerprint: string,
  value: T,
  ttlMs: number = DEFAULT_TTL_MS,
): void {
  const entry: CacheEntry<T> = {
    value,
    expiresAt: Date.now() + ttlMs,
    fingerprint,
  };
  try {
    localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(entry));
  } catch {
    // localStorage may be full or disabled – silently ignore
  }
}

/**
 * Retrieve a cached value.
 * Returns `null` if the entry is absent, expired, or the fingerprint
 * doesn't match (i.e., the underlying data changed).
 */
export function cacheGet<T>(
  key: string,
  fingerprint: string,
): T | null {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    const entry: CacheEntry<T> = JSON.parse(raw) as CacheEntry<T>;
    if (entry.expiresAt < Date.now()) {
      localStorage.removeItem(CACHE_PREFIX + key);
      return null;
    }
    if (entry.fingerprint !== fingerprint) {
      localStorage.removeItem(CACHE_PREFIX + key);
      return null;
    }
    return entry.value;
  } catch {
    return null;
  }
}

/** Remove a single cache entry. */
export function cacheDelete(key: string): void {
  try {
    localStorage.removeItem(CACHE_PREFIX + key);
  } catch {
    // ignore
  }
}

/** Remove all AI cache entries (all versions for this app). */
export function cacheClearAll(): void {
  try {
    const keysToRemove: string[] = [];
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith('rag7:ai-cache:')) {
        keysToRemove.push(k);
      }
    }
    keysToRemove.forEach((k) => localStorage.removeItem(k));
  } catch {
    // ignore
  }
}

// ---------------------------------------------------------------------------
// Fingerprinting
// ---------------------------------------------------------------------------

/**
 * Build a stable string fingerprint from arbitrary input.
 * Uses a simple but consistent hash of the JSON-serialised value.
 */
export function buildFingerprint(input: unknown): string {
  const str = JSON.stringify(input, sortObjectKeys);
  return simpleHash(str);
}

/** Recursively sort object keys for deterministic JSON. */
function sortObjectKeys(
  _key: string,
  value: unknown,
): unknown {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).sort(([a], [b]) =>
        a.localeCompare(b),
      ),
    );
  }
  return value;
}

/** djb2-style hash that returns a hex string. */
export function simpleHash(str: string): string {
  let hash = 5381;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) ^ str.charCodeAt(i);
    hash = hash >>> 0; // keep unsigned 32-bit
  }
  return hash.toString(16).padStart(8, '0');
}
