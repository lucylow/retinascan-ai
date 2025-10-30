-- Staging: Biostrap vitals
select
	cast(timestamp as timestamp) as observed_at,
	userId as user_id,
	heartRate as heart_rate,
	respirationRate as respiration_rate,
	* except(timestamp, userId, heartRate, respirationRate)
from {{ source('raw', 'biostrap_heart_rate') }} -- adjust if using different schemas
