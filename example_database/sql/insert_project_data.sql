/*
Script to insert data into the LIVE project_data table
Process:
1. Stage a new custom table in the pieval_stage schema with columns matching those
in the project_data table.  See the README file in pieval/example_database for
table info
2. Use this script to insert new data into the project data table
*/
insert into pieval.project_data(project_name, example_id, source_id, [data], data_ext, prompt)
select project_name, example_id, source_id, data, data_ext, prompt
from pieval_stage.<YOUR TABLE NAME HERE>;



--QA
-- Make sure the PK is unique, it's not set as an enforced constraint on the table
select
  project_name,
  example_id,
  count(*) as count_should_be_1
from
  pieval.project_data
group by
  project_name,
  example_id
order by
  count(*) desc;
