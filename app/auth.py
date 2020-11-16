'''
auth.py - Shamelessly copied from CDI aguapanela dashboard code
Only slightly adapted for use in Pieval.
Credit to Matt Renquist.

auth.py is a blueprint for the 'pieval' dashboard flask
web app. It follows the flask app factory pattern as described here:

https://flask.palletsprojects.com/en/1.1.x/blueprints/

This blueprint is 'auth': a basic blueprint to connect to the Flask-OIDC
extension and ensure that a user is logged in before accessing
specific routes.

Flask-OIDC is configured via the instance/client_secrets.json file
as described in the main README.md file.

See the README.md file for more information regarding installation, deployment, and
end user usage of the main dashboard flask app.

Matthew Renquist
msrenquist@ucdavis.edu
CDI3 @ UC Davis Health IT Health Informatics
Copyright 2020, Regents of the University of California

'''

# native imports
import logging
from functools import wraps

# 3rd party modules
from flask import Blueprint, redirect, url_for, session, current_app, request, render_template, flash
from flask_oidc import OpenIDConnect

# get a handle to the logger
logger = logging.getLogger(__name__)

# register this blueprint...and fudge here a little bit because we are assuming
# that this blueprint lives under the main dashboard prefix...flask doesn't
# currently support nested blueprints so this is the hacky solution...
bp = Blueprint("auth", __name__)
# initialize the Flask OIDC extension
oidc = OpenIDConnect()


# build a logged in decorator to avoid duplicating login code...
def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        else:
            flash('Please log in first.')
            return redirect(url_for('auth.login'))
    return decorated_function


@bp.route('/login')
@oidc.require_login
def login():
    logger.debug(f"Entry to login func session: {session}")
    if oidc.user_loggedin:
        session['user_name'] = oidc.user_getfield('preferred_username')
        session['user_groups'] = oidc.user_getfield('groups')
        session['logged_in'] = True
        logger.debug(f"After OIDC param updates to session: {session}")
        return redirect(url_for('pieval.pievalIndex'))
    else:
        return render_template('user_not_found.html')


@bp.route('/logout')
def logout():
    if session.get('logged_in'):
        session.pop('logged_in')
    if session.get('user_name'):
        session.pop('user_name')
    if session.get('example_order'):
        session.pop('example_order')
    if session.get('cur_example'):
        session.pop('cur_example')
    oidc.logout()
    # should be as simple as:
    # return redirect(url_for('pievalIndex'))
    # but due to flask-oidc bug it needs to be
    return redirect(oidc.client_secrets.get('issuer')+'/protocol/openid-connect/logout?redirect_uri='+request.host_url+'pieval')


# this is a group checking decortator to check authz on a per module/route basis
# logic is a little complex b/c to get a decorator to take args, you need to
# make a func that passes the arg to the wrapped function.
# Logic/code from: https://stackoverflow.com/questions/10176226/how-do-i-pass-extra-arguments-to-a-python-decorator
def group(group_name):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # check to see if the user that we have set in the session after login
            # is in the group, if so, procede with the route
            if group_name in session.get('user_groups'):
                logger.info(f"In group: {group_name}")
                return func(*args, **kwargs)
            # otherwise, just bounce back to the main dashboard page.
            else:
                logger.info(f"Not in group {group_name}")
                return redirect(url_for(current_app.config['MASTER_BLUEPRINT']))
            # return func(*args, **kwargs)
        return wrapper
    return actual_decorator






####################################################################################
####################################################################################
####################################################################################
####################################################################################

# # the primary route for the auth blueprint. There's no template for the login page
# # because the login is handled via keycloak/oidc
# @bp.route("/login")
# @oidc.require_login
# def login():
#     """
#     Force the user to login, then redirect them to the dashboard.
#     """
#     # Once logged in via keycloak, set a bunch of fields on the session dictionary
#     # so that we can check later for group membership, etc.
#     if oidc.user_loggedin:
#         user_groups = oidc.user_getfield('groups')
#         session['username'] = oidc.user_getfield('preferred_username')
#         session['user_groups'] = oidc.user_getfield('groups')
#         session['email'] = oidc.user_getfield('email')
#         session['fullname'] = oidc.user_getfield('full name')
#         logger.info(f"User: {session['username']} logged in.")

#         # by default, users can't look up patients, unless in patient group.
#         session['patient_search'] = False
#         for group_name in session['user_groups']:
#             # can the user look up patients, if so, then redefine it to true to enable the search button.
#             if current_app.config['PATIENT_GROUP'] in group_name:
#                 session['patient_search'] = True
#         # if the user is already logged in, then just redirect to the base
#         # page/route for the dashboard.
#         # check to see if the user is in at least one of the dashboard user groups
#         if current_app.config['USER_GROUP'] in group_name:
#             return redirect(url_for(current_app.config['MASTER_BLUEPRINT']))
#     return render_template('user_not_found.html')