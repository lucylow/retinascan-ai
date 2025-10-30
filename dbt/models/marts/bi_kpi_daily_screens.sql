-- BI KPI: Daily screens and positive rate (last 30 days)
-- Depends on base tables: scans, predictions

with base as (
  select 
    date_trunc('day', s.upload_ts) as day,
    p.predicted_class
  from {{ ref('scans') }} s
  join {{ ref('predictions') }} p on p.scan_id = s.scan_id
  where s.upload_ts >= now() - interval '30 days'
)

select
  day,
  count(*) as screens,
  sum(case when predicted_class >= 2 then 1 else 0 end)::float / nullif(count(*),0) as positive_rate
from base
group by 1
order by 1
;


