import React, { useEffect, useRef, useState } from 'react';

interface AutoSaveNoteProps {
  storageKey: string;
  placeholder?: string;
}

export const AutoSaveNote: React.FC<AutoSaveNoteProps> = ({ storageKey, placeholder }) => {
  const [value, setValue] = useState('');
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const saveTimeout = useRef<number | null>(null);

  useEffect(() => {
    const existing = localStorage.getItem(storageKey);
    if (existing) setValue(existing);
  }, [storageKey]);

  useEffect(() => {
    if (saveTimeout.current) window.clearTimeout(saveTimeout.current);
    saveTimeout.current = window.setTimeout(() => {
      localStorage.setItem(storageKey, value);
      setSavedAt(new Date().toLocaleTimeString());
    }, 600);
    return () => {
      if (saveTimeout.current) window.clearTimeout(saveTimeout.current);
    };
  }, [value, storageKey]);

  return (
    <div>
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="w-full min-h-[120px] p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
        placeholder={placeholder || 'Add clinical notes...'}
      />
      <div className="text-xs text-gray-500 mt-1" aria-live="polite">
        {savedAt ? `Auto-saved at ${savedAt}` : 'Typing… auto-save enabled'}
      </div>
    </div>
  );
};


