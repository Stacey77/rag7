# Enterprise Components

This directory contains enterprise-grade React TypeScript components for the AI Design Platform.

## Components

### 1. IndustryTemplates.tsx
Pre-configured AI solution templates for 7+ industries:
- **Healthcare**: HIPAA-compliant medical imaging, diagnosis support
- **Finance**: Fraud detection, risk analysis, trading algorithms
- **Retail**: Customer behavior analytics, demand forecasting, pricing
- **Manufacturing**: Predictive maintenance, quality control, production optimization
- **Logistics**: Route optimization, fleet management, delivery prediction
- **Education**: Personalized learning paths, performance prediction
- **Energy**: Smart grid optimization, consumption forecasting

Features:
- ROI projections for each template
- Implementation timelines
- Compliance framework tracking
- Use case descriptions
- Grid layout with glass morphism cards

### 2. SecurityCompliance.tsx
Comprehensive compliance dashboard for security standards:
- **Frameworks**: SOC 2, ISO 27001, GDPR, HIPAA, PCI DSS, FedRAMP
- Progress bars for compliance status
- Security controls count tracking
- Last audit date monitoring
- Certificate tracking and expiry
- Status indicators (compliant/in-progress/not-compliant)

Features:
- Overall compliance percentage
- Framework-specific progress tracking
- Active certificates display
- Recent audit activity log
- Security controls summary

### 3. ROICalculator.tsx
Interactive ROI calculator with real-time projections:
- Input fields for current costs, team size, hourly rates
- Real-time calculation of monthly/annual savings
- Productivity metrics and improvements
- Break-even analysis
- Cost comparison charts (Recharts)
- Cumulative savings projections

Features:
- Labor cost reduction calculations
- Error cost reduction tracking
- Time efficiency gains
- Monthly vs. With-AI cost comparison charts
- 12-month cumulative savings projection
- Key insights and recommendations

### 4. IntegrationMarketplace.tsx
Integration marketplace with 14+ platforms:

**ML Platforms**:
- AWS SageMaker
- Azure ML
- Google Cloud AI

**Data Platforms**:
- Snowflake
- Databricks
- BigQuery

**Databases**:
- PostgreSQL
- MongoDB
- Redis

**Other Tools**:
- Apache Kafka
- Elasticsearch
- Apache Spark
- MLflow
- Kubeflow

Features:
- Category-based filtering
- Search functionality
- Installation status tracking
- Connection testing UI
- Popular integration stacks
- Integration benefits breakdown

## Usage

```tsx
import { 
  IndustryTemplates, 
  SecurityCompliance, 
  ROICalculator, 
  IntegrationMarketplace 
} from './components/enterprise';

// In your routing or tab component
<IndustryTemplates />
<SecurityCompliance />
<ROICalculator />
<IntegrationMarketplace />
```

## Design System

All components follow the AI Design Platform design system:
- **Glass morphism**: `card`, `card-hover` classes
- **Gradients**: `gradient-text`, `btn-primary`, `btn-secondary`
- **Icons**: lucide-react icon library
- **Charts**: Recharts library for data visualization
- **Animations**: `fade-in` class for smooth transitions

## Type Safety

All components use TypeScript types from `src/types/index.ts`:
- `IndustryTemplate`
- `SecurityFramework`
- `ROICalculation`
- `Integration`

## Sample Data

Each component includes comprehensive mock data for demonstration:
- Industry templates with realistic use cases
- Compliance frameworks with progress tracking
- ROI calculations with multiple variables
- Integration platforms with status indicators
