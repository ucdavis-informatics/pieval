'''
Data Loader for pieval
'''
################################################################
# imports and config
################################################################
import os
import pandas as pd
import sqlalchemy
from sqlalchemy.sql import text
import urllib
import hvac


#########################################################################
# functions
#########################################################################
def getOraDBEngine(inUsername, inPassword, inURL):
    '''
    Returns sqlalchemy database engine, specific to database type
    Oracle and MSSQL only current supported platforms
    '''
    ORAEngineConString = 'oracle+cx_oracle://{}:{}@{}'.format(inUsername,
                                                              inPassword,
                                                              inURL)
    ORAEngine = sqlalchemy.create_engine(ORAEngineConString, pool_size=100)

    # update NLS format for this session
    O_CON = ORAEngine.raw_connection()
    O_CURSOR = O_CON.cursor()
    O_CURSOR.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")

    return ORAEngine


def getMSSQLEngine(inDriver, inServer, inDb, inUsername, inPassword):
    # Setting up connection string using params:
    # Adding PORT seems to make no difference
    # 'PORT=' + myPort + ';' \
    conString = 'DRIVER=' + inDriver + ';' \
            'SERVER=' + inServer + ';' \
            'DATABASE=' + inDb + ';' \
            'UID=' + inUsername + ';' \
            'PWD=' + inPassword + ';' \
            'Trusted_Connection=No;'

    # URL encode the connection string
    conString = urllib.parse.quote_plus(conString)

    # Create the connection engine object
    MSSQLEngine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect=%s' % conString)
    return MSSQLEngine


################################################################
# classes
################################################################
class FileDataLoader(object):
    '''
    Data loader class for pieval, assuming csv file based backend.
    This backend is best for devlopment and fast prototyping
    Consider DBDataLoader for production systems
    '''

    def __init__(self, database_dir='database/', logger=None):
        self.database_dir = database_dir
        self.logger=logger

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
        if pd.isnull(project_name) and pd.isnull(user_name):
            # cant do anything
            if self.logger:
                self.logger.error("I need a project AND a username!")
                return {}
        elif pd.isnull(project_name) and pd.notnull(user_name):
            # get all prior annotations for this user, all projects
            data_df = pd.read_csv(os.path.join(self.database_dir, 'annotation_events.csv'))
            data_df = data_df.loc[data_df['user_name'] == user_name]
            return data_df if return_as_dataframe else data_df.to_dict(orient='records')
        elif pd.notnull(project_name) and pd.notnull(user_name):
            # get prior annotations for this use for one project
            data_df = pd.read_csv(os.path.join(self.database_dir, 'annotation_events.csv'))
            data_df = data_df.loc[((data_df['user_name'] == user_name) & (data_df['project_name'] == project_name))]
            return data_df if return_as_dataframe else data_df.to_dict(orient='records')
        else:
            pass

    def saveAnnot(self, response_time, project_name, user_name, user_ip, example_id, response):
        new_row = pd.DataFrame(data={'response_time': response_time,
                                     'project_name': project_name,
                                     'user_name': user_name,
                                     'user_ip': user_ip,
                                     'example_id': example_id,
                                     'response': response}, index=[0])

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
    def __init__(self, VAULT_TOKEN, VAULT_SERVER, io_db_vault_path, schema_name, logger=None):
        self.vault_token = VAULT_TOKEN
        self.vault_server = VAULT_SERVER
        self.io_db_vault_path = io_db_vault_path
        self.schema_name = schema_name
        self.logger = logger
        self.io_db_engine = None

    def createEngine(self):
        '''
        Creates a database engine
        '''
        vaultClient = hvac.Client(url=self.vault_server,
                                  token=self.vault_token)
        pieval_secret = vaultClient.read(self.io_db_vault_path)

        print("creating sqlalchemy engine")
        pievalDBType = pieval_secret.get('data').get('dbtype')
        if pievalDBType == 'oracle':
            if self.logger:
                self.logger.info("Creating Oracle Database Engine")
            pievalUser = pieval_secret.get('data').get('username')
            pievalPass = pieval_secret.get('data').get('password')
            pievalURL = pieval_secret.get('data').get('url')
            pievalEngine = getOraDBEngine(pievalUser, pievalPass, pievalURL)
        elif pievalDBType == 'mssql':
            if self.logger:
                self.logger.info("Creating MSSQL Database Engine")
            myUsername = pieval_secret.get('data').get('username')
            myPassword = pieval_secret.get('data').get('password')
            myServer = pieval_secret.get('data').get('server')
            myDriver = pieval_secret.get('data').get('driver')
            myDB = pieval_secret.get('data').get('db')
            pievalEngine = getMSSQLEngine(myDriver, myServer, myDB,
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
            self.io_db_engine = self.createEngine()

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
        if pd.isnull(project_name) and pd.isnull(user_name):
            # cant do anything
            if self.logger:
                self.logger.error("I need a project AND a username!")
                return {}
        else:
            # get data
            sql = """select * from {}.annotation_events""".format(self.schema_name)
            data_df = pd.read_sql(sql, self.io_db_engine)
            if pd.isnull(project_name) and pd.notnull(user_name):
                # get all prior annotations for this user, all projects
                data_df = data_df.loc[data_df['user_name'] == user_name]
                return data_df if return_as_dataframe else data_df.to_dict(orient='records')
            elif pd.notnull(project_name) and pd.notnull(user_name):
                # get prior annotations for this use for one project
                data_df = data_df.loc[((data_df['user_name'] == user_name) & (data_df['project_name'] == project_name))]
                return data_df if return_as_dataframe else data_df.to_dict(orient='records')

    def saveAnnot(self, response_time, project_name, user_name, user_ip, example_id, response):
        self.checkEngine()
        my_schema = self.schema_name
        sql = f"insert into {my_schema}.annotation_events (response_time, project_name, user_name, user_ip, example_id, response) values(:rt, :pn, :un, :uip, :eid, :rsp)"

        if self.logger:
            self.logger.debug(f"Save Annot SQL is {sql}")
            self.logger.debug(f"Save Annot SQL is {type(sql)}")
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
        O_CON = self.io_db_engine.raw_connection()
        O_CURSOR = O_CON.cursor()
        O_CURSOR.execute(sql,
                         rt=response_time,
                         pn=project_name,
                         un=user_name,
                         uip=user_ip,
                         eid=example_id,
                         rsp=response)
        O_CON.commit()
        O_CURSOR.close()

    def deleteAnnot(self, project_name, user_name, example_id):
        self.checkEngine()
        my_schema = self.schema_name
        sql = f"delete from {my_schema}.annotation_events where user_name = :un and project_name = :pn and example_id = :eid"
        O_CON = self.io_db_engine.raw_connection()
        O_CURSOR = O_CON.cursor()
        O_CURSOR.execute(sql,
                         un=user_name,
                         pn=project_name,
                         eid=example_id)
        O_CON.commit()
        O_CURSOR.close()
