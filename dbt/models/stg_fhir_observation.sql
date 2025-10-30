-- Staging: FHIR Observation (example for HbA1c)
select
	(resource->>'id') as observation_id,
	(resource#>>'{subject,reference}') as subject_ref,
	(resource#>>'{code,coding,0,code}') as loinc_code,
	(resource#>>'{valueQuantity,value}')::numeric as value,
	(resource#>>'{valueQuantity,unit}') as unit,
	(resource->>'effectiveDateTime')::timestamp as effective_at
from {{ source('raw', 'fhir_observation') }}
where (resource#>>'{code,coding,0,system}') = 'http://loinc.org'
