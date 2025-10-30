import { useState, useEffect } from 'react';
import { AccessibilitySettings } from '../types/retina';

export const useAccessibility = () => {
  const [settings, setSettings] = useState<AccessibilitySettings>({
    highContrast: false,
    largeText: false,
    screenReader: false,
    colorBlindMode: 'none',
    reducedMotion: false,
    voiceNavigation: false,
  });

  useEffect(() => {
    const saved = localStorage.getItem('retinaScan_accessibility');
    if (saved) {
      try {
        setSettings(JSON.parse(saved));
      } catch {
        // ignore invalid JSON
      }
    }
  }, []);

  useEffect(() => {
    const root = document.documentElement;

    if (settings.highContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    if (settings.largeText) {
      root.classList.add('large-text');
    } else {
      root.classList.remove('large-text');
    }

    if (settings.reducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }

    root.setAttribute('data-color-blind', settings.colorBlindMode);

    localStorage.setItem('retinaScan_accessibility', JSON.stringify(settings));
  }, [settings]);

  const updateSettings = (newSettings: Partial<AccessibilitySettings>) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  return { settings, updateSettings };
};


