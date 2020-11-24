# Tasks to get pieval running fully containerized AND in dev mode with sidecar KC docker image!

Do it manully first
1. run pv in docker with file data backend but using UCD kc instance - test
1. start up kc docker, auto configure
    - Then flip pv to dev mode which will wire it to kc docker - test

If those tests work, then move towards docker compose

## Inventory
At the end of this in dev mode we will have:
1. Docker Network - pv_net
1. 3 docker containers
    - pv - the pieval app
    - pv_kc - keycloak instance - using container image from JBOSS
    - pv_client - debian linux with firefox and selenium installed.  Using image from Selenium.  This is nice because VNC jsut works but, I want this modded and don't really need selenium.  The way their image is russian dolled, its hard to add new things that just work...

---
## Running with compose
```sh
docker-compose --verbose up --force-recreate
```

--- 
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



### Running PieVal helper scripts
Build Database:
```sh
docker run --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 python build_sql_database.py --keep_example_data yes --build_or_update build
```

Create Project:
```sh
docker run --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 python create_project.py -dt aml_bm_blast_cycle1 -u awriedl -u jmcawood -pd "test project description" -pm binary
```

Delete Project:
```sh
docker run --mount source="$(pwd)",target=/pieval,type=bind -p 5001:5001 ariedl/pieval:v1.0.0 python delete_project.py -pn aml_bone_marrow_results
```


---

## Legacy Commands
**PieVal via Pipenv**
```sh
pipenv run python run.py
```
```sh
pipenv run gunicorn --timeout 1000 -w 4 -b 127.0.0.1:5001 "run:create_app()"
```

```sh
# flip yes to no in the keep_example_data argument if you want an empty database
# flip build to updated in build_or_update argument to have your current database upgraded to latest version!
pipenv run python build_sql_database.py --keep_example_data yes --build_or_update build
```

Create Project:
```shell script
# assumes pipenv is activated
$ python create_project.py -dt aml_bm_blast_cycle1 -u awriedl -u jmcawood -pd "test project description" -pm binary
```


Delete Project
A specific example:  
```shell script
# assumes pipenv is activated
$ python delete_project.py -pn aml_bone_marrow_results
```