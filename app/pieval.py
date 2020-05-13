'''
index.py - main app module for pieval.  Will put user on home page
'''
# Imports
from flask import (
    Blueprint, url_for, render_template, session, request, redirect, flash
)
import pandas as pd
from datetime import datetime
from random import shuffle
import logging
from logging.handlers import TimedRotatingFileHandler
from functools import wraps
# auth imports
from flask_oidc import OpenIDConnect

# siblings
from app.data_loader import (
    FileDataLoader, DBDataLoader, InvalidVaultTokenError
)

# define the app
from app import app
#from app import scheduler
# wrap app in auth
oidc = OpenIDConnect(app)

bp = Blueprint('pieval', __name__, static_folder='static')
##########################################################################
# app environ
# variables/dataloader/logger
##########################################################################
logger = logging.getLogger()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger.setLevel(logging.DEBUG)

fh = TimedRotatingFileHandler(app.config['LOGFILE_LOCATION'], when="midnight", interval=1, encoding='utf8')
fh.suffix = "%Y-%m-%d"
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# construct data loader based on env file
# consider using flask-sqlalchemy.  This is app scoped not sessio managed
# >may< not scale.  Tested with 3 concurrent users and all things fine
if app.config['DATASOURCE_TYPE'] == 'file':
    pv_dl = FileDataLoader(app.config['DATASOURCE_LOCATION'], logger)
elif app.config['DATASOURCE_TYPE'] == 'db':
    pv_dl = DBDataLoader(app.config['VAULT_ROLE_ID'],
                         app.config['VAULT_SECRET_ID'],
                         app.config['VAULT_SERVER'],
                         app.config['DATASOURCE_LOCATION'],
                         app.config['DB_SCHEMA'],
                         logger)


################################################################
# Functions
################################################################
# build a logged in decorator to avoid duplicating login code...
def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return f(*args, **kwargs)
        else:
            flash('Please log in first.')
            return redirect(url_for('pieval.login'))
    return decorated_function


def checkAuthZ(project_name, user_name):
    try:
        user_proj_list = pv_dl.getProjectUsers()[user_name]
    except InvalidVaultTokenError:
        return render_template('bad_vault_token.html')
    return True if project_name in user_proj_list else False


def list_diff(l1, l2):
    return list(set(l1) - set(l2))


####################################################################
# web events
####################################################################
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


@bp.route("/")
@logged_in
def pievalIndex():
    if not session.get('logged_in'):
        # if not logged in
        # return render_template('login.html')
        redirect(url_for('pieval.login'))
    else:
        # user is logged in
        # user is returning to index, possibly after annotating
        # reset their state by conditionally clearing session vars
        vars_to_pop = ['cur_proj', 'project_mode', 'example_order', 'cur_example', 'prev_example']
        for var in vars_to_pop:
            if var in session.keys():
                session.pop(var)
        # log session
        logger.debug(f'Index session var is {session}')
        # get all projects for user
        try:
            pieval_projects = pv_dl.getProjects(user_name=session['user_name'], return_as_dataframe = True)
            data = pv_dl.getProjectData(return_as_dataframe=True)
            prev_annots_for_user = pv_dl.getPriorAnnotations(user_name=session['user_name'], return_as_dataframe=True)
        except InvalidVaultTokenError as e:
            logger.error(f"Caught bad token error{e}")
            return render_template('bad_vault_token.html')
        except KeyError as e:
            logger.error(f"Caught missing person key error{e}")
            return render_template('user_not_found.html')
        except Exception as e:
            logger.error(f"Caught unidentified error{e}")
            return render_template('error.html')

        # Assuming no exceptions: compute project stats
        proj_example_counts = (data.groupby(['project_name'])
                                   .size()
                                   .to_frame()
                                   .rename(columns={0:'num_examples'})
                                   .reset_index())

        user_proj_counts = (prev_annots_for_user.groupby(['project_name'])
                                   .size()
                                   .to_frame()
                                   .rename(columns={0:'num_annotated'})
                                   .reset_index())

        proj_status = pd.merge(proj_example_counts,
                               user_proj_counts,
                               on='project_name',
                               how='left')
        proj_status['pct_complete'] = round( (proj_status['num_annotated'] / proj_status['num_examples']) * 100)
        proj_status = proj_status.fillna(0)

        # join tables together
        pieval_projects = pieval_projects.merge(proj_status.filter(['project_name','pct_complete']), on='project_name', how='left')

        return render_template('index.html', projects=pieval_projects.to_dict(orient='records'))


