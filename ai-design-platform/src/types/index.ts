// Core Types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'developer' | 'viewer';
  avatar?: string;
  createdAt: Date;
}

export interface AIModel {
  id: string;
  name: string;
  version: string;
  status: 'active' | 'training' | 'deployed' | 'archived';
  accuracy: number;
  latency: number;
  throughput: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface SystemMetrics {
  cpu: number;
  memory: number;
  gpu: number;
  activeModels: number;
  totalRequests: number;
  avgLatency: number;
}

export interface AnalyticsData {
  timestamp: Date;
  requests: number;
  latency: number;
  accuracy: number;
  throughput: number;
}

export interface TeamMember {
  id: string;
  name: string;
  role: string;
  avatar?: string;
  status: 'online' | 'offline' | 'busy';
  lastActive: Date;
}

export interface IndustryTemplate {
  id: string;
  name: string;
  industry: string;
  description: string;
  models: string[];
  roi: number;
  timeline: string;
  compliance: string[];
  icon: string;
}

export interface Integration {
  id: string;
  name: string;
  category: string;
  description: string;
  icon: string;
  installed: boolean;
  status: 'active' | 'inactive' | 'configuring';
}

export interface SecurityFramework {
  id: string;
  name: string;
  status: 'compliant' | 'in-progress' | 'not-compliant';
  progress: number;
  lastAudit: Date;
  controls: number;
}

export interface AIPersonality {
  id: 'professional' | 'friendly' | 'teacher' | 'mentor';
  name: string;
  description: string;
  traits: string[];
}

export interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  emotion?: string;
  language?: string;
}

export interface VoiceSettings {
  alwaysOn: boolean;
  voiceResponse: boolean;
  personality: AIPersonality['id'];
  language: string;
  speechRate: number;
  pitch: number;
}

export interface ROICalculation {
  currentCost: number;
  aiCost: number;
  monthlySavings: number;
  annualSavings: number;
  productivity: number;
  breakEven: number;
}

export interface Playbook {
  id: string;
  title: string;
  description: string;
  timeline: string;
  steps: PlaybookStep[];
  progress: number;
}

export interface PlaybookStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  resources: string[];
}
