# Running The App

PieVal is a WebApplication that runs on top of the following technologies (starting from lowest, OS and working up)

1. Linux VM - This can be any flavor of linux supported at UCDHS that is capable of running Docker
1. Apache/httpd - This is web server that runs on linux.  It must be configured with a UCDHS AD proxy to whatever port the webapplication is running on inside of Docker
1. [Docker](https://www.docker.com/) - A technology for created isolated runtime environments.  The following technologies are packaged inside of a Docker container desinged to run this app
    - [Gunicorn](https://gunicorn.org/) - A python WebApplication server.  It recieves requests that have been previously authenticated by Apache on the linux VM via a proxy
    - [Flask](https://flask.palletsprojects.com/en/2.2.x/) - Python WebApplication framework.  Handles web application routing, logic, and rendering inside the typical request/response lifecycle of the web
    - [PieVal Application Code](https://gitlab.ri.ucdavis.edu/ri/pydatautils/pieval) - The code that makes PieVal, PieVal



The PieVal application needs to run in 2 different contexts:

1. Development - new feature development, patching, package upgrades, etc..
1. Production - load balanced for multiple users, authentication, backed by robust persistence store

These are very different in terms of what's required of the app.  It is currently a pretty manual process to switch between these two modes.  For now, only running in development mode will be addressed

--- 

## Development mode

In thise mode the linux vm and apache/httpd (with associated auth) are irrelevant.  You will only be running from the Docker layer down through the application code.  To do this is pretty easy and takes only a few steps

#### Step 1 - build the docker container

From project root run:

```sh
docker build -t ariedl/pieval:v1.0.0 .
```

This will create an image named ariedl/pieval:v1.0.0 based on the Dockerfile at project root

#### Step 2 - run the app

From project root, run this:

```sh
docker run -it \
--mount src=$(pwd),target=/pieval,type=bind \
-p 5001:5001 \
ariedl/pieval:v1.0.0 /bin/bash -c "cd /pieval && python run.py"
```

This:
1. starts the app with an interactive shell so that you can view the logs
1. Mounts the current directory (the pieval codebase) to the container so that the code is available to execute
1. Forwards port 5001 from the container to the host - so you can navigate to the app running in the container
1. Launches the application in the contaier by calling run.py

> NOTE: Since this is development mode, you can alter the code and the app will reload any changes allowing for rapid iteration


## Production Mode

In order to run the app in production mode, please contact Bill Riedl at awriedl@ucdavis.edu in order to set up a secured/authed version of the app for you to use!