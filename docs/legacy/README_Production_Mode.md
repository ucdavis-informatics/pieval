# Deploying PieVal for production usage
PieVal runs as a WSGI (pronounced Whiskey) app as a set of microservices on Docker.  This is primarily due to the distribution of local expertise and specific requirements we have for securing and auditing application deployments.

There are 3 technologies involved with any deployment of PieVal:

1. apache httpd
1. Gunicorn web application server
1. PieVal App

Web requests to the app are accepted proxied to/from gunicorn by Apache, a web server which is the only point of web traffic to and from the host.  Apache is configured to enforce 'https' communication with clients.  We set up a proxy/reverse proxy pass for all communiction to the host at https://host.com/pieval to the underlying gunicorn web app server. Here are the rules encoded in yaml (we use [Puppet](https://puppet.com) to configure our VM's):
```yaml
proxy_pass:
  -
    path: '/pieval'
    url: 'http://localhost:5001/pieval'
    reverse_urls:
      - 'http://localhost:5001/pieval'
```
The URL to access the app once deployed on a server will be dependent on your hostname.


## Deployment Steps

### Step 1 - build the Pipenv
Build the Docker Image.  We use it for DB creation and project managment

### Step 2 - build the database and update pointers to it
Build the database. See README_persistence for details about how to build the SQL database

### Step 3 - Optionally import your own data
Optionally import your own data.  See [README_project_management](README_project_management.md) for details about how to import your own project data

### Step 4 - run the app
This command will start the app running behing gunicorn.  There are many methods to running this as background service which is what you want.  We leave that implementation detail up to you.
```sh
# This runs the code in the same way it will be run in production
docker-compose --verbose up -d --force-recreate
```

> At this point the app is running on the VM and accepting only connections from local host.  By chaning 127.0.0.1 to 0.0.0.0 you can allow the gunicorn server to accept request from other hosts as well.  This can be valuable temporarily if trying to debug the proxy between Apache and Gunicorn but it is NOT recommened to use 0.0.0.0 for full time deployments.


