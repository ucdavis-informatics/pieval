# PieVal

PieVal is an open source text annotation tool, with a few tricks up its sleave that make it fast and fun to use!  Please start [here](docs/index.md) to learn more about the app.

## Repo Manifest

- .devcontainer - VS Code specific files that build a docker based development environment
- app/ - source code for the flask application
- docs/ - Go [here](docs/index.md) for all your documentation needs
- example_database/ - fake data for development and testing
- instance/ - location of app config (config.py).  Go see [running the app documentation](docs/README_run_app.md) to get your config set up correctly
- log/ - placeholder for log files.  You can choose to use this location or not in config.py
- mongo_data/ - placeholder for mongo db docker container bind mount enabling permanence to persistence.  You can can configure this in docker-compose-prod.yml
- src/ - home for jup notebooks used during testing/prototyping
- .gitignore - tells git to ingore certain files in this repo - secrets, compiled files, log file, etc...
- create_project.py - used to help you create projects from data you create.  See [Creating a project](docs/README_persistence.md#how-to-create-a-project) for additional info
- delete_project.py - will be used rarely but, should you need it, it will delete all project data from the database for you
- docker-compose-dev.yml - used to launch app in dev mode
- docker-compose-prod.yml - used to luanch app in production mode (will take some work to ensure security and data persistance - some of it beyond the included docs)
- Dockerfile - defines runtime for app
- license.txt - Indicates the licences that applies to this code
- mkdocs.yml - Layout instructions for [mkdocs](https://www.mkdocs.org) based documentation site
- README.md - how meta
- requirements.txt - list of python dependencies required to make this app go
- run.py - App entrypoint for launching in dev mode (called in docker-compose-dev.yml)
