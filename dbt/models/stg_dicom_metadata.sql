-- Staging: DICOM metadata
select
	file_path,
	"StudyInstanceUID" as study_uid,
	"SeriesInstanceUID" as series_uid,
	"SOPInstanceUID" as instance_uid,
	"Modality" as modality,
	"StudyDate" as study_date,
	"PatientID" as patient_id,
	"PatientSex" as patient_sex,
	"PatientBirthDate" as patient_birth_date
from {{ source('raw', 'dicom_metadata') }}
