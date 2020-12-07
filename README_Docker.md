# PieVal on Docker
The primary purpose for leveraing Docker, and specifically, Docker Compose in the PieVal project is due to the fact that PieVal leverages the capabilities of other open source technologies to operate.  This allows PieVal to focus specifically on the task of annotation.  Docker Compose allows us to succintly describe all of the dependencies and spin them up on a self contained, docker defined, network for the purposes of testing and development.  This project is largely leveraging off the shelf docker containers, however, we did build one custom one for running the pieval app itself.  This documentation will walk you through that build process.  This document will also walk you through all the testing that was done using just docker prior to encoding the suite of services using the Docker Compose as a convienience layer.


## Building the PieVal docker container
The PieVal docker container is described by the Dockerfile that is a sibling of this document.  This command builds a container from the Dockerfile description.
```sh
# build the image
docker build -t ariedl/pieval:v1.0.0 .
```


## Running All the Docker steps Manually - testing before tidying up into a docker compose file
After everyhing is up and running you will have these artifacts created/operational:
1. Docker Bridge Network - net_pv
1. 3 containers - all connected to net_pv
    - PieVal App - runs the pieval application code
    - Keycloak App - runs the keycloak application code and provides auth as a service
    - Client - To access the app, you must VNC on to this machine which places you 'on' the net_pv network where the app and other services are running


### Step 0 - PRE-REQS
1. Create the net_pv bridge network:
```sh 
docker network create --driver=bridge net_pv
```

### STEP 1 KeyCloak
This command spins up a generic, non-configured instance of KeyCloak.  It is completely ephemeral.  For this reason, the pieval launch contains a step that 'autoconfigures' keycloak over the keycloak API so that it will be ready to offer auth to the app!  This method of configuration is not secure, rather it is intended to be transparent to developers so they can learn the process and understand what needs to be secured when moving into production.

Starting the KeyCloak container:
```sh
docker run -d --name pv_kc --network net_pv -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin jboss/keycloak:11.0.2
```

### STEP 2 - Launch Pieval App
The PieVal app can be launched in 2 ways:
1. Using the Flask built in development web app server
1. Using Gunicorn
We offer up both commands here.  Our DockerCompose file launches using the built in Flask server since Docker is primarily used to create a production like replica of all required services in a development friendly environment.  

During startup, assuming your config.py has RUN_MODE='dev', the pieval app will create all the default configuration necessary for the PieVal app to operate by exercising the KeyCloak API.

> Using Gunicorn:
```sh
docker run --name pieval --network net_pv --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 gunicorn --timeout 1000 -w 4 -b 0.0.0.0:5001 "run:create_app()"
```
> Using Flask development server - This enables autoreload for rapid prototyping code changes:
```sh
docker run --name pieval --network net_pv --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 python run.py
```


If you would like to review the steps required to configure the keycloak instance, please review docker_kc/config_keycloak.py.  To run it:  
```sh
pipenv run python docker_kc/config_keycloak.py
```
After the keycloak container is running it will be accessible at these URLS for testing of the configuration:  
1. Admin console:[http://localhost:8080/auth/admin](http://localhost:8080/auth/admin).  creds = admin/admin
1. Account Test Page: [http://localhost:8080/auth/realms/pieval_realm/account](http://localhost:8080/auth/realms/pieval_realm/account)


### Step 3 - Create a client on net_pv we can use to interact with the services
This command starts a 3rd container on the net_pv network, the sole purpose of which is to allow you to access the PieVal services on the network on which they are running.  This is done because within the network there is 'free' DNS resolution.  This becomes really imporant when we consider how PieVal and KeyCloak interact.  Think of this lifecycle:
1. Navigate to PieVal URL
1. KeyCloak config recognizes you require a login event -> get redirected to KeyCloak service
1. Login
1. Re-directed back to PieVal app

Those redirections require un-ambiguous URL references to all the services from both the perspective of the client AND the PieVal app.  In a production environment this will be handled by a DNS server entry configured by your system administrators that both the client and the container can speak to to resolve URLS.  During development, there is no need for these registrations.  Instead, we can simply rely on the free DNS provided by Docker.
```sh
docker run -d --name sel --network net_pv -p 4444:4444 -p 5900:5900 selenium/standalone-firefox-debug
```

After the client container is started you can VNC onto it with:  
VNC URL: vnc://localhost:5900  
VNC pw : 'secret'