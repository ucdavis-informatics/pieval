'''
Data Loader for pieval
'''
################################################################
# imports and config
################################################################
import os
import pandas as pd


################################################################
# classes
################################################################
class FileDataLoader(object):
    '''
    Data loader class for pieval, assuming csv file based backend.
    This backend is best for devlopment and fast prototyping
    Consider DBDataLoader for production systems
    '''

    def __init__(self, database_dir='database/'):
        self.database_dir = database_dir

    def getProjects(self, user_name=None, logger=None, return_as_dataframe=False):
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

    def getProjectData(self, project_name=None, example_id=None, logger=None, return_as_dataframe=False):
        data_df = pd.read_csv(os.path.join(self.database_dir, 'project_data.csv'))
        if pd.isnull(project_name) and pd.isnull(example_id):
            # return all data
            return data_df if return_as_dataframe else data_df.to_dict(orient='records')
        elif pd.notnull(project_name) and pd.isnull(example_id):
            # return all records for project
            try:
                return data_df.loc[(data_df['project_name'] == project_name)].to_dict(orient='records')
            except IndexError as e:
                if logger:
                    logger.error(e)
                return None
        elif pd.notnull(project_name) and pd.notnull(example_id):
            try:
                return data_df.loc[((data_df['project_name'] == project_name) & (data_df['example_id'] == example_id))].to_dict(orient='records')[0]
            except IndexError as e:
                if logger:
                    logger.error(e)
                return None

    def getProjectClasses(self, project_name=None):
        class_df = pd.read_csv(os.path.join(self.database_dir, 'project_classes.csv'))
        class_df = class_df.loc[class_df['project_name'] == project_name]
        return class_df['class'].to_list()

    def getPriorAnnotations(self, project_name=None, user_name=None, logger=None, return_as_dataframe=False):
        if pd.isnull(project_name) and pd.isnull(user_name):
            # cant do anything
            if logger:
                logger.error("I need a project AND a username!")
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
    def __init__(self, VAULT_TOKEN, VAULT_SERVER, io_db_vault_path):
        self.vault_token = VAULT_TOKEN
        self.vault_server = VAULT_SERVER
        self.io_db_vault_path = io_db_vault_path
        self.io_db_engine = self.getEngine()

    def getEngine(self):
        # hvac
        # ridbutils
        # etc...
        # return engine
        print('TBD')
