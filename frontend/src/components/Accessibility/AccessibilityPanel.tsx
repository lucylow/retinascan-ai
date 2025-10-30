import React from 'react';
import { AccessibilitySettings } from '../../types/retina';

interface AccessibilityPanelProps {
  settings: AccessibilitySettings;
  onSettingsChange: (settings: Partial<AccessibilitySettings>) => void;
  isOpen: boolean;
  onClose: () => void;
}

export const AccessibilityPanel: React.FC<AccessibilityPanelProps> = ({
  settings,
  onSettingsChange,
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div
      className="fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out"
      role="dialog"
      aria-label="Accessibility Settings"
    >
      <div className="p-6 h-full flex flex-col">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900">Accessibility Settings</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            aria-label="Close accessibility settings"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="space-y-6 flex-grow overflow-y-auto">
          <div className="space-y-3">
            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-lg font-medium text-gray-900">High Contrast Mode</span>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={settings.highContrast}
                  onChange={(e) => onSettingsChange({ highContrast: e.target.checked })}
                  className="sr-only"
                />
                <div className={`block w-14 h-8 rounded-full transition-colors ${
                  settings.highContrast ? 'bg-blue-600' : 'bg-gray-300'
                }`} />
                <div className={`absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${
                  settings.highContrast ? 'transform translate-x-6' : ''
                }`} />
              </div>
            </label>
            <p className="text-sm text-gray-600">Increase contrast for better visibility</p>
          </div>

          <div className="space-y-3">
            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-lg font-medium text-gray-900">Large Text</span>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={settings.largeText}
                  onChange={(e) => onSettingsChange({ largeText: e.target.checked })}
                  className="sr-only"
                />
                <div className={`block w-14 h-8 rounded-full transition-colors ${
                  settings.largeText ? 'bg-blue-600' : 'bg-gray-300'
                }`} />
                <div className={`absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${
                  settings.largeText ? 'transform translate-x-6' : ''
                }`} />
              </div>
            </label>
            <p className="text-sm text-gray-600">Increase text size throughout the application</p>
          </div>

          <div className="space-y-3">
            <label className="text-lg font-medium text-gray-900 block">Color Vision Mode</label>
            <select
              value={settings.colorBlindMode}
              onChange={(e) => onSettingsChange({
                colorBlindMode: e.target.value as AccessibilitySettings['colorBlindMode']
              })}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="none">Default Colors</option>
              <option value="protanopia">Protanopia (Red-Blind)</option>
              <option value="deuteranopia">Deuteranopia (Green-Blind)</option>
              <option value="tritanopia">Tritanopia (Blue-Blind)</option>
            </select>
            <p className="text-sm text-gray-600">Adjust colors for different types of color vision deficiency</p>
          </div>

          <div className="space-y-3">
            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-lg font-medium text-gray-900">Reduced Motion</span>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={settings.reducedMotion}
                  onChange={(e) => onSettingsChange({ reducedMotion: e.target.checked })}
                  className="sr-only"
                />
                <div className={`block w-14 h-8 rounded-full transition-colors ${
                  settings.reducedMotion ? 'bg-blue-600' : 'bg-gray-300'
                }`} />
                <div className={`absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${
                  settings.reducedMotion ? 'transform translate-x-6' : ''
                }`} />
              </div>
            </label>
            <p className="text-sm text-gray-600">Reduce animations and transitions</p>
          </div>

          <div className="space-y-3">
            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-lg font-medium text-gray-900">Screen Reader Optimized</span>
              <div className="relative">
                <input
                  type="checkbox"
                  checked={settings.screenReader}
                  onChange={(e) => onSettingsChange({ screenReader: e.target.checked })}
                  className="sr-only"
                />
                <div className={`block w-14 h-8 rounded-full transition-colors ${
                  settings.screenReader ? 'bg-blue-600' : 'bg-gray-300'
                }`} />
                <div className={`absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${
                  settings.screenReader ? 'transform translate-x-6' : ''
                }`} />
              </div>
            </label>
            <p className="text-sm text-gray-600">Optimize for screen reader compatibility</p>
          </div>
        </div>

        <div className="pt-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Apply Settings
          </button>
        </div>
      </div>
    </div>
  );
};


