import React, { useState } from 'react';
import { 
  BookOpen, 
  Clock, 
  CheckCircle, 
  Circle, 
  Rocket, 
  Building2, 
  Cloud, 
  Database, 
  Shield, 
  Users,
  Download,
  Play,
  ChevronRight,
  Award
} from 'lucide-react';
import type { Playbook } from '../../types';

export const ImplementationPlaybooks: React.FC = () => {
  const [selectedPlaybook, setSelectedPlaybook] = useState<string | null>('quick-start');

  const playbooks: Playbook[] = [
    {
      id: 'quick-start',
      title: 'Quick Start',
      description: 'Get up and running with AI platform in 30 days',
      timeline: '0-30 days',
      progress: 65,
      steps: [
        {
          id: '1',
          title: 'Environment Setup',
          description: 'Configure cloud infrastructure and development environment',
          completed: true,
          resources: ['AWS Setup Guide', 'Azure Quick Start', 'GCP Configuration']
        },
        {
          id: '2',
          title: 'User Onboarding',
          description: 'Create user accounts and assign roles',
          completed: true,
          resources: ['User Management Guide', 'RBAC Documentation', 'SSO Integration']
        },
        {
          id: '3',
          title: 'First Model Deployment',
          description: 'Deploy your first pre-trained AI model',
          completed: true,
          resources: ['Model Deployment Guide', 'API Documentation', 'Testing Checklist']
        },
        {
          id: '4',
          title: 'Integration Testing',
          description: 'Test API endpoints and model responses',
          completed: false,
          resources: ['Testing Framework', 'API Examples', 'Postman Collection']
        },
        {
          id: '5',
          title: 'Production Launch',
          description: 'Deploy to production and monitor performance',
          completed: false,
          resources: ['Launch Checklist', 'Monitoring Setup', 'Rollback Plan']
        }
      ]
    },
    {
      id: 'enterprise-deployment',
      title: 'Enterprise Deployment',
      description: 'Full-scale enterprise rollout with governance',
      timeline: '30-90 days',
      progress: 40,
      steps: [
        {
          id: '1',
          title: 'Architecture Review',
          description: 'Design scalable architecture for enterprise workloads',
          completed: true,
          resources: ['Architecture Blueprint', 'Scalability Guide', 'High Availability Setup']
        },
        {
          id: '2',
          title: 'Security Audit',
          description: 'Implement security controls and compliance measures',
          completed: true,
          resources: ['Security Checklist', 'Compliance Framework', 'Penetration Testing']
        },
        {
          id: '3',
          title: 'Multi-Region Setup',
          description: 'Deploy across multiple geographic regions',
          completed: false,
          resources: ['Global Deployment Guide', 'Data Residency', 'Latency Optimization']
        },
        {
          id: '4',
          title: 'Governance Framework',
          description: 'Establish AI governance policies and approval workflows',
          completed: false,
          resources: ['Governance Guide', 'Policy Templates', 'Approval Workflows']
        },
        {
          id: '5',
          title: 'Department Rollout',
          description: 'Progressive rollout across business units',
          completed: false,
          resources: ['Rollout Plan', 'Change Management', 'Training Materials']
        }
      ]
    },
    {
      id: 'cloud-migration',
      title: 'Cloud Migration',
      description: 'Migrate existing AI workloads to cloud platform',
      timeline: '60-120 days',
      progress: 25,
      steps: [
        {
          id: '1',
          title: 'Workload Assessment',
          description: 'Analyze existing AI models and dependencies',
          completed: true,
          resources: ['Assessment Template', 'Dependency Mapping', 'Cost Analysis']
        },
        {
          id: '2',
          title: 'Migration Strategy',
          description: 'Plan migration approach and timeline',
          completed: false,
          resources: ['Migration Framework', 'Risk Assessment', 'Downtime Planning']
        },
        {
          id: '3',
          title: 'Data Migration',
          description: 'Transfer training data and model artifacts',
          completed: false,
          resources: ['Data Transfer Tools', 'Validation Scripts', 'Backup Strategy']
        },
        {
          id: '4',
          title: 'Model Retraining',
          description: 'Retrain models on cloud infrastructure',
          completed: false,
          resources: ['Training Pipeline', 'Hyperparameter Tuning', 'Performance Benchmarks']
        },
        {
          id: '5',
          title: 'Cutover & Validation',
          description: 'Switch to cloud platform and validate performance',
          completed: false,
          resources: ['Cutover Checklist', 'Validation Tests', 'Rollback Procedures']
        }
      ]
    },
    {
      id: 'data-integration',
      title: 'Data Integration',
      description: 'Connect enterprise data sources for AI training',
      timeline: '45-90 days',
      progress: 55,
      steps: [
        {
          id: '1',
          title: 'Data Discovery',
          description: 'Identify and catalog available data sources',
          completed: true,
          resources: ['Data Catalog', 'Source Inventory', 'Quality Assessment']
        },
        {
          id: '2',
          title: 'ETL Pipeline Setup',
          description: 'Build data extraction and transformation pipelines',
          completed: true,
          resources: ['Pipeline Templates', 'Transformation Logic', 'Scheduling Guide']
        },
        {
          id: '3',
          title: 'Data Quality Gates',
          description: 'Implement validation and quality controls',
          completed: true,
          resources: ['Quality Metrics', 'Validation Rules', 'Monitoring Dashboard']
        },
        {
          id: '4',
          title: 'Real-time Streaming',
          description: 'Enable real-time data ingestion for live models',
          completed: false,
          resources: ['Streaming Architecture', 'Kafka Setup', 'Stream Processing']
        },
        {
          id: '5',
          title: 'Data Governance',
          description: 'Establish data lineage and access controls',
          completed: false,
          resources: ['Governance Policies', 'Access Control', 'Audit Logging']
        }
      ]
    },
    {
      id: 'security-hardening',
      title: 'Security Hardening',
      description: 'Implement advanced security measures',
      timeline: '30-60 days',
      progress: 70,
      steps: [
        {
          id: '1',
          title: 'Access Control',
          description: 'Configure RBAC and MFA requirements',
          completed: true,
          resources: ['RBAC Guide', 'MFA Setup', 'Identity Provider Integration']
        },
        {
          id: '2',
          title: 'Network Security',
          description: 'Implement firewalls and network segmentation',
          completed: true,
          resources: ['Network Architecture', 'Firewall Rules', 'VPN Configuration']
        },
        {
          id: '3',
          title: 'Encryption',
          description: 'Enable encryption at rest and in transit',
          completed: true,
          resources: ['Encryption Guide', 'Key Management', 'Certificate Setup']
        },
        {
          id: '4',
          title: 'Vulnerability Scanning',
          description: 'Schedule regular security scans and penetration tests',
          completed: false,
          resources: ['Scanning Tools', 'Test Procedures', 'Remediation Workflow']
        },
        {
          id: '5',
          title: 'Incident Response',
          description: 'Create security incident response plan',
          completed: false,
          resources: ['Response Playbook', 'Contact List', 'Communication Plan']
        }
      ]
    },
    {
      id: 'team-onboarding',
      title: 'Team Onboarding',
      description: 'Train teams on AI platform usage',
      timeline: '15-45 days',
      progress: 80,
      steps: [
        {
          id: '1',
          title: 'Training Program',
          description: 'Develop role-based training curriculum',
          completed: true,
          resources: ['Training Modules', 'Video Tutorials', 'Hands-on Labs']
        },
        {
          id: '2',
          title: 'Certification',
          description: 'Certify users on platform competency',
          completed: true,
          resources: ['Certification Exam', 'Study Guide', 'Practice Tests']
        },
        {
          id: '3',
          title: 'Documentation',
          description: 'Create internal documentation and best practices',
          completed: true,
          resources: ['Documentation Templates', 'Best Practices', 'FAQ Database']
        },
        {
          id: '4',
          title: 'Support Structure',
          description: 'Establish internal support channels',
          completed: true,
          resources: ['Support Portal', 'Ticketing System', 'Office Hours']
        },
        {
          id: '5',
          title: 'Continuous Learning',
          description: 'Set up ongoing training and knowledge sharing',
          completed: false,
          resources: ['Learning Path', 'Community Forum', 'Monthly Workshops']
        }
      ]
    }
  ];

  const getIcon = (id: string) => {
    const icons: Record<string, React.ReactNode> = {
      'quick-start': <Rocket className="w-5 h-5" />,
      'enterprise-deployment': <Building2 className="w-5 h-5" />,
      'cloud-migration': <Cloud className="w-5 h-5" />,
      'data-integration': <Database className="w-5 h-5" />,
      'security-hardening': <Shield className="w-5 h-5" />,
      'team-onboarding': <Users className="w-5 h-5" />
    };
    return icons[id] || <BookOpen className="w-5 h-5" />;
  };

  const activePlaybook = playbooks.find(p => p.id === selectedPlaybook);

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Implementation Playbooks</h1>
          <p className="text-gray-400">Step-by-step guides for successful AI platform adoption</p>
        </div>
        <div className="flex gap-2">
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export Plan
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Award className="w-4 h-4" />
            Track Progress
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Playbook List */}
        <div className="lg:col-span-1 space-y-3">
          {playbooks.map((playbook) => (
            <div
              key={playbook.id}
              onClick={() => setSelectedPlaybook(playbook.id)}
              className={`card-hover transition-all duration-300 ${
                selectedPlaybook === playbook.id
                  ? 'ring-2 ring-purple-500 bg-white/10'
                  : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${
                  selectedPlaybook === playbook.id
                    ? 'bg-purple-500/20 text-purple-400'
                    : 'bg-white/5 text-gray-400'
                }`}>
                  {getIcon(playbook.id)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-white mb-1">{playbook.title}</h3>
                  <p className="text-xs text-gray-400 mb-2 line-clamp-2">
                    {playbook.description}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <Clock className="w-3 h-3" />
                    {playbook.timeline}
                  </div>
                  <div className="mt-2">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="text-gray-400">Progress</span>
                      <span className="text-purple-400 font-medium">{playbook.progress}%</span>
                    </div>
                    <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-500"
                        style={{ width: `${playbook.progress}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Playbook Details */}
        {activePlaybook && (
          <div className="lg:col-span-2 space-y-4">
            <div className="card">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-xl">
                    {getIcon(activePlaybook.id)}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white mb-2">
                      {activePlaybook.title}
                    </h2>
                    <p className="text-gray-400 mb-3">{activePlaybook.description}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-2 text-gray-400">
                        <Clock className="w-4 h-4" />
                        Timeline: {activePlaybook.timeline}
                      </div>
                      <div className="flex items-center gap-2 text-purple-400">
                        <CheckCircle className="w-4 h-4" />
                        {activePlaybook.steps.filter(s => s.completed).length} of {activePlaybook.steps.length} completed
                      </div>
                    </div>
                  </div>
                </div>
                <button className="btn-primary flex items-center gap-2">
                  <Play className="w-4 h-4" />
                  Start
                </button>
              </div>

              {/* Progress Bar */}
              <div className="mb-6 p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Overall Progress</span>
                  <span className="text-lg font-bold gradient-text">{activePlaybook.progress}%</span>
                </div>
                <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-500 via-purple-400 to-blue-500 rounded-full transition-all duration-700 glow"
                    style={{ width: `${activePlaybook.progress}%` }}
                  />
                </div>
              </div>

              {/* Steps */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white mb-4">Implementation Steps</h3>
                {activePlaybook.steps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`p-4 rounded-lg border transition-all duration-300 ${
                      step.completed
                        ? 'bg-green-500/10 border-green-500/30'
                        : 'bg-white/5 border-white/10 hover:bg-white/10'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        {step.completed ? (
                          <CheckCircle className="w-5 h-5 text-green-400" />
                        ) : (
                          <Circle className="w-5 h-5 text-gray-500" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-4 mb-2">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className={`text-xs font-medium px-2 py-1 rounded ${
                                step.completed ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'
                              }`}>
                                Step {index + 1}
                              </span>
                              <h4 className={`font-semibold ${
                                step.completed ? 'text-green-400' : 'text-white'
                              }`}>
                                {step.title}
                              </h4>
                            </div>
                            <p className="text-sm text-gray-400 mt-1">{step.description}</p>
                          </div>
                          {!step.completed && (
                            <button className="btn-secondary text-xs whitespace-nowrap">
                              Mark Complete
                            </button>
                          )}
                        </div>
                        <div className="mt-3 pt-3 border-t border-white/10">
                          <p className="text-xs text-gray-500 mb-2">Resources:</p>
                          <div className="flex flex-wrap gap-2">
                            {step.resources.map((resource, idx) => (
                              <span
                                key={idx}
                                className="text-xs px-2 py-1 bg-white/5 rounded hover:bg-white/10 cursor-pointer flex items-center gap-1 transition-colors"
                              >
                                <ChevronRight className="w-3 h-3" />
                                {resource}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