@bp.route("/project/<project_name>")
@logged_in
def project(project_name=None):
    if not project_name:
        return "You did not provide a project name, Try again" + url_for('pievalIndex')
    else:
        if checkAuthZ(project_name, session['user_name']):
            # get project metadata
            try:
                project_metadata = pv_dl.getProjectMetadata(project_name)
                logger.debug(f'In project() function project metadata is: {project_metadata}')
                # get all records for project and use it to set an order variable in the users session
                project_data = pv_dl.getProjectData(project_name=project_name)
                # logger.debug(f'In project() Project data for {project_name} is {project_data}')
                proj_example_list = [x['example_id'] for x in project_data]

                # get prior annotations for this project
                prev_proj_annots_for_user_df = pv_dl.getPriorAnnotations(project_name=project_name, return_as_dataframe=True)
                if prev_proj_annots_for_user_df.shape[0] > 0:
                    project_leaderboard = (prev_proj_annots_for_user_df.groupby(['user_name']).size()
                                           .to_frame()
                                           .rename(columns={0: 'annotation_count'})
                                           .sort_values(['annotation_count'], ascending=False)
                                           .reset_index(drop=False))
                    # add medals
                    if project_leaderboard.shape[0] >= 1:
                        project_leaderboard.loc[0, 'medal'] = 'images/gold_small.png'
                    if project_leaderboard.shape[0] >= 2:
                        project_leaderboard.loc[1, 'medal'] = 'images/silver_small.png'
                    if project_leaderboard.shape[0] >= 3:
                        project_leaderboard.loc[2, 'medal'] = 'images/bronze_small.png'
                    project_leaderboard['medal'] = project_leaderboard['medal'].fillna('images/sad_small.png')
                else:
                    project_leaderboard = pd.DataFrame()

                project_leaderboard = project_leaderboard.to_dict(orient='records')
                project_leaderboard

                prev_proj_annots_for_user = prev_proj_annots_for_user_df.loc[prev_proj_annots_for_user_df['user_name']==session['user_name']].to_dict(orient='records')
                prior_example_list = [x['example_id'] for x in prev_proj_annots_for_user]

            except InvalidVaultTokenError:
                return render_template('bad_vault_token.html')

            # compute remaining annot list
            remaining_examples = list_diff(proj_example_list, prior_example_list)
            shuffle(remaining_examples)
            # user is entering this project - update their session to reflect that
            session['example_order'] = remaining_examples
            session['cur_proj'] = project_name
            session['project_mode'] = project_metadata['project_mode']

            logger.debug(f'In Project() session is {session}')
            # land them on a page that says something like you have selected to annotate for <project name>, you have already annotated <n> records.  There are N left
            return render_template('project.html',
                                   project_metadata=project_metadata,
                                   total_examples=len(proj_example_list),
                                   user_examples=len(prior_example_list),
                                   project_leaderboard=project_leaderboard)
        else:
            logger.error('Not authorized for this project')
            return pievalIndex()


@bp.route("/annotate_example")
@bp.route("/annotate_example/<doh>")
@logged_in
def annotate_example(doh='no'):
    if checkAuthZ(session['cur_proj'], session['user_name']):
        if doh == 'yes':
            if 'prev_example' in session.keys():
                # give user the previous annotation again
                session['cur_example'] = session['prev_example']
                session['example_order'] = session['example_order'] + [session['cur_example']]
                try:
                    one_example = pv_dl.getProjectData(project_name=session['cur_proj'], example_id=session['cur_example'])
                    # remove existing annotation from database, before re-adding
                    pv_dl.deleteAnnot(session['cur_proj'], session['user_name'], session['cur_example'])
                except InvalidVaultTokenError:
                    return render_template('bad_vault_token.html')
                return render_template('annotation.html', one_example=one_example)
            else:
                logger.error('No Previous example to doh!')
                return pievalIndex()

        # get annot_index from example_order list in session.  If it doesn't exist send them back to the project back, where it should be inited
        example_order = session['example_order']
        if len(example_order) > 0:
            example_idx = example_order[0]
            session['cur_example'] = example_idx
            logger.debug(f"In annotate_example() session: {session}")
            try:
                one_example = pv_dl.getProjectData(project_name=session['cur_proj'], example_id=session['cur_example'])
            except InvalidVaultTokenError:
                return render_template('bad_vault_token.html')
            # return annotation template with a single example
            return render_template('annotation.html', one_example=one_example)
        else:
            logger.debug('Done Annotating')
            return render_template('done.html')
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


@logged_in
def get_multiclass_annotation(context_viewed='no'):
    logger.debug('Getting a multiclass example')
    if checkAuthZ(session['cur_proj'], session['user_name']):
        # get current example
        try:
            one_example = pv_dl.getProjectData(project_name=session['cur_proj'], example_id=session['cur_example'])
            logger.debug(f"In get_multiclass_annotation() one_example = {one_example}")
            # get project classes
            proj_classes = pv_dl.getProjectClasses(project_name=session['cur_proj'])
            logger.debug(f"In get_multiclass_annotation() proj_classes = {proj_classes}")
        except InvalidVaultTokenError:
            return render_template('bad_vault_token.html')
        return render_template('annotation_mc.html',
                               one_example=one_example,
                               proj_classes=proj_classes,
                               proj_class_data=proj_classes,
                               context_viewed=context_viewed)
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


@bp.route("/record_annotation", methods=['POST'])
@logged_in
def record_annotation():
    if checkAuthZ(session['cur_proj'], session['user_name']):
        # extract sess vars
        user_name = session['user_name']
        cur_proj = session['cur_proj']
        project_mode = session['project_mode']
        cur_example = session['cur_example']
        response = request.form['response']
        context_viewed = request.form['context_viewed']
        user_ip = request.remote_addr
        cur_time = datetime.now().replace(microsecond=0)

        if project_mode == 'multiclass' and response == 'disagree':
            # get class specification
            return get_multiclass_annotation(context_viewed=context_viewed)
        else:
            # transact annotation event to persistence layer
            try:
                # record annotation
                pv_dl.saveAnnot(cur_time,
                          cur_proj,
                          user_name,
                          user_ip,
                          cur_example,
                          response,
                          context_viewed)
            except InvalidVaultTokenError:
                return render_template('bad_vault_token.html')
            # update session variable by removing this object from their list
            temp_example_order = session['example_order']
            temp_example_order.remove(session['cur_example'])
            session['example_order'] = temp_example_order
            # save cur_example as previous example
            session['prev_example'] = session['cur_example']
            # remove cur_example from session
            session.pop('cur_example')
            logger.debug(f"After removing the example from example_order {session}")
            # return next annotation
            return annotate_example()
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


################################################################
# main
################################################################
if __name__ == '__main__':
    print("Somehow you called main in pieval.py")
