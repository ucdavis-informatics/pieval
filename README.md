# PieVal
![pieval logo](app/static/images/pieVal_Logo_medium.png)  
Author: Bill Riedl  
Contributors: Joseph Cawood, Matt Renquist, Aaron Rosenburg, Jp Graff, Cy Huynh  
Original Author Date: 2019-01-13   
Current Status: Stable  
Cur Status Date: 2019-05-29

--- 

# Project Status/TODOs
Project is currently being re-worked to:
- run in containers so it's easier to package
- work on different types of data, notably images and table data

## Reworking to package in containers
There are at least 3, if not 4 technologies that add up to pieval:
1. Python Flask
1. Vault - kind of optional.  We could just put secrets in instance/config
1. KeyCloak - Non-optional.  Acts as ID store abstraction layer.  future users can use KC directly OR link KC to IDp of their choosing
  - I only intend to solve demo deployments by packaging with a KC docker image.  It will always be the intention to make it easy to demo but, running will necessarily take more effort

---

## Background
PieVal is the product of an idea, many work hours, a prototype in another language, and fairly extensive user testing.  And it's still growing.  The idea was a clever repurposing of common web app functionality seen in viral social apps like Tinder.  In these apps, users record their preferences with a quick swipe of the screen.  We wanted to bring that efficiency to data labeling efforts.  This work originated in a clinical setting in which data labelling has been prohibitively expensive, stunting the expanded use of machine learning.  Typically, data labelling efforts involves clinical experts reviewing data directly in an Electronic Medical Record, often taking minutes just to locate the data being reviewed, then entering their findings in a separate tool.  PieVal removes all of this complexity, placing the data and the response capture in a lightweight, distraction free UI.  Admittedly, this makes the annotation job set-up a bit more expensive.  However, that's concentrated as a one-time effort rather than forcing each annotator to pay the cost over and over.

