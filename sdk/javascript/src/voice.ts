/**
 * Voice/Retell client for Ragamuffin SDK
 */

import type { RagamuffinClient } from './client';
import type {
  RetellStatus,
  RetellAgent,
  WebCallResponse,
  Call,
} from './types';

export interface WebCallOptions {
  metadata?: Record<string, unknown>;
  dynamicVariables?: Record<string, string>;
}

export interface PhoneCallOptions {
  fromPhone?: string;
  metadata?: Record<string, unknown>;
}

export class VoiceClient {
  private client: RagamuffinClient;

  constructor(client: RagamuffinClient) {
    this.client = client;
  }

  /**
   * Check Retell.ai configuration status
   */
  async status(): Promise<RetellStatus> {
    return this.client.request<RetellStatus>('GET', '/retell/status');
  }

  /**
   * List all Retell agents
   */
  async agents(): Promise<{ agents: RetellAgent[] }> {
    return this.client.request<{ agents: RetellAgent[] }>('GET', '/retell/agents');
  }

  /**
   * Get a specific agent
   */
  async getAgent(agentId: string): Promise<RetellAgent> {
    return this.client.request<RetellAgent>('GET', `/retell/agents/${agentId}`);
  }

  /**
   * Create a web call
   */
  async createWebCall(
    agentId: string,
    options: WebCallOptions = {}
  ): Promise<WebCallResponse> {
    return this.client.request<WebCallResponse>('POST', '/retell/web-call', {
      body: {
        agent_id: agentId,
        metadata: options.metadata,
        dynamic_variables: options.dynamicVariables,
      },
    });
  }

  /**
   * Create a phone call
   */
  async createPhoneCall(
    agentId: string,
    toPhone: string,
    options: PhoneCallOptions = {}
  ): Promise<Call> {
    return this.client.request<Call>('POST', '/retell/phone-call', {
      body: {
        agent_id: agentId,
        to_phone: toPhone,
        from_phone: options.fromPhone,
        metadata: options.metadata,
      },
    });
  }

  /**
   * List call history
   */
  async calls(options: { limit?: number; offset?: number } = {}): Promise<{ calls: Call[] }> {
    const params = new URLSearchParams();
    if (options.limit) params.append('limit', String(options.limit));
    if (options.offset) params.append('offset', String(options.offset));
    
    const query = params.toString();
    const path = query ? `/retell/calls?${query}` : '/retell/calls';
    
    return this.client.request<{ calls: Call[] }>('GET', path);
  }

  /**
   * Get a specific call
   */
  async getCall(callId: string): Promise<Call> {
    return this.client.request<Call>('GET', `/retell/calls/${callId}`);
  }

  /**
   * End a call
   */
  async endCall(callId: string): Promise<{ message: string }> {
    return this.client.request<{ message: string }>('POST', `/retell/end-call/${callId}`);
  }

  /**
   * List available voices
   */
  async voices(): Promise<{ voices: { voice_id: string; voice_name: string }[] }> {
    return this.client.request<{ voices: { voice_id: string; voice_name: string }[] }>(
      'GET',
      '/retell/voices'
    );
  }
}
