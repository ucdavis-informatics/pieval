# Quickstart Instructions
These instructions will help you launch PieVal quickly for Demonstration or Development.

## Overview
Because PieVal has some necessary dependencies, namely KeyCloak for Authentication, we have chosen to develop an execution environment based on Docker for use during development and demonstrations.  In this mode, the app is running in a very similar manner to how it will run in production mode except that it's not actually secure and everything is exposed to you the developer so you can fully experiment as you add new features.  We package the app with everything needed to simply download and launch, including demo data.  This prevents the expense of establishing service dependencies simply to get a feel for the app or to participate in the open source development process.

After following these instructions you will have these Docker objects up and running:
1. Docker Network - pv_net
1. 3 docker containers
    - pv - the pieval app
    - pv_kc - keycloak instance - using container image from JBOSS
    - pv_client - debian linux with firefox and selenium installed.  Using image from Selenium that can be used for viewing the app and/or automating web tests

After these objects are running, you access the app by logging into the pv_client over [VNC](https://en.wikipedia.org/wiki/Virtual_Network_Computing) using a vnc viewer.  This places you 'on' the fully self contained network, net_pv, on which the minimum set of dependencies are running in order to re-create an environemt technically similar to that which would exist in a production deployment.

## Pre-Reqs
1. docker and docker-compose

## Launch Steps
1. Clone repo from [here](https://gitlab.ri.ucdavis.edu/ri/pydatautils/pieval)
```sh
git clone <clone url from repo>
```
2. Navigate into the pieval directory
```sh
cd pieval
```
3. Set up the secrets files.  You need to create 3 files in the instance/ directory:
    - config.py - Flask app configuration. 
    - client_secrets.json/client_secrets_dev.json - KeyCloak connection information.  We keep two version of this file.  One for Development Mode and one for Production mode for convinience.  We suggest you do the same, even if they contain the same settings.
We do not include 'real' secrets files in the git repo.  In fact they are specifically gitignored to prevent secret leakage back to a code repository!  We do include example files you can use as a quickstart prefixed with 'example_' in the instance directory.  To take advantage of them create copies of them and then rename them, removing the 'instance_' prefix.  Using the example files will allow you to run the app in Dev Mode with Docker.
```sh
cd instance
cp example_config.py config.py
cp example_client_secrets.json client_secrets.json
cp example_client_secrets_dev.json client_secrets_dev.json
cd ..
```
4. Start the app
```sh
docker-compose --verbose up --force-recreate
```

Now the services are started, its time to access them  
Open a VNC client.  On mac you can use safari.  
vnc://localhost:5900  
password: 'secret'

> It gets annoying here.  I will build a custom client image thats easier to use.  For now, I'm using a pre-built image from selenium purely for proof of concept.  I want to alter the client image to simply have a clickable firefox icon (and other browesers too for compatibility testing) on the desktop.

1. Right click -> Applications -> Shells -> bash
2. Launch firefox
```sh
$ firefox
```
3. Navigate to app: 'pieval:5001/pieval'
    - u/p = pieval/pieval
4. play with app

Things to try:  
On your host you can watch annotation events being recorded as you interact by watching example_database/annotation_events.csv

Take a look at the other files in example_database.  App behavior is modified by some of the data in these tables.  
- Try adding a class to the one of the projects in classes.csv and seeing how that alters the drop down options in the disagreement workflow.
- Try changing a from multiclass to binary and back again in projects.csv.  See how this impacts the disagreement workflow.

Take a look at the code.  You can make changes in real time.  The app will reload with your changes.  This enables rapid development.

> Pro Tip: These changes will have an immediate impact because the PieVal app container is sharing these files with you via Docker Bind Mount.  This means that PieVal is merely referencing these files that exist on your computers filesystem!




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






Running on Docker:  
```sh
# build the image
docker build -t ariedl/pieval:v1.0.0 .
```

```sh
docker run --name pieval --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 gunicorn --timeout 1000 -w 4 -b 0.0.0.0:5001 "run:create_app()" 
```

- Access app by URL - [localhost:5001](http://localhost:5001)


## Running Manually

### PRE-REQS Creating a docker network.  This only needs to happen once
docker network create --driver=bridge net_pv


### STEP 1 Start KC on Docker
```sh
docker run -d --name pv_kc --network net_pv -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin jboss/keycloak:11.0.2
```

### STEP 2 - Launch Pieval App
> Using Gunicorn
```sh
docker run --name pieval --network net_pv --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 gunicorn --timeout 1000 -w 4 -b 0.0.0.0:5001 "run:create_app()"
```
> Using Flask development server - This enables autoreload for rapid prototyping code changes
```sh
docker run --name pieval --network net_pv --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 python run.py
```
**APP URL**: [localhost:5001/pieval](http://localhost:5001/pieval)

This includes the autoconfiguration of the keycloak service.  If you wish to prototype/develop the autoconfiguration step, you can use this command to run the autoconfiguration step manually.
```sh
pipenv run python docker_kc/config_keycloak.py
```
Admin console:[http://localhost:8080/auth/admin](http://localhost:8080/auth/admin).  creds = admin/admin
Account Test page for pieval realm: [http://localhost:8080/auth/realms/pieval_realm/account](http://localhost:8080/auth/realms/pieval_realm/account)



### Step 3 - Create a client on net_pv we can use to interact with the services
```sh
docker run -d --name sel --network net_pv -p 4444:4444 -p 5900:5900 selenium/standalone-firefox-debug
```

vnc://localhost:5900  pw = secret