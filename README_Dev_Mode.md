# Quickstart Instructions
These instructions will help you launch PieVal quickly for Demonstration or Development.

## Overview
Because PieVal has some necessary dependencies, namely KeyCloak for Authentication, we have chosen to develop an execution environment based on Docker for use during development and demonstrations.  In this mode, the app is running in a very similar manner to how it will run in production mode except that it's not actually secure and everything is exposed to you the developer so you can fully experiment as you add new features.  We package the app with everything needed to simply download and launch, including demo data.  This prevents the expense of establishing service dependencies simply to get a feel for the app or to participate in the open source development process.

After following these instructions you will have these Docker objects up and running:
1. Docker Network - pv_net
1. 3 docker containers
    - pieval - the pieval app
    - pv_kc - keycloak instance - using container image from JBOSS
    - pv_client - debian linux with firefox and selenium installed.  Using image from Selenium that can be used for viewing the app and/or automating web tests

After these objects are running, you access the app by logging into the pv_client over [VNC](https://en.wikipedia.org/wiki/Virtual_Network_Computing) using a vnc viewer.  This places you 'on' the fully self contained [Docker Bridge Network](https://docs.docker.com/network/bridge/), 'net_pv', on which the minimum set of dependencies are running in order to re-create an environemt technically similar to that which would exist in a production deployment.

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
    - client_secrets.json/client_secrets_dev.json - KeyCloak connection information.  We keep two version of this file.  One for Development Mode and one for Production mode for convenience.  We suggest you do the same.  

We do not include 'real' secrets files in the git repo.  In fact they are specifically 'gitignored' to prevent secret leakage into the code repository!  We include example files you can use as a quickstart prefixed with 'example_' in the instance directory.  To use them create renamed copies of them, removing the 'instance_' prefix.  The included examples are complete and allow you to run the app in development mode - make the approprate copies using the commands below (*nix systems) or via your operating systems file explorer.
```sh
cd instance
cp example_config.py config.py
cp example_client_secrets.json client_secrets.json
cp example_client_secrets_dev.json client_secrets_dev.json
cd ..
```
> Since you have followed these instructions and copied the example files you can simply proceed.  However there are a few key settings I'll call out that will increase your understanding:  
In config.py RUN_MODE is set to dev.  This, in turn sets a number of parameters for KeyCloak and tells the app to use client_secrets_dev.json for any KeyCloak secrets.  Given that these are exposed in plain text in this repo, it should be known that dev mode is not intended to be secure.  It is intended to give developers complete control and understanding of the app build.  

4. Start the app
```sh
docker-compose --verbose up --force-recreate
```
Wait about 15 seconds until the terminal output calms down indicating startup is complete.  

It's now time to access the PieVal App:  
1. Open a VNC client.  On mac you can use safari.  If on windows, you might need a VNC client.  Download one of your choice. 
    - VNC URL: vnc://localhost:5900  
    - VNC password: 'secret'


> NOTE: process improvement in the works.  This step is a little annoying.  I will build a custom client image thats easier to use.  For now, PieVal is using a pre-built docker container from selenium for proof of concept.
TODO's include:
> - Clickable browser icons (firefox, chrome, opera, etc..) on the desktop

For now:  
1. Right click -> Applications -> Shells -> bash
2. Launch firefox using the shel
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
