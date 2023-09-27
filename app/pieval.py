'''
index.py - main app module for pieval.  Will put user on home page
'''
##################
# Imports
##################
# Core
from functools import wraps
from datetime import datetime
from random import shuffle
import logging

# Flask
from flask import (
    Blueprint, url_for, render_template, 
    session, request, current_app, redirect,
    flash
)
from flask.helpers import send_from_directory

# Other 3rd party
import pandas as pd
import funcy

# siblings
try:
    from app.data_loader import get_data_loader
except ModuleNotFoundError:
    from data_loader import get_data_loader

# initializing global vars
# @TODO - see if we can remove globals - not high priority but nice to have
pv_dl = None
logger = None

bp = Blueprint('pieval', __name__, static_folder='static')
##########################################################################
# app init funcs
# variables/dataloader/logger
##########################################################################
def init_logging(logger_name):
    global logger
    logger = logging.getLogger(logger_name)


def init_pv_dl(mongo_connect_dict, db_name, user_collection_name, 
               project_collection_name, project_data_collection_name,
                logger=logger):
    global pv_dl
    pv_dl = get_data_loader(type, mongo_connect_dict, db_name, user_collection_name, 
                            project_collection_name, project_data_collection_name,
                            logger=logger)

################################################################
# Functions
################################################################
################
# login wrapper
################
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
    """
    Simple check to ensure the user is associated with the project
    """
    return True if len(pv_dl.get_projects(user_name=user_name, project_name=project_name)) > 0 else False

def list_diff(l1, l2):
    """
    Returns a difference between two lists, using set operations
    """
    return list(set(l1) - set(l2))

