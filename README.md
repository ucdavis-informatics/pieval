# pieval
Author: Bill Riedl  
Current Status: Development  
Original Author Date: 2019-01-13  

Due to the limitations of the Shiny ecosystem, this is a port/improvement of [valR](https://gitlab.ri.ucdavis.edu/ri/pydatautils/ucd-ri-dataval/tree/dev-br/valR) from R into Python using [Flask](https://flask.palletsprojects.com/en/1.1.x/) as the web app framework.


## Technical Deets
Python version: 3.6.x (3.6.9 for development)  
Venv manager: python3 -m venv  
Package manager: pip  

**NOTE:** using standard pip/virtualenv instead of pipenv due to some users complaining about flask/pipenv interoperability.  The virtual environment is 'self-contained', meaning it lives at pieval/venv/.  NOTE the the venv/ folder has been gitignored.  It will not be checked into the repo and needs to be built wherever this is deployed.  See building the project below.

### App Config
All config is housed in instance/config.py
This file is NOT checked into the git repo because it may contain secrets.  This file is a pre-requisite to a working example.  Be sure to create it with these variables defined.  Read inline comments for options

```py
#################
# data source config
#################
'''
The persistence layer can be either filesystem (csv files) or and RDMBS database
The file system approach is good for feature development but not appropriate for
production deployments

For prod deployments:
- change DATASOURCE_TYPE = 'db'
- change DATASOURCE_LOCATION to the vault path of your desired db
Yes, this pretty much binds the app to UCD deployments but, vault goodness...
'''
DATASOURCE_TYPE = 'file'

# value is either filesystem if DATASOURCE_TYPE == 'file' path or vault path if DATASOURCE_TYPE == 'db'
DATASOURCE_LOCATION = 'example_database/'

# defaulted to pieval.
# Change this is you want to place tables in a different schema
# only relevant if DATASOURCE_TYPE == 'db'
DB_SCHEMA = 'pieval'

####################
# logging config
####################
'''
Logged locally for development
Change this to any absolute path on the hosting filesystem (ensure r/w privs) to log elsewhere
'''
LOGFILE_LOCATION = 'example_log/flask_server.log'

####################
# secret config
####################
'''
PIEVAL_SECRET_KEY is used to encrypt the session object to prevent user tampering.  This not 100pct foolproof but pretty good.  You can set this to anything.  Complicated key suggested.

vault variables are only important if DATASOURCE_TYPE is set to 'db'
'''
PIEVAL_SECRET_KEY = 'super_secret_key'
VAULT_SERVER = 'https://vault-ri.ucdmc.ucdavis.edu:8200'
VAULT_TOKEN = 'vault_token'

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

**Notice the reference to instance/client_secrets.json**  
This is another secrets file, also in the instance/ folder that must be created for each deployment.  It's structure is presented below:
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
Fill in all <> values before running the app

### Building the project
Building the environment is a little different than using pipenv.
Clone the repo:
```sh
git clone
cd ucd-ri-pieval
```

Create virtualenv
```sh
python3 -m venv venv
```

Activate virtualenv
```sh
source venv/bin/activate
```

Install dependencies from requirements.txt
```sh
pip install -r requirements.txt
```

### Building the database - optional
If you want to use an RDMBS, you will need to first build out the database schema.  In theory, any RDMBS you can connect to with sqlalchemy will work but this has only been tested against MSSQL and Oracle to date.  The database build has been scripted to make your life easy(er).  
**NOTE:**  The script assumes you have already created an empty 'pieval' schema on the destination database and you have working credentials for this schema store in a vault server at the vault path in config.py  

Creating the database schema in Oracle (assuming you have a privileged account and can sign in):  
Oracle users are equal to schemas, so you will create a new db user here.  
```sql
create user pieval identified by a_strong_password;
grant create table to pieval;
grant create session to pieval;
grant unlimited tablespace to pieval;
```

Creating the pieval schema in mssql server (assuming you have a privileged account and can sign in):
This also assumes you already have a database in which to host the pieval schema  
```sql
CREATE SCHEMA pieval;
```

To have build_sql_database.py build the tables for you:  
1. modify instance/config.py with the database paramaters of your choosing
1. from within an activated pieval venv run:
```sh
# flip yes to no in the keep_example_data argument if you want an empty database
python build_sql_database.py --keep_example_data yes
```


### Running the app - locally
When running the app locally, it is best to start by using the example database that comes packaged in the repo.  If you set DATASOURCE_TYPE = 'file' and DATASOURCE_LOCATION = 'example_database/' in your instance/config.py file then the app will launch using the example data provide with the code.  When you launch you will land on a login screen.  There are 3 users pre-created in the example data:
1. awriedl
1. jp
1. asr

Simply enter one of these names in the box to log in as that user.  There is currently no password.  Feel free to cycle through them to get a better feeling for how the code based limits project access.  Read example_database/README.md for more info.  This is just enough to get you past the login screen.


1. Activate the venv (don't redo if already activated from building the app)
```sh
source venv/bin/activate
```
1. Optionally set FLASK_ENV=development.  This activates helpful actions during the development process such as aut-reloading on file save and debug logging messages.  Only run this when doing development.  When this env variable is not set, Flask will default to 'production' mode, which is what we want for deployments
```sh
export FLASK_ENV=development
```
1. Run App
```sh
python run.py
```

1. Access app by URL
  - Local development [localhost:5000](http://localhost:5000)
  - Production - depends on factors configured in Apache


### Running the app on a server - wsgi deployment
**This section assumes Apache and mod_wsgi**  
project_home is assumed to be '/var/www/pieval', meaning git clone <pieval url> and venv builds are run as root in /var/www

A wsgi, aka whiskey, file is provided at 'app/pieval.wsgi'.  This file will need modification if project location is not /var/www

Since this project is using a virtual env, we need to tell mod_wsgi where to get the correct python version and project packages.  These settings should go somewhere in the Apache config for this app.  These also need mods if not cloned/built in /var/www
WSGIPythonHome /var/www/pieval/venv/bin/python
WSGIPythonPath /var/www/pieval/venv/lib/python3.6/site-packages



### App Sessions
This app makes heavy use of the session variable, a dictionary for holding stateful content.  This app manages these session variables
1. logged_in - bool indicating whether logged in or not
1. user_name - contains unique id for current user.  After shib'd, this entry will hold the REMOTE_USER variable
1. cur_proj - unique name of current active project
1. project_mode - binary or multi-class, alters behavior when saving annotations
1. example_order - a list of integers, where each integer uniquely identifies an example from the current project
1. cur_example - a single integer, containing the current active example id in this users session
1. prev_example - a single integer, containing the previous example annotated.  Used to allow for 'Doh!' functionality

### Stackoverflow resources used to accelerate this development
https://stackoverflow.com/questions/7478366/create-dynamic-urls-in-flask-with-url-for


## Outstanding Development work:
1. Determine best auth strategy
1. finish rdbms data loader class to allow for production use
