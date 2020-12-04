# PieVal
![pieval logo](app/static/images/pieVal_Logo_medium.png)  


# About
PieVal is the product of an idea, many work hours, a prototype in rShiny, and fairly extensive user testing.  And it's still growing.  The idea was a clever repurposing of common web app functionality seen in viral social apps like Tinder.  In these apps, users record their preferences with a quick swipe of the screen.  We wanted to bring that efficiency to data labeling.  

PieVal originated in a clinical setting in which data labelling has been prohibitively expensive, stunting the use of machine learning.  Typically, data labelling efforts involve clinical experts reviewing data directly in an Electronic Medical Record, often taking minutes just to locate the data being reviewed, then entering their findings in a separate tool.  PieVal removes all of this complexity, placing the data and the response capture in a lightweight, distraction free UI.  While this adds a set-up cost, it's concentrated as a one-time effort rather than forcing each annotator to pay it for each and every annotation.

PieVal was a response to a need as our team grappled with how to accelerate a growing number of natural language processing techniques for the UC Davis Cancer center.  The first attempt started with some tweaked open source tooling, written in R, and leveraging the rShiny ecosystem.  After a few iterations in R/rShiny it became apparent that the framework was not up to the task but, it had been extremely helpful in shaping the final requirements.  The app was ported to Python using the Flask webapp framework in January 2020.

## Key Features
- Secure (when served over HTTPS and secured by [Keycloak](https://www.keycloak.org))
- Gamified - This is accomplished primarily with a project leaderboard, allowing for friendly competitions.  Best if combined with incentives, like coffee cards. 
- Assertion tester - Rather than presenting the user with data and asking for an annotation, we present the user with data, an assertion (either human or machine generated) and ask them to Agree, Disagree, Review, or Pass.  The result is a consistent UI that does not change, no matter the task allowing users to become extremely efficient with the tool.
- Built in enrichment strategy testing.  By default the user is presented with a clipped, enriched, or otherwise modified version of the data designed to speed up both the annotation times and downstream ML training times simply by acting on less, more specific data, to the task.  Enriching in this way requires a framework to ensure the enrichement is effective.  PieVal can also present the unmodified data IF the annotator asks for it.  The ask is recorded with the annotation allowing you to measure how often the enrichment failed and required a 'full review' to annotate correctly.
- Annotation compliance - PieVal can be configured to send reminder emails to keep annotators engaged after defined periods of inactivity.
- Post annotation tooling to measure IntrA and IntER operator agreement statistics

---

## Technical Deets
There are MANY ways to run PieVal and a reason for each one.  For documentation brevity, we will spell out an opinionated view of the two ways we run the app, which are:
1. **Development Mode** - This mode provides a fully offline development ecosystem well suited to development.  We use docker to provide all the service dependencies such the app functions the same as it would in production, allowing for rapid iteration protoyping and development in the context of a real looking envrionment.  We also encourage this mode be used for tool demonstrations!  Please note that running in Dev Mode is NOT SECURE.  See README_Dev_Mode for quickstart instructions.
1. **Production Mode** - We do not run pieval on docker in production.  This is simply due to the existing expertise and deployment practices at our instituion.  When in production, we use run PieVal as a WSGI app inside of a Pipenv managed python virtual environment.  Deploying in production is a heavier lift primarily due to the extra steps to ensure your deployment is secure and running against a SQL database instead of the filesystem backen.  You should do this if you are ready to run your own data through PieVal.  Please see README_Production_Mode for instructions about how to deploy and add your own data to the project.

Required Dependencies:
1. Python runtime envrionment which can be provided either by Pipenv or Docker, depending on how you choose to run the app
  - Python 3.6 or greater
  - A set of pip installable modules defined in Pipfile and also in requirements.txt
1. A [KeyCloak](https://www.keycloak.org) instance which provides AuthN services to the app
1. Persistance Strategy.  The app can always run using filesystem and csv files.  One can optionallly connect to a SQL database.  See README_peristence for more detail

Optional dependencies:
1. RDBMS if choosing to run a SQL database for persistence.  See README_persistence for more detail
1. [Vault](https://www.vaultproject.io) - Vault provides secrets as a service.  We use this to provide the RDBMS connection credentials.  Given it's limited scope it would be a fairly trivial operation to modify the code to simply pull the secrets from a secrets file instead of from vault.  For more information about how vault is used in this project see README_vault

### App Config
All App config is housed in the instance/.  App configuration:
- Dictates Run Mode ['dev','prod]
- Instructs the app where to look for KeyCloak, the only required dependency.  
- It also instructions the app of which persistence strategy will be used, its location, and how to access secrets and connect to it.  

Configuration is managed in 2 files that **require your attention**.  The 'real' versions of these files are excluded from the git reposityr they contain, instance specific, configuration that should not be shared.  For convinence we include examples of these files prefixed with 'example_' in the instance/ directory.  You will need to create copies of these files, removing the 'example_' prefix and populate them with your own instance specific configuration.  See the example files for inline documentation:
1. config.py - Flask app configuration.  
1. client_secrets.json/client_secrets_dev.json - KeyCloak connection information.  We keep two version of this file.  One for Development Mode and one for Production mode for convinience.  We suggest you do the same, even if they contain the same settings.


### App Sessions
While the app is running, it makes heavy use of the session variable, a dictionary for holding stateful content.  This app manages these session variables
1. logged_in - bool indicating whether logged in or not
1. user_name - contains unique id for current user.  After shib'd, this entry will hold the REMOTE_USER variable
1. cur_proj - unique name of current active project
1. project_mode - binary or multi-class, alters behavior when saving annotations
1. example_order - a list of integers, where each integer uniquely identifies an example from the current project
1. cur_example - a single integer, containing the current active example id in this users session
1. prev_example - a single integer, containing the previous example annotated.  Used to allow for 'Doh!' functionality

### Background Tasks
Using the [Flask AP Scheduler](https://github.com/viniciuschiele/flask-apscheduler) some helpful background tasks are triggered:
1. Renew Vault approle token - Without any utilization the approle tokens expire every 192 hours.  This triggered task renews the token every 13 hours to prevent the approle token from expiring
1. Send Reminder Emails - If configured, this task will send emails (only M-F at 0900) to all system users that have exceeded the configurable number of days since recording an annotation while they have active projects.  Helpful for annotation compliance.


---
### Contributor Credits
Bill Riedl: Idea guy / Lead dev  
Joseph Cawood: valR prototype author/ PieVal power user  
Matt Renquist: Auth and Deployment strategy  
Aaron Rosenburg: Primary clinical test user  
Jp Graff: Clincal test user  
Cy Huynh: Logo Developer  


### Authorship
- Bill Riedl   
- Original Author Date: 2019-01-13   
- Copyright Regents of the University of California
- 2020