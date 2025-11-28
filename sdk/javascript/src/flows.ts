/**
 * Flows client for Ragamuffin SDK
 */

import type { RagamuffinClient } from './client';
import type { Flow, FlowRunResponse } from './types';

export interface FlowRunOptions {
  tweaks?: Record<string, unknown>;
}

export class FlowsClient {
  private client: RagamuffinClient;

  constructor(client: RagamuffinClient) {
    this.client = client;
  }

  /**
   * List all saved flows
   */
  async list(): Promise<{ flows: string[] }> {
    return this.client.request<{ flows: string[] }>('GET', '/list_flows/');
  }

  /**
   * Get a flow by name
   */
  async get(name: string): Promise<Flow> {
    return this.client.request<Flow>('GET', `/get_flow/${name}`);
  }

  /**
   * Save a flow
   */
  async save(
    name: string,
    content: Record<string, unknown> | string
  ): Promise<{ message: string }> {
    const flowContent = typeof content === 'string' 
      ? content 
      : JSON.stringify(content);
    
    const blob = new Blob([flowContent], { type: 'application/json' });
    const formData = new FormData();
    formData.append('flow_file', blob, `${name}.json`);

    return this.client.request<{ message: string }>('POST', '/save_flow/', {
      formData,
    });
  }

  /**
   * Run a flow
   */
  async run(
    flow: string | Record<string, unknown>,
    userInput: string,
    options: FlowRunOptions = {}
  ): Promise<FlowRunResponse> {
    const formData = new FormData();
    formData.append('user_input', userInput);
    
    if (options.tweaks) {
      formData.append('tweaks', JSON.stringify(options.tweaks));
    }

    if (typeof flow === 'string') {
      // Flow name
      formData.append('flow_name', flow);
    } else {
      // Flow content as object
      const blob = new Blob([JSON.stringify(flow)], { type: 'application/json' });
      formData.append('flow_file', blob, 'flow.json');
    }

    return this.client.request<FlowRunResponse>('POST', '/run_flow/', {
      formData,
    });
  }

  /**
   * Delete a flow
   */
  async delete(name: string): Promise<{ message: string }> {
    return this.client.request<{ message: string }>('DELETE', `/delete_flow/${name}`);
  }
}
