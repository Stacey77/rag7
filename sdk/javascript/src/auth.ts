/**
 * Authentication client for Ragamuffin SDK
 */

import type { RagamuffinClient } from './client';
import type { User, TokenResponse } from './types';

export class AuthClient {
  private client: RagamuffinClient;

  constructor(client: RagamuffinClient) {
    this.client = client;
  }

  /**
   * Login with email and password
   */
  async login(email: string, password: string): Promise<TokenResponse> {
    const response = await this.client.request<TokenResponse>('POST', '/auth/login', {
      body: { email, password },
      authenticated: false,
    });

    if (response.access_token) {
      this.client.setTokens(response.access_token, response.refresh_token);
    }

    return response;
  }

  /**
   * Register a new user account
   */
  async register(name: string, email: string, password: string): Promise<{ message: string }> {
    return this.client.request<{ message: string }>('POST', '/auth/register', {
      body: { name, email, password },
      authenticated: false,
    });
  }

  /**
   * Logout and clear tokens
   */
  logout(): void {
    this.client.clearTokens();
  }

  /**
   * Refresh the access token
   */
  async refresh(): Promise<TokenResponse> {
    const refreshToken = this.client.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.client.request<TokenResponse>('POST', '/auth/refresh', {
      body: { refresh_token: refreshToken },
      authenticated: false,
    });

    if (response.access_token) {
      this.client.setTokens(response.access_token, response.refresh_token);
    }

    return response;
  }

  /**
   * Get current user information
   */
  async me(): Promise<User> {
    return this.client.request<User>('GET', '/auth/me');
  }

  /**
   * Update user profile
   */
  async updateProfile(data: { name?: string; email?: string }): Promise<User> {
    return this.client.request<User>('PATCH', '/auth/me', {
      body: data,
    });
  }

  /**
   * Change password
   */
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> {
    return this.client.request<{ message: string }>('POST', '/auth/change-password', {
      body: {
        current_password: currentPassword,
        new_password: newPassword,
      },
    });
  }

  /**
   * Check if client is authenticated
   */
  get isAuthenticated(): boolean {
    return this.client.isAuthenticated();
  }
}
