# Integrations

This directory contains integrations with third-party services.

## 📁 Structure

```
integrations/
└── supabase/
    ├── client.ts    # Supabase client configuration
    └── types.ts     # TypeScript type definitions
```

## 🔗 Supabase Integration

### client.ts
- Initializes Supabase client
- Configures connection settings
- Handles environment variables

### types.ts
- Type definitions for Supabase tables
- Database schema types
- API response types

## 🔧 Configuration

Required environment variables:
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_PUBLISHABLE_KEY` - Supabase anon key

## 📖 Usage

```typescript
import { supabase } from "@/integrations/supabase/client";
```

## 🔗 Edge Functions

Supabase Edge Functions are located at:
`../supabase/functions/`

The `analyze-retina` function provides AI analysis via Lovable AI Gateway.