PieVal began as an idea as a 5 person team grappled with how to accelerate a growing number of natural language processing techniques for the UC Davis Cancer center.  The first attempt started with some tweaked open source tooling, written in R, and leveraging the rShiny ecosystem to provide a prototype we could put in front of users: ([valR - link not accessible from outside UCD](https://gitlab.ri.ucdavis.edu/ri/pydatautils/ucd-ri-dataval/tree/dev-br/valR)).  After a few iterations in R/rShiny it became apparent that the framework was not up to the task but, it had been extremely helpful in shaping the final requirements.  The app was ported to Python using the Flask webapp framework in January 2020.

## Demo Title and Copy
Title: PieVal - Accelerating label capture for Natural Language Processing 
Copy: PieVal, combining the words Python and Validation, is a web-based, secure, text data labelling tool designed for distributed annotation of sensitive data supporting document level annotations and captures binary and multi-class labels.  It is designed to be part of an iterative continuous improvement cycle by reframing the labelling process as an assertion test.  This reframing provides a consistent interface regardless of class number or project stage.  It also had the side effect of decreasing annotation time by an average of 50% compared with other tools.  Additional features include the ability to directly test the impact of text enrichment strategies on both annotation times as well as downstream model performance.

## About the Author(s)
Bill Riedl has been building applications for secondary use of clinical data since 2009 as a graduate student researcher in clinical informatics.  Since graduating in 2011, he has held a variety of roles with UC Davis Health, working in clinical domains focused on chronic disease registries, to modelling high volume, high throughput ICU data, to most recently building precision medicine tools for cancer.  Bill specializes in Natural Language Processing, Time Series analysis, data standards and API's, as well as a little web application development.

### Contributors
Bill Riedl: Idea guy / Lead dev  
Joseph Cawood: valR prototype author/ PieVal power user  
Matt Renquist: Auth and Deployment strategy  
Aaron Rosenburg: Primary clinical test user  
Jp Graff: Clincal test user  
Cy Huynh: Logo Developer  

---
## Key Features
- Secure (when served over HTTPS and secured by Keycloak)
- Gamified - Make annotating fun again!  #MAFA.  This is accomplished primarily with a project leaderboard, allowing for friendly competitions.  Best if combined with incentives, like coffee cards. 
- Assertion tester - Rather than presenting the user with data and asking for an annotation, we present the user with data, an assertion (either human or machine generated) and ask them to Agree, Disagree, Review, or Pass.  The result is a consistent UI that does not change, no matter the task.  This allows user to become extremely efficient at using the tool.
- Built in enrichment strategy testing.  By default present the user a clipped, enriched, or otherwise modified version of the data designed to improve both the annotation and downstream ML process.  But, save the unmodified data and present it IF the annotator asks for it.  The ask is recorded with the annotation.  This allows you measure the effectiveness of enrichment strategies.
- Easy configuration to set up annotation quality with both IntrA and IntER operator agreement statistics
- Annotation compliance - system can be configured to send reminder emails to keep people engaged without you having to lift a finger.

---

## Technical Deets
Python version: 3.6.x (3.6.9 for development)  
Venv manager: python3 -m venv  
Package manager: pipenv  
Auth: Keycloak  
Persistence Architecture: filesystem(dev only) or RDBMS (tested on ora or mssql)
Secrets Management: Vault.  With modification, the app could be convinced to obtain all secrets from config.py (see below) if Vault is not available to you.

We built on top of two technologies we really like.  This disclaimer is to let you know we recognize this could make it hard to get this code running in your environment.  We use:
1. [KeyCloak](https://www.keycloak.org) - for Authentication
1. [Vault](https://www.vaultproject.io) - for Secret management
Both technologies are open source and we cannot recommend them enough.  Having said that, if you are unable to run them in your environment, you will have to make some code changes and some config changes before this code will run.

### App Config
All App config is housed in the instance/ directory.  There are 2 configuration files that must be present:
1. config.py - contains app configuration
1. client_secrets.json - referenced in config.py, contains keycloak auth configuration
These files are NOT checked into the git repo because they may contain secrets.  These files are a pre-requisite to a working example.  Be sure to create them using these examples as reference:
**NOTE:**  As you create these files be EXTREMELY careful about which environment you are connecting to, espeically if using a database as the persistence architecture.  This repo contains code that can overwrite an exisiting database schema.  If you trigger this during development against a non-development database you can lose data!

See README_example_config.md for an example config file

---

### Cloning/Building the project
Clone the repo.  Obtain clone URL from [HERE](https://gitlab.ri.ucdavis.edu/ri/pydatautils/pieval):
```sh
git clone <git url>
cd ucd-ri-pieval
```

---

### Persistence architecture
The pieval webapp is data driven.  The input and output data need to be accessible to the app while it's running.  Pieval can use either filesystem (csv) or a relational database (Oracle or MSSQL) to store and retrieve data.  It should be noted the filesystem option should only be used in development environments or for single user applications.  All other applications should plan to use a relational database.  The app has been tested against Oracle and MSSQL.  With very minor modifications, it will work against any SQL database of your choosing.  Please see example_database/README.md for more information about the data schema.

To use an RDMBS, you will need to first build out the database schema.  In theory, any RDMBS you can connect to with sqlalchemy will work but this has only been tested against MSSQL and Oracle.  The database build has been scripted to make your life easy(er).  
**NOTE:**  The script assumes:
 - You have already created an empty 'pieval' schema on the destination database
 - You have working credentials for this schema stored in vault at the vault path listed in config.py

#### Creating the database schema
**Oracle**  
In Oracle users are equal to schemas, so we create a pieval user.  
```sql
create user pieval identified by a_strong_password;
grant create table to pieval;
grant create session to pieval;
grant unlimited tablespace to pieval;
```

**MSSQL**
In MSSQL, the meaning of schema is a bit different.  Assuming you 'own' a database in MSSQL, all you need to do is create the pieval schema with this command:  
```sql
CREATE SCHEMA pieval;
```

#### Scriptified schema build
To have build_sql_database.py build OR update the tables for you:  
1. Modify instance/config.py with the database parameters of your choosing
  - Set DATASOURCE_TYPE = 'db'
  - Set DATASOURCE_LOCATION = <vault path of your desired database>
1. From within an activated pieval venv run:
```sh
# flip yes to no in the keep_example_data argument if you want an empty database
# flip build to updated in build_or_update argument to have your current database upgraded to latest version!
pipenv run python build_sql_database.py --keep_example_data yes --build_or_update build
```

---

## Generating your own data for pieval
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
# assumes pipenv is activated
$ python create_project.py --help
```

```shell script
# assumes pipenv is activated
$ python create_project.py -dt aml_bm_blast_cycle1 -u awriedl -u jmcawood -pd "test project description" -pm binary
```

### Using delete_project.py
Assuming your using a backing database, this script will help you delete a project.  This is intened more for production applications.  In local development, editing the csv files in example database is so easy we won't build a script to manage them.

Pass the script a project_name and it will remove all data for that project, AFTER creating a full backup in the pieval_backup schema.  It is up to you to use this tool responsibly.  Please ensure you have captured the data you want BEFORE removing a project.  The backup does exist, but you should not rely on it!  This is implemented as a CLI script.  The API can be examined here:
```shell script
# assumes pipenv is activated
$ python delete_project.py --help
```

A specific example:  
```shell script
# assumes pipenv is activated
$ python delete_project.py -pn aml_bone_marrow_results
```

---

### Running the app
This app runs in 2 modes:
1. Dev/Demo - runs the minimal 'complete' environment that allows for development work as well as easy out of the box demonstrations.  Notably, when running in Dev mode, the app assumes you will be using the csv file based persistance strategy, not connecting to a database.  This allows to avoid worrying about both running a DB and accessing the secrets to sign into it.  Dev Mode runs:
  - PieVal app - as a container
  - KeyCloak - as a container that is loaded with the minimal security configuration for the service to support PieVal with Auth.  This is NOT secure.  It is intended to give you a feel for how security works in the platform.  This also means we did not need to implement an auth layer togggle switch OR guranateed that a fully baked keycloak service is running simply to demo/develop on the tool.  
1. Production - Runs only the PieVal application as a container.  It is assumed you have a fully baked:
  - KeyCloak instance
  - Vault instance - for retrieving database secrets.  **NOTE:** You could alter the codebase to simply draw the db secrets from instance/config.py, where other secrets are already kept.
  - Database [oracle|mssql]  


Run mode is toggled in instance/config.py.  Find the block near the top and modify...
config.py is also how you wire the app up to either the demo services or the production services
use demo_config.py


#### Launching the app
Directly on your hardware:  

```sh
# This runs the code with reload set to true such that code changes can be tested quickly
pipenv run python run.py
```

```sh
# This runs the code in the same way it will be run in production
pipenv run gunicorn --timeout 1000 -w 4 -b 127.0.0.1:5001 "run:create_app()"
```

Running on Docker:  
```sh
# build the image
docker build -t ariedl/pieval:v1.0.0 .
```

```sh
docker run --name pieval --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 gunicorn --timeout 1000 -w 4 -b 0.0.0.0:5001 "run:create_app()" 
```

- Access app by URL - [localhost:5001](http://localhost:5001)


### Deploying for production
Pieval is deployed on gunicorn python app server proxied by Apache.  In this deployment method, pieval must be running on gunicorn binding a localhost port/sub-url.  Apache must be configured to accept web requests and proxy them to the application.  Apache also enforces 'https'.
1. Gunicorn - app container
1. Apache - web server wich accepts web requests and proxies to Gunicorn

Basic puppet config to run app at '/pieval':
```yaml
proxy_pass:
  -
    path: '/pieval'
    url: 'http://localhost:5001/pieval'
    reverse_urls:
      - 'http://localhost:5001/pieval'
```

The URL to access the app once deployed on a server will be dependent on your hostname and other decistions you may have made.

---

#### App Sessions
While the app is running, it makes heavy use of the session variable, a dictionary for holding stateful content.  This app manages these session variables
1. logged_in - bool indicating whether logged in or not
1. user_name - contains unique id for current user.  After shib'd, this entry will hold the REMOTE_USER variable
1. cur_proj - unique name of current active project
1. project_mode - binary or multi-class, alters behavior when saving annotations
1. example_order - a list of integers, where each integer uniquely identifies an example from the current project
1. cur_example - a single integer, containing the current active example id in this users session
1. prev_example - a single integer, containing the previous example annotated.  Used to allow for 'Doh!' functionality

### Background Tasks
Using the [Flask AP Scheduler](https://github.com/viniciuschiele/flask-apscheduler) some helpful background tasks are triggered:
1. Renew Vault approle token - Without any utilization the approle tokens expire every 192 hours.  This triggered task renews the token every 13 hours to prevent the approle token from expiring
1. Send Reminder Emails - If configured, this task will send emails (only M-F at 0900) to all system users that have exceeded the configurable number of days since recording an annotation while they have active projects.  Helpful for annotation compliance.

