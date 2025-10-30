-- BI: Per-clinic model performance (simplified accuracy/recall)
-- Depends on predictions, scans, feedbacks, devices

with joined as (
  select 
    d.clinic_id,
    p.predicted_class,
    f.corrected_class as correct_class
  from {{ ref('predictions') }} p
  join {{ ref('scans') }} s on s.scan_id = p.scan_id
  join {{ ref('devices') }} d on d.device_id = s.device_id
  join {{ ref('feedbacks') }} f on f.prediction_id = p.prediction_id
)

select
  clinic_id,
  avg(case when predicted_class = correct_class then 1 else 0 end) as accuracy,
  sum(case when predicted_class >= 2 and correct_class >= 2 then 1 else 0 end)::float
    / nullif(sum(case when correct_class >= 2 then 1 else 0 end),0) as recall_severe
from joined
group by 1
order by recall_severe desc nulls last
;


