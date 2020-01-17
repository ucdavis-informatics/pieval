'''
index.py - main app module for pieval.  Will put user on home page
'''
# Imports
from flask import url_for, render_template, session, request
import pandas as pd
from datetime import datetime
from random import shuffle
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
# siblings
from app.data_loader import FileDataLoader, DBDataLoader

# define the app
from app import app
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
if app.config['DATASOURCE_TYPE'] == 'file':
    pv_dl = FileDataLoader(app.config['DATASOURCE_LOCATION'], logger)
elif app.config['DATASOURCE_TYPE'] == 'db':
    pv_dl = DBDataLoader(app.config['VAULT_TOKEN'],
                         app.config['VAULT_SERVER'],
                         app.config['DATASOURCE_LOCATION'],
                         app.config['DB_SCHEMA'],
                         logger)

####################################################################
# web events
####################################################################
@app.route("/")
def pievalIndex():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        # user is returning to index, possibly after annotating
        # reset their state by conditionally clearing session vars
        vars_to_pop = ['cur_proj', 'project_mode', 'example_order', 'cur_example', 'prev_example']
        for var in vars_to_pop:
            if var in session.keys():
                session.pop(var)
        # log session
        logger.debug(f'Index session var is {session}')
        # get all projects for user
        pieval_projects = pv_dl.getProjects(user_name=session['user_name'], return_as_dataframe = True)
        data = pv_dl.getProjectData(return_as_dataframe=True)
        prev_annots_for_user = pv_dl.getPriorAnnotations(user_name=session['user_name'], return_as_dataframe=True)

        # compute project stats
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    user_name = request.form['user_name']
    session['logged_in'] = True
    session['user_name'] = user_name
    return pievalIndex()


@app.route('/logout')
def logout():
    if session.get('logged_in'):
        session.pop('logged_in')
    if session.get('example_order'):
        session.pop('example_order')
    if session.get('cur_example'):
        session.pop('cur_example')
    return pievalIndex()


@app.route("/project/<project_name>")
def project(project_name=None):
    if not project_name:
        return "You did not provide a project name, Try again" + url_for('pievalIndex')
    else:
        if checkAuthZ(project_name, session['user_name']):
            # get project metadata
            project_metadata = pv_dl.getProjectMetadata(project_name)
            logger.debug(f'In project() function project metadata is: {project_metadata}')
            # get all records for project and use it to set an order variable in the users session
            project_data = pv_dl.getProjectData(project_name=project_name)
            # logger.debug(f'In project() Project data for {project_name} is {project_data}')
            proj_example_list = [x['example_id'] for x in project_data]
            # check to see if they have annotated this project before.  If so, alter order object by removing already seen examples
            prev_proj_annots_for_user = pv_dl.getPriorAnnotations(project_name=project_name, user_name=session['user_name'])
            prior_example_list = [x['example_id'] for x in prev_proj_annots_for_user]

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
                                   user_examples=len(prior_example_list))
        else:
            logger.error('Not authorized for this project')
            return pievalIndex()


@app.route("/annotate_example")
@app.route("/annotate_example/<doh>")
def annotate_example(doh='no'):
    if checkAuthZ(session['cur_proj'], session['user_name']):
        if doh == 'yes':
            if 'prev_example' in session.keys():
                # give user the previous annotation again
                session['cur_example'] = session['prev_example']
                session['example_order'] = session['example_order'] + [session['cur_example']]
                one_example = pv_dl.getProjectData(project_name=session['cur_proj'], example_id=session['cur_example'])
                # remove existing annotation from database, before re-adding
                pv_dl.deleteAnnot(session['cur_proj'], session['user_name'], session['cur_example'])
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
            one_example = pv_dl.getProjectData(project_name=session['cur_proj'], example_id=session['cur_example'])
            # return annotation template with a single example
            return render_template('annotation.html', one_example=one_example)
        else:
            logger.debug('Done Annotating')
            return render_template('done.html')
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


# @app.route("/annotate_mc_example")
def get_multiclass_annotation():
    logger.debug('Getting a multiclass example')
    if checkAuthZ(session['cur_proj'], session['user_name']):
        # get current example
        one_example = pv_dl.getProjectData(project_name=session['cur_proj'], example_id=session['cur_example'])
        logger.debug(f"In get_multiclass_annotation() one_example = {one_example}")
        # get project classes
        proj_classes = pv_dl.getProjectClasses(project_name=session['cur_proj'])
        logger.debug(f"In get_multiclass_annotation() proj_classes = {proj_classes}")
        return render_template('annotation_mc.html',
                                one_example=one_example,
                                proj_classes=proj_classes,
                                proj_class_data = proj_classes)
    else:
        logger.error("Not authorized for this project")
        return pievalIndex()


@app.route("/record_annotation", methods=['POST'])
def record_annotation():
    if checkAuthZ(session['cur_proj'], session['user_name']):
        # extract sess vars
        user_name = session['user_name']
        cur_proj = session['cur_proj']
        project_mode = session['project_mode']
        cur_example = session['cur_example']
        response = request.form['response']
        user_ip = request.remote_addr
        cur_time = datetime.now().replace(microsecond=0)

        if project_mode == 'multiclass' and response == 'disagree':
            # get class specification
            return get_multiclass_annotation()
        else:
            # transact annotation event to persistence layer
            pv_dl.saveAnnot(cur_time,
                      cur_proj,
                      user_name,
                      user_ip,
                      cur_example,
                      response)
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
# Functions
################################################################
def checkAuthZ(project_name, user_name):
    user_proj_list = pv_dl.getProjectUsers()[user_name]
    return True if project_name in user_proj_list else False


def list_diff(l1, l2):
    return list(set(l1) - set(l2))


################################################################
# main
################################################################
if __name__ == '__main__':
    print("Somehow you called main in pieval.py")
