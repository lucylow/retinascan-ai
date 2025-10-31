// Lightweight demo API to simulate clinician and patient data fetching

export interface ClinicalBatchItem {
  patientId: string;
  name: string;
  age: number;
  history: string[];
  latestDiagnosis: string;
  drGrade: string;
  confidence: number; // 0..1
  referralRequired: boolean;
}

export async function getBatchResults(): Promise<ClinicalBatchItem[]> {
  return [
    {
      patientId: 'p123',
      name: 'John Doe',
      age: 58,
      history: ['Type 2 diabetes', 'Hypertension'],
      latestDiagnosis: 'Visit 2025-10-15',
      drGrade: 'Moderate',
      confidence: 0.89,
      referralRequired: true,
    },
    {
      patientId: 'p124',
      name: 'Jane Smith',
      age: 47,
      history: ['Type 1 diabetes'],
      latestDiagnosis: 'Visit 2025-09-08',
      drGrade: 'No DR',
      confidence: 0.93,
      referralRequired: false,
    },
  ];
}

export async function fetchClinicalGuidelines(): Promise<string> {
  return [
    'Refer severe/proliferative DR cases immediately.',
    'Screening recommended annually for diabetics.',
    'Refer to ophthalmology for positive glaucoma risk.',
  ].join('\n');
}

export async function getLatestPatientResults(): Promise<{
  drGrade: string;
  confidence: number; // 0..1
  requiresReferral: boolean;
}> {
  return {
    drGrade: 'Mild',
    confidence: 0.78,
    requiresReferral: false,
  };
}

export async function getEducationalContent(): Promise<string> {
  return [
    'Diabetic retinopathy is a diabetes complication that can cause blindness if untreated.',
    'Regular screening and early treatment can prevent vision loss.',
  ].join('\n');
}

export async function getNearbyClinics(): Promise<
  Array<{ id: string; name: string; address: string; phone: string; website: string }>
> {
  return [
    {
      id: 'c1',
      name: 'City Optometry Clinic',
      address: '123 Main St',
      phone: '123-456-7890',
      website: 'https://cityoptometry.com',
    },
    {
      id: 'c2',
      name: 'Regional Eye Center',
      address: '456 Elm Rd',
      phone: '098-765-4321',
      website: 'https://regionaleye.org',
    },
  ];
}


