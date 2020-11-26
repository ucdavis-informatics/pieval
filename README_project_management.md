## Creating Pieval projects with your own data
Now that the app is up and running, it's time to add data meaningful to your project.  This is entirely your responsibility but, here is some helpful information to get your on your way.  We will assume you will be adding a new project to your pieval instance.  You need to complete 3 major steps to make this a reality.
1. Define a project - Add an entry to projects.csv OR the projects table in your preferred database, filling out all columns
1. Add Users to the project - Add entries to project_users.csv OR the projec_users table in your preferred database
1. Add data to project_data

Of these, #3 is the heaviest.  Assuming you can get your data into csv file format with these columns:
```py
pieval_cols=['project_name','example_id','source_id','data','data_ext','prompt']
```
described in example_database/README.md for the project_data table, you can either append your data to the project_data.csv file or the project_data database table, depending on whether or not you are using filesystem or RDBMS as your persistence architecture.

### Using create_project.py
Assuming your using a backing database, this script will help you create a new project.  This is intened more for production applications.  In local development, editing the csv files in example database is so easy we won't build a script to manage them.

You must first create a table in the pieval_stage schema, with the same columns as pieval.project_data, containing the data for the new project.  If your project is a multi-class project, then you must also create a table containing the project classes in the pieval_stage schema.  The you can run the create_project.py script to insert the new data into all the necessary tables.  It is a CLI script with a pretty well document api available here:

A specific example here which creates a project from the staging table:  
  pieval_stage.aml_bm_blast_cycle1  
  with 2 users test1 and 2  
  with project description test project description
  with project mode binary


```shell script
$ pipenv run python create_project.py --help
```

```shell script
$ pipenv run python create_project.py -dt aml_bm_blast_cycle1 -u awriedl -u jmcawood -pd "test project description" -pm binary
```

### Using delete_project.py
Assuming your using a backing database, this script will help you delete a project.  This is intened more for production applications.  In local development, editing the csv files in example database is so easy we won't build a script to manage them.

Pass the script a project_name and it will remove all data for that project, AFTER creating a full backup in the pieval_backup schema.  It is up to you to use this tool responsibly.  Please ensure you have captured the data you want BEFORE removing a project.  The backup does exist, but you should not rely on it!  This is implemented as a CLI script.  The API can be examined here:
```shell script
$ pipenv run python delete_project.py --help
```

A specific example:  
```shell script
$ pipenv run python delete_project.py -pn aml_bone_marrow_results
```


```sh
# flip yes to no in the keep_example_data argument if you want an empty database
# flip build to updated in build_or_update argument to have your current database upgraded to latest version!
pipenv run python build_sql_database.py --keep_example_data yes --build_or_update build
```

Create Project:
```shell script
# assumes pipenv is activated
$ python create_project.py -dt aml_bm_blast_cycle1 -u awriedl -u jmcawood -pd "test project description" -pm binary
```


Delete Project
A specific example:  
```shell script
# assumes pipenv is activated
$ python delete_project.py -pn aml_bone_marrow_results
```