import React from 'react';
import { 
  Heart, 
  DollarSign, 
  ShoppingCart, 
  Factory, 
  Truck, 
  GraduationCap,
  Clock,
  TrendingUp,
  Shield,
  CheckCircle
} from 'lucide-react';
import type { IndustryTemplate } from '../../types';

export const IndustryTemplates: React.FC = () => {
  const templates: IndustryTemplate[] = [
    {
      id: '1',
      name: 'Healthcare AI Suite',
      industry: 'Healthcare',
      description: 'HIPAA-compliant medical imaging analysis, patient diagnosis support, and treatment recommendation systems',
      models: ['Medical Imaging CNN', 'Diagnosis NLP', 'Treatment Optimizer'],
      roi: 340,
      timeline: '8-12 weeks',
      compliance: ['HIPAA', 'HL7', 'FHIR', 'FDA 21 CFR Part 11'],
      icon: 'heart'
    },
    {
      id: '2',
      name: 'Financial Services Platform',
      industry: 'Finance',
      description: 'Real-time fraud detection, credit risk analysis, algorithmic trading, and anti-money laundering',
      models: ['Fraud Detection ML', 'Risk Scoring', 'Transaction Anomaly Detection'],
      roi: 420,
      timeline: '10-14 weeks',
      compliance: ['PCI DSS', 'SOC 2', 'GLBA', 'SOX'],
      icon: 'dollar'
    },
    {
      id: '3',
      name: 'Retail Intelligence',
      industry: 'Retail',
      description: 'Customer behavior analytics, demand forecasting, dynamic pricing, and inventory optimization',
      models: ['Customer Segmentation', 'Demand Forecasting LSTM', 'Price Optimization'],
      roi: 285,
      timeline: '6-10 weeks',
      compliance: ['GDPR', 'CCPA', 'PCI DSS'],
      icon: 'cart'
    },
    {
      id: '4',
      name: 'Manufacturing Optimizer',
      industry: 'Manufacturing',
      description: 'Predictive maintenance, quality control automation, production optimization, and supply chain forecasting',
      models: ['Predictive Maintenance', 'Quality Vision AI', 'Production Scheduler'],
      roi: 380,
      timeline: '12-16 weeks',
      compliance: ['ISO 9001', 'ISO 27001', 'OSHA'],
      icon: 'factory'
    },
    {
      id: '5',
      name: 'Logistics Optimizer',
      industry: 'Logistics',
      description: 'Route optimization, fleet management, delivery prediction, and warehouse automation',
      models: ['Route Optimizer', 'Demand Prediction', 'Fleet Management AI'],
      roi: 310,
      timeline: '8-12 weeks',
      compliance: ['ISO 28000', 'CTPAT', 'GDPR'],
      icon: 'truck'
    },
    {
      id: '6',
      name: 'Education Platform',
      industry: 'Education',
      description: 'Personalized learning paths, student performance prediction, content recommendation, and automated grading',
      models: ['Learning Path Generator', 'Performance Predictor', 'Content Recommender'],
      roi: 220,
      timeline: '6-8 weeks',
      compliance: ['FERPA', 'COPPA', 'GDPR'],
      icon: 'graduation'
    },
    {
      id: '7',
      name: 'Energy Management',
      industry: 'Energy',
      description: 'Smart grid optimization, energy consumption forecasting, renewable energy prediction, and fault detection',
      models: ['Load Forecasting', 'Grid Optimizer', 'Anomaly Detection'],
      roi: 350,
      timeline: '10-14 weeks',
      compliance: ['NERC CIP', 'ISO 50001', 'IEC 62443'],
      icon: 'zap'
    }
  ];

  const getIcon = (iconName: string) => {
    const icons: { [key: string]: React.ReactNode } = {
      heart: <Heart className="w-8 h-8" />,
      dollar: <DollarSign className="w-8 h-8" />,
      cart: <ShoppingCart className="w-8 h-8" />,
      factory: <Factory className="w-8 h-8" />,
      truck: <Truck className="w-8 h-8" />,
      graduation: <GraduationCap className="w-8 h-8" />,
      zap: <TrendingUp className="w-8 h-8" />
    };
    return icons[iconName] || <Heart className="w-8 h-8" />;
  };

  return (
    <div className="space-y-6 fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text mb-2">Industry Templates</h1>
          <p className="text-gray-400">Pre-configured AI solutions tailored for your industry</p>
        </div>
        <button className="btn-primary">Request Custom Template</button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Total Templates</div>
          <div className="text-2xl font-bold gradient-text">{templates.length}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Avg ROI</div>
          <div className="text-2xl font-bold text-green-400">
            {Math.round(templates.reduce((sum, t) => sum + t.roi, 0) / templates.length)}%
          </div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Industries Covered</div>
          <div className="text-2xl font-bold">{templates.length}</div>
        </div>
        <div className="card">
          <div className="text-sm text-gray-400 mb-1">Compliance Standards</div>
          <div className="text-2xl font-bold">
            {new Set(templates.flatMap(t => t.compliance)).size}
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <div key={template.id} className="card card-hover group">
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 text-purple-400 group-hover:scale-110 transition-transform">
                {getIcon(template.icon)}
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                {template.roi}% ROI
              </span>
            </div>

            {/* Content */}
            <h3 className="text-xl font-bold mb-2">{template.name}</h3>
            <div className="text-sm text-purple-400 mb-3">{template.industry}</div>
            <p className="text-sm text-gray-400 mb-4 line-clamp-3">{template.description}</p>

            {/* Models */}
            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Included Models:</div>
              <div className="space-y-1">
                {template.models.map((model, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs">
                    <CheckCircle className="w-3 h-3 text-green-400" />
                    <span className="text-gray-300">{model}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Timeline & Compliance */}
            <div className="space-y-3 mb-4">
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-gray-400">Timeline:</span>
                <span className="text-white font-medium">{template.timeline}</span>
              </div>
              <div className="flex items-start gap-2 text-sm">
                <Shield className="w-4 h-4 text-gray-400 mt-0.5" />
                <div>
                  <span className="text-gray-400">Compliance:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {template.compliance.slice(0, 3).map((cert, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded text-xs bg-blue-500/20 text-blue-400">
                        {cert}
                      </span>
                    ))}
                    {template.compliance.length > 3 && (
                      <span className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-400">
                        +{template.compliance.length - 3}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4 border-t border-gray-700">
              <button className="flex-1 btn-secondary text-sm py-2">View Details</button>
              <button className="flex-1 btn-primary text-sm py-2">Deploy</button>
            </div>
          </div>
        ))}
      </div>

      {/* Use Cases Section */}
      <div className="card">
        <h3 className="text-xl font-bold mb-4">Popular Use Cases by Industry</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20">
            <div className="font-semibold mb-2">Healthcare</div>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Radiology image analysis</li>
              <li>• Patient readmission prediction</li>
              <li>• Drug interaction detection</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-blue-500/10 to-transparent border border-blue-500/20">
            <div className="font-semibold mb-2">Finance</div>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Credit card fraud prevention</li>
              <li>• Loan default prediction</li>
              <li>• Market sentiment analysis</li>
            </ul>
          </div>
          <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-transparent border border-green-500/20">
            <div className="font-semibold mb-2">Retail</div>
            <ul className="text-sm text-gray-400 space-y-1">
              <li>• Churn prediction & prevention</li>
              <li>• Product recommendation</li>
              <li>• Visual search & discovery</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
