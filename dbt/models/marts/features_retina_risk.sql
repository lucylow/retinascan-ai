-- Mart: features for retina risk modeling (example)
with last_hba1c as (
	select subject_ref, max(effective_at) as last_obs_at
	from {{ ref('stg_fhir_observation') }}
	group by 1
), a1c as (
	select o.subject_ref, o.value as hba1c, o.unit, o.effective_at
	from {{ ref('stg_fhir_observation') }} o
	join last_hba1c l on l.subject_ref = o.subject_ref and l.last_obs_at = o.effective_at
)
select
	d.patient_id,
	a.hba1c,
	a.unit as hba1c_unit,
	b.heart_rate,
	b.respiration_rate,
	d.modality,
	d.study_date
from {{ ref('stg_dicom_metadata') }} d
left join a1c a on a.subject_ref like concat('%', d.patient_id)
left join {{ ref('stg_biostrap') }} b on true -- align by time in a real model
