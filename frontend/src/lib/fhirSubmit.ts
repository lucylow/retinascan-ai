export async function submitIntakeToFHIR(
  patientId: string,
  form: any,
  token: string,
  baseUrl: string
) {
  const resource = {
    resourceType: 'QuestionnaireResponse',
    status: 'completed',
    subject: { reference: `Patient/${patientId}` },
    authored: new Date().toISOString(),
    item: [
      { linkId: 'diabetesType', text: 'Diabetes Type', answer: [{ valueString: form.diabetesType }] },
      { linkId: 'yearsWithDiabetes', text: 'Years with diabetes', answer: [{ valueInteger: Number(form.yearsWithDiabetes) }] },
      { linkId: 'medications', text: 'Medications', answer: [{ valueString: form.medications }] },
      { linkId: 'allergies', text: 'Allergies', answer: [{ valueString: form.allergies }] },
      { linkId: 'visionChanges', text: 'Vision changes', answer: [{ valueString: form.visionChanges }] },
      { linkId: 'priorEyeConditions', text: 'Prior eye conditions', answer: (form.priorEyeConditions || []).map((x: string) => ({ valueString: x })) },
    ],
  } as const;

  const res = await fetch(`${baseUrl}/QuestionnaireResponse`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/fhir+json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(resource),
  });

  if (!res.ok) throw new Error('FHIR submission failed');
  return res.json();
}


