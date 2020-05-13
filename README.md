# pieval
![pieval logo](app/static/images/pieVal_Logo_medium.png)  
Author: Bill Riedl  
Contributors: Joseph Cawood, Matt Renquist, Aaron Rosenburg, Jp Graff, Cy Huynh  
Original Author Date: 2019-01-13   
Current Status: Alpha  
Cur Status Date: 2019-01-29

## Background
pieval is the product of an idea, many work hours, a prototype in another language, and fairly extensive user testing.  And it's still growing.  The idea was a clever repurposing of common web app functionality seen in viral social apps like Tinder.  In these apps, users record their preferences with a quick swipe of the screen.  We wanted to bring that efficiency to data labeling efforts.  This work originated in a clinical setting in which data labelling has been prohibitively expensive, stunting the expanded use of machine learning.  Typically, data labelling efforts involves clinical experts reviewing data directly in an Electronic Medical Record, often taking minutes just to locate the data being reviewed, then entering their findings in a separate tool.  pieval removes all of this complexity, placing the data and the response capture in a lightweight, distraction free UI.  Admittedly, this makes the annotation job set-up a bit more expensive.  However, that's concentrated as a one-time effort rather than forcing each annotator to pay the cost over and over.

pieval began as an idea as a 5 person team grappled with how to accelerate a growing number of natural language processing techniques for the UC Davis Cancer center.  A few months after the idea was floated, Joseph Cawood tweaked some open source tooling, written in R, and leveraging the rShiny ecosystem to provide a prototype we could put in front of users([valR](https://gitlab.ri.ucdavis.edu/ri/pydatautils/ucd-ri-dataval/tree/dev-br/valR)).  This prototype was invaluable in helping to shape the requirements of a production system.  After a few iterations in R/rShiny it became apparent that the framework was not up to the task.  The app was ported to Python using the Flask webapp framework in January 2020.

### Contributors
Bill Riedl: Idea guy / Lead dev  
Joseph Cawood: valR prototype author  
Matt Renquist: Keycloak auth strategy and deployment strategy using Gunicorn and Apache Proxies.  
Aaron Rosenburg: Primary clincal test user  
Jp Graff: Clincal test user  
Cy Huynh: Logo Developer  

___

## Technical Deets
Python version: 3.6.x (3.6.9 for development)  
Venv manager: python3 -m venv  
Package manager: pipenv  
Auth: Keycloak  
Persistence Architecture: filesystem(dev only) or RDBMS (tested on ora or mssql)
Secrets Management: Vault.  With modification, the app could be convinced to obtain all secrets from config.py (see below) if Vault is not available to you.

### App Config
All App config is housed in the instance/ directory.  There are 2 configuration files that must be present:
1. config.py - contains app configuration
1. client_secrets.json - referenced in config.py, contains keycloak auth configuration
These files are NOT checked into the git repo because they may contain secrets.  These files are a pre-requisite to a working example.  Be sure to create them using these examples as reference:

**NOTE:**  As you create these files be EXTREMELY careful about which environment you are connecting to, espeically if using a database as the persistence architecture.  This repo contains code that can overwrite an exisiting database schema.  If you trigger this during development against a non-development database you can lose data!

```py
#################
# App config
# this will change the default prefix added by the blueprint
# For this app, common sense choices are either '/' or '/pieval'
#################
BLUEPRINT_URL_PREFIX = '/'

#################
# data source config
#################
'''
The persistence layer can be either filesystem (csv files) or and RDMBS database
The file system approach is good for feature development but not appropriate for
production deployments

For dev deployments
DATASOURCE_TYPE = 'file'
DATASOURCE_LOCATION = 'example_database/'

For prod deployments:
- change DATASOURCE_TYPE = 'db'
- change DATASOURCE_LOCATION to the vault path of your desired db
Yes, this pretty much binds the app to UCD deployments but, vault goodness...
'''
DATASOURCE_TYPE = 'file'
DATASOURCE_LOCATION = 'example_database/'

# DATASOURCE_TYPE = 'db'
# DATASOURCE_LOCATION = 'cdi3/db/cdi3sql01/dev'

# defaulted to pieval.
# Change this is you want to place tables in a different schema
# only relevant if DATASOURCE_TYPE == 'db'
DB_SCHEMA = 'pieval'

####################
# logging config
####################
'''
Logged locally for development
Change this to any absolute path on the hosting filesystem (ensure r/w privs)
to log elsewhere
'''
LOGFILE_LOCATION = 'example_log/flask_server.log'

####################
# secret config
####################
# Vault config.  Vault is secrets as a service.  If you don't have Vault,
# You must put a number of additional values in this file.  Namely, DB
# connection info (host, port, user, password, db_type[oracle|mssql])
# and then modify the source code a bit to grab these values rather than
# vaults values
VAULT_SERVER = 'https://vault-ri.ucdmc.ucdavis.edu:8200'
VAULT_TOKEN = '<vault_token>'
# used by Flask to sign the session object
SECRET_KEY = '<super_secret_key>'


####################
# auth config
####################
# TESTING=True
# DEBUG=True
OIDC_CLIENT_SECRETS='instance/client_secrets.json'
OIDC_ID_TOKEN_COOKIE_SECURE=False
OIDC_REQUIRE_VERIFIED_EMAIL=False
OIDC_USER_INFO_ENABLED=True
OIDC_OPENID_REALM='cdi3'
OIDC_SCOPES=['openid', 'email', 'profile']
OIDC_INTROSPECTION_AUTH_METHOD='client_secret_post'
```

**client_secrets.json**  
This is another secrets file, also in the instance/ folder that must be created for each deployment.  All values must be updated for your deployment.  It's structure is presented below:
```json
{
    "web": {
        "issuer": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3",
        "auth_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/auth",
        "client_id": "<Unique client id - defined in keycloak>",
        "client_secret": "<unique key value here>",
        "redirect_uris": [
            "<url where app is hosted>"
        ],
        "userinfo_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/userinfo",
        "token_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/token",
        "token_introspection_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/token/introspect"
    }
}
```
---
## Creating a Vault approle for pieval
Create the approle
```shell script
vault write auth/approle/role/pieval_role policies="pieval_policy" period="192h"
```

Get the role id
```shell script
vault read auth/approle/role/pieval_role/role-id
```

Get the Secret id
```shell script
vault write -force auth/approle/role/pieval_role/secret-id
```



---

### Cloning/Building the project
Building the environment is a little different than using pipenv.
Clone the repo.  Obtain clone URL from [HERE](https://gitlab.ri.ucdavis.edu/ri/pydatautils/pieval):
```sh
git clone <git url>
cd ucd-ri-pieval
```

Create pipenv
```sh
pipenv --python 3.6.9 install
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
To have build_sql_database.py build the tables for you:  
1. Modify instance/config.py with the database parameters of your choosing
  - Set DATASOURCE_TYPE = 'db'
  - Set DATASOURCE_LOCATION = <vault path of your desired database>
1. From within an activated pieval venv run:
```sh
# flip yes to no in the keep_example_data argument if you want an empty database
pipenv run python build_sql_database.py --keep_example_data yes
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
```shell script
# assumes pipenv is activated
$ python create_project.py --help
```
A specific example here which creates a project from the staging table:  
  pieval_stage.aml_bm_blast_cycle1  
  with 2 users test1 and 2  
  with project description test project description
  with project mode binary
  
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
**NOTE:  There are pre-reqs to running this app locally, without them it will not work.  They are:**
1. keycloak - The keycloak service must be running, configured to accept this app as a client, and you must have network connectivity to it.

Assuming you meet the above requirements, you can run the app locally! It is best to start by using the example database that comes packaged in the repo.  If you set DATASOURCE_TYPE = 'file' and DATASOURCE_LOCATION = 'example_database/' in your instance/config.py file then the app will launch using the example data provide with the code.  You will need to modify the example_database/project_users.csv file and add an entry giving your username access to one or more of the demo projects.

If you want to run the app against a database locally, it adds another pre-req.  You must have a database you control and previously built the pieval schema.  If you plan to use this code out of the box, you must also be running Vault and update instance/config.py with the correct vault information.  In the absence of vault, you must modify instance/config.py as well as some of the source code to instead pull database secrets/parameters from the config file.


- Activate the venv (don't redo if already activated from building the app)  

```sh
pipenv shell
```

- Run App


```sh
# Using development server with auto-reload
python run.py
```
-OR-

```sh
# Run App using gunicorn that more closely matches the deployment environment
gunicorn -w 4 -b 127.0.0.1:5001 app:app
```

- Access app by URL - by default app launches on localhost:5001
  - Local development [localhost:5001](http://localhost:5001)
  - Production - depends on deployment specific factors



#### App Sessions
While the app is running, it makes heavy use of the session variable, a dictionary for holding stateful content.  This app manages these session variables
1. logged_in - bool indicating whether logged in or not
1. user_name - contains unique id for current user.  After shib'd, this entry will hold the REMOTE_USER variable
1. cur_proj - unique name of current active project
1. project_mode - binary or multi-class, alters behavior when saving annotations
1. example_order - a list of integers, where each integer uniquely identifies an example from the current project
1. cur_example - a single integer, containing the current active example id in this users session
1. prev_example - a single integer, containing the previous example annotated.  Used to allow for 'Doh!' functionality

---

### Deploying/Running the app on a server
Pieval is deployed on gunicorn python app server proxied by Apache.  In this deployment method, pieval must be running on gunicorn binding a localhost port/sub-url.  Apache must be configured to accept web requests and proxy them to the application.  Apache also enforces 'https'.
1. Gunicorn - app container
1. Apache - web server wich accepts web requests and proxies to Gunicorn

Running the app:  
```sh
# Note only binding 127.0.0.1 - makes app localhost only and ensures the only external access path
# will be through apache, which enforces https
pipenv run gunicorn -w 4 -b 127.0.0.1:5001 app:app
```

Basic puppet config to run app at '/pieval':
```yaml
proxy_pass:
  -
    path: '/pieval'
    url: 'http://localhost:5001/pieval'
    reverse_urls:
      - 'http://localhost:5001/pieval'
```


#### Apache and mod_wsgi
This is not reccomended.  It requires using the same python version as mod_wsgi was compiled for.  Instead we reccomend using a wsgi container like Gunicorn, covered above.
Since this project is using a virtual env, we need to tell mod_wsgi where to get the correct python version and project packages.  These settings should go somewhere in the Apache config for this app.  These also need mods if not cloned/built in /var/www
WSGIPythonHome /var/www/pieval/venv/bin/python
WSGIPythonPath /var/www/pieval/venv/lib/python3.6/site-packages
