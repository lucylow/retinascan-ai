/**
 * Configuration helper for environment variables
 */

export const config = {
  api: {
    // Flask backend base URL; override with VITE_API_BASE_URL in .env
    baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
  },
  supabase: {
    url: import.meta.env.VITE_SUPABASE_URL || '',
    anonKey: import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '',
  },
  
  isConfigured: () => {
    // Frontend can work with either backend API or Supabase function
    const hasApi = !!config.api.baseUrl;
    const hasSupabase = !!(config.supabase.url && config.supabase.anonKey);
    return hasApi || hasSupabase;
  },
  
  getMissingConfig: () => {
    const missing: string[] = [];
    // Only mark Supabase vars missing if none of the backends are configured
    if (!config.api.baseUrl) missing.push('VITE_API_BASE_URL');
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

