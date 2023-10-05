# PieVal Persistance

Persistance is handled by a MongoDB no matter what context you run the app in, Dev or Prod.  

- In [Dev](#dev-mode) mode the persistance is treated as completely emphemeral and example data is packaged with the app to allow for development/testing/demos/etc...
- In [Prod](#prod-mode) mode, you have a few options to prevent the data from vaporizing when you shut down the app.  All three options have tradeoffs
    - Use Docker built in volumes
    - Use Docker bind mounts
    - Use a pre-exsiting mongoDB you're already running

---
## Database Structure

Regardless of the mode, the mongo database contains 3 collections:

1. projects - Contains project level data like project name, data type, mode (binary or multiclass), and allowed users (authZ)
1. project_data - Contains the data you wish to annotate with pieval.  For any given project, there will be many project_data documents
1. users (optional) - Extended user data, like email address and pretty print name.  Primarily used to obtain email address if you set up automated annotation reminders.  It becomes required for reminders.


### Projects collection

```py
{   
    "_id": Name of the project # guarantees unique project names
    "project_name": Name of the project - same ad _id,
    "project_description":Description of project,
    "project_mode": Either multiclass or binary: ['multiclass','binary'],
    "data_type": Either text or image: ['text','image'],
    "class_list": If multiclass, this is list of all the labels['one class', 'two class', 'etc..'],
    "user_list": The users who are authorized to annotate data in this project['user 1', 'user 2', 'user 3']
}
```

**Primary key:** project_name

### Project Data Collection

```py
{
    "_id": project name and example id concatenated together so project_name + '_' + example_id.  Ensures unique records in project namespace,
    "project_name": The name of the project to which this data belongs,
    "source_id":Link back to source data system,
    "example_id":Numeric value indicating how many examples there are for this annotation project.  Also used for ordering presentation if required,
    "data":Could be an enriched block of text OR the full text,
    "data_ext":The full text of the note,
    "prompt":The challenge to which the annotator must respond,
    "annots": list of annotations (max one per annotator)[
        "response_time":Datetime response was recorded from the user,
        "user_name":Username of the annotator.  Tehcnically this gets pulled from auth header - value of REMOTE_USER,
        "user_ip":IP address from which the user annotated the document,
        "response":The users response,
        "context_viewed":["yes","no"]
    ]
}
```

**Primary key:** project_name and example_id concatenated together - technically a composite key  
**Foreign key:** project_name -> projects['project_name']

### Users Collection

```py
{
    "_id":unique user name of for user,
    "user_name":unique user name for user - same as _id,
    "print_name":Name thats printed to the screen when this user logs in,
    "email":Email associated with this user.  May be used to bug them to perform annoations,
}
```

**Primary key:** user_name

> Note: '_id' in each document contains duplicate data from other fields in the document.  This is primarily because unique keys can be generated using values meaningful to the pieval application.  It is also to prevent Mongo from autogenerating unique _id's on insert.  These get return to the python app and an ObjectId rather than a standard string object.  String objects are just easier to deal with.

---
## How to create a project

You must create data for PieVal.  This requires creating 3 files, staging them on disk, and running the create_project.py script at the root of this repo and supplying the path to the directory where you have staged your files.  The 3 files are:

1. projects.json
1. project_data.json
1. users.json

They are all arranged as arrays of JSON objects that must follow the [database structuredefined above](#database-structure).  It is optional to include pre-existing annot arrays in your project data.  There are examples of these files in this repository:

1. /example_database/default - illustrates the loading of 4 different projects at the same time
1. /example_database/example_create - illustrates how to load one project

Please review and copy their structure for your own projects.

Once your data is loaded in these 3 files you:

1. open up VS Code - [set up instructions here - read the entire section!](README_run_app.md#development-mode)
1. Open and integrated VS Code terminal
1. Ensure /instance/config.py has the correct entry for CREAT_PROJ_MONGO_CONNECT_DICT
1. Run the create_project.py

```sh
python create_project.py --project_data_root_dir /path/to/directory/with/files/defined/above
```

### Project creation data considerations
The data generation process is where you decide how to leverage the functionality in PieVal to capture efficient annotations.  While most of the fields in the mongo db are informational, or present just to help the app work, these 3 fields are where you get to be creative in how you structure the annotation process (fields in each document of the project_data collection):

1. data - The data initially displayed to the user in the pieval UI.  Ideally, you place enriched text here.  Enrichment is the act of removing potenitally off target text to shorten the amount of data annotators must review.
1. data_ext - This is the full, unaltered, text body.  If the annotator feels ambiguous after reviewing the enriched data, they can opt to view the extened data in the pieval UI, which will display the contents of this field from the database.
1. prompt - The prompt is an assertion.  You are asking annotator to agree or disagree that this prompt applies to the text in data/data_ext


---
## How to delete a project

Deleting a project is easy:

1. open up VS Code - see [here](README_run_app.md#development-mode)
1. Open and integrated VS Code terminal
1. Ensure /instance/config.py has the correct entry for CREAT_PROJ_MONGO_CONNECT_DICT
1. Run the delete_project.py
```sh
python delete_project.py --project_name <name of project to delete>
```

---
## Dev Mode



---
## Prod Mode