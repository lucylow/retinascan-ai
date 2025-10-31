import React, { createContext, useContext, useMemo, useState } from 'react';

export type UserRole = 'clinician' | 'patient';

interface RoleContextValue {
  role: UserRole;
  setRole: (role: UserRole) => void;
}

const RoleContext = createContext<RoleContextValue | undefined>(undefined);

export const RoleProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [role, setRole] = useState<UserRole>('clinician');
  const value = useMemo(() => ({ role, setRole }), [role]);
  return <RoleContext.Provider value={value}>{children}</RoleContext.Provider>;
};

export const useRole = () => {
  const ctx = useContext(RoleContext);
  if (!ctx) throw new Error('useRole must be used within RoleProvider');
  return ctx;
};


