import React from 'react';
import { useTranslation } from '@/lib/i18n';
import { Button } from './button';
import { Globe } from 'lucide-react';

/**
 * Simple Language Selector component
 * Note: If you don't have a dropdown menu component, this is a simplified version
 */
export const LanguageSelector: React.FC = () => {
  const { language, setLanguage, availableLanguages } = useTranslation();

  return (
    <div className="relative">
      <Button
        variant="outline"
        size="sm"
        className="gap-2"
        aria-label="Select language"
        aria-haspopup="true"
        aria-expanded="false"
      >
        <Globe className="w-4 h-4" />
        <span className="hidden sm:inline">{availableLanguages.find(l => l.code === language)?.name || 'Language'}</span>
      </Button>
      
      {/* Simple dropdown - you may want to replace with a proper dropdown component */}
      <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700 z-50 hidden group-hover:block">
        <div className="py-1">
          {availableLanguages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => setLanguage(lang.code)}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 ${
                language === lang.code ? 'bg-primary text-primary-foreground' : ''
              }`}
              role="menuitem"
            >
              {lang.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

// Alternative simpler version using a select element
export const LanguageSelectorSimple: React.FC = () => {
  const { language, setLanguage, availableLanguages } = useTranslation();

  return (
    <select
      value={language}
      onChange={(e) => setLanguage(e.target.value as 'en' | 'fr' | 'wo')}
      className="px-3 py-1.5 text-sm border rounded-md bg-background"
      aria-label="Select language"
    >
      {availableLanguages.map((lang) => (
        <option key={lang.code} value={lang.code}>
          {lang.name}
        </option>
      ))}
    </select>
  );
};

