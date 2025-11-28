/**
 * TypeScript type definitions for Ragamuffin SDK
 */

// Auth types
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
}

// RAG types
export interface EmbedRequest {
  texts: string[];
  collection?: string;
  metadata?: Record<string, unknown>[];
}

export interface EmbedResponse {
  ids: string[];
  collection: string;
  count: number;
}

export interface SearchRequest {
  query: string;
  topK?: number;
  collection?: string;
  filter?: string;
}

export interface SearchResult {
  id: string;
  text: string;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
  collection: string;
}

export interface QueryRequest {
  query: string;
  topK?: number;
  collection?: string;
  useHybrid?: boolean;
}

export interface QueryResponse {
  answer: string;
  context: SearchResult[];
  query: string;
}

export interface Collection {
  name: string;
  count: number;
  dimension: number;
  description?: string;
}

// Flow types
export interface Flow {
  name: string;
  content: Record<string, unknown>;
  created_at?: string;
  updated_at?: string;
}

export interface FlowRunRequest {
  flow: string | Record<string, unknown>;
  userInput: string;
  tweaks?: Record<string, unknown>;
}

export interface FlowRunResponse {
  result: unknown;
  execution_time?: number;
}

// Voice types
export interface RetellStatus {
  configured: boolean;
  api_key_set: boolean;
}

export interface RetellAgent {
  agent_id: string;
  agent_name: string;
  voice_id: string;
  llm_websocket_url?: string;
}

export interface WebCallRequest {
  agentId: string;
  metadata?: Record<string, unknown>;
  dynamicVariables?: Record<string, string>;
}

export interface WebCallResponse {
  call_id: string;
  access_token: string;
  agent_id: string;
}

export interface PhoneCallRequest {
  agentId: string;
  toPhone: string;
  fromPhone?: string;
  metadata?: Record<string, unknown>;
}

export interface Call {
  call_id: string;
  agent_id: string;
  call_type: 'web_call' | 'phone_call';
  call_status: string;
  start_timestamp?: number;
  end_timestamp?: number;
  transcript?: string;
  metadata?: Record<string, unknown>;
}

// Client options
export interface RagamuffinClientOptions {
  baseUrl?: string;
  timeout?: number;
  apiKey?: string;
}

// API response wrapper
export interface ApiResponse<T> {
  data: T;
  status: number;
}
