/**
 * Configuration helper for environment variables
 */

export const config = {
  supabase: {
    url: import.meta.env.VITE_SUPABASE_URL || '',
    anonKey: import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '',
  },
  
  backend: {
    apiUrl: import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000',
  },
  
  isConfigured: () => {
    return !!(config.supabase.url && config.supabase.anonKey);
  },
  
  isBackendConfigured: () => {
    return !!config.backend.apiUrl;
  },
  
  getMissingConfig: () => {
    const missing: string[] = [];
    if (!config.supabase.url) missing.push('VITE_SUPABASE_URL');
    if (!config.supabase.anonKey) missing.push('VITE_SUPABASE_PUBLISHABLE_KEY');
    return missing;
  },
};

// Log configuration status in development
if (import.meta.env.DEV) {
  console.log('🔧 Environment Configuration:', {
    hasSupabaseUrl: !!config.supabase.url,
    hasAnonKey: !!config.supabase.anonKey,
    backendApiUrl: config.backend.apiUrl,
    isSupabaseConfigured: config.isConfigured(),
    isBackendConfigured: config.isBackendConfigured(),
    missing: config.getMissingConfig(),
  });
}

