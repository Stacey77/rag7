# Auth Components & Main Application

This directory contains authentication components and the main application shell for the AI Design Platform.

## Components

### Auth Components (`/components/auth/`)

#### 1. LoginForm.tsx
A glass morphism login form with the following features:
- Email/password input fields with validation
- Password visibility toggle
- Remember me checkbox
- Forgot password link
- OAuth login buttons (Google, GitHub, Microsoft)
- Real-time validation feedback
- Loading states

**Usage:**
```tsx
import { LoginForm } from './components/auth';

<LoginForm
  onLogin={(email, password, rememberMe) => {
    // Handle login
  }}
  onOAuthLogin={(provider) => {
    // Handle OAuth login
  }}
  onForgotPassword={() => {
    // Navigate to forgot password page
  }}
/>
```

#### 2. RegisterForm.tsx
A comprehensive registration form with:
- Name, email, and password fields
- Password confirmation
- Real-time password strength indicator
- Password requirements checklist:
  - At least 8 characters
  - One uppercase letter
  - One lowercase letter
  - One number
  - One special character
- Terms and conditions acceptance checkbox
- OAuth registration options
- Comprehensive validation

**Usage:**
```tsx
import { RegisterForm } from './components/auth';

<RegisterForm
  onRegister={(name, email, password, acceptTerms) => {
    // Handle registration
  }}
  onOAuthRegister={(provider) => {
    // Handle OAuth registration
  }}
/>
```

#### 3. UserProfile.tsx
A user profile settings component featuring:
- Profile information display/editing
- Role badge with color coding (Admin, Developer, User)
- Two-factor authentication toggle
- API key management:
  - Create new API keys
  - View/hide API keys
  - Copy to clipboard
  - Delete API keys
  - Last used tracking
- Active session management:
  - View all sessions
  - Current session indicator
  - Revoke sessions
  - Device and location info

**Usage:**
```tsx
import { UserProfile } from './components/auth';

const userData = {
  name: 'John Doe',
  email: 'john.doe@example.com',
  role: 'Admin',
  twoFactorEnabled: false,
};

const apiKeys = [
  {
    id: '1',
    name: 'Production API',
    key: 'sk_prod_abc123xyz789',
    createdAt: '2024-01-15',
    lastUsed: '2024-01-20',
  },
];

const sessions = [
  {
    id: '1',
    device: 'Chrome on MacOS',
    location: 'San Francisco, CA',
    lastActive: '2 minutes ago',
    current: true,
  },
];

<UserProfile
  user={userData}
  apiKeys={apiKeys}
  sessions={sessions}
  onUpdateProfile={(data) => {}}
  onToggle2FA={(enabled) => {}}
  onCreateApiKey={(name) => {}}
  onDeleteApiKey={(id) => {}}
  onRevokeSession={(id) => {}}
/>
```

### Main Application (`App.tsx`)

The main application shell featuring:

#### Features:
- **Glass morphism sidebar navigation**
  - Collapsible sidebar (full width ↔ icon only)
  - Navigation items with icons:
    - Dashboard
    - Models (AI model management)
    - Analytics
    - Monitoring
    - Data
    - Users
    - Security
    - Settings
  - Active state highlighting with gradient background

- **Top header bar**
  - Global search bar
  - Theme toggle (dark/light mode)
  - Notification bell with badge counter
  - User profile dropdown menu:
    - Profile link
    - Settings link
    - Logout button

- **Main content area**
  - Dynamic content based on active section
  - Placeholder pages for all sections
  - Dashboard with:
    - 4 metric cards (Total Models, Active Users, API Calls, Avg Response)
    - Recent activity feed
    - System status indicators

- **AI Companion button**
  - Fixed bottom-right position
  - Floating action button with chat icon
  - Hover scale animation

#### Usage:
```tsx
import { App } from './App';

// Simply render the App component
<App />
```

The app manages its own state for:
- Active navigation section
- Sidebar open/closed state
- User menu visibility
- Dark/light mode
- Notification count

## Design System

All components follow a consistent design language:

### Colors:
- Primary gradient: Blue (500) → Purple (500)
- Background: Glass morphism with backdrop blur
- Text: White (primary), Gray (300-400) for secondary
- Borders: White with 10-20% opacity

### Typography:
- Headings: Bold, White
- Body text: Medium/Regular, Gray-300
- Small text: Text-sm/xs, Gray-400

### Interactive Elements:
- Buttons: Gradient backgrounds with hover effects
- Inputs: Glass morphism with focus rings
- Icons: lucide-react icons throughout

### Spacing:
- Consistent padding/margin using Tailwind scale (2, 3, 4, 6, 8)
- Rounded corners: lg (8px), 2xl (16px) for cards

## Tech Stack

- **React 18+** with TypeScript
- **lucide-react** for icons
- **Tailwind CSS** for styling
- **Glass morphism** design aesthetic

## File Structure

```
src/
├── components/
│   └── auth/
│       ├── LoginForm.tsx
│       ├── RegisterForm.tsx
│       ├── UserProfile.tsx
│       └── index.ts
├── App.tsx
└── AuthExample.tsx (example usage)
```

## Notes

- All components use TypeScript for type safety
- Forms include comprehensive validation
- OAuth providers can be easily customized
- Components are fully responsive
- Glass morphism effects require backdrop-filter support
