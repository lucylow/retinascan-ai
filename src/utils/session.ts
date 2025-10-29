import { UserSession, UserSessionSchema } from '@/lib/validation';

/**
 * Session management utilities
 * Handles secure token refresh and timeout logic
 */

const SESSION_STORAGE_KEY = 'retinascan_session';
const TOKEN_REFRESH_THRESHOLD = 5 * 60 * 1000; // 5 minutes before expiry
const INACTIVITY_TIMEOUT = 30 * 60 * 1000; // 30 minutes

export class SessionManager {
  private static session: UserSession | null = null;
  private static refreshTimer: NodeJS.Timeout | null = null;
  private static inactivityTimer: NodeJS.Timeout | null = null;

  /**
   * Initialize session from storage
   */
  static initialize(): UserSession | null {
    try {
      const stored = localStorage.getItem(SESSION_STORAGE_KEY);
      if (!stored) return null;

      const parsed = JSON.parse(stored);
      const session = UserSessionSchema.parse(parsed);

      // Check if session is expired
      if (session.expiresAt < Date.now()) {
        this.clear();
        return null;
      }

      this.session = session;
      this.startRefreshTimer();
      this.startInactivityTimer();
      return session;
    } catch (error) {
      console.error('Failed to initialize session:', error);
      this.clear();
      return null;
    }
  }

  /**
   * Create new session
   */
  static create(sessionData: Omit<UserSession, 'lastActivity'>): UserSession {
    const session: UserSession = {
      ...sessionData,
      lastActivity: Date.now(),
    };

    this.session = UserSessionSchema.parse(session);
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session));
    this.startRefreshTimer();
    this.startInactivityTimer();
    return session;
  }

  /**
   * Get current session
   */
  static get(): UserSession | null {
    if (!this.session) {
      return this.initialize();
    }

    // Check if expired
    if (this.session.expiresAt < Date.now()) {
      this.clear();
      return null;
    }

    // Update last activity
    this.updateActivity();
    return this.session;
  }

  /**
   * Update last activity timestamp
   */
  static updateActivity(): void {
    if (!this.session) return;

    this.session.lastActivity = Date.now();
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(this.session));
    this.startInactivityTimer();
  }

  /**
   * Refresh session token
   */
  static async refresh(): Promise<UserSession | null> {
    if (!this.session) return null;

    try {
      // In a real implementation, this would call your auth API
      // For now, we'll extend the expiry time
      const newExpiresAt = Date.now() + 60 * 60 * 1000; // 1 hour from now

      this.session.expiresAt = newExpiresAt;
      this.session.lastActivity = Date.now();

      localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(this.session));
      this.startRefreshTimer();

      return this.session;
    } catch (error) {
      console.error('Failed to refresh session:', error);
      this.clear();
      return null;
    }
  }

  /**
   * Clear session
   */
  static clear(): void {
    this.session = null;
    localStorage.removeItem(SESSION_STORAGE_KEY);
    this.stopRefreshTimer();
    this.stopInactivityTimer();
  }

  /**
   * Start token refresh timer
   */
  private static startRefreshTimer(): void {
    this.stopRefreshTimer();

    if (!this.session) return;

    const timeUntilExpiry = this.session.expiresAt - Date.now();
    const refreshTime = Math.max(timeUntilExpiry - TOKEN_REFRESH_THRESHOLD, 0);

    this.refreshTimer = setTimeout(() => {
      this.refresh();
    }, refreshTime);
  }

  /**
   * Stop refresh timer
   */
  private static stopRefreshTimer(): void {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  /**
   * Start inactivity timer
   */
  private static startInactivityTimer(): void {
    this.stopInactivityTimer();

    this.inactivityTimer = setTimeout(() => {
      // Session expired due to inactivity
      this.clear();
      
      // Trigger event for UI to react
      window.dispatchEvent(new CustomEvent('session-expired', { 
        detail: { reason: 'inactivity' } 
      }));
    }, INACTIVITY_TIMEOUT);
  }

  /**
   * Stop inactivity timer
   */
  private static stopInactivityTimer(): void {
    if (this.inactivityTimer) {
      clearTimeout(this.inactivityTimer);
      this.inactivityTimer = null;
    }
  }

  /**
   * Check if user has required role
   */
  static hasRole(role: UserSession['role']): boolean {
    const session = this.get();
    if (!session) return false;

    const roleHierarchy: Record<UserSession['role'], number> = {
      patient: 0,
      clinician: 1,
      admin: 2,
    };

    return roleHierarchy[session.role] >= roleHierarchy[role];
  }
}

// Initialize on module load
if (typeof window !== 'undefined') {
  SessionManager.initialize();

  // Track user activity
  ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach((event) => {
    document.addEventListener(event, () => SessionManager.updateActivity(), { passive: true });
  });
}

