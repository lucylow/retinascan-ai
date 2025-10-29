import { AuditLog, AuditLogSchema } from '@/lib/validation';

/**
 * Audit logging utility for compliance and tracking
 * Logs user actions that modify data or represent significant clinical decisions
 */

const AUDIT_STORAGE_KEY = 'retinascan_audit_logs';
const MAX_LOG_AGE = 7 * 24 * 60 * 60 * 1000; // 7 days

export class AuditLogger {
  /**
   * Log an audit event
   */
  static async log(action: string, resource: string, metadata?: Record<string, any>): Promise<void> {
    try {
      const session = await import('./session').then(m => m.SessionManager.get());
      
      const log: AuditLog = AuditLogSchema.parse({
        id: crypto.randomUUID(),
        userId: session?.id || 'anonymous',
        action,
        resource,
        timestamp: Date.now(),
        metadata,
        ipAddress: await this.getIPAddress(),
        userAgent: navigator.userAgent,
      });

      // Store in localStorage (in production, this would go to a backend)
      this.storeLog(log);

      // Also attempt to send to backend if available
      this.sendToBackend(log).catch(console.error);

      console.log('[Audit Log]', action, resource, metadata);
    } catch (error) {
      console.error('Failed to log audit event:', error);
    }
  }

  /**
   * Log prediction/analysis action
   */
  static async logPrediction(imageId: string, severityClass: number, confidence: number): Promise<void> {
    await this.log('prediction', 'retinal_image', {
      imageId,
      severityClass,
      confidence,
      type: 'ai_analysis',
    });
  }

  /**
   * Log data modification
   */
  static async logDataModification(resource: string, action: string, recordId: string, changes?: Record<string, any>): Promise<void> {
    await this.log(`${action}_${resource}`, resource, {
      recordId,
      changes,
      type: 'data_modification',
    });
  }

  /**
   * Log authentication events
   */
  static async logAuthentication(action: 'login' | 'logout' | 'session_refresh', userId: string): Promise<void> {
    await this.log(action, 'authentication', {
      userId,
      type: 'security',
    });
  }

  /**
   * Log export/download actions
   */
  static async logExport(resource: string, format: string, recordId?: string): Promise<void> {
    await this.log('export', resource, {
      format,
      recordId,
      type: 'data_export',
    });
  }

  /**
   * Store log in localStorage
   */
  private static storeLog(log: AuditLog): void {
    try {
      const stored = localStorage.getItem(AUDIT_STORAGE_KEY);
      const logs: AuditLog[] = stored ? JSON.parse(stored) : [];

      // Add new log
      logs.push(log);

      // Clean up old logs
      const cutoff = Date.now() - MAX_LOG_AGE;
      const filteredLogs = logs.filter(l => l.timestamp > cutoff);

      // Keep only last 1000 logs
      const recentLogs = filteredLogs.slice(-1000);

      localStorage.setItem(AUDIT_STORAGE_KEY, JSON.stringify(recentLogs));
    } catch (error) {
      console.error('Failed to store audit log:', error);
    }
  }

  /**
   * Send log to backend API
   */
  private static async sendToBackend(log: AuditLog): Promise<void> {
    try {
      // In production, this would send to your backend API
      // const response = await fetch('/api/audit', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(log),
      // });
      
      // For now, we'll just use console
      if (process.env.NODE_ENV === 'development') {
        console.log('[Audit] Would send to backend:', log);
      }
    } catch (error) {
      console.error('Failed to send audit log to backend:', error);
    }
  }

  /**
   * Get IP address (simplified - in production use proper service)
   */
  private static async getIPAddress(): Promise<string> {
    try {
      // In production, get IP from backend or use a service
      // For now, return a placeholder
      return 'client-side';
    } catch {
      return 'unknown';
    }
  }

  /**
   * Get audit logs (for admin/reporting)
   */
  static getLogs(userId?: string, startDate?: number, endDate?: number): AuditLog[] {
    try {
      const stored = localStorage.getItem(AUDIT_STORAGE_KEY);
      if (!stored) return [];

      let logs: AuditLog[] = JSON.parse(stored);

      // Filter by userId if provided
      if (userId) {
        logs = logs.filter(log => log.userId === userId);
      }

      // Filter by date range if provided
      if (startDate) {
        logs = logs.filter(log => log.timestamp >= startDate);
      }
      if (endDate) {
        logs = logs.filter(log => log.timestamp <= endDate);
      }

      return logs.sort((a, b) => b.timestamp - a.timestamp);
    } catch (error) {
      console.error('Failed to retrieve audit logs:', error);
      return [];
    }
  }
}

// Auto-log common user actions
if (typeof window !== 'undefined') {
  // Log page views
  const originalPushState = history.pushState;
  history.pushState = function(...args) {
    originalPushState.apply(history, args);
    AuditLogger.log('page_view', window.location.pathname).catch(console.error);
  };

  window.addEventListener('popstate', () => {
    AuditLogger.log('page_view', window.location.pathname).catch(console.error);
  });
}

