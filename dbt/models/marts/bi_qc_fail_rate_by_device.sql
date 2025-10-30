-- BI: QC Failure rate by device (last 14 days)
-- Assumes scans.quality_flags contains an array or jsonb with failure reasons

with base as (
  select 
    s.device_id,
    s.upload_ts,
    (coalesce(jsonb_array_length(s.quality_flags), 0) > 0) as failed_qc
  from {{ ref('scans') }} s
  where s.upload_ts >= now() - interval '14 days'
)

select
  device_id,
  avg(case when failed_qc then 1 else 0 end) as qc_fail_rate,
  count(*) as screens
from base
group by 1
having avg(case when failed_qc then 1 else 0 end) > 0.0
order by qc_fail_rate desc
;


