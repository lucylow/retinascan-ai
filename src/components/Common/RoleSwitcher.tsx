import React from 'react';
import { useRole, UserRole } from '../../contexts/RoleContext';

export const RoleSwitcher: React.FC = () => {
  const { role, setRole } = useRole();

  const btn = (value: UserRole, label: string) => (
    <button
      onClick={() => setRole(value)}
      className={`px-3 py-1 rounded-md text-sm border ${
        role === value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-700 border-gray-300'
      }`}
      aria-pressed={role === value}
    >
      {label}
    </button>
  );

  return (
    <div className="flex items-center gap-2" aria-label="Switch role">
      {btn('clinician', 'Clinician')}
      {btn('patient', 'Patient')}
    </div>
  );
};


