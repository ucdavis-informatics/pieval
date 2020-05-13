/*
  Creates a backup of the pieval tables.
  Assumes you are creating the backup in the SAME database as the current tables
  but in a schema named pieval_backup
  NOTE: script syntax assumes MSSQL.  Wont work for oracle, the other db supported unless the table has been previously created.
*/
drop table pieval_backup.annotation_events;
select * into pieval_backup.annotation_events from pieval.annotation_events;
drop table pieval_backup.project_classes;
select * into pieval_backup.project_classes from pieval.project_classes;
drop table pieval_backup.project_data;
select * into pieval_backup.project_data from pieval.project_data;
drop table pieval_backup.project_users;
select * into pieval_backup.project_users from pieval.project_users;
drop table pieval_backup.projects;
select * into pieval_backup.projects from pieval.projects;