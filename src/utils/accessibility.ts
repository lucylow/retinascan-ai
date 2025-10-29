/**
 * Accessibility utilities for WCAG 2.1 AA compliance
 */

// ARIA helpers
export const ARIA = {
  // Generate ARIA labels for interactive elements
  label: (text: string, context?: string) => {
    return context ? `${text} - ${context}` : text;
  },

  // Generate ARIA descriptions
  describe: (elementId: string, description: string) => {
    return {
      'aria-describedby': elementId,
      id: elementId,
      description,
    };
  },

  // Screen reader only text
  srOnly: (text: string) => (
    <span className="sr-only">{text}</span>
  ),
};

// Keyboard navigation helpers
export const keyboard = {
  // Check if Enter key is pressed
  isEnter: (e: React.KeyboardEvent) => e.key === 'Enter' || e.key === ' ',

  // Check if Escape key is pressed
  isEscape: (e: React.KeyboardEvent) => e.key === 'Escape',

  // Keyboard navigation handler for lists
  handleListNavigation: (
    e: React.KeyboardEvent,
    currentIndex: number,
    totalItems: number,
    onSelect: (index: number) => void
  ) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        onSelect(Math.min(currentIndex + 1, totalItems - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        onSelect(Math.max(currentIndex - 1, 0));
        break;
      case 'Home':
        e.preventDefault();
        onSelect(0);
        break;
      case 'End':
        e.preventDefault();
        onSelect(totalItems - 1);
        break;
      default:
        break;
    }
  },

  // Focus trap for modals
  trapFocus: (element: HTMLElement | null) => {
    if (!element) return;

    const focusableElements = element.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    element.addEventListener('keydown', handleTab);
    firstElement?.focus();

    return () => {
      element.removeEventListener('keydown', handleTab);
    };
  },
};

// Color contrast checker
export const contrast = {
  // Calculate relative luminance
  getLuminance: (r: number, g: number, b: number): number => {
    const [rs, gs, bs] = [r, g, b].map((val) => {
      const v = val / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  },

  // Calculate contrast ratio
  getContrastRatio: (rgb1: [number, number, number], rgb2: [number, number, number]): number => {
    const lum1 = contrast.getLuminance(...rgb1);
    const lum2 = contrast.getLuminance(...rgb2);
    const lighter = Math.max(lum1, lum2);
    const darker = Math.min(lum1, lum2);
    return (lighter + 0.05) / (darker + 0.05);
  },

  // Check if contrast meets WCAG AA standards
  meetsWCAGAA: (rgb1: [number, number, number], rgb2: [number, number, number]): boolean => {
    return contrast.getContrastRatio(rgb1, rgb2) >= 4.5;
  },
};

// Skip link component helper
export const createSkipLink = (targetId: string, label: string = 'Skip to main content') => ({
  href: `#${targetId}`,
  className: 'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md',
  children: label,
});

