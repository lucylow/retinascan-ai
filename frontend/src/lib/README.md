# Library Functions

This directory contains utility functions and configuration.

## 📁 Structure

```
lib/
├── config.ts    # Application configuration
└── utils.ts     # Helper utilities
```

## ⚙️ config.ts

Contains:
- API endpoints
- Upload limits
- File type validations
- Application settings

Edit this file to customize:
- API base URLs
- File size limits
- Allowed file formats
- UI behavior

## 🛠️ utils.ts

Contains:
- Type checking utilities
- Date formatting
- Data transformation helpers
- Common validations

## 📝 Usage

```typescript
import { cn } from "@/lib/utils";
import config from "@/lib/config";
```

The `cn` utility combines class names using clsx and tailwind-merge.

