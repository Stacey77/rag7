/**
 * Custom error classes for Ragamuffin SDK
 */

export class RagamuffinError extends Error {
  public statusCode?: number;
  public details?: Record<string, unknown>;

  constructor(
    message: string,
    statusCode?: number,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'RagamuffinError';
    this.statusCode = statusCode;
    this.details = details;
  }
}

export class AuthenticationError extends RagamuffinError {
  constructor(message: string, statusCode?: number) {
    super(message, statusCode);
    this.name = 'AuthenticationError';
  }
}

export class APIError extends RagamuffinError {
  constructor(
    message: string,
    statusCode?: number,
    details?: Record<string, unknown>
  ) {
    super(message, statusCode, details);
    this.name = 'APIError';
  }
}

export class ValidationError extends RagamuffinError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 400, details);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends RagamuffinError {
  constructor(message: string) {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

export class RateLimitError extends RagamuffinError {
  public retryAfter?: number;

  constructor(message: string, retryAfter?: number) {
    super(message, 429);
    this.name = 'RateLimitError';
    this.retryAfter = retryAfter;
  }
}
