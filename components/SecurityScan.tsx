'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Shield, AlertTriangle, CheckCircle, Download, Loader2 } from 'lucide-react';
import type { Vulnerability } from '@/types';

const languageOptions = [
  'JavaScript',
  'TypeScript',
  'Python',
  'Java',
  'PHP',
  'Ruby',
  'Go',
  'C#',
  'SQL',
  'Bash',
];

export function SecurityScan() {
  const [codeSnippet, setCodeSnippet] = useState('');
  const [language, setLanguage] = useState('JavaScript');
  const [scanning, setScanning] = useState(false);
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [severity, setSeverity] = useState<string>('');
  const [owaspMappings, setOwaspMappings] = useState<Record<string, number>>({});

  const handleScan = async () => {
    if (!codeSnippet.trim()) {
      alert('Please enter code to scan');
      return;
    }

    setScanning(true);
    try {
      // TODO: Call API to scan code with Gemini
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Mock vulnerabilities
      const mockVulnerabilities: Vulnerability[] = [
        {
          type: 'SQL Injection',
          severity: 'high',
          line: 5,
          description:
            'User input is directly concatenated into SQL query without sanitization',
          cwe: 'CWE-89',
          owasp: 'A03:2021',
          remediation: 'Use parameterized queries or prepared statements',
          codeExample: `// Instead of:
const query = "SELECT * FROM users WHERE id = " + userId;

// Use:
const query = "SELECT * FROM users WHERE id = ?";
db.query(query, [userId]);`,
        },
        {
          type: 'Hardcoded Secret',
          severity: 'critical',
          line: 2,
          description: 'API key is hardcoded in the source code',
          cwe: 'CWE-798',
          owasp: 'A07:2021',
          remediation: 'Store secrets in environment variables or a secrets manager',
          codeExample: `// Instead of:
const apiKey = "sk-1234567890abcdef";

// Use:
const apiKey = process.env.API_KEY;`,
        },
      ];

      setVulnerabilities(mockVulnerabilities);
      setSeverity('critical');
      setOwaspMappings({
        'A03:2021': 1,
        'A07:2021': 1,
      });
    } catch (error) {
      alert('Failed to scan code');
    } finally {
      setScanning(false);
    }
  };

  const getSeverityColor = (sev: string) => {
    switch (sev.toLowerCase()) {
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

  const getSeverityIcon = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-4 w-4" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4" />;
      case 'low':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <CheckCircle className="h-4 w-4" />;
    }
  };

  return (
    <div className="container mx-auto max-w-6xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security Scan</h1>
          <p className="text-muted-foreground">
            AI-powered vulnerability detection for your code and configurations
          </p>
        </div>
        {vulnerabilities.length > 0 && (
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        )}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Input Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Code Input</CardTitle>
              <CardDescription>
                Paste your code snippet or configuration file
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="language">Programming Language</Label>
                <div className="flex flex-wrap gap-2">
                  {languageOptions.map((lang) => (
                    <Badge
                      key={lang}
                      variant={language === lang ? 'default' : 'outline'}
                      className="cursor-pointer"
                      onClick={() => setLanguage(lang)}
                    >
                      {lang}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="code">Code Snippet</Label>
                <Textarea
                  id="code"
                  placeholder={`// Enter your ${language} code here...
const apiKey = "sk-1234567890";
const userId = req.query.id;
const query = "SELECT * FROM users WHERE id = " + userId;
db.query(query);`}
                  value={codeSnippet}
                  onChange={(e) => setCodeSnippet(e.target.value)}
                  className="font-mono text-sm min-h-[300px]"
                />
              </div>

              <Button onClick={handleScan} disabled={scanning} className="w-full">
                {scanning ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Scanning...
                  </>
                ) : (
                  <>
                    <Shield className="mr-2 h-4 w-4" />
                    Run Security Scan
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Scan Summary */}
          {vulnerabilities.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Scan Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 grid-cols-2">
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Overall Severity</p>
                    <Badge variant={getSeverityColor(severity)} className="text-lg">
                      {severity.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="space-y-1">
                    <p className="text-sm text-muted-foreground">Vulnerabilities Found</p>
                    <p className="text-2xl font-bold">{vulnerabilities.length}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-sm font-medium">OWASP Top 10 Mapping</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(owaspMappings).map(([owasp, count]) => (
                      <Badge key={owasp} variant="outline">
                        {owasp} ({count})
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Results Panel */}
        <div className="space-y-6">
          {vulnerabilities.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-center">
                <Shield className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No Scan Results</h3>
                <p className="text-muted-foreground">
                  Enter your code and click "Run Security Scan" to detect vulnerabilities
                </p>
              </CardContent>
            </Card>
          ) : (
            <Tabs defaultValue="vulnerabilities" className="space-y-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="vulnerabilities">Vulnerabilities</TabsTrigger>
                <TabsTrigger value="remediation">Remediation</TabsTrigger>
              </TabsList>

              <TabsContent value="vulnerabilities" className="space-y-4">
                {vulnerabilities.map((vuln, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="text-lg flex items-center gap-2">
                            {getSeverityIcon(vuln.severity)}
                            {vuln.type}
                          </CardTitle>
                          <CardDescription>{vuln.description}</CardDescription>
                        </div>
                        <Badge variant={getSeverityColor(vuln.severity)}>
                          {vuln.severity.toUpperCase()}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div className="grid gap-2 text-sm">
                        {vuln.line && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Line:</span>
                            <span className="font-mono">{vuln.line}</span>
                          </div>
                        )}
                        {vuln.cwe && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">CWE:</span>
                            <Badge variant="outline">{vuln.cwe}</Badge>
                          </div>
                        )}
                        {vuln.owasp && (
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">OWASP:</span>
                            <Badge variant="outline">{vuln.owasp}</Badge>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>

              <TabsContent value="remediation" className="space-y-4">
                {vulnerabilities.map((vuln, index) => (
                  <Card key={index}>
                    <CardHeader>
                      <CardTitle className="text-lg">{vuln.type}</CardTitle>
                      <CardDescription>How to fix this vulnerability</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium mb-2">Remediation Steps:</h4>
                        <p className="text-sm text-muted-foreground">{vuln.remediation}</p>
                      </div>
                      {vuln.codeExample && (
                        <div>
                          <h4 className="text-sm font-medium mb-2">Code Example:</h4>
                          <pre className="bg-muted p-3 rounded-lg text-xs font-mono overflow-x-auto">
                            {vuln.codeExample}
                          </pre>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>
            </Tabs>
          )}
        </div>
      </div>
    </div>
  );
}
