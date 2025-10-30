-- BI: Utilization heatmap (hour-of-day x day-of-week) counts
-- Based on scans.upload_ts

select 
  extract(dow from upload_ts)::int as dow,
  extract(hour from upload_ts)::int as hour,
  count(*) as screens
from {{ ref('scans') }}
where upload_ts >= now() - interval '30 days'
group by 1,2
order by 1,2
;


