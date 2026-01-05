import { GoogleGenerativeAI } from '@google/generative-ai';
import type { ContextConfig, Bottleneck, Opportunity, RoadmapPhase, Vulnerability } from '@/types';

export class GeminiService {
  private ai: GoogleGenerativeAI;
  private model: any;

  constructor(apiKey: string) {
    this.ai = new GoogleGenerativeAI(apiKey);
    this.model = this.ai.getGenerativeModel({ model: 'gemini-pro' });
  }

  async analyzeWorkflow(interviewData: any): Promise<{
    bottlenecks: Bottleneck[];
    opportunities: Opportunity[];
  }> {
    const prompt = `You are a workflow automation expert. Analyze the following interview responses and identify:
1. Top 3-5 workflow bottlenecks with severity levels (critical, high, medium, low)
2. Automation opportunities with impact (high, medium, low) and effort (easy, moderate, difficult)

Interview Data:
${JSON.stringify(interviewData, null, 2)}

Return your analysis in valid JSON format with this structure:
{
  "bottlenecks": [
    {
      "name": "string",
      "description": "string",
      "severity": "critical|high|medium|low",
      "impact": "string",
      "frequency": "string"
    }
  ],
  "opportunities": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "impact": "high|medium|low",
      "effort": "easy|moderate|difficult",
      "priority": number
    }
  ]
}`;

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      // Extract JSON from response
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      
      throw new Error('Failed to parse AI response');
    } catch (error) {
      console.error('Error analyzing workflow:', error);
      throw error;
    }
  }

  async generateRoadmap(opportunities: Opportunity[]): Promise<RoadmapPhase[]> {
    const prompt = `You are a project planning expert. Based on these automation opportunities, create a phased implementation roadmap with realistic timelines.

Opportunities:
${JSON.stringify(opportunities, null, 2)}

Return a JSON array of implementation phases with this structure:
[
  {
    "phase": 1,
    "name": "Phase Name",
    "duration": "2-4 weeks",
    "items": ["item1", "item2"],
    "considerations": ["consideration1", "consideration2"]
  }
]`;

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      const jsonMatch = text.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      
      throw new Error('Failed to parse AI response');
    } catch (error) {
      console.error('Error generating roadmap:', error);
      throw error;
    }
  }

  async scanForVulnerabilities(code: string, language: string): Promise<{
    vulnerabilities: Vulnerability[];
    severity: string;
    owaspMappings: Record<string, number>;
  }> {
    const prompt = `You are a security expert. Analyze this ${language} code for common vulnerabilities including:
- SQL Injection
- Cross-Site Scripting (XSS)
- Hardcoded secrets (API keys, passwords, tokens)
- Path traversal
- Command injection
- Insecure deserialization
- CSRF vulnerabilities

Code:
\`\`\`${language}
${code}
\`\`\`

Return your analysis in valid JSON format:
{
  "vulnerabilities": [
    {
      "type": "string",
      "severity": "critical|high|medium|low",
      "line": number,
      "description": "string",
      "cwe": "CWE-XXX",
      "owasp": "A01:2021",
      "remediation": "string",
      "codeExample": "string"
    }
  ],
  "severity": "critical|high|medium|low",
  "owaspMappings": {
    "A01:2021": 1,
    "A03:2021": 2
  }
}`;

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      
      throw new Error('Failed to parse AI response');
    } catch (error) {
      console.error('Error scanning for vulnerabilities:', error);
      throw error;
    }
  }

  async engineerContext(config: ContextConfig): Promise<string> {
    const prompt = `You are an AI prompt engineering expert. Create an optimized system prompt for an AI agent with these specifications:

Role: ${config.role}
Domain: ${config.domain}
Context: ${config.context}
Tone: ${config.tone}
Behavioral Constraints:
${config.constraints.map((c, i) => `${i + 1}. ${c}`).join('\n')}

Generate a comprehensive system prompt that will make the AI agent perform optimally for this use case.`;

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Error engineering context:', error);
      throw error;
    }
  }
}
