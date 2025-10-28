# Components

This directory contains all React components for the RetinaScan AI frontend.

## 📁 Structure

```
components/
├── ImageUpload.tsx       # Main image upload interface
├── DiagnosisResult.tsx   # Displays analysis results
├── ConfigWarning.tsx     # Shows configuration alerts
└── ui/                   # Reusable UI components (shadcn/ui)
```

## 🎯 Core Components

### ImageUpload.tsx
- Handles image file selection and upload
- Drag-and-drop support
- Preview functionality
- Progress indicators

### DiagnosisResult.tsx
- Displays severity classification
- Shows confidence scores
- Displays class probabilities
- Renders structured recommendations

### ConfigWarning.tsx
- Warns about missing configuration
- Shows setup instructions
- Environment variable status

## 🎨 UI Components

Located in `ui/` subdirectory:
- Customizable and composable components
- Built with Radix UI primitives
- Styled with Tailwind CSS
- Fully typed with TypeScript

## 📝 Usage

```typescript
import { ImageUpload } from "@/components/ImageUpload";
import { DiagnosisResult } from "@/components/DiagnosisResult";
```

All components use the `@/` alias for clean imports.

