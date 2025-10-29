/**
 * Internationalization (i18n) utilities
 * Supports multiple languages including English, French, and Wolof
 */

import React from 'react';

export type Language = 'en' | 'fr' | 'wo';

const translations: Record<Language, Record<string, string>> = {
  en: {
    // Common
    'common.loading': 'Loading...',
    'common.error': 'Error',
    'common.success': 'Success',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.confirm': 'Confirm',
    'common.close': 'Close',
    
    // Navigation
    'nav.home': 'Home',
    'nav.features': 'Features',
    'nav.pricing': 'Pricing',
    'nav.contact': 'Contact',
    
    // Hero
    'hero.title': 'RetinaScan AI',
    'hero.subtitle': 'Revolutionary AI-powered diabetic retinopathy detection',
    'hero.description': 'Get instant analysis of retinal fundus images with clinical-grade accuracy',
    'hero.getStarted': 'Get Started',
    'hero.learnMore': 'Learn More',
    
    // Upload
    'upload.title': 'Upload Retinal Image',
    'upload.instructions': 'Click to upload or drag and drop',
    'upload.formats': 'PNG, JPG, JPEG (max 16MB)',
    'upload.analyze': 'Analyze Image',
    'upload.analyzing': 'Analyzing...',
    'upload.change': 'Change image',
    
    // Results
    'results.title': 'Diagnosis Result',
    'results.confidence': 'Confidence',
    'results.recommendation': 'Recommendation',
    'results.probabilities': 'Class Probabilities',
    'results.showExplanation': 'Show AI Explanation',
    'results.hideExplanation': 'Hide AI Explanation',
    
    // Features
    'features.lightningFast': 'Lightning Fast',
    'features.highlyAccurate': 'Highly Accurate',
    'features.detailedInsights': 'Detailed Insights',
    
    // Medical Disclaimer
    'disclaimer.title': 'Medical Disclaimer',
    'disclaimer.text': 'This tool is for research and educational purposes only. Always consult a qualified healthcare professional for medical diagnosis.',
  },
  
  fr: {
    // Common
    'common.loading': 'Chargement...',
    'common.error': 'Erreur',
    'common.success': 'Succès',
    'common.save': 'Enregistrer',
    'common.cancel': 'Annuler',
    'common.confirm': 'Confirmer',
    'common.close': 'Fermer',
    
    // Navigation
    'nav.home': 'Accueil',
    'nav.features': 'Fonctionnalités',
    'nav.pricing': 'Tarification',
    'nav.contact': 'Contact',
    
    // Hero
    'hero.title': 'RetinaScan AI',
    'hero.subtitle': 'Détection révolutionnaire de la rétinopathie diabétique alimentée par l\'IA',
    'hero.description': 'Obtenez une analyse instantanée des images du fond d\'œil avec une précision de niveau clinique',
    'hero.getStarted': 'Commencer',
    'hero.learnMore': 'En savoir plus',
    
    // Upload
    'upload.title': 'Télécharger une image rétinienne',
    'upload.instructions': 'Cliquez pour télécharger ou faites glisser-déposer',
    'upload.formats': 'PNG, JPG, JPEG (max 16 Mo)',
    'upload.analyze': 'Analyser l\'image',
    'upload.analyzing': 'Analyse en cours...',
    'upload.change': 'Changer l\'image',
    
    // Results
    'results.title': 'Résultat du diagnostic',
    'results.confidence': 'Confiance',
    'results.recommendation': 'Recommandation',
    'results.probabilities': 'Probabilités de classe',
    'results.showExplanation': 'Afficher l\'explication IA',
    'results.hideExplanation': 'Masquer l\'explication IA',
    
    // Features
    'features.lightningFast': 'Ultra rapide',
    'features.highlyAccurate': 'Hautement précis',
    'features.detailedInsights': 'Informations détaillées',
    
    // Medical Disclaimer
    'disclaimer.title': 'Avertissement médical',
    'disclaimer.text': 'Cet outil est uniquement à des fins de recherche et d\'éducation. Consultez toujours un professionnel de la santé qualifié pour un diagnostic médical.',
  },
  
  wo: {
    // Common
    'common.loading': 'Ci yépp...',
    'common.error': 'Njëkk',
    'common.success': 'Dëgg',
    'common.save': 'Aar',
    'common.cancel': 'Yiw',
    'common.confirm': 'Jeex',
    'common.close': 'Taw',
    
    // Navigation
    'nav.home': 'Kanam',
    'nav.features': 'Jëfandikoo',
    'nav.pricing': 'Njëkkee',
    'nav.contact': 'Soxla',
    
    // Hero
    'hero.title': 'RetinaScan AI',
    'hero.subtitle': 'Seet woon ci xam-xam bu tëy bu gën a am ag jiital ci seet mbootum bët ci xamul mëtë',
    'hero.description': 'Gën a seet ci dëgg ci mbootum bët ngir xam mëtë',
    'hero.getStarted': 'Jëkk',
    'hero.learnMore': 'Yéen xam leen',
    
    // Upload
    'upload.title': 'Yeb nu mbootum bët',
    'upload.instructions': 'Taxawal ngir yeb walla tënkal',
    'upload.formats': 'PNG, JPG, JPEG (max 16MB)',
    'upload.analyze': 'Seet mbootum',
    'upload.analyzing': 'Seet ci...',
    'upload.change': 'Sopp mbootum',
    
    // Results
    'results.title': 'Xeetug seet',
    'results.confidence': 'Sikker',
    'results.recommendation': 'Njàng',
    'results.probabilities': 'Rëy ci klas',
    'results.showExplanation': 'Wone njàngum AI',
    'results.hideExplanation': 'Soxlu njàngum AI',
    
    // Features
    'features.lightningFast': 'Yàgg loolu',
    'features.highlyAccurate': 'Gën a dëgg',
    'features.detailedInsights': 'Xam-xam bu laafa',
    
    // Medical Disclaimer
    'disclaimer.title': 'Jëmaleem pënd',
    'disclaimer.text': 'Lëkkal bii mooy jëlal ci njàngaleek ci fekk. Loolu mooy seet ndong ak fàttalikatu bu gën a am ag jëmaleem.',
  },
};

