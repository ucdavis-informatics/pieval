# Keycloak on Docker
Primary use-case:  Package keycloak with a containerized PieVal to make for a better release into the open source world.  This first requires understanding how to run keycloak on docker on it's own.  We will need to figure out how to package default pieval accounts to make for a more interesting out of the box run/demo

## Documentation links
https://www.keycloak.org/documentation.html
https://www.keycloak.org/docs-api/11.0/rest-api/index.html#_overview

## Quickstart guide to running KeyCloak on Docker
[Link](https://www.keycloak.org/getting-started/getting-started-docker)

```sh
# start KC docker image with
docker run -p 8080:8080 -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin quay.io/keycloak/keycloak:11.0.2
```

### Configuration with UI
After Docker is running, we need to set up a realm and at least one user. One way to do this is with the UI.  We need to log in to the admin console [http://localhost:8080/auth/admin](http://localhost:8080/auth/admin).  Use admin/admin (defined in docker command above to login)

- create a realm
- create a user within the realm

Test the user by logging into account portal (assuming realm is 'myrealm'): 
[http://localhost:8080/auth/realms/myrealm/account](http://localhost:8080/auth/realms/myrealm/account)  
When prompted enter user credentials create earlier


### Configuration with API
An alternative way to accomplish this is to automate it using the Keycloak API.  Much inspiration drawn from [this gentlemens blog](https://suedbroecker.net/2020/08/04/how-to-create-a-new-realm-with-the-keycloak-rest-api/)  

Please review the sibling file api_config.py for interactive examples

GOAL: create a python script that can be run from the docker HOST, exercising the API to build a default realm and default users for the purposes of development/ easy demo deployments


### KC Tech Deets
KC Docker Image is running Red Hat Enterprise Linux v8.2 (as of 20201013)
KC, the software appears to be a Java webapp running on Wildfly

