# Running The App

PieVal is a WebApplication that runs on top of the following technologies (starting from lowest, OS and working up)

1. Linux VM - This can be any flavor of linux that is capable of running Docker
1. Apache/httpd - This is web server that runs on linux.  In production deployments, the webserver should proxy web trafffic to and from the webapp
1. [Docker](https://www.docker.com/) - A technology for creating isolated runtime environments.
1. [Docker Compose](https://www.docker.com/) - used to orchestrate 2 containers for this project
1. Container 1 - WebApp
    - [Gunicorn](https://gunicorn.org/) - A python WebApplication server.  It recieves requests that have been previously authenticated by Apache on the linux VM via a proxy
    - [Flask](https://flask.palletsprojects.com/en/2.2.x/) - Python WebApplication framework.  Handles web application routing, logic, and rendering inside the typical request/response lifecycle of the web
    - [PieVal Application Code](https://gitlab.ri.ucdavis.edu/ri/pydatautils/pieval) - The code that makes PieVal, PieVal
1. Container 2 - Mongo - provides persistance

**NOTE:** Layers 1 and 2 can be modified to your liking.  They are only important in production.  For development only levels 3-5 are relevant.  You can develop anywhere Docker is installed.

The PieVal application can run in 2 different contexts:

1. Development - new feature development, patching, package upgrades, etc..
1. Production - load balanced for multiple users, authentication, backed by robust persistence store

The repo is packaged with 2 docker compose files:

1. docker-compose-dev.yml - launches the app in dev mode
    - The pieval command directive calls run.py which:
        - starts the app using the built in flask development server
        - runs the create_project.py helper file using data in example_database/default to seed sample data
    - The mongo db container is started without a mapped volume which means no changes are saved from on development session to another
1. docker-compose-prod.yml - launches the app in prod mode
    - The pieval command directive launches a gunicorn web app server suitable for production deployments
    - The mongo db container is started with a bind mount to ./mongo_data:/data/db which will persist data at ./mongo_data permanently (you can configure this - [pieval persistance](README_persistence.md))

### App Config

App config is located in ./instance/config.py.  This file is gitignored since it can contain sensitive information.  You will need to create one by copying instance/example_config.py to instance/config.py, then modyfing as needed.

Some key fields in config.py:

1. SECRET_KEY - used to encrypt the session object in flask.  This should be a long random string that is kept secure.
1. AUTH_ENABLED - Toggles whether or not the app enables 'auth'.  The app DOES NOT have any built in authentication.  If you wish to enable auth see [auth section below](#auth)
    - IF NO - the app is completely insecure.  It will allow you emulate any 'user' simply by entering their username on the logon screen - this can be useful for debugging
    - IF YES - then the app assumes it is running behind an auth'd proxy and will expect {REMOTE_USER_HEADER_KEY} to be in the request headers.  If the value of {REMOTE_USER_HEADER_KEY} matches entries in user_list associated with each project then that user will be granted access to that project
1 REMOTE_USER_HEADER_KEY - configurable value that allows for quickly updating which header key to look for in the request headers for previously authenticated username information.
1. MONGO_CONNECT_DICT - The connection dictionary the app uses to authenticate into mongo DB.
1. CREAT_PROJ_MONGO_CONNECT_DICT - The connection dictionary the create_project.py and delete_project.py scripts use to authenticate into the mongo db.  Since the app and the scripts may run in different contexts, these were seperated to allow flexibility


**For more information about pieval persistance and mongodb, please see [persistance](README_persistence.md)**

--- 
## Development mode

In this mode the linux vm and apache/httpd (with associated auth) are irrelevant.  You will only be running from the Docker layer down through the application code.  It only takes one command to launch the app in dev mode:

```sh
# must be run from pieval/ repo root directory
docker compose -f docker-compose-dev.yml up
```

This command:

1. starts the app with an interactive shell so that you can view the logs
1. Mounts the current directory (the pieval codebase) to the container so that the code is available to execute
1. Forwards port 5001 from the container to the host - so you can navigate to the app running in the container
1. Launches the application in the contaier by calling run.py, which will:
    - start the built in flask development server
    - create an instance of the app
    - spin up a sibling container to the webapp to host Mongo and load it with example data

> NOTE: Since this is development mode, you can alter the code and the app will reload any changes allowing for rapid iteration

> NOTE 2: This will launch the app in development mode AND will overwrite the database with packaged example data.  This mode is for developing new functionality, debugging, or demonstration of the apps functionality.

The app will be available at [http://localhost:5001/pieval](http://localhost:5001/pieval)

When you are done, please be sure to shut down the app gracefully:

```sh
# two steps
# must be run from pieval/ repo root directory
ctrl+'c'
docker compose -f docker-compose-dev.yml down
```

### Editing the code

Development mode also requires a text editor or IDE (whatever you prefer) plus some form of python environment.  The instructions here will be written assuming you are using [Visual Studio Code](https://code.visualstudio.com).  The project was originally developed on this platform and leverages the VSC extension ecosystem to create and manage a development environment, specifically we use [VSCode devcontainers](https://code.visualstudio.com/docs/devcontainers/containers).

You will need:

1. [Visual Studio Code](https://code.visualstudio.com) installed on your system
    - Once installed use the build in Extensions Manager to install these extensions:
        - Remote Development Extension Pack
        - Docker 
1. [Docker](https://www.docker.com) installed on your system

Assuming thes pre-reqs are met, and docker is running, you can simply open the pieval folder in VSCode and you will be prompted to 'Reopen In Container'.  That's it.

#### Remote Development
This will work just as well on your local workstation AND on remote servers using the Remote SSH extension for VSCode.  See [the remote ssh docs here](https://code.visualstudio.com/docs/remote/ssh).  Assuming you have a server you control the high level steps are:

1. Git clone the pieval code to the server
1. use vscode + remote ssh extension to open a remote development window on that server
1. Open the pieval repo directory in the remote vscode window
1. When prompted to reopen in container, accept the prompt


#### Running the helper scripts

Using the vscode devcontainer is the single easiest way to run the helper scripts create and delete project dot pie.  Once you have vscode running ([see above](#editing-the-code)) and attached to the devcontainer (optionally on a remote host with remote ssh plugin) you can run create and or delete project dot pie with in the VSC integrated terminal as indicated in [pieval persistance](README_persistence.md)


#### Developing without VScode

It is entirely possible to develop the codebase without using VS Code.  To do this you will need:

1. A python environment of some kind with the pips in requirements.txt installed
1. Code/text editor of your choice

If you are taking this route I assume you can manage opening this repo in your desired environment on your own.

---
## Production Mode

In order to run the app in production mode, you need to have a host server with a web server avialable to you.  These instructions will be written assuming a Linux server running an [Apache](https://httpd.apache.org) web server.

### Apache Web Server Config

1. Ensure your web server is listening and accessible to the web
1. Optional - if you wish to run this app securely, configure your web server to operate over HTTPS only
    - Requires web certificates signed by a signing authority
    - Specifics will vary based on signing authority and your specific web server
1. Install mod_proxy for apache
1. Configfure a proxy on your web server.  In apache, something like this:
```sh
# in your apache config
ProxyPass /pieval http://localhost:5001/pieval
ProxyPassReverse /pieval http://localhost:5001/pieval
```


### Auth
The app can be run with or without auth in production mode.  If running without auth, no additional steps are required.

If running with Auth, choose an auth strategy that Apache supports.  There are many.
- Built in basic auth
- Integration with an IdP
    - mod_auth_mellon allows for integration with Microsofts ADFS
- etc...

Configue it such that after a user has autheNticated (authN) the username is forwarded to the pieval app in the request headers.  Take note of the key that will hold the username value based on your specific auth setup.  Enter this key in config.py as the value of 'REMOTE_USER_HEADER_KEY'

AuthoriZation is handled in the app based on the user_list in each project.  Please see [Pieval Persistance](README_persistence.md), the projects section, for more information.


### Running the app

Here, we take advantage of the Docker Daemon to run the process for us in the background.  Simply launch it with the following command:

```sh
# Must be run from pieval/ repo root directory
docker compose -f docker-compose-prod.yml up -d
```


And to bring it down:

```sh
# must be run from pieval/ repo root directory
docker compose -f docker-compose-prod.yml down 
```

### Persistance

Please see [Pieval Persistance](README_persistence.md) for more information.  But, a note to remind you here that if you launch the app without any data, it will run, but will functionally do nothing.  You must create at least one project before the app has any functionality.