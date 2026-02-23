import { describe, it, expect, beforeEach, vi } from 'vitest';
import { cacheGet, cacheSet, cacheDelete, cacheClearAll, buildFingerprint, simpleHash } from '../services/aiCache';

// ---------------------------------------------------------------------------
// localStorage stub
// ---------------------------------------------------------------------------

const store: Record<string, string> = {};

const localStorageMock = {
  getItem: (key: string) => store[key] ?? null,
  setItem: (key: string, value: string) => { store[key] = value; },
  removeItem: (key: string) => { delete store[key]; },
  get length() { return Object.keys(store).length; },
  key: (index: number) => Object.keys(store)[index] ?? null,
  clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
};

beforeEach(() => {
  localStorageMock.clear();
  vi.stubGlobal('localStorage', localStorageMock);
});

describe('cacheSet / cacheGet', () => {
  it('stores and retrieves a value', () => {
    cacheSet('test-key', 'fp1', 'hello world');
    const result = cacheGet<string>('test-key', 'fp1');
    expect(result).toBe('hello world');
  });

  it('returns null for missing key', () => {
    expect(cacheGet('missing', 'fp1')).toBeNull();
  });

  it('returns null when fingerprint does not match', () => {
    cacheSet('test-key', 'fp-original', 'value');
    expect(cacheGet('test-key', 'fp-different')).toBeNull();
  });

  it('returns null for expired entry', () => {
    cacheSet('test-key', 'fp1', 'expired', -1); // negative TTL → already expired
    expect(cacheGet<string>('test-key', 'fp1')).toBeNull();
  });

  it('does not return expired entries (negative TTL)', () => {
    cacheSet('test-key', 'fp1', 'soon-gone', -100);
    // expiresAt = Date.now() - 100 → already in the past
    expect(cacheGet<string>('test-key', 'fp1')).toBeNull();
  });
});

describe('cacheDelete', () => {
  it('removes the key', () => {
    cacheSet('del-key', 'fp', 'data');
    cacheDelete('del-key');
    expect(cacheGet('del-key', 'fp')).toBeNull();
  });
});

describe('cacheClearAll', () => {
  it('removes all rag7:ai-cache: prefixed entries', () => {
    cacheSet('key-a', 'fp', 'a');
    cacheSet('key-b', 'fp', 'b');
    // Also add a non-ai-cache entry directly
    localStorageMock.setItem('other-app:something', 'keep');
    cacheClearAll();
    expect(cacheGet('key-a', 'fp')).toBeNull();
    expect(cacheGet('key-b', 'fp')).toBeNull();
    expect(localStorageMock.getItem('other-app:something')).toBe('keep');
  });
});

describe('buildFingerprint', () => {
  it('returns the same fingerprint for equal inputs', () => {
    const input = { a: 1, b: [2, 3] };
    expect(buildFingerprint(input)).toBe(buildFingerprint(input));
  });

  it('returns different fingerprints for different inputs', () => {
    expect(buildFingerprint({ x: 1 })).not.toBe(buildFingerprint({ x: 2 }));
  });

  it('is stable regardless of object key order', () => {
    const a = buildFingerprint({ z: 1, a: 2 });
    const b = buildFingerprint({ a: 2, z: 1 });
    expect(a).toBe(b);
  });

  it('returns a non-empty hex string', () => {
    const fp = buildFingerprint({ type: 'dashboard', transactions: [] });
    expect(fp).toMatch(/^[0-9a-f]+$/);
    expect(fp.length).toBeGreaterThan(0);
  });
});

describe('simpleHash', () => {
  it('returns consistent results', () => {
    expect(simpleHash('hello')).toBe(simpleHash('hello'));
  });

  it('returns different hashes for different strings', () => {
    expect(simpleHash('foo')).not.toBe(simpleHash('bar'));
  });

  it('returns an 8-character hex string', () => {
    expect(simpleHash('test')).toMatch(/^[0-9a-f]{8}$/);
  });
});
