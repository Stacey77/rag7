export interface Interview {
  id: string;
  userId?: string;
  title: string;
  responses: InterviewResponse[];
  status: 'draft' | 'completed';
  createdAt: Date;
  updatedAt: Date;
}

export interface InterviewResponse {
  question: string;
  answer: string;
  category: string;
}

export interface Bottleneck {
  name: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  impact: string;
  frequency: string;
}

export interface Opportunity {
  id: string;
  name: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  effort: 'easy' | 'moderate' | 'difficult';
  priority: number;
}

export interface RoadmapPhase {
  phase: number;
  name: string;
  duration: string;
  items: string[];
  considerations: string[];
}

export interface Analysis {
  id: string;
  interviewId: string;
  bottlenecks: Bottleneck[];
  opportunities: Opportunity[];
  roadmap: RoadmapPhase[];
  createdAt: Date;
}

export interface Vulnerability {
  type: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  line?: number;
  description: string;
  cwe?: string;
  owasp?: string;
  remediation: string;
  codeExample?: string;
}

export interface SecurityScan {
  id: string;
  codeSnippet: string;
  language: string;
  vulnerabilities: Vulnerability[];
  severity: string;
  owaspMappings: Record<string, number>;
  createdAt: Date;
}

export interface ContextTemplate {
  id: string;
  userId?: string;
  name: string;
  description?: string;
  role: string;
  domain: string;
  context: string;
  tone: string;
  constraints: string;
  createdAt: Date;
}

export type ToneStyle = 
  | 'professional'
  | 'casual'
  | 'technical'
  | 'consultative'
  | 'executive';

export interface ContextConfig {
  role: string;
  domain: string;
  context: string;
  tone: ToneStyle;
  constraints: string[];
}
