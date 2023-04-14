# Creating Pieval projects and adding your own data
When it's time to add your own data and create a new project in PieVal there are 3 major steps to accomplish this step.

1. Define/Create a project - Add an entry to projects.csv OR the projects table in your preferred database, filling out all columns
    - This determines the prject name, data type, and annotation mode (binary or multiclass)
1. Add Users to the project - Add entries to project_users.csv OR the project_users table in your preferred database
    - Add one entry for each user
1. Add data to project_data
    - You should first stage your data, then move it into whatever persistence strategy you are using to run the app.  See below

The process will be different depending upon whether or not you are using the Filesystem backend or the DB backend.  Since the filesystem backend is intended primarily for development we have not developed any helpful tooling to add data to these files.  Instead, we intended for manual updates since these files should only be used to house a limited number of examples to test out new features.  On the Database side, we do include a few helpful scripts that will help create/upgrade your database schema and load pre-staged data as a new project into PieVal.  The rest of this document will focus on describing the database sepcific tooling.

## Using the PieVal project create/delete helpers
> Assumptions:
> - You have already configured your database according to [README_Persistence.md](README_Persistence.md)

### Creating Projects - using create_project.py
The first step of creating a new project is to stage some data that needs human annoation.  To do this, create a table with these columns (See the project_data section of [README_Persistence.md](README_Persistence.md) for column definitions):
```py
pieval_cols=['project_name','example_id','source_id','data','data_ext','prompt']
```

Each row should be a unique annotation event that requires review from a subject matter expert.
> Pro Tip: Sometimes multiple annoation events contain duplicated data.  By duplicating data, you can measure intra-annotator agreement by measuring how often each revieiwer agrees with their own assessments!

IF your project requires multi-class annotations you must also define what the range of class annoations could be in a simple two column table with the following columns:
1. project_name
1. class
There should be one row for each possible class label. (See the project_classes section of [README_Persistence.md](README_Persistence.md) for column definitions) 

#### Running Project Creation step
Review the project create CLI api here:
```shell script
$ python create_project.py --help
```

Assuming:  
staging table: test_project_data  
users: test1, test2  
project description: 'test project description'  
project mode: binary  

The command would look like:

```shell script
$ python create_project.py -dt test_project_data \
-u test1 \
-u test2 \
-pd "test project description" \
-pm binary
```

> Pro Tip: since PieVal does not manage its own Auth directly, only usernames are provided here, no passwords.  You must keep in mind that only usernames that KeyCloak is aware of, either directly, or via a pass through mechanism can possibly gain access to the PieVal app

> NOTE: The create proejct script does not accept a project_name directly.  Project name will be drawn from the project name column in your staging table.  Be sure you are happy with this as a name BEFORE running this script!

### Deleting Projects - using delete_project.py
Delting a project is easy, almost too easy!  Simply call the delete_project.py script with a single paramenter, project name and all project data will be deleted for you.  To help ensure you don't lose any data, a full backup will be created in the pieval backup schema.  It is up to you to use this tool responsibly.  Please ensure you have captured the data you want BEFORE removing a project.  The backup does exist, but you should not rely on it!  This is implemented as a CLI script.  The API can be examined here:
```shell script
$ python delete_project.py --help
```

A specific example (assuming you have a project named 'test_project' in your database):  
```shell script
$ python delete_project.py -pn test_project
```