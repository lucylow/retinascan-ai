import { z } from 'zod';

// Prediction response validation
export const PredictionResponseSchema = z.object({
  severity_class: z.number().int().min(0).max(4),
  severity_level: z.string(),
  confidence: z.number().min(0).max(1),
  label: z.string(),
  recommendation: z.string(),
  structured_recommendation: z.object({
    action: z.string(),
    urgency: z.string(),
    follow_up_time: z.string(),
    note: z.string(),
  }).optional(),
  class_probabilities: z.record(z.string(), z.number().min(0).max(1)),
  visualization: z.object({
    grad_cam_overlay: z.string().url().optional(),
    description: z.string().optional(),
  }).optional(),
  uncertainty: z.object({
    epistemic: z.number().min(0).max(1).optional(),
    confidence_interval: z.object({
      lower: z.number().min(0).max(1),
      upper: z.number().min(0).max(1),
    }).optional(),
  }).optional(),
  risk_stratification: z.object({
    risk_level: z.string(),
    requires_specialist_review: z.boolean(),
    recommendation_note: z.string(),
  }).optional(),
});

export type PredictionResponse = z.infer<typeof PredictionResponseSchema>;

// User session validation
export const UserSessionSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  role: z.enum(['patient', 'clinician', 'admin']),
  name: z.string().optional(),
  expiresAt: z.number(),
  lastActivity: z.number(),
});

export type UserSession = z.infer<typeof UserSessionSchema>;

// Contact form validation
export const ContactFormSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  company: z.string().optional(),
  message: z.string().min(10, 'Message must be at least 10 characters'),
  interest: z.array(z.string()).optional(),
});

export type ContactForm = z.infer<typeof ContactFormSchema>;

// Image upload validation
export const ImageUploadSchema = z.object({
  file: z.instanceof(File),
  maxSize: z.number().default(16 * 1024 * 1024), // 16MB
  allowedTypes: z.array(z.string()).default(['image/png', 'image/jpeg', 'image/jpg']),
});

// Audit log validation
export const AuditLogSchema = z.object({
  id: z.string(),
  userId: z.string(),
  action: z.string(),
  resource: z.string(),
  timestamp: z.number(),
  metadata: z.record(z.string(), z.any()).optional(),
  ipAddress: z.string().optional(),
  userAgent: z.string().optional(),
});

export type AuditLog = z.infer<typeof AuditLogSchema>;

