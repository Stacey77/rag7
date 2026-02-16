# Internationalization (i18n) System

This directory contains the internationalization configuration for the AI Design Platform.

## Structure

```
src/i18n/
├── i18n.config.ts       # Main i18n configuration with react-i18next
└── locales/             # Translation files for supported languages
    ├── en.json          # English (default)
    ├── es.json          # Spanish
    ├── fr.json          # French
    ├── de.json          # German
    ├── zh.json          # Chinese (Simplified)
    ├── ja.json          # Japanese
    ├── hi.json          # Hindi
    ├── ar.json          # Arabic
    ├── pt.json          # Portuguese
    └── ru.json          # Russian
```

## Features

- **10 Languages Supported**: English, Spanish, French, German, Chinese, Japanese, Hindi, Arabic, Portuguese, Russian
- **61 Translation Keys** per language across 5 categories
- **Auto Language Detection**: Browser language, localStorage, HTML tag
- **Fallback Language**: English (en)
- **Type-Safe**: Full TypeScript support with react-i18next

## Translation Categories

Each language file includes translations for:

1. **common** - Dashboard, models, analytics, monitoring, settings, profile, help
2. **actions** - Save, cancel, delete, edit, export, import, create, update, etc.
3. **messages** - Success, error, warning, loading states, confirmations
4. **nav** - Navigation items (overview, projects, team, reports, etc.)
5. **auth** - Authentication (login, register, logout, username, password, etc.)

## Usage

Import and initialize i18n in your app entry point:

```typescript
import './i18n/i18n.config';
```

Use in React components:

```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t, i18n } = useTranslation();
  
  return (
    <div>
      <h1>{t('common.dashboard')}</h1>
      <button onClick={() => i18n.changeLanguage('es')}>
        {t('actions.save')}
      </button>
    </div>
  );
}
```

## Adding New Translations

1. Add the key to `en.json` (reference language)
2. Add translations to all other language files
3. Keys must be consistent across all languages
4. Use nested structure: `category.key`

## Configuration

The i18n system is configured with:
- **Language Detection**: localStorage → browser → HTML tag
- **Fallback**: English (en)
- **Interpolation**: Enabled (no escaping needed)
- **React Integration**: Full react-i18next support
