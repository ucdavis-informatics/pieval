# Persistence architecture
The pieval webapp is data driven.  The app reads and writes data from/to the persistence layer.  It reads project specific configuration to set up the correct annotation workflows.  It writes the annotations captured from the user.  Pieval can use either filesystem (csv) or a relational database (Oracle or MSSQL) as the persistence layer.  Think of the filesystem persistence strategy as a 'cheap database' and, in this context, think of the csv files as tables.  The filesystem option is intended to be used primarily during development and/or demonstrations.  This allows for extremely rapid protoyping against a table like structure that can later be ported to a SQL database for production use.  This means that the csv files and sql tables should have similar structure as development unfolds.
It is reccomended that a SQL database be used for production deployments.  The app has been tested against Oracle and MSSQL.  With very minor modifications, it should work against any SQL database of your choosing.


## Tables (or csv file names)
1. annotation_events - Annotations from system users are saved here
1. project_classes - If the project is collecting annotations for a multi-class problem the class list is stored here
1. project_data - These are the annotation examples that get presented to the user
1. project_users - simple 2 column table, one row for each project_name:user_name pair.  An entry in this table gives the user permissions to annotate on that project
1. projects - Defines each unique project with a name, description and mode
1. user_details - Contains users print name and email address to be used in system prompts or communications

---
### annotation_events
Unique_key: response_time, project_name, user_name, example_id

1. response_time - timestamp of response event  
1. project_name - unique project name  
1. user_name - unique user_name  
1. user_ip - IP address from which the response was submitted  
1. example_id - The specific example within the project_name to which the response applies  
1. response - the response value  
1. context_viewed - Set to 'yes' if the annotator looked at the expanded context, i.e. non-truncated, data when making their decision.  Default 'no'  

---
### project_classes
Unique_key: project_name, class

Columns:  
1. project_name - unique project name  
1. class - class value

---
#### project_data
Unique_key: project_name, example_id

Columns:
1. project_name - unique project name
1. example_id - the unique_id of this example
1. source_id - the unique source_id of this example.  Allows us to tie annotations back to original data
1. data - the data presented to the user for review, commonly truncated from source (aka enriched  with the content specific to the annotation task)
1. data_ext - the data presented to the user for review, the full source of the original report from which the truncated/enriched content was selected
1. prompt - The prompt containing the assertion the user either agrees or disagrees with

---
#### project_users
Columns:  
1. project_name - unique project name
1. user_name - user_name

---
#### projects
Columns:  
1. project_name - unique project name
1. description - Short description of the project to be displayed to users
1. project_mode - Binary or Multiclass.  This alters the disagreement workflow to capture correct class in multiclass projects

---
#### User Details
Columns:  
1. user_name - unique username  
1. print_name - Printable name for use in system prompts and generated emails/communication  
1. email - Users email for system communication  


## Building the schema in SQL
We include code that automates the build of a SQL database, based on a combination of the example csv files (if you want to include the demo data) and table_metadata.py to ensure the correct datatypes.  Follow these steps to create a SQL database in your environment.

### Step 1 Create the schemas
We reccomend 3 schemas to optimally run PieVal:
1. pieval
1. pieval_stage
1. pieval_backup

**Oracle**  
In Oracle users are equal to schemas, so we create a pieval user.  
```sql
-- pieval
create user pieval identified by a_strong_password;
grant create table to pieval;
grant create session to pieval;
grant unlimited tablespace to pieval;
-- pieval_stage
create user pieval_stage identified by a_strong_password;
grant create table to pieval_stage;
grant create session to pieval_stage;
grant unlimited tablespace to pieval_stage;
-- pieval_backup
create user pieval_backup identified by a_strong_password;
grant create table to pieval_backup;
grant create session to pieval_backup;
grant unlimited tablespace to pieval_backup;
```

**MSSQL**
In MSSQL, the meaning of schema is a bit different.  Assuming you 'own' a database in MSSQL, all you need to do is create the pieval schema with this command:  
```sql
CREATE SCHEMA pieval;
CREATE SCHEMA pieval_stage;
CREATE SCHEMA pieval_backup;
```

### Step 2 - update instance/config.py with the details for your database
**NOTE:** We assume you are using Vault to provide secrets as a service, which means we inlcude only a Vault Secret Path in config.py.  Please see README_vault for more information about Vault as well as what to do if Vault is not available to you.
1. Modify instance/config.py with the database parameters of your choosing
  - Set DATASOURCE_TYPE = 'db'
  - Set DATASOURCE_LOCATION = <vault path of your desired database>

### Step 3 - run the build_sql_database.py script
```sh
# flip yes to no in the keep_example_data argument if you want an empty database
# flip build to updated in build_or_update argument to have your current database upgraded to latest version!
pipenv run python build_sql_database.py --keep_example_data yes --build_or_update build
```
