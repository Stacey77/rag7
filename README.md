# AI Workflow Automation Discovery Platform

A comprehensive AI-powered platform that helps founders and business owners discover hidden automation opportunities in their operations through systematic interviews and analysis.

## Features

### 🎯 Core Capabilities
- **Systematic Workflow Interviews**: Guided interview process to map daily operations, tasks, and bottlenecks
- **AI-Powered Analysis**: Gemini AI analyzes responses to identify top bottlenecks and automation opportunities
- **Prioritization Matrix**: Visual impact vs. effort matrix for decision-making
- **Implementation Roadmap**: Phased automation implementation plans with timelines
- **Context Engineering Studio**: Design optimized AI agent prompts with behavioral constraints
- **Security Scanning**: AI-powered vulnerability detection supporting multiple languages

### 🛠️ Technical Stack
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript with strict type checking
- **Styling**: Tailwind CSS + shadcn/ui components
- **Database**: Prisma ORM with SQLite (dev) / PostgreSQL (production)
- **AI Integration**: Google Gemini AI API
- **Export**: PDF (jsPDF) and CSV formats

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Google Gemini API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=file:./dev.db
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

4. Initialize the database:
```bash
npx prisma db push
npx prisma generate
```

5. Run the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
rag7/
├── app/                      # Next.js App Router pages
│   ├── api/                 # API routes
│   │   ├── analysis/        # Analysis generation
│   │   ├── contexts/        # Context templates
│   │   ├── interviews/      # Interview CRUD
│   │   └── security/        # Security scanning
│   ├── analysis/            # Analysis page
│   ├── context-studio/      # Context engineering
│   ├── interview/           # Interview flow
│   ├── security/            # Security scan
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Dashboard
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   ├── Analysis.tsx         # Analysis visualization
│   ├── ContextStudio.tsx    # Context engineering
│   ├── Dashboard.tsx        # Main dashboard
│   ├── Interview.tsx        # Interview flow
│   ├── SecurityScan.tsx     # Security scanner
│   └── Sidebar.tsx          # Navigation
├── lib/                     # Utilities and services
│   ├── db/                  # Database client
│   ├── export/              # PDF/CSV export
│   ├── gemini/              # Gemini AI service
│   └── utils.ts             # Helper functions
├── prisma/                  # Database schema
├── types/                   # TypeScript types
└── public/                  # Static assets
```

## API Routes

### Interviews
- `GET /api/interviews` - List all interviews
- `POST /api/interviews` - Create new interview

### Analysis
- `POST /api/analysis` - Generate analysis from interview

### Security
- `POST /api/security` - Scan code for vulnerabilities

### Context Templates
- `GET /api/contexts` - List templates
- `POST /api/contexts` - Create template

## Database Schema

- **Interview**: Stores workflow interview data
- **Analysis**: AI-generated bottleneck and opportunity analysis
- **SecurityScan**: Vulnerability scan results
- **ContextTemplate**: Saved AI agent prompt templates

## Features in Detail

### Interview System
Systematic question flow covering:
- Daily workflow mapping
- Task frequency and duration
- Manual bottleneck identification
- Data entry patterns
- Approval processes
- Error correction workflows

### Analysis Engine
- **Bottleneck Visualization**: Top 3-5 workflow pain points with severity
- **Opportunity Matrix**: Impact vs. effort prioritization
- **Implementation Roadmap**: Phased automation plan

### Context Studio
- AI agent role and expertise configuration
- Output tone/style selection (Professional, Casual, Technical, Consultative, Executive)
- Behavioral constraints with quick-add examples
- Prompt generation and template saving

### Security Scanner
Multi-language vulnerability detection:
- SQL Injection, XSS, CSRF
- Hardcoded secrets
- Path traversal, Command injection
- Insecure deserialization
- OWASP Top 10 mapping
- Remediation suggestions with code examples

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Security

See [SECURITY.md](SECURITY.md) for reporting security vulnerabilities.