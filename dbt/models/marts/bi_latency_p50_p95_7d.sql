-- BI KPI: Latency distribution (p50/p95) over last 7 days
-- Depends on base table: predictions (must include inference_latency_ms and inference_ts)

select
  percentile_cont(0.5) within group (order by inference_latency_ms) as p50_ms,
  percentile_cont(0.95) within group (order by inference_latency_ms) as p95_ms,
  count(*) as n
from {{ ref('predictions') }}
where inference_ts >= now() - interval '7 days'
;


