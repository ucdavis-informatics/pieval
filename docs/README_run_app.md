# Running The App

PieVal is a WebApplication that runs on top of the following technologies (starting from lowest, OS and working up)

1. Linux VM - This can be any flavor of linux supported at UCDHS that is capable of running Docker
1. Apache/httpd - This is web server that runs on linux.  It must be configured with a UCDHS AD proxy to whatever port the webapplication is running on inside of Docker
1. [Docker](https://www.docker.com/) - A technology for creating isolated runtime environments.
1. [Docker Compose](https://www.docker.com/) - used to orchestrate 2 containers for this project
1. Container 1 - WebApp
    - [Gunicorn](https://gunicorn.org/) - A python WebApplication server.  It recieves requests that have been previously authenticated by Apache on the linux VM via a proxy
    - [Flask](https://flask.palletsprojects.com/en/2.2.x/) - Python WebApplication framework.  Handles web application routing, logic, and rendering inside the typical request/response lifecycle of the web
    - [PieVal Application Code](https://gitlab.ri.ucdavis.edu/ri/pydatautils/pieval) - The code that makes PieVal, PieVal
1. Container 2 - Mongo - provides persistance


The PieVal application needs to run in 2 different contexts:

1. Development - new feature development, patching, package upgrades, etc..
1. Production - load balanced for multiple users, authentication, backed by robust persistence store

Docker Compose is used to launch the app in either context.

--- 

## Development mode

In this mode the linux vm and apache/httpd (with associated auth) are irrelevant.  You will only be running from the Docker layer down through the application code.  It only takes one command to launch the app in dev mode:

```sh
# must be run from pieval/ repo root directory
docker compose -f docker-compose-dev.yml up
```

This:
1. starts the app with an interactive shell so that you can view the logs
1. Mounts the current directory (the pieval codebase) to the container so that the code is available to execute
1. Forwards port 5001 from the container to the host - so you can navigate to the app running in the container
1. Launches the application in the contaier by calling app/wsgi.py
    - wsgi.py contains a main func for when its called in this context

> NOTE: Since this is development mode, you can alter the code and the app will reload any changes allowing for rapid iteration


This will launch the app in development mode AND will overwrite the database with packaged example data.  This mode is for developing new functionality, debugging, or demonstration of the apps functionality.

When you are done, please be sure to shut down the app gracefully:

```sh
# two steps
# must be run from pieval/ repo root directory
ctrl+'c'
docker compose -f docker-compose-dev.yml down
```


## Production Mode

In order to run the app in production mode, please contact Bill Riedl at awriedl@ucdavis.edu in order to set up a secured/authed version of the app for you to use!

Bill Riedl will help:
1. Choose a Linux host on which to run the application (you must provide the host)
1. Implement UCDH AD auth proxy using Apache httpd (web server)
1. provision and launch PieVal codebase behind proxy established in step 2


```sh
# Must be run from pieval/ repo root directory
docker compose -f docker-compose-prod.yml up -d
```


And to bring it down


```sh
# must be run from pieval/ repo root directory
docker compose -f docker-compose-prod.yml down 
```