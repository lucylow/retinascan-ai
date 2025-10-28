import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
const SUPABASE_PUBLISHABLE_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '';

// Create a mock client with stub methods when credentials are missing
const createMockClient = (): any => {
  return {
    functions: {
      invoke: () => Promise.resolve({ 
        data: null, 
        error: { message: 'Supabase credentials not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY' } 
      })
    }
  };
};

export const supabase = SUPABASE_URL && SUPABASE_PUBLISHABLE_KEY 
  ? createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
      auth: {
        storage: localStorage,
        persistSession: true,
        autoRefreshToken: true,
      }
    })
  : createMockClient();