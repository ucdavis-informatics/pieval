# %%  Imports and config
from numpy.lib.financial import pv
import pandas as pd
from app.data_loader import DBDataLoader
import os
import logging
from instance import config
# %%
##########################################################################
# app environ
# variables/dataloader/logger
##########################################################################
logger = logging.getLogger()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# %%
pv_dl = DBDataLoader(config.VAULT_ROLE_ID,
                         config.VAULT_SECRET_ID,
                         config.VAULT_SERVER,
                         config.DATASOURCE_LOCATION,
                         config.DB_SCHEMA,
                         logger)

#########################################################################
# Creating a more realistic example of the extra context button
# Set-up: Hypothesis.  All the data we need to evaluate sentiment can be
# found in the first sentence of the 
#########################################################################
# %%
project_name = 'movie_reviews_demo'
proj_meta = pd.DataFrame(pv_dl.getProjectMetadata(project_name), index=[0])
new_proj_meta = proj_meta.copy()
new_proj_meta['project_name'] = new_proj_meta['project_name'] + '_2'
new_proj_meta

# %%
# new_proj_meta.to_sql('projects',pv_dl.io_db_engine,
#     schema='pieval',
#     if_exists='append',
#     index=False)

# %%

cur_mr_df = pd.DataFrame(pv_dl.getProjectData(project_name=project_name))
mr2_df = cur_mr_df.copy()
mr2_df['data_ext'] = mr2_df['data']
mr2_df['data'] = mr2_df['data'].str.split('.').str[0]
mr2_df['project_name'] = project_name + '_2'
mr2_df.head()
# %%
mr2_df['data'].str.len()
# %%
mr2_df['data_ext'].str.len()

# %%
# mr2_df.to_sql('project_data',
#                 pv_dl.io_db_engine,
#                 schema='pieval',
#                 if_exists='append',
#                 index=False)

# %%
sql = 'select * from pieval.project_classes'
mv_classes_df = pd.read_sql(sql, pv_dl.io_db_engine)
new_classes_df = mv_classes_df.loc[mv_classes_df['project_name'] == project_name]
new_classes_df['project_name'] = project_name + '_2'
new_classes_df
# %%
# new_classes_df.to_sql('project_classes', pv_dl.io_db_engine,
#                     schema='pieval',
#                     if_exists='append',
#                     index=False)
# %%
sql = 'select * from pieval.project_users'
mv_users_df = pd.read_sql(sql, pv_dl.io_db_engine)
new_users_df = mv_users_df.loc[mv_users_df['project_name'] == project_name]
new_users_df['project_name'] = project_name + '_2'
new_users_df
# %%
# new_users_df.to_sql('project_users',
#                     pv_dl.io_db_engine,
#                     schema='pieval',
#                     if_exists='append',
#                     index=False)
# %%
