'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Brain, Copy, Save, Sparkles } from 'lucide-react';
import type { ToneStyle } from '@/types';

const toneStyles: { value: ToneStyle; label: string; description: string }[] = [
  {
    value: 'professional',
    label: 'Professional',
    description: 'Formal, courteous, and business-oriented',
  },
  {
    value: 'casual',
    label: 'Casual',
    description: 'Friendly, approachable, and conversational',
  },
  {
    value: 'technical',
    label: 'Technical',
    description: 'Precise, detailed, and technical',
  },
  {
    value: 'consultative',
    label: 'Consultative',
    description: 'Advisory, strategic, and insightful',
  },
  {
    value: 'executive',
    label: 'Executive Summary',
    description: 'Concise, high-level, and strategic',
  },
];

const constraintExamples = [
  'Flag any task requiring >3 manual handoffs',
  'Identify manual data entry between systems',
  'Highlight workflows with >2 hour wait times',
  'Flag manual copy-paste operations',
  'Detect error-prone manual corrections',
  'Identify approval delays >24 hours',
  'Highlight repetitive tasks done >5 times daily',
  'Flag processes without error tracking',
  'Identify tasks taking >30 minutes daily',
  'Detect missing automation opportunities',
];

export function ContextStudio() {
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [domain, setDomain] = useState('');
  const [context, setContext] = useState('');
  const [tone, setTone] = useState<ToneStyle>('professional');
  const [constraints, setConstraints] = useState<string[]>([]);
  const [customConstraint, setCustomConstraint] = useState('');
  const [generatedPrompt, setGeneratedPrompt] = useState('');
  const [generating, setGenerating] = useState(false);

  const handleAddConstraint = (constraint: string) => {
    if (constraint && !constraints.includes(constraint)) {
      setConstraints([...constraints, constraint]);
    }
    setCustomConstraint('');
  };

  const handleRemoveConstraint = (index: number) => {
    setConstraints(constraints.filter((_, i) => i !== index));
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      // TODO: Call API to generate prompt with Gemini
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      const prompt = `You are ${role}, an expert in ${domain}.

${context}

Communication Style: ${tone}

Behavioral Guidelines:
${constraints.map((c, i) => `${i + 1}. ${c}`).join('\n')}

Your responses should be ${toneStyles.find((t) => t.value === tone)?.description}.

Always maintain focus on identifying automation opportunities and providing actionable insights.`;

      setGeneratedPrompt(prompt);
    } catch (error) {
      alert('Failed to generate prompt');
    } finally {
      setGenerating(false);
    }
  };

  const handleCopyPrompt = () => {
    navigator.clipboard.writeText(generatedPrompt);
    alert('Prompt copied to clipboard!');
  };

  const handleSaveTemplate = async () => {
    // TODO: Implement API call to save template
    alert('Template saved successfully!');
  };

  return (
    <div className="container mx-auto max-w-6xl p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Context Engineering Studio</h1>
        <p className="text-muted-foreground">
          Design and optimize AI agent prompts for workflow analysis
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Configuration Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Agent Configuration</CardTitle>
              <CardDescription>Define the AI agent's role and expertise</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Template Name</Label>
                <Input
                  id="name"
                  placeholder="e.g., Sales Workflow Analyzer"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Agent Role</Label>
                <Input
                  id="role"
                  placeholder="e.g., Workflow Automation Consultant"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="domain">Domain Expertise</Label>
                <Input
                  id="domain"
                  placeholder="e.g., Sales Operations, Customer Service"
                  value={domain}
                  onChange={(e) => setDomain(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="context">System Context</Label>
                <Textarea
                  id="context"
                  placeholder="Describe the agent's purpose, knowledge base, and objectives..."
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  className="min-h-[120px]"
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Output Tone & Style</CardTitle>
              <CardDescription>Select the communication style</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-2">
                {toneStyles.map((style) => (
                  <button
                    key={style.value}
                    onClick={() => setTone(style.value)}
                    className={`text-left p-3 rounded-lg border transition-colors ${
                      tone === style.value
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:bg-accent'
                    }`}
                  >
                    <div className="font-medium">{style.label}</div>
                    <div className="text-sm text-muted-foreground">{style.description}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Behavioral Constraints</CardTitle>
              <CardDescription>Define specific behaviors and patterns to detect</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Quick Add Examples</Label>
                <div className="flex flex-wrap gap-2">
                  {constraintExamples.slice(0, 6).map((example, i) => (
                    <Badge
                      key={i}
                      variant="outline"
                      className="cursor-pointer hover:bg-accent"
                      onClick={() => handleAddConstraint(example)}
                    >
                      + {example}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="custom-constraint">Custom Constraint</Label>
                <div className="flex gap-2">
                  <Input
                    id="custom-constraint"
                    placeholder="Enter a custom constraint..."
                    value={customConstraint}
                    onChange={(e) => setCustomConstraint(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleAddConstraint(customConstraint);
                      }
                    }}
                  />
                  <Button onClick={() => handleAddConstraint(customConstraint)}>Add</Button>
                </div>
              </div>

              {constraints.length > 0 && (
                <div className="space-y-2">
                  <Label>Active Constraints</Label>
                  <div className="space-y-1">
                    {constraints.map((constraint, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between p-2 bg-accent rounded-lg"
                      >
                        <span className="text-sm">{constraint}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveConstraint(i)}
                        >
                          Remove
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <div className="flex gap-2">
            <Button onClick={handleGenerate} disabled={generating} className="flex-1">
              {generating ? (
                <>
                  <Sparkles className="mr-2 h-4 w-4 animate-pulse" />
                  Generating...
                </>
              ) : (
                <>
                  <Brain className="mr-2 h-4 w-4" />
                  Generate Prompt
                </>
              )}
            </Button>
            <Button variant="outline" onClick={handleSaveTemplate}>
              <Save className="mr-2 h-4 w-4" />
              Save Template
            </Button>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="space-y-6">
          <Card className="lg:sticky lg:top-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Generated Prompt</CardTitle>
                {generatedPrompt && (
                  <Button variant="outline" size="sm" onClick={handleCopyPrompt}>
                    <Copy className="mr-2 h-4 w-4" />
                    Copy
                  </Button>
                )}
              </div>
              <CardDescription>Optimized system prompt for your AI agent</CardDescription>
            </CardHeader>
            <CardContent>
              {generatedPrompt ? (
                <div className="space-y-4">
                  <div className="bg-muted p-4 rounded-lg font-mono text-sm whitespace-pre-wrap">
                    {generatedPrompt}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    This prompt can be used to configure your AI agent for optimal workflow analysis
                    and automation opportunity detection.
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Brain className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">
                    Fill in the configuration and click "Generate Prompt" to create your optimized
                    AI agent prompt.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
