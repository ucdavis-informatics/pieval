# Deploying PieVal for production usage
We choose to run pieval in production as a WSGI (pronounce Whiskey) app on managed Virtual Machines instead of using Docker.  This is primarily due to the distribution of local expertise and specific requirements we have for securing and auditing application deployments.  You may absolutely build on the development mode approach to create a Docker based production ecosytem for this app, however this documentation will not cover those steps.

When run as a WSGI app, The PieVal app is running on top of the gunicorn python app server and bound to a localhost port on the host machine.  Web requests to the app are accepted proxied to/from gunicorn by Apache, a web server which is the only point of web traffic to and from the host.  Apache is configured to enforce 'https' communication with clients.  We set up a proxy/reverse proxy pass for all communiction to the host at httpe://host.com/pieval to the underlying gunicorn web app server with rules encoded in yaml like this:
```yaml
proxy_pass:
  -
    path: '/pieval'
    url: 'http://localhost:5001/pieval'
    reverse_urls:
      - 'http://localhost:5001/pieval'
```
The URL to access the app once deployed on a server will be dependent on your hostname and other decistions you may have made.


## Deployment Steps

### Step 1 - build the Pipenv
Build the pipenv.  We use it for DB creation and project managment

### Step 2 - build the database and update pointers to it
Build the database. See README_persistence for details about how to build the SQL database

### Step 3 - Optionally import your own data
Optionally import your own data.  See README_project_management for details about how to import your own project data

### Step 4 - run the app
This command will start the app running behing gunicorn.  There are many methods to running this as background service which is what you want.  We leave that implementation detail up to you.
```sh
# This runs the code in the same way it will be run in production
pipenv run gunicorn --timeout 1000 -w 4 -b 127.0.0.1:5001 "run:create_app()"
```



