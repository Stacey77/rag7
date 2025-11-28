/**
 * RAG client for Ragamuffin SDK
 */

import type { RagamuffinClient } from './client';
import type {
  EmbedResponse,
  SearchResponse,
  QueryResponse,
  Collection,
} from './types';

export interface EmbedOptions {
  collection?: string;
  metadata?: Record<string, unknown>[];
}

export interface SearchOptions {
  topK?: number;
  collection?: string;
  filter?: string;
}

export interface QueryOptions {
  topK?: number;
  collection?: string;
  useHybrid?: boolean;
}

export class RAGClient {
  private client: RagamuffinClient;

  constructor(client: RagamuffinClient) {
    this.client = client;
  }

  /**
   * Embed text documents into vector database
   */
  async embed(
    texts: string[],
    options: EmbedOptions = {}
  ): Promise<EmbedResponse> {
    return this.client.request<EmbedResponse>('POST', '/rag/embed', {
      body: {
        texts,
        collection_name: options.collection || 'text_embeddings',
        metadata: options.metadata,
      },
    });
  }

  /**
   * Embed an image into vector database
   */
  async embedImage(
    file: File | Blob,
    options: { collection?: string; metadata?: Record<string, unknown> } = {}
  ): Promise<EmbedResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('collection_name', options.collection || 'image_embeddings');
    if (options.metadata) {
      formData.append('metadata', JSON.stringify(options.metadata));
    }

    return this.client.request<EmbedResponse>('POST', '/rag/embed_image', {
      formData,
    });
  }

  /**
   * Search for similar documents
   */
  async search(
    query: string,
    options: SearchOptions = {}
  ): Promise<SearchResponse> {
    return this.client.request<SearchResponse>('POST', '/rag/search', {
      body: {
        text: query,
        top_k: options.topK || 5,
        collection_name: options.collection,
        filter: options.filter,
      },
    });
  }

  /**
   * Perform RAG query with context retrieval
   */
  async query(
    query: string,
    options: QueryOptions = {}
  ): Promise<QueryResponse> {
    return this.client.request<QueryResponse>('POST', '/rag/query', {
      body: {
        query,
        top_k: options.topK || 5,
        collection_name: options.collection,
        use_hybrid: options.useHybrid ?? true,
      },
    });
  }

  /**
   * List all collections
   */
  async collections(): Promise<{ collections: Collection[] }> {
    return this.client.request<{ collections: Collection[] }>('GET', '/rag/collections');
  }

  /**
   * Create a new collection
   */
  async createCollection(
    name: string,
    options: { dimension?: number; description?: string } = {}
  ): Promise<Collection> {
    return this.client.request<Collection>('POST', '/rag/collections', {
      body: {
        name,
        dimension: options.dimension || 384,
        description: options.description,
      },
    });
  }

  /**
   * Delete a collection
   */
  async deleteCollection(name: string): Promise<{ message: string }> {
    return this.client.request<{ message: string }>('DELETE', `/rag/collections/${name}`);
  }

  /**
   * Get collection statistics
   */
  async collectionStats(name: string): Promise<Collection> {
    return this.client.request<Collection>('GET', `/rag/collections/${name}/stats`);
  }
}
