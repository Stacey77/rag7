/**
 * Main Ragamuffin client for JavaScript/TypeScript SDK
 */

import { AuthClient } from './auth';
import { RAGClient } from './rag';
import { FlowsClient } from './flows';
import { VoiceClient } from './voice';
import {
  RagamuffinClientOptions,
} from './types';
import {
  AuthenticationError,
  APIError,
  RateLimitError,
  NotFoundError,
} from './errors';

export class RagamuffinClient {
  private baseUrl: string;
  private timeout: number;
  private apiKey?: string;
  private accessToken?: string;
  private refreshToken?: string;

  public readonly auth: AuthClient;
  public readonly rag: RAGClient;
  public readonly flows: FlowsClient;
  public readonly voice: VoiceClient;

  constructor(options: RagamuffinClientOptions | string = {}) {
    if (typeof options === 'string') {
      options = { baseUrl: options };
    }

    this.baseUrl = (options.baseUrl || 'http://localhost:8000').replace(/\/$/, '');
    this.timeout = options.timeout || 30000;
    this.apiKey = options.apiKey;

    this.auth = new AuthClient(this);
    this.rag = new RAGClient(this);
    this.flows = new FlowsClient(this);
    this.voice = new VoiceClient(this);
  }

  /**
   * Set authentication tokens
   */
  setTokens(accessToken: string, refreshToken?: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
  }

  /**
   * Clear authentication tokens
   */
  clearTokens(): void {
    this.accessToken = undefined;
    this.refreshToken = undefined;
  }

  /**
   * Get current access token
   */
  getAccessToken(): string | undefined {
    return this.accessToken;
  }

  /**
   * Get current refresh token
   */
  getRefreshToken(): string | undefined {
    return this.refreshToken;
  }

  /**
   * Check if client is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  /**
   * Make an API request
   */
  async request<T>(
    method: string,
    path: string,
    options: {
      body?: unknown;
      headers?: Record<string, string>;
      authenticated?: boolean;
      formData?: FormData;
    } = {}
  ): Promise<T> {
    const { body, headers = {}, authenticated = true, formData } = options;

    const requestHeaders: Record<string, string> = {
      'Accept': 'application/json',
      'User-Agent': 'Ragamuffin-JS-SDK/1.0.0',
      ...headers,
    };

    if (authenticated && this.accessToken) {
      requestHeaders['Authorization'] = `Bearer ${this.accessToken}`;
    }

    if (this.apiKey) {
      requestHeaders['X-API-Key'] = this.apiKey;
    }

    let requestBody: string | FormData | undefined;
    if (formData) {
      requestBody = formData;
    } else if (body) {
      requestHeaders['Content-Type'] = 'application/json';
      requestBody = JSON.stringify(body);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.baseUrl}${path}`, {
        method,
        headers: requestHeaders,
        body: requestBody,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      return await this.handleResponse<T>(response);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new APIError('Request timeout', 408);
      }
      throw error;
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (response.status === 401) {
      throw new AuthenticationError(
        'Authentication required or token expired',
        401
      );
    }

    if (response.status === 403) {
      throw new AuthenticationError('Access forbidden', 403);
    }

    if (response.status === 404) {
      throw new NotFoundError('Resource not found');
    }

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      throw new RateLimitError(
        'Rate limit exceeded',
        retryAfter ? parseInt(retryAfter, 10) : undefined
      );
    }

    if (response.status >= 400) {
      let message = 'Unknown error';
      try {
        const errorData = await response.json();
        message = errorData.detail || JSON.stringify(errorData);
      } catch {
        message = response.statusText || 'Unknown error';
      }
      throw new APIError(message, response.status);
    }

    if (response.status === 204) {
      return {} as T;
    }

    try {
      return await response.json();
    } catch {
      return { text: await response.text() } as T;
    }
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<void> {
    await this.auth.login(email, password);
  }

  /**
   * Register a new account
   */
  async register(name: string, email: string, password: string): Promise<void> {
    await this.auth.register(name, email, password);
  }

  /**
   * Logout and clear tokens
   */
  logout(): void {
    this.auth.logout();
  }

  /**
   * Check API health
   */
  async health(): Promise<{ status: string }> {
    return this.request<{ status: string }>('GET', '/health', {
      authenticated: false,
    });
  }
}
