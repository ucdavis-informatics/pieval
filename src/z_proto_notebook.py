'''
Notebook style script for testing various functionaity
Mostly the data_loader
'''

# %%  Imports and config
import pandas as pd
from data_loader import FileDataLoader, DBDataLoader
import os

# %% create data loader - file based
pv_dl = FileDataLoader('example_database/')

# %%
pv_dl.getProjectUsers()

proj_list = pv_dl.getProjects(user_name='awriedl')
proj_list

project_metadata = pv_dl.getProjectMetadata('cncr_hist')
project_metadata
type(project_metadata)

proj_data = pv_dl.getProjectData(project_name='kappa_lambda')
proj_data

proj_annot_list = [x['annot_id'] for x in proj_data]
proj_annot_list


one_example = pv_dl.getProjectData(project_name='kappa_lambda', example_id=0)
one_example

data_df = pd.DataFrame(proj_data)
data_df.loc[data_df['annot_id']==2]
data_df.loc[data_df['project_name']=='kappa_lambda']
data_df.loc[((data_df['project_name'] == 'kappa_lambda') & (data_df['annot_id'] == '2'))]
data_df.loc[((data_df['project_name'] == 'kappa_lambda') & (data_df['annot_id'] == '2'))].to_dict(orient='records')


# %% session prototyping
session={'user_name':'awriedl'}
session['cur_proj'] = 'kappa_lambda'
session

if 'cur_proj' in session.keys():
    session.pop('cur_proj')

session


# %%
project_name = 'project'
user_name = 'user'
annot_id = 'annot'
response = 'response'
new_row = pd.DataFrame(data={'project_name': project_name,  'user_name': user_name,  'annot_id': annot_id,  'response': response}, index=[0])

new_row


# %%
user_name = 'jp'
pieval_projects = pv_dl.getProjects(user_name = user_name, return_as_dataframe = True)
data = pv_dl.getProjectData(return_as_dataframe=True)
prev_annots_for_user = pv_dl.getPriorAnnotations(user_name=user_name, return_as_dataframe=True)

# %%
pieval_projects
data
prev_annots_for_user

# %%
proj_example_counts = (data.groupby(['project_name'])
                           .size()
                           .to_frame()
                           .rename(columns={0:'num_examples'})
                           .reset_index())

proj_example_counts

# %%
prev_annots_for_user
user_proj_counts = (prev_annots_for_user.groupby(['project_name'])
                           .size()
                           .to_frame()
                           .rename(columns={0:'num_annotated'})
                           .reset_index())
user_proj_counts

# %% join status frames together
proj_status = pd.merge(proj_example_counts,
                       user_proj_counts,
                       on='project_name',
                       how='left')
proj_status['pct_complete'] = round( (proj_status['num_annotated'] / proj_status['num_examples']) * 100)
proj_status = proj_status.fillna(0)
proj_status



# join in with projects
pieval_projects = pieval_projects.merge(proj_status.filter(['project_name','pct_complete']), on='project_name', how='left')
pieval_projects


# %%
pv_dl.getProjectClasses(project_name='cncr_hist')


# %%
test_list = [1,2,3,4]
test_list

test_list + [2]

test_list.remove(2)


# %%
schema_name = 'my_schema_name'
f"""select * from {my_schema_name}"""