####################################################################
# web events
####################################################################
@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Second of two functions that help ensure the app is
    handling user identity correctly.  This varies between
    'dev' and 'prod' modes - please see docs for clarification
    """
    if request.method == 'POST':
        if current_app.config['AUTH_ENABLED'] == 'no':
            user_name = request.form['user_name']
            session['logged_in'] = True
            session['user_name'] = user_name
            return pievalIndex()
        else:
            return render_template('error_bs.html')
    if request.method == 'GET':
        if current_app.config['AUTH_ENABLED'] == 'no':
            return render_template('login.html')
        else:
            # check to see if some iteration of remote user is in the headers
            my_remote_user = request.headers.get(current_app.config['REMOTE_USER_HEADER_KEY'])
            if my_remote_user:
                session['logged_in'] = True
                session['user_name'] = my_remote_user
                return pievalIndex()
            else:
                return render_template('error_bs.html', error_msg="We were unable to find your user account in our systems")
            
@bp.route('/logout', methods=['GET'])
def logout():
    session['logged_in'] = False
    return pievalIndex()
            
@bp.route("/")
@logged_in
def pievalIndex():
    vars_to_pop = ['cur_proj', 'project_mode', 'example_order', 'cur_example', 'prev_example','data_type','annot_id_list']
    for var in vars_to_pop:
        if var in session.keys():
            session.pop(var)
    # log session
    logger.debug('Index session var is {}'.format(session))
    # get all projects for user
    try:
        logger.debug("User Name = {}".format(session['user_name']))
        pieval_projects = pv_dl.get_projects(user_name=session['user_name'])
        pieval_projects_df = pd.DataFrame(pieval_projects)
        logger.debug(f"User project df has shape: {pieval_projects_df.shape}")
        prj_data = pv_dl.get_project_data()
        prj_data_df = pd.DataFrame(prj_data)
        logger.debug(f"User project data df has shape: {prj_data_df.shape}")

        #########################
        # dealing with previous annotations
        #########################
        if 'annots' in prj_data_df.columns:
            prj_data_annots = prj_data_df.explode('annots').reset_index(drop=True)
            logger.info("There are {} total examples for this project".format(prj_data_annots.shape))
            
            prj_data_annots_final = prj_data_annots.join(prj_data_annots['annots'].apply(pd.Series))
            logger.info("There are {} total annotations for this project".format(prj_data_annots_final.shape))
            
            user_annots = prj_data_annots_final.loc[prj_data_annots_final['user_name'] == session['user_name']]

        else:
            user_annots = pd.DataFrame()
            print("No annots for this project")

        if user_annots.shape[0] > 0:
            user_proj_counts = (user_annots.groupby(['project_name'])
                            .size()
                            .to_frame()
                            .rename(columns={0:'num_annotated'})
                            .reset_index())
            
            proj_example_counts = (prj_data_df.groupby(['project_name'])
                                    .size()
                                    .to_frame()
                                    .rename(columns={0:'num_examples'})
                                    .reset_index())
            
            proj_status = pd.merge(proj_example_counts,
                                user_proj_counts,
                                on='project_name',
                                how='left')
            proj_status['pct_complete'] = round( (proj_status['num_annotated'] / proj_status['num_examples']) * 100)
            proj_status = proj_status.fillna(0)

            # join tables together
            pieval_projects_df = pieval_projects_df.merge(proj_status.filter(['project_name','pct_complete']), on='project_name', how='left')
            
        else:
            pieval_projects_df['pct_complete'] = 0

    except KeyError as e:
        logger.error("Caught missing person key error{}".format(e))
        return render_template('error_bs.html', error_msg="User not found in our records")
    except Exception as e:
        logger.error("Caught unidentified error{}".format(e))
        return render_template('error_bs.html')

    # Assuming no exceptions: compute project stats
    return render_template('index_bs.html', projects=pieval_projects_df.to_dict(orient='records'))
    

@bp.route("/project/<project_name>")
@logged_in
def project(project_name=None):
    if not project_name:
        return "You did not provide a project name, Try again" + url_for('pievalIndex')
    else:
        # if user has not passed login, this will throw a key error
        if checkAuthZ(project_name, session['user_name']):
            # get project metadata
        
            project_metadata = pv_dl.get_projects(project_name = project_name)[0]
            logger.debug(f'In project() function project metadata is: {project_metadata}')
            # get all records for project and use it to set an order variable in the users session
            prj_data = pv_dl.get_project_data(project_name)
            prj_data_df = pd.DataFrame(prj_data)
            proj_example_list = [x['example_id'] for x in prj_data]

            ########################
            # dealing with previous annotations
            ########################
            if 'annots' in prj_data_df.columns:
                prj_data_annots = prj_data_df.explode('annots').reset_index(drop=True)
                logger.info(f"project :: There are {prj_data_annots.shape} total examples for this project")
                
                prj_data_annots_final = prj_data_annots.join(prj_data_annots['annots'].apply(pd.Series))
                logger.info(f"project :: There are {prj_data_annots_final.shape} total annotations for this project")
                
                user_annots = prj_data_annots_final.loc[prj_data_annots_final['user_name'] == session['user_name']]

                prior_example_list = user_annots['example_id'].unique().tolist()
            else:
                user_annots = pd.DataFrame()
                prior_example_list = []
                logger.info("project :: No annots for this project")      

            if user_annots.shape[0] > 0:
                project_leaderboard = (prj_data_annots_final.groupby(['user_name']).size()
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

            # compute remaining annot list
            remaining_examples = list_diff(proj_example_list, prior_example_list)
            shuffle(remaining_examples)
            # user is entering this project - update their session to reflect that
            session['example_order'] = remaining_examples
            session['cur_proj'] = project_name
            session['project_mode'] = project_metadata['project_mode']
            session['data_type'] = project_metadata['data_type']

            logger.debug(f'In Project() session is {session}')
            # land them on a page that says something like you have selected to annotate for <project name>, 
            # you have already annotated <n> records.  There are N left
            return render_template('project_bs.html',
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
    # if user has not passed login, this will throw a key error
    if checkAuthZ(session['cur_proj'], session['user_name']):
        if doh == 'yes':
            if 'prev_example' in session.keys():
                # give user the previous annotation again
                session['cur_example'] = session['prev_example']
                session['example_order'] = session['example_order'] + [session['cur_example']]
            
                # this line recalls the example that we are 'doh!'ing' back to
                one_example = pv_dl.get_project_data(project_name=session['cur_proj'], example_id=session['cur_example'])[0]
                # Following code removes 'mistaken' annotation
                # Making the assumption that one user can ONLY annotate any specific example ONE time
                # under this assumption, we can delete any/all previous annoations for the current user safely
                if 'annots' in one_example:
                    lg_msg = f"annotate_example :: deleting previous annots for {session['user_name']} \
                                on example {session['cur_example']} in project {session['cur_proj']}"
                    logger.info(lg_msg)
                    new_annots = [x for x in one_example['annots'] if x['user_name'] != session['user_name']]
                    pv_dl.update_example(one_example, {'annots':new_annots})
                else:
                    logger.info("annotate_example :: no previous annotations to delete!")

                logger.debug(f"In annotate example: One Example = {one_example}")
                return render_template('annotation_bs.html', one_example=one_example, data_type=session['data_type'])
            else:
                logger.error('No Previous example to doh!')
                return pievalIndex()

        # get annot_index from example_order list in session.  If it doesn't exist send them back to the project back, where it should be inited
        example_order = session['example_order']
        if len(example_order) > 0:
            example_idx = example_order[0]
            session['cur_example'] = example_idx
            logger.debug(f"In annotate_example() session: {session}")
            one_example = pv_dl.get_project_data(project_name=session['cur_proj'], example_id=session['cur_example'])[0]
            logger.debug(f"In annotate example: One Example = {one_example}")
            # return annotation template with a single example
            return render_template('annotation_bs.html', one_example=one_example, data_type=session['data_type'])
        else:
            logger.debug('Done Annotating')
            return render_template('done_bs.html')
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


@logged_in
def get_multiclass_annotation(context_viewed='no'):
    logger.debug('Getting a multiclass example')
    # if user has not passed login, this will throw a key error
    if checkAuthZ(session['cur_proj'], session['user_name']):
        # get current example
        one_example = pv_dl.get_project_data(project_name=session['cur_proj'], example_id=session['cur_example'])[0]
        logger.debug(f"In get_multiclass_annotation() one_example = {one_example}")
        # get project classes
        project_metadata = pv_dl.get_projects(project_name=session['cur_proj'])[0]
        proj_classes = project_metadata['class_list']
        logger.debug(f"In get_multiclass_annotation() proj_classes = {proj_classes}")

        return render_template('annotation_bs_mc.html',
                               one_example=one_example,
                               proj_classes=proj_classes,
                               proj_class_data=proj_classes,
                               context_viewed=context_viewed,
                               data_type=session['data_type'])
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


@bp.route("/record_annotation", methods=['POST'])
@logged_in
def record_annotation():
    # if user has not passed login, this will throw a key error
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

        one_example = pv_dl.get_project_data(project_name=cur_proj, example_id=cur_example)[0]
        
        if project_mode == 'multiclass' and response == 'disagree':
            # get class specification
            return get_multiclass_annotation(context_viewed=context_viewed)
        else:
            # transact annotation event to persistence layer
            if 'annots' in one_example:
                print("There are prior annotations!")
                # in this case grab the current annot array
                annot_array = one_example['annots']
                try:
                    # hacky way to handle the case that someone "doh!'d" leaving annots as an empty list
                    max_annot_id = max([x['annot_id'] for x in annot_array])
                    new_annot_id = max_annot_id + 1
                except ValueError:
                    new_annot_id = 0
                one_annot = {
                    # 'project_name':cur_proj,
                    # 'example_id':cur_example,
                    'annot_id':new_annot_id,                        
                    'response_time':cur_time,
                    'user_name':user_name,
                    'user_ip':user_ip,
                    'response':response,
                    'context_viewed':context_viewed
                }
                annot_array.append(one_annot)
            else:
                print("There are no prior annotations")
                # in this case create a new annot array
                one_annot = {
                    # 'project_name':cur_proj,
                    # 'example_id':cur_example,
                    'annot_id':0,                        
                    'response_time':cur_time,
                    'user_name':user_name,
                    'user_ip':user_ip,
                    'response':response,
                    'context_viewed':context_viewed
                }    
                annot_array = [one_annot]

            extra_feature_dict = {'annots':annot_array}
            pv_dl.update_example(one_example, extra_feature_dict)
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

@bp.route("/get_image/<path:filename>")
@logged_in
def get_image(filename):
    # if user has not passed login, this will throw a key error
    if checkAuthZ(session['cur_proj'], session['user_name']):
        logger.info(f"GET_IMAGE CALL, root_dir = {pv_dl.image_dir}, filename = {filename}...")
        return send_from_directory(pv_dl.image_dir, filename, as_attachment=True)
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()

################################################################
# main
################################################################
if __name__ == '__main__':
    print("Somehow you called main in pieval.py")
