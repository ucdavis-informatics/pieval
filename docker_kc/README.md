# Keycloak on Docker
Primary use-case:  Package keycloak with a containerized PieVal to make for a better release into the open source world.  This first requires understanding how to run keycloak on docker on it's own.  We will need to figure out how to package default pieval accounts to make for a more interesting out of the box run/demo

## Documentation links
[KC docs](https://www.keycloak.org/documentation.html)
[KC API Docs](https://www.keycloak.org/docs-api/11.0/rest-api/index.html#_overview)
[KC on Docker Quickstart](https://www.keycloak.org/getting-started/getting-started-docker)
[KC Securing Apps](https://www.keycloak.org/docs/latest/securing_apps/)

```sh
# start KC docker image with
docker run --name pv_kc -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin -d quay.io/keycloak/keycloak:11.0.2
```

### Necessary Configuration Steps
The basic unit in KeyCloak is the Realm.
1. Create a Realm
1. Create Users in that realm
    - usernames/passwords
1. Create client of that realm
    - client id
    - client secret


### KC Admin UI
Admin console [http://localhost:8080/auth/admin](http://localhost:8080/auth/admin).  creds = admin/admin


### Configuration with API
An alternative way to accomplish this is to automate it using the Keycloak API.  Much inspiration drawn from [this gentlemens blog](https://suedbroecker.net/2020/08/04/how-to-create-a-new-realm-with-the-keycloak-rest-api/)  

Please review the sibling file api_config.py for interactive examples

GOAL: create a python script that can be run from the docker HOST, exercising the API to build a default realm and default users for the purposes of development/ easy demo deployments

This is now complete.  After the containter starts up run:
```sh
pipenv run python docker_kc/config_keycloak.py
```

Now, we must test!  At minimum, we need to try logging in with the user we added in the autoconfig.  This will tell us that the realm and user were created successfully.
[http://localhost:8080/auth/realms/pieval_realm/account](http://localhost:8080/auth/realms/pieval_realm/account)

### KC Tech Deets
KC Docker Image is running Red Hat Enterprise Linux v8.2 (as of 20201013)
KC, the software appears to be a Java webapp running on Wildfly

