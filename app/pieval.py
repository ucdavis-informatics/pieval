'''
index.py - main app module for pieval.  Will put user on home page
'''
# Imports
from flask import (
    Blueprint, url_for, render_template, session, request
)
from flask.helpers import send_from_directory
import pandas as pd
from datetime import datetime
from random import shuffle
import logging
import funcy
# siblings
from app.data_loader import (
    InvalidVaultTokenError, get_data_loader
)

pv_dl = None
logger = None

bp = Blueprint('pieval', __name__, static_folder='static')
##########################################################################
# app init funcs
# variables/dataloader/logger
##########################################################################
def init_pv_dl(mongo_connect_dict, db_name, user_collection_name, 
               project_collection_name, project_data_collection_name,
                logger=None):
    global pv_dl
    pv_dl = get_data_loader(type, mongo_connect_dict, db_name, user_collection_name, 
                            project_collection_name, project_data_collection_name,
                            logger=logger)

def init_logging(logger_name):
    global logger
    logger = logging.getLogger(logger_name)

################################################################
# Functions
################################################################
def checkAuthZ(project_name, user_name):
    try:
        user_proj_list = pv_dl.get_projects(user_name=user_name)
    except InvalidVaultTokenError:
        return render_template('bad_vault_token_bs.html')
    return True if len(user_proj_list) > 0 else False

def list_diff(l1, l2):
    return list(set(l1) - set(l2))

####################################################################
# web events
####################################################################
@bp.route("/")
def pievalIndex():
    if not session.get('logged_in'):
        # if not logged in
        return render_template('login.html')
        # redirect(url_for('auth.login'))
    else:
        # user is logged in
        # user is returning to index, possibly after annotating
        # reset their state by conditionally clearing session vars
        vars_to_pop = ['cur_proj', 'project_mode', 'example_order', 'cur_example', 'prev_example','data_type','annot_id_list']
        for var in vars_to_pop:
            if var in session.keys():
                session.pop(var)
        # log session
        logger.debug(f'Index session var is {session}')
        # get all projects for user
        try:
            logger.debug(f"User Name = {session['user_name']}")
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
                logger.info(f"There are {prj_data_annots.shape} total examples for this project")
                
                prj_data_annots_final = prj_data_annots.join(prj_data_annots['annots'].apply(pd.Series))
                logger.info(f"There are {prj_data_annots_final.shape} total annotations for this project")
                
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

        except InvalidVaultTokenError as e:
            logger.error(f"Caught bad token error{e}")
            return render_template('bad_vault_token_bs.html')
        except KeyError as e:
            logger.error(f"Caught missing person key error{e}")
            return render_template('user_not_found_bs.html')
        except Exception as e:
            logger.error(f"Caught unidentified error{e}")
            return render_template('error_bs.html')

        # Assuming no exceptions: compute project stats
        return render_template('index_bs.html', projects=pieval_projects_df.to_dict(orient='records'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    user_name = request.form['user_name']
    session['logged_in'] = True
    session['user_name'] = user_name
    return pievalIndex()


@bp.route("/project/<project_name>")
# @logged_in
def project(project_name=None):
    if not project_name:
        return "You did not provide a project name, Try again" + url_for('pievalIndex')
    else:
        if checkAuthZ(project_name, session['user_name']):
            # get project metadata
            try:
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

            except InvalidVaultTokenError:
                return render_template('bad_vault_token_bs.html')

            # compute remaining annot list
            remaining_examples = list_diff(proj_example_list, prior_example_list)
            shuffle(remaining_examples)
            # user is entering this project - update their session to reflect that
            session['example_order'] = remaining_examples
            session['cur_proj'] = project_name
            session['project_mode'] = project_metadata['project_mode']
            session['data_type'] = project_metadata['data_type']

            logger.debug(f'In Project() session is {session}')
            # land them on a page that says something like you have selected to annotate for <project name>, you have already annotated <n> records.  There are N left
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
# @logged_in
def annotate_example(doh='no'):
    if checkAuthZ(session['cur_proj'], session['user_name']):
        if doh == 'yes':
            if 'prev_example' in session.keys():
                # give user the previous annotation again
                session['cur_example'] = session['prev_example']
                session['example_order'] = session['example_order'] + [session['cur_example']]
                try:
                    one_example = pv_dl.get_project_data(project_name=session['cur_proj'], example_id=session['cur_example'])[0]
                    logger.debug(f"In annotate example: One Example = {one_example}")
                except InvalidVaultTokenError:
                    return render_template('bad_vault_token_bs.html')
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
            try:
                one_example = pv_dl.get_project_data(project_name=session['cur_proj'], example_id=session['cur_example'])[0]
                logger.debug(f"In annotate example: One Example = {one_example}")
            except InvalidVaultTokenError:
                return render_template('bad_vault_token_bs.html')
            # return annotation template with a single example
            return render_template('annotation_bs.html', one_example=one_example, data_type=session['data_type'])
        else:
            logger.debug('Done Annotating')
            return render_template('done_bs.html')
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


# @logged_in
def get_multiclass_annotation(context_viewed='no'):
    logger.debug('Getting a multiclass example')
    if checkAuthZ(session['cur_proj'], session['user_name']):
        # get current example
        try:
            one_example = pv_dl.get_project_data(project_name=session['cur_proj'], example_id=session['cur_example'])[0]
            logger.debug(f"In get_multiclass_annotation() one_example = {one_example}")
            # get project classes
            project_metadata = pv_dl.get_projects(project_name=session['cur_proj'])[0]
            proj_classes = project_metadata['class_list']
            logger.debug(f"In get_multiclass_annotation() proj_classes = {proj_classes}")
        except InvalidVaultTokenError:
            return render_template('bad_vault_token_bs.html')
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
# @logged_in
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

        one_example = pv_dl.get_project_data(project_name=cur_proj, example_id=cur_example)[0]
        
        if project_mode == 'multiclass' and response == 'disagree':
            # get class specification
            return get_multiclass_annotation(context_viewed=context_viewed)
        else:
            # transact annotation event to persistence layer
            try:
                if 'annots' in one_example:
                    print("There are prior annotations!")
                    # in this case grab the current annot array
                    annot_array = one_example['annots']
                    max_annot_id = max([x['annot_id'] for x in annot_array])
                    one_annot = {
                        # 'project_name':cur_proj,
                        # 'example_id':cur_example,
                        'annot_id':max_annot_id+1,                        
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

            except InvalidVaultTokenError:
                return render_template('bad_vault_token_bs.html')
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
# @logged_in
def get_image(filename):
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
