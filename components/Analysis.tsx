'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertTriangle, TrendingUp, Download, Loader2 } from 'lucide-react';
import type { Bottleneck, Opportunity, RoadmapPhase } from '@/types';

export function Analysis() {
  const [loading, setLoading] = useState(false);
  const [bottlenecks, setBottlenecks] = useState<Bottleneck[]>([]);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [roadmap, setRoadmap] = useState<RoadmapPhase[]>([]);

  // Mock data for demonstration
  const mockBottlenecks: Bottleneck[] = [
    {
      name: 'Manual Data Entry',
      description: 'Team spends 10+ hours weekly manually copying data between CRM and accounting software',
      severity: 'high',
      impact: 'High productivity loss and error-prone',
      frequency: 'Daily',
    },
    {
      name: 'Approval Delays',
      description: 'Purchase approvals take 3-5 days due to email-based workflow',
      severity: 'medium',
      impact: 'Delayed procurement and vendor relationships',
      frequency: 'Weekly',
    },
    {
      name: 'Report Generation',
      description: 'Monthly reports require 2 days of manual data compilation',
      severity: 'medium',
      impact: 'Time-consuming and delays decision-making',
      frequency: 'Monthly',
    },
  ];

  const mockOpportunities: Opportunity[] = [
    {
      id: '1',
      name: 'CRM-Accounting Integration',
      description: 'Automated data sync between systems',
      impact: 'high',
      effort: 'moderate',
      priority: 1,
    },
    {
      id: '2',
      name: 'Automated Approval Workflow',
      description: 'Digital approval system with notifications',
      impact: 'high',
      effort: 'easy',
      priority: 2,
    },
    {
      id: '3',
      name: 'Automated Reporting Dashboard',
      description: 'Real-time dashboard with automated report generation',
      impact: 'medium',
      effort: 'moderate',
      priority: 3,
    },
  ];

  const mockRoadmap: RoadmapPhase[] = [
    {
      phase: 1,
      name: 'Quick Wins',
      duration: '2-4 weeks',
      items: [
        'Implement automated approval workflow',
        'Set up basic email notifications',
        'Create approval tracking dashboard',
      ],
      considerations: [
        'Start with non-critical approvals for testing',
        'Train team on new approval process',
        'Monitor adoption and gather feedback',
      ],
    },
    {
      phase: 2,
      name: 'Core Integration',
      duration: '6-8 weeks',
      items: [
        'Design CRM-Accounting data mapping',
        'Implement bi-directional sync',
        'Set up error handling and logging',
      ],
      considerations: [
        'Ensure data integrity during migration',
        'Plan for downtime windows',
        'Create rollback procedures',
      ],
    },
    {
      phase: 3,
      name: 'Analytics & Optimization',
      duration: '4-6 weeks',
      items: [
        'Build automated reporting dashboard',
        'Implement KPI tracking',
        'Set up automated alerts',
      ],
      considerations: [
        'Define key metrics with stakeholders',
        'Ensure data accuracy and validation',
        'Plan for ongoing maintenance',
      ],
    },
  ];

  const handleLoadAnalysis = () => {
    setLoading(true);
    // Simulate loading
    setTimeout(() => {
      setBottlenecks(mockBottlenecks);
      setOpportunities(mockOpportunities);
      setRoadmap(mockRoadmap);
      setLoading(false);
    }, 1500);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'destructive';
      case 'high':
        return 'destructive';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high':
        return 'default';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'outline';
      default:
        return 'outline';
    }
  };

  if (bottlenecks.length === 0) {
    return (
      <div className="container mx-auto max-w-6xl p-6">
        <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
          <AlertTriangle className="h-16 w-16 text-muted-foreground" />
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-bold">No Analysis Available</h2>
            <p className="text-muted-foreground">
              Complete an interview first to generate workflow analysis
            </p>
          </div>
          <div className="flex gap-4">
            <Button onClick={handleLoadAnalysis} disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Load Sample Analysis
            </Button>
            <Button variant="outline" asChild>
              <a href="/interview">Start New Interview</a>
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-6xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Analysis</h1>
          <p className="text-muted-foreground">
            AI-powered insights into your workflow bottlenecks and opportunities
          </p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="bottlenecks" className="space-y-6">
        <TabsList>
          <TabsTrigger value="bottlenecks">Bottlenecks</TabsTrigger>
          <TabsTrigger value="opportunities">Opportunities</TabsTrigger>
          <TabsTrigger value="roadmap">Implementation Roadmap</TabsTrigger>
        </TabsList>

        {/* Bottlenecks Tab */}
        <TabsContent value="bottlenecks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Identified Workflow Bottlenecks</CardTitle>
              <CardDescription>
                Key pain points discovered in your current processes
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {bottlenecks.map((bottleneck, index) => (
                <Card key={index}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">{bottleneck.name}</CardTitle>
                        <CardDescription>{bottleneck.description}</CardDescription>
                      </div>
                      <Badge variant={getSeverityColor(bottleneck.severity)}>
                        {bottleneck.severity.toUpperCase()}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Impact:</span>
                        <span className="font-medium">{bottleneck.impact}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Frequency:</span>
                        <span className="font-medium">{bottleneck.frequency}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Opportunities Tab */}
        <TabsContent value="opportunities" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Automation Opportunities</CardTitle>
              <CardDescription>
                Potential AI agent implementations prioritized by impact and effort
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {opportunities.map((opportunity) => (
                  <Card key={opportunity.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="text-lg">{opportunity.name}</CardTitle>
                          <CardDescription>{opportunity.description}</CardDescription>
                        </div>
                        <span className="text-2xl font-bold text-muted-foreground">
                          #{opportunity.priority}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex gap-2">
                        <Badge variant={getImpactColor(opportunity.impact)}>
                          {opportunity.impact.toUpperCase()} Impact
                        </Badge>
                        <Badge variant="outline">
                          {opportunity.effort.toUpperCase()} Effort
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Priority Matrix */}
          <Card>
            <CardHeader>
              <CardTitle>Impact vs Effort Matrix</CardTitle>
              <CardDescription>
                Visual prioritization of automation opportunities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 min-h-[300px]">
                {/* High Impact */}
                <div className="col-span-3 grid grid-cols-3 gap-4">
                  <div className="border-2 border-green-500/20 bg-green-500/5 p-4 rounded-lg">
                    <p className="text-xs font-medium mb-2">High Impact / Easy</p>
                    <div className="space-y-2">
                      {opportunities
                        .filter((o) => o.impact === 'high' && o.effort === 'easy')
                        .map((o) => (
                          <div key={o.id} className="text-xs bg-background p-2 rounded border">
                            {o.name}
                          </div>
                        ))}
                    </div>
                  </div>
                  <div className="border-2 border-yellow-500/20 bg-yellow-500/5 p-4 rounded-lg">
                    <p className="text-xs font-medium mb-2">High Impact / Moderate</p>
                    <div className="space-y-2">
                      {opportunities
                        .filter((o) => o.impact === 'high' && o.effort === 'moderate')
                        .map((o) => (
                          <div key={o.id} className="text-xs bg-background p-2 rounded border">
                            {o.name}
                          </div>
                        ))}
                    </div>
                  </div>
                  <div className="border-2 border-red-500/20 bg-red-500/5 p-4 rounded-lg">
                    <p className="text-xs font-medium mb-2">High Impact / Difficult</p>
                    <div className="space-y-2">
                      {opportunities
                        .filter((o) => o.impact === 'high' && o.effort === 'difficult')
                        .map((o) => (
                          <div key={o.id} className="text-xs bg-background p-2 rounded border">
                            {o.name}
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Roadmap Tab */}
        <TabsContent value="roadmap" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Implementation Roadmap</CardTitle>
              <CardDescription>
                Phased approach to implementing automation opportunities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {roadmap.map((phase) => (
                <Card key={phase.phase}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <CardTitle className="text-lg">
                          Phase {phase.phase}: {phase.name}
                        </CardTitle>
                        <CardDescription>Duration: {phase.duration}</CardDescription>
                      </div>
                      <Badge>{phase.duration}</Badge>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="text-sm font-medium mb-2">Implementation Items:</h4>
                      <ul className="space-y-1">
                        {phase.items.map((item, i) => (
                          <li key={i} className="text-sm text-muted-foreground flex items-start">
                            <TrendingUp className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium mb-2">Key Considerations:</h4>
                      <ul className="space-y-1">
                        {phase.considerations.map((consideration, i) => (
                          <li key={i} className="text-sm text-muted-foreground flex items-start">
                            <AlertTriangle className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                            {consideration}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
