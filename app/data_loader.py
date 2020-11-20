'''
Data Loader for pieval
'''
################################################################
# imports and config
################################################################
import os
import pandas as pd
import sqlalchemy
import urllib
import hvac
from piesafe import piesafe
from flask import current_app
import logging
import ucdripydbutils

################################################################
# classes
################################################################
## #################
# Custom Exception Classes
## #################
class InvalidVaultTokenError(Exception):
    """Raised when token doesn't authenticate to vault."""
    pass

## #################
# Data Loader Classes
## #################
class FileDataLoader(object):
    """
    Data loader class for pieval, assuming csv file based backend.
    This backend is best for devlopment and fast prototyping
    Consider DBDataLoader for production systems
    """

    def __init__(self, database_dir='database/', logger=None):
        self.database_dir = database_dir
        self.logger=logger

    def getUserData(self, return_as_data_frame=False):
        user_data = pd.read_csv(os.path.join(self.database_dir, 'user_data.csv'))
        return user_data if return_as_data_frame else user_data.to_dict(orient='records')

    def getProjects(self, user_name=None, return_as_dataframe=False):
        projects = pd.read_csv(os.path.join(self.database_dir, 'projects.csv'))
        if user_name:
            # get projects associated with this user
            user_proj_list = self.getProjectUsers()[user_name]
            projects = projects.loc[projects['project_name'].isin(user_proj_list)]
        return projects if return_as_dataframe else projects.to_dict(orient='records')

    def getProjectMetadata(self, project_name):
        projects = pd.read_csv(os.path.join(self.database_dir, 'projects.csv'))
        return projects.loc[projects['project_name'] == project_name].to_dict(orient = 'records')[0]

    def getProjectUsers(self):
        proj_users = pd.read_csv(os.path.join(self.database_dir, 'project_users.csv'))
        proj_users = (proj_users.groupby(['user_name'])
                                .agg({'project_name': lambda x: list(x)})
                                .reset_index())
        return dict(zip(proj_users['user_name'].to_list(), proj_users['project_name'].to_list()))

    def getProjectData(self, project_name=None, example_id=None, return_as_dataframe=False):
        data_df = pd.read_csv(os.path.join(self.database_dir, 'project_data.csv'))
        if pd.isnull(project_name) and pd.isnull(example_id):
            # return all data
            return data_df if return_as_dataframe else data_df.to_dict(orient='records')
        elif pd.notnull(project_name) and pd.isnull(example_id):
            # return all records for project
            try:
                return data_df.loc[(data_df['project_name'] == project_name)].to_dict(orient='records')
            except IndexError as e:
                if self.logger:
                    self.logger.error(e)
                return None
        elif pd.notnull(project_name) and pd.notnull(example_id):
            try:
                return data_df.loc[((data_df['project_name'] == project_name) & (data_df['example_id'] == example_id))].to_dict(orient='records')[0]
            except IndexError as e:
                if self.logger:
                    self.logger.error(e)
                return None

    def getProjectClasses(self, project_name=None):
        class_df = pd.read_csv(os.path.join(self.database_dir, 'project_classes.csv'))
        class_df = class_df.loc[class_df['project_name'] == project_name]
        return class_df['class'].to_list()

    def getPriorAnnotations(self, project_name=None, user_name=None, return_as_dataframe=False):
            data_df = pd.read_csv(os.path.join(self.database_dir, 'annotation_events.csv'))
            if pd.isnull(project_name) and pd.notnull(user_name):
                # get all prior annotations for this user, all projects
                data_df = data_df.loc[data_df['user_name'] == user_name]
            elif pd.notnull(project_name) and pd.notnull(user_name):
                # get prior annotations for this use for one project
                data_df = data_df.loc[((data_df['user_name'] == user_name) & (data_df['project_name'] == project_name))]
            elif pd.notnull(project_name) and pd.isnull(user_name):
                # get prior annotations for this project, all users
                data_df = data_df.loc[data_df['project_name'] == project_name]
            else:
                # return all data
                pass

            return data_df if return_as_dataframe else data_df.to_dict(orient='records')


    def saveAnnot(self, response_time, project_name, user_name, user_ip, example_id, response, context_viewed):
        new_row = pd.DataFrame(data={'response_time': response_time,
                                     'project_name': project_name,
                                     'user_name': user_name,
                                     'user_ip': user_ip,
                                     'example_id': example_id,
                                     'response': response,
                                     'context_viewed': context_viewed}, index=[0])

        prev_data = pd.read_csv(os.path.join(self.database_dir, 'annotation_events.csv'))
        new_data = prev_data.append(new_row, ignore_index=True, sort=False).reset_index(drop=True)
        new_data.to_csv(os.path.join(self.database_dir, 'annotation_events.csv'), index=False)

    def deleteAnnot(self, project_name, user_name, example_id):
        prev_data = pd.read_csv(os.path.join(self.database_dir, 'annotation_events.csv'))
        new_data = prev_data.loc[~((prev_data['user_name'] == user_name) & (prev_data['project_name'] == project_name) & (prev_data['example_id']==example_id))]
        new_data.to_csv(os.path.join(self.database_dir, 'annotation_events.csv'), index=False)


