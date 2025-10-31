export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: 'male' | 'female' | 'other';
  diabetesType: 'type1' | 'type2' | 'gestational';
  diabetesDuration: number; // years
  lastScreening: string | null;
  riskLevel: 'low' | 'medium' | 'high';
}

export interface RetinaScan {
  id: string;
  patientId: string;
  image: File | string;
  uploadDate: string;
  status: 'uploading' | 'processing' | 'completed' | 'failed';
  eye: 'left' | 'right' | 'both';
  quality: number; // 0-100
}

export interface AnalysisResult {
  id: string;
  scanId: string;
  patientId: string;
  confidence: number;
  severity: 'none' | 'mild' | 'moderate' | 'severe' | 'proliferative';
  findings: string[];
  recommendations: string[];
  riskScore: number;
  processedDate: string;
  highlightedAreas: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
    type: 'microaneurysm' | 'hemorrhage' | 'exudate' | 'edema';
    confidence: number;
  }>;
}

export interface AccessibilitySettings {
  highContrast: boolean;
  largeText: boolean;
  screenReader: boolean;
  colorBlindMode: 'none' | 'protanopia' | 'deuteranopia' | 'tritanopia';
  reducedMotion: boolean;
  voiceNavigation: boolean;
}


