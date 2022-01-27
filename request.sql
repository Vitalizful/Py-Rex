select patient_num, location_cd, start_date, observation_blob
from observation_fact
where scheme_key = 'IMA:'
and LOCATION_CD = '/cpt_ren_ide=0001840777'
-- and START_DATE >= '$s'
--and contains (observation_blob, 'RECIST', 1) > 0
order by patient_num, start_date
