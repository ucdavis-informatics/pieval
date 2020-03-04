/*
  Script to review annotations per project per user in Prod and Dev on cdi3sql01
  This script is specific to MSSQL and must be run after connecting as 'master'
*/
-- Annoations per project/per user in PROD
select
  project_name,
  user_name,
  count(*)
from
  CDI3_Prod.pieval.annotation_events
group by
  project_name,
  user_name
order by
  project_name,
  user_name;


-- Annoations per project/per user in Dev
select
  project_name,
  user_name,
  count(*)
from
  CDI3_dev.pieval.annotation_events
group by
  project_name,
  user_name
order by
  project_name,
  user_name;
