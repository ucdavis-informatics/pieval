/*
  When you are finished with a pieval project, you may want to remove the project data
  Process:
  1. run the sibling file 'create_backup.sql' so you can recover from an oops moment
  1. modify this script with the project name of the data you wish to delete and run it
*/
-- RUN create_backup.sql!!!
delete from pieval.project_data where project_name = '<your project name here>'
