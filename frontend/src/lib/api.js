/**
 * API client for backend communication
 */
import { authHeaders } from './auth';

const API_BASE = '/api';

export const api = {
  /**
   * Create a new task
   */
  async createTask(taskData) {
    const response = await fetch(`${API_BASE}/decisions/task`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(taskData),
    });

    if (!response.ok) {
      throw new Error('Failed to create task');
    }

    return response.json();
  },

  /**
   * Get task details
   */
  async getTask(taskId) {
    const response = await fetch(`${API_BASE}/decisions/task/${taskId}`, {
      headers: authHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to get task');
    }

    return response.json();
  },

  /**
   * List tasks
   */
  async listTasks(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${API_BASE}/decisions/tasks?${params}`, {
      headers: authHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to list tasks');
    }

    return response.json();
  },

  /**
   * Override a decision
   */
  async overrideDecision(taskId, overrideDecision, reason) {
    const response = await fetch(`${API_BASE}/decisions/override`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        task_id: taskId,
        override_decision: overrideDecision,
        reason,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to override decision');
    }

    return response.json();
  },

  /**
   * Escalate a task
   */
  async escalateTask(taskId, reason) {
    const response = await fetch(`${API_BASE}/decisions/escalate`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        task_id: taskId,
        reason,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to escalate task');
    }

    return response.json();
  },

  /**
   * Get system stats
   */
  async getStats() {
    const response = await fetch(`${API_BASE}/admin/stats`, {
      headers: authHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to get stats');
    }

    return response.json();
  },

  /**
   * List agents
   */
  async listAgents(agentType = null) {
    const params = agentType ? `?agent_type=${agentType}` : '';
    const response = await fetch(`${API_BASE}/admin/agents${params}`, {
      headers: authHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to list agents');
    }

    return response.json();
  },

  /**
   * Create agent
   */
  async createAgent(agentData) {
    const response = await fetch(`${API_BASE}/admin/agents`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(agentData),
    });

    if (!response.ok) {
      throw new Error('Failed to create agent');
    }

    return response.json();
  },

  /**
   * Trigger training
   */
  async triggerTraining(agentType) {
    const response = await fetch(`${API_BASE}/admin/training/trigger`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ agent_type: agentType }),
    });

    if (!response.ok) {
      throw new Error('Failed to trigger training');
    }

    return response.json();
  },
};