##############################################################################
#  Db Loader Class
##############################################################################
class DBDataLoader(object):
    def __init__(self, VAULT_ROLE_ID, VAULT_SECRET_ID, VAULT_SERVER, io_db_vault_path, schema_name, logger=None):
        #self.vault_token = VAULT_TOKEN
        self.vault_role_id = VAULT_ROLE_ID
        self.vault_secret_id = VAULT_SECRET_ID
        self.vault_server = VAULT_SERVER
        self.io_db_vault_path = io_db_vault_path
        self.schema_name = schema_name
        self.logger = logger
        self.io_db_engine = None

    def createEngine(self):
        '''
        Creates a database engine
        '''
        # try:
        #     vaultClient = hvac.Client(url=self.vault_server,
        #                               token=self.vault_token)
        #     pieval_secret = vaultClient.read(self.io_db_vault_path)
        # except hvac.exceptions.Forbidden as e:
        #     self.logger.error(e)
        #     raise InvalidVaultTokenError(f"Vault token is invalid!")
        vaultClient = piesafe.init_vault(None,
                                         vault_server=self.vault_server,
                                         vault_role_id=self.vault_role_id,
                                         vault_secret_id=self.vault_secret_id)
        pieval_secret = vaultClient.read(self.io_db_vault_path)

        self.logger.info("creating sqlalchemy engine")
        self.pieval_db_type = pieval_secret.get('data').get('dbtype')
        if self.pieval_db_type == 'oracle':
            if self.logger:
                self.logger.info("Creating Oracle Database Engine")
            pievalUser = pieval_secret.get('data').get('username')
            pievalPass = pieval_secret.get('data').get('password')
            pievalURL = pieval_secret.get('data').get('tns')
            pievalEngine = ucdripydbutils.getOraDBEngine(pievalUser, pievalPass, pievalURL)
        elif self.pieval_db_type == 'mssql':
            if self.logger:
                self.logger.info("Creating MSSQL Database Engine")
            myUsername = pieval_secret.get('data').get('username')
            myPassword = pieval_secret.get('data').get('password')
            myServer = pieval_secret.get('data').get('fqdn')
            myDriver = pieval_secret.get('data').get('driver')
            myDB = pieval_secret.get('data').get('db')
            pievalEngine = ucdripydbutils.getMSSQLEngine(myDriver, myServer, myDB,
                                          myUsername, myPassword)
        return pievalEngine

    def checkEngine(self):
        if self.io_db_engine:
            try:
                self.io_db_engine.connect()
                if self.logger:
                    self.logger.debug("DB Engine Check Successful")
            except sqlalchemy.exc.OperationalError as e:
                if self.logger:
                    self.logger.debug(f"DB Engine Check UN-Successful for error: {e}")
                    self.logger.debug("Will now attempt re-connect")
                self.io_db_engine.dispose()
                self.io_db_engine = self.createEngine()
        else:
            self.logger.info("Creating DB Engine for the first time!")
            self.io_db_engine = self.createEngine()

    def getUserData(self, return_as_data_frame=False):
        self.checkEngine()
        sql="select * from {}.user_details".format(self.schema_name)
        user_data = pd.read_sql(sql, self.io_db_engine)
        return user_data if return_as_data_frame else user_data.to_dict(orient='records')

    def getProjects(self, user_name=None, return_as_dataframe=False):
        self.checkEngine()
        sql = """select * from {}.projects""".format(self.schema_name)
        projects = pd.read_sql(sql, self.io_db_engine)
        if user_name:
            # get projects associated with this user
            user_proj_list = self.getProjectUsers()[user_name]
            projects = projects.loc[projects['project_name'].isin(user_proj_list)]
        return projects if return_as_dataframe else projects.to_dict(orient='records')

    def getProjectMetadata(self, project_name):
        self.checkEngine()
        sql = """select * from {}.projects""".format(self.schema_name)
        projects = pd.read_sql(sql, self.io_db_engine)
        return projects.loc[projects['project_name'] == project_name].to_dict(orient = 'records')[0]

    def getProjectUsers(self):
        self.checkEngine()
        sql = """select * from {}.project_users""".format(self.schema_name)
        proj_users = pd.read_sql(sql, self.io_db_engine)
        proj_users = (proj_users.groupby(['user_name'])
                                .agg({'project_name': lambda x: list(x)})
                                .reset_index())
        return dict(zip(proj_users['user_name'].to_list(), proj_users['project_name'].to_list()))

    def getProjectData(self, project_name=None, example_id=None, return_as_dataframe=False):
        self.checkEngine()
        sql = """select * from {}.project_data""".format(self.schema_name)
        data_df = pd.read_sql(sql, self.io_db_engine)
        if pd.isnull(project_name) and pd.isnull(example_id):
            # return all data
            return data_df if return_as_dataframe else data_df.to_dict(orient='records')
        elif pd.notnull(project_name) and pd.isnull(example_id):
            # return all records for project
            try:
                return data_df.loc[(data_df['project_name'] == project_name)].to_dict(orient='records')
            except IndexError as e:
                if self.logger:
                    self.logger.error(e)
                return None
        elif pd.notnull(project_name) and pd.notnull(example_id):
            try:
                return data_df.loc[((data_df['project_name'] == project_name) & (data_df['example_id'] == example_id))].to_dict(orient='records')[0]
            except IndexError as e:
                if self.logger:
                    self.logger.error(e)
                return None

    def getProjectClasses(self, project_name=None):
        self.checkEngine()
        sql = """select * from {}.project_classes""".format(self.schema_name)
        class_df = pd.read_sql(sql, self.io_db_engine)
        class_df = class_df.loc[class_df['project_name'] == project_name]
        return class_df['class'].to_list()

    def getPriorAnnotations(self, project_name=None, user_name=None, return_as_dataframe=False):
        self.checkEngine()
        sql = """select * from {}.annotation_events""".format(self.schema_name)
        data_df = pd.read_sql(sql, self.io_db_engine)
        if pd.isnull(project_name) and pd.notnull(user_name):
            # get all prior annotations for this user, all projects
            data_df = data_df.loc[data_df['user_name'] == user_name]
        elif pd.notnull(project_name) and pd.notnull(user_name):
            # get prior annotations for this user for one project
            data_df = data_df.loc[((data_df['user_name'] == user_name) & (data_df['project_name'] == project_name))]
        elif pd.notnull(project_name) and pd.isnull(user_name):
            # get prior annotations for this project, all users
            data_df = data_df.loc[data_df['project_name'] == project_name]
        else:
            # return all the data
            if self.logger:
                self.logger.info("Requesting ALL annotations!")
            pass

        # return the data
        return data_df if return_as_dataframe else data_df.to_dict(orient='records')

    def saveAnnot(self, response_time, project_name, user_name, user_ip, example_id, response, context_viewed):
        self.checkEngine()
        my_schema = self.schema_name

        if self.logger:
            self.logger.debug(f"Response Time: {response_time}")
            self.logger.debug(f"Response Time Type: {type(response_time)}")
            self.logger.debug(f"Project Name: {project_name}")
            self.logger.debug(f"Project Name Type: {type(project_name)}")
            self.logger.debug(f"User Name: {user_name}")
            self.logger.debug(f"User Name Type: {type(user_name)}")
            self.logger.debug(f"User IP: {user_ip}")
            self.logger.debug(f"User IP Type: {type(user_ip)}")
            self.logger.debug(f"Example ID: {example_id}")
            self.logger.debug(f"Example ID Type: {type(example_id)}")
            self.logger.debug(f"Response: {response}")
            self.logger.debug(f"Response Type: {type(response)}")
            self.logger.debug(f"Context Viewed: {context_viewed}")
            self.logger.debug(f"Context Viewed Type: {type(context_viewed)}")
        O_CON = self.io_db_engine.raw_connection()
        O_CURSOR = O_CON.cursor()

        if self.pieval_db_type == 'oracle':
            sql = f"insert into {my_schema}.annotation_events (response_time, project_name, user_name, user_ip, example_id, response, context_viewed) values(:rt, :pn, :un, :uip, :eid, :rsp, :cv)"
            if self.logger:
                self.logger.debug("Saving annotation to Oracle")
                self.logger.debug(f"Save Annot SQL is {sql}")
                self.logger.debug(f"Save Annot SQL is {type(sql)}")
            O_CURSOR.execute(sql,
                             rt=response_time,
                             pn=project_name,
                             un=user_name,
                             uip=user_ip,
                             eid=example_id,
                             rsp=response,
                             cv=context_viewed)
        elif self.pieval_db_type == 'mssql':
            sql = f"insert into {my_schema}.annotation_events (response_time, project_name, user_name, user_ip, example_id, response, context_viewed) values(?, ?, ?, ?, ?, ?, ?)"
            if self.logger:
                self.logger.debug("Saving annotation to MSSQL")
                self.logger.debug(f"Save Annot SQL is {sql}")
            O_CURSOR.execute(sql,
                             response_time,
                             project_name,
                             user_name,
                             user_ip,
                             example_id,
                             response,
                             context_viewed)
        else:
            if self.logger:
                self.logger.error("Unsupported DB type!")
        O_CON.commit()
        O_CURSOR.close()

    def deleteAnnot(self, project_name, user_name, example_id):
        self.checkEngine()
        my_schema = self.schema_name

        O_CON = self.io_db_engine.raw_connection()
        O_CURSOR = O_CON.cursor()
        if self.pieval_db_type == 'oracle':
            sql = f"delete from {my_schema}.annotation_events where user_name = :un and project_name = :pn and example_id = :eid"
            if self.logger:
                self.logger.debug("DELETING annotation from Oracle")
                self.logger.debug(f"Delete Annot SQL is {sql}")
            O_CURSOR.execute(sql,
                             un=user_name,
                             pn=project_name,
                             eid=example_id)

        elif self.pieval_db_type == 'mssql':
            sql = f"delete from {my_schema}.annotation_events where user_name = ? and project_name = ? and example_id = ?"
            if self.logger:
                self.logger.debug("DELETING annotation from MSSQL")
                self.logger.debug(f"Delete Annot SQL is {sql}")
            O_CURSOR.execute(sql,
                             user_name,
                             project_name,
                             example_id)
        else:
            if self.logger:
                self.logger.error("Unsupported DB type!")
        O_CON.commit()
        O_CURSOR.close()


#########################################################################
# functions
#########################################################################
def get_data_loader(type, path, v_role_id=None, v_sec_id=None, v_server=None, db_schema=None, logger=None):
    # construct data loader based on env file
    # consider using flask-sqlalchemy.  This is app scoped not sessio managed
    # >may< not scale.  Tested with 3 concurrent users and all things fine
    logger.info(f"Obtaining a PieVal Data Loader with type {type}") if logger else print("No logger")
    if type == 'file':
        pv_dl = FileDataLoader(path, logger)
    elif type == 'db':
        pv_dl = DBDataLoader(v_role_id,
                            v_sec_id,
                            v_server,
                            path,
                            db_schema,
                            logger)
    else:
        pv_dl = None

    return pv_dl