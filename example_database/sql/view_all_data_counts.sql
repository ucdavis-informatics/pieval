select project_name, count(*) from pieval.annotation_events group by project_name;
select project_name, count(*) from pieval.project_classes group by project_name;
select project_name, count(*) from pieval.project_data group by project_name;
select project_name, count(*) from pieval.project_users group by project_name;
select project_name, count(*) from pieval.projects group by project_name;