class I18n {
  private currentLanguage: Language = 'en';

  constructor() {
    // Try to load from localStorage
    const stored = localStorage.getItem('retinascan_language');
    if (stored && (stored === 'en' || stored === 'fr' || stored === 'wo')) {
      this.currentLanguage = stored as Language;
    } else {
      // Try to detect from browser
      const browserLang = navigator.language.split('-')[0];
      if (browserLang === 'fr') {
        this.currentLanguage = 'fr';
      } else {
        this.currentLanguage = 'en';
      }
    }
  }

  /**
   * Get translation for a key
   */
  t(key: string, params?: Record<string, string | number>): string {
    const translation = translations[this.currentLanguage]?.[key] || translations.en[key] || key;
    
    if (params) {
      return translation.replace(/\{\{(\w+)\}\}/g, (match, paramKey) => {
        return params[paramKey]?.toString() || match;
      });
    }
    
    return translation;
  }

  /**
   * Set current language
   */
  setLanguage(language: Language): void {
    this.currentLanguage = language;
    localStorage.setItem('retinascan_language', language);
    
    // Dispatch event for components to react
    window.dispatchEvent(new CustomEvent('language-change', { detail: { language } }));
  }

  /**
   * Get current language
   */
  getLanguage(): Language {
    return this.currentLanguage;
  }

  /**
   * Get all available languages
   */
  getAvailableLanguages(): Array<{ code: Language; name: string }> {
    return [
      { code: 'en', name: 'English' },
      { code: 'fr', name: 'Français' },
      { code: 'wo', name: 'Wolof' },
    ];
  }
}

export const i18n = new I18n();

// React hook for translations
export function useTranslation() {
  const [language, setLanguage] = React.useState<Language>(i18n.getLanguage());

  React.useEffect(() => {
    const handleLanguageChange = (event: CustomEvent<{ language: Language }>) => {
      setLanguage(event.detail.language);
    };

    window.addEventListener('language-change', handleLanguageChange as EventListener);
    
    return () => {
      window.removeEventListener('language-change', handleLanguageChange as EventListener);
    };
  }, []);

  return {
    t: (key: string, params?: Record<string, string | number>) => i18n.t(key, params),
    language,
    setLanguage: (lang: Language) => {
      i18n.setLanguage(lang);
      setLanguage(lang);
    },
    availableLanguages: i18n.getAvailableLanguages(),
  };
}


