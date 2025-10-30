# RetinaScan AI - Frontend Source

This directory contains the React + TypeScript frontend for RetinaScan AI.

## 📁 Directory Structure

```
src/
├── main.tsx              # Application entry point
├── App.tsx                # Root component with routing
├── index.css              # Global styles
│
├── components/            # React UI components
│   ├── ImageUpload.tsx    # Image upload interface
│   ├── DiagnosisResult.tsx # Results display component
│   ├── ConfigWarning.tsx  # Configuration alerts
│   └── ui/                # Reusable UI components (shadcn/ui)
│       ├── badge.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── progress.tsx
│       ├── toast.tsx
│       └── toaster.tsx
│
├── pages/                 # Page components
│   └── Index.tsx          # Main application page
│
├── hooks/                 # Custom React hooks
│   └── use-toast.ts       # Toast notification hook
│
├── lib/                   # Utility functions and configs
│   ├── config.ts          # Application configuration
│   └── utils.ts           # Helper utilities
│
└── integrations/          # Third-party integrations
    └── supabase/          # Supabase client and types
        ├── client.ts      # Supabase client setup
        └── types.ts       # TypeScript type definitions
```

## 🔧 Navigation Tips for Lovable

### Key Files to Edit

- **`pages/Index.tsx`** - Main page layout and logic
- **`components/ImageUpload.tsx`** - Upload functionality
- **`components/DiagnosisResult.tsx`** - Results display
- **`lib/config.ts`** - Configuration settings
- **`integrations/supabase/client.ts`** - API configuration

### Path Resolution

This project uses TypeScript path aliases configured in `tsconfig.json`:

```typescript
// Instead of:
import { Button } from "../../components/ui/button";

// You can use:
import { Button } from "@/components/ui/button";
```

The `@` alias maps to the `src/` directory.

## 🚀 Quick Start

```bash
# Development
npm run dev

# Build
npm run build

# Preview
npm run preview
```

## 📚 Component Hierarchy

```
App
 └── QueryClientProvider
     └── BrowserRouter
         └── Routes
             └── Index (main page)
                 ├── ConfigWarning
                 ├── ImageUpload
                 └── DiagnosisResult
```

## 🎨 UI Components

This project uses [shadcn/ui](https://ui.shadcn.com/) components built on:
- **Radix UI** - Accessible component primitives
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

All UI components are in `src/components/ui/`.

## 🔗 Integrations

### Supabase
- Client: `src/integrations/supabase/client.ts`
- Edge Functions location: `../supabase/functions/analyze-retina/`
- Used for AI analysis via Lovable AI Gateway

### Configuration
- API settings: `src/lib/config.ts`
- Environment variables required:
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_PUBLISHABLE_KEY`

## 📖 File Naming Convention

- Components: PascalCase (e.g., `ImageUpload.tsx`)
- Utilities: camelCase (e.g., `utils.ts`)
- Configuration: kebab-case (e.g., `config.ts`)
- Types: camelCase with `.ts` extension (e.g., `types.ts`)

