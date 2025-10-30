/**
 * Configuration helper for environment variables
 */

export const config = {
  api: {
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  },
  supabase: {
    url: import.meta.env.VITE_SUPABASE_URL || '',
    anonKey: import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '',
  },
  
  isConfigured: () => {
    return !!(config.supabase.url && config.supabase.anonKey);
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
    apiBaseUrl: config.api.baseUrl,
    hasSupabaseUrl: !!config.supabase.url,
    hasAnonKey: !!config.supabase.anonKey,
    isConfigured: config.isConfigured(),
    missing: config.getMissingConfig(),
  });
}

