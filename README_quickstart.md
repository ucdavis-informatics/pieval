# Quickstart Instructions
Assuming you have docker and docker compose already installed
1. Clone repo from [here](https://gitlab.ri.ucdavis.edu/ri/pydatautils/pieval)
1. cd pieval
1. docker-compose --verbose up --force-recreate

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