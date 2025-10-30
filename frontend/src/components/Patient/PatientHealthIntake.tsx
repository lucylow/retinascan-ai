import React from 'react';

export interface PatientIntakeData {
  firstName: string;
  lastName: string;
  age: string;
  diabetesType: string;
  yearsWithDiabetes: string;
  medications: string;
  allergies: string;
  visionChanges: string;
  priorEyeConditions: string[];
  consentDataUse: boolean;
  preferredLanguage: string;
}

export default function PatientHealthIntake({
  onSubmit,
}: {
  onSubmit?: (data: PatientIntakeData) => void;
}) {
  const [form, setForm] = React.useState<PatientIntakeData>({
    firstName: '',
    lastName: '',
    age: '',
    diabetesType: '',
    yearsWithDiabetes: '',
    medications: '',
    allergies: '',
    visionChanges: '',
    priorEyeConditions: [],
    consentDataUse: false,
    preferredLanguage: 'en',
  });

  const [saving, setSaving] = React.useState(false);
  const update = (k: keyof PatientIntakeData, v: any) => setForm((f) => ({ ...f, [k]: v }));

  const toggleCondition = (key: string, checked: boolean) => {
    const list = new Set(form.priorEyeConditions);
    checked ? list.add(key) : list.delete(key);
    update('priorEyeConditions', Array.from(list));
  };

  const handleSubmit = async () => {
    if (!form.consentDataUse) {
      alert('Please provide consent to continue.');
      return;
    }
    setSaving(true);
    try {
      localStorage.setItem('patient_intake', JSON.stringify({ ...form, savedAt: new Date().toISOString() }));
      onSubmit?.(form);
      alert('Health intake saved.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Health Intake</h1>
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input className="input" placeholder="First name" value={form.firstName} onChange={(e) => update('firstName', e.target.value)} />
          <input className="input" placeholder="Last name" value={form.lastName} onChange={(e) => update('lastName', e.target.value)} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <input className="input" placeholder="Age" type="number" value={form.age} onChange={(e) => update('age', e.target.value)} />
          <select className="input" value={form.preferredLanguage} onChange={(e) => update('preferredLanguage', e.target.value)}>
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="wo">Wolof</option>
            <option value="sw">Swahili</option>
          </select>
        </div>

        <select className="input" value={form.diabetesType} onChange={(e) => update('diabetesType', e.target.value)}>
          <option value="">Diabetes type</option>
          <option value="t1">Type 1</option>
          <option value="t2">Type 2</option>
          <option value="gestational">Gestational</option>
          <option value="none">None</option>
        </select>
        <input className="input" placeholder="Years with diabetes" type="number" value={form.yearsWithDiabetes} onChange={(e) => update('yearsWithDiabetes', e.target.value)} />

        <textarea className="input min-h-[80px]" placeholder="Current medications" value={form.medications} onChange={(e) => update('medications', e.target.value)} />
        <textarea className="input min-h-[80px]" placeholder="Allergies" value={form.allergies} onChange={(e) => update('allergies', e.target.value)} />
        <textarea className="input min-h-[80px]" placeholder="Any recent vision changes?" value={form.visionChanges} onChange={(e) => update('visionChanges', e.target.value)} />

        <div>
          <div className="font-semibold text-gray-900 mb-2">Prior eye conditions</div>
          <div className="flex flex-wrap gap-4">
            {[
              { id: 'dr', label: 'Diabetic Retinopathy' },
              { id: 'glaucoma', label: 'Glaucoma' },
              { id: 'amd', label: 'AMD' },
            ].map((c) => (
              <label key={c.id} className="inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={form.priorEyeConditions.includes(c.id)}
                  onChange={(e) => toggleCondition(c.id, e.target.checked)}
                />
                <span>{c.label}</span>
              </label>
            ))}
          </div>
        </div>

        <label className="inline-flex items-start gap-2">
          <input type="checkbox" checked={form.consentDataUse} onChange={(e) => update('consentDataUse', e.target.checked)} />
          <span>I consent to the use of my data for screening and care coordination.</span>
        </label>

        <button
          onClick={handleSubmit}
          disabled={saving}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-60"
        >
          {saving ? 'Saving…' : 'Save & Continue'}
        </button>
      </div>
    </div>
  );
}


