# Database Schema for pieval
pieval can use either the filesystem (a directory with set of csv files that >act< as a database) or a SQL RDBMS (currently in development).  The file system approach is great for local development while adding/testing new features.  It is not so great for production use...

Conventions used in this document.  Table means csv file when using the filesystem, and database table when using an RDBMS.  The csv files will have the same columns names at the RDBMS table.  This is by design.  To make development easy and production apps robust.  You can switch between the two modes by altering a flag in instance/config.py.  This is accomplished by encapsulating data access inside of a class definition, one class for file based persistence and one for RDBMS based persistence.

## Tables
These are the tables used in this project:  
1. annotation_events - Annotations from system users are saved here
1. project_classes - If the project is collecting annotations for a multi-class problem the class list is stored here
1. project_data - These are the annotation examples that get presented to the user
1. project_users - simple 2 column table, one row for each project_name:user_name pair.  An entry in this table gives the user permissions to annotate on that project
1. projects - Defines each unique project with a name, description and mode

### annotation_events
Unique_key: response_time, project_name, user_name, example_id

response_time - timestamp of response event
project_name - unique project name
user_name - unique user_name
user_ip - IP address from which the response was submitted
example_id - The specific example within the project_name to which the response applies
response - the response value

### project_classes
Contains entries for class values in multiclass projects.  If the project has 13 classes, there will be 13 rows in this table
Unique_key: project_name, class

project_name - unique project name
class - class value


#### project_data
Unique_key: project_name, example_id
project_name - unique project name
example_id - the unique_id of this example
source_id - the unique source_id of this example.  Allows us to tie annotations back to original data
data - the data presented to the user for review
prompt - The prompt containing the assertion the user either agrees or disagrees with

#### project_users
project_name - unique project name
user_name - user_name

#### projects
name - unique project name
description - Short description of the project to be displayed to users


### Helper SQL
```SQL
select * from annotation_events;

select * from project_data;

select * from project_users;

select * from projects;
```
