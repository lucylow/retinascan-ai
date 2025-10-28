# Lovable File Structure Guide

This document provides a clear overview of the file structure for RetinaScan AI optimized for Lovable development.

## 🏗️ Project Structure

```
retina-zero-code/
├── src/                          # ⭐ MAIN FRONTEND (Lovable workspace)
│   ├── main.tsx                  # Entry point
│   ├── App.tsx                   # Root component with routing
│   ├── index.css                 # Global styles
│   │
│   ├── pages/                    # 📄 Page Components
│   │   └── Index.tsx             # Main application page
│   │
│   ├── components/               # 🧩 UI Components
│   │   ├── ImageUpload.tsx       # Image upload interface
│   │   ├── DiagnosisResult.tsx   # Results display
│   │   ├── ConfigWarning.tsx    # Configuration alerts
│   │   └── ui/                   # Reusable UI components
│   │       ├── badge.tsx
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── progress.tsx
│   │       ├── toast.tsx
│   │       └── toaster.tsx
│   │
│   ├── hooks/                    # 🎣 Custom Hooks
│   │   └── use-toast.ts          # Toast notifications
│   │
│   ├── lib/                      # 📚 Utilities
│   │   ├── config.ts             # App configuration
│   │   └── utils.ts              # Helper functions
│   │
│   └── integrations/             # 🔗 Third-party Services
│       └── supabase/
│           ├── client.ts         # Supabase client
│           └── types.ts          # Type definitions
│
├── supabase/                     # Supabase Configuration
│   └── functions/
│       └── analyze-retina/      # Edge Function
│           └── index.ts         # AI analysis endpoint
│
├── services/                     # 🔧 Backend Services (Python)
│   └── prediction_service.py    # ML prediction logic
│
├── utils/                        # 🛠️ Backend Utilities (Python)
│   ├── image_processor.py       # Image preprocessing
│   └── model_manager.py         # Model handling
│
└── Configuration Files
    ├── package.json              # Node dependencies
    ├── vite.config.ts            # Vite configuration
    ├── tsconfig.json             # TypeScript config
    ├── tailwind.config.ts        # Tailwind CSS config
    └── postcss.config.js         # PostCSS config
```

## 🎯 Key Files for Lovable Development

### Most Important Files

1. **`src/pages/Index.tsx`**
   - Main application page
   - Layout and page logic
   - Components composition

2. **`src/components/ImageUpload.tsx`**
   - Image upload functionality
   - Drag-and-drop support
   - API integration

3. **`src/components/DiagnosisResult.tsx`**
   - Results display
   - Severity visualization
   - Recommendations

4. **`src/lib/config.ts`**
   - Application settings
   - API endpoints
   - Configuration constants

5. **`src/integrations/supabase/client.ts`**
   - Supabase setup
   - API configuration
   - Environment variables

## 🔍 Navigation Tips

### Path Aliases

This project uses TypeScript path aliases in `tsconfig.json`:

```typescript
// All imports can use '@' prefix for src/
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import config from "@/lib/config";
```

### Component Hierarchy

```
App (Routes + Providers)
 └── Index (Main Page)
     ├── ConfigWarning
     ├── ImageUpload
     └── DiagnosisResult
```

### File Naming

- **Components**: PascalCase (e.g., `ImageUpload.tsx`)
- **Utilities**: camelCase (e.g., `utils.ts`)
- **Config**: kebab-case (e.g., `config.ts`)
- **Hooks**: camelCase with `use-` prefix (e.g., `use-toast.ts`)

## 📖 Additional Documentation

Each major directory has a README:

- `src/README.md` - Frontend overview
- `src/components/README.md` - Component documentation
- `src/components/ui/README.md` - UI components guide
- `src/integrations/README.md` - Supabase integration
- `src/lib/README.md` - Utility functions

## 🚀 Development Workflow

1. **Edit pages**: Start with `src/pages/Index.tsx`
2. **Add components**: Create in `src/components/`
3. **Use UI components**: Import from `src/components/ui/`
4. **Modify config**: Edit `src/lib/config.ts`
5. **Update API**: Edit `src/integrations/supabase/client.ts`

## 🔧 Configuration

Environment variables needed:
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
```

Set these in Lovable → Settings → Environment Variables

## 📝 Notes

- ✅ Old `retinascan-frontend/` directory removed
- ✅ Unified structure in `src/` directory
- ✅ Better path navigation with `@` alias
- ✅ Comprehensive README files for navigation
- ✅ Optimized for Lovable development

