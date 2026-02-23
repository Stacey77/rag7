import { describe, it, expect } from 'vitest';
import {
  classifyHttpError,
  classifyNetworkError,
} from '../services/aiErrors';

describe('classifyHttpError', () => {
  it('classifies 429 as quota error', () => {
    const err = classifyHttpError(429, null);
    expect(err.kind).toBe('quota');
    expect(err.statusCode).toBe(429);
  });

  it('classifies RESOURCE_EXHAUSTED body as quota even on 200', () => {
    const body = { error: { code: 200, status: 'RESOURCE_EXHAUSTED', message: 'quota exceeded' } };
    const err = classifyHttpError(200, body);
    expect(err.kind).toBe('quota');
  });

  it('classifies body with quota in message as quota', () => {
    const body = { error: { message: 'You exceeded your quota limit' } };
    const err = classifyHttpError(200, body);
    expect(err.kind).toBe('quota');
  });

  it('classifies 401 as invalid_key', () => {
    const err = classifyHttpError(401, null);
    expect(err.kind).toBe('invalid_key');
  });

  it('classifies 403 as invalid_key', () => {
    const err = classifyHttpError(403, null);
    expect(err.kind).toBe('invalid_key');
  });

  it('classifies 400 as invalid_key', () => {
    const err = classifyHttpError(400, null);
    expect(err.kind).toBe('invalid_key');
  });

  it('classifies 500 as server error', () => {
    const err = classifyHttpError(500, null);
    expect(err.kind).toBe('server');
    expect(err.statusCode).toBe(500);
  });

  it('classifies 503 as server error', () => {
    const err = classifyHttpError(503, null);
    expect(err.kind).toBe('server');
  });

  it('classifies unknown status as unknown', () => {
    const err = classifyHttpError(418, null);
    expect(err.kind).toBe('unknown');
  });

  it('includes the raw body in the error', () => {
    const body = { error: { code: 500, message: 'oops' } };
    const err = classifyHttpError(500, body);
    expect(err.raw).toEqual(body);
  });
});

describe('classifyNetworkError', () => {
  it('classifies fetch failures as network error', () => {
    const err = classifyNetworkError(new TypeError('Failed to fetch'));
    expect(err.kind).toBe('network');
    expect(err.message).toContain('Failed to fetch');
  });

  it('handles non-Error values', () => {
    const err = classifyNetworkError('timeout');
    expect(err.kind).toBe('network');
    expect(err.message).toContain('timeout');
  });
});
