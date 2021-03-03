# %%  Imports and config
from numpy.lib.financial import pv
import pandas as pd
import numpy as np
import scipy.stats
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
                         '',
                         logger)

# %%
def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h

# %%
projects = pv_dl.getProjects()
len(projects)
# %%
ae = pv_dl.getPriorAnnotations()
print(type(ae))
print(len(ae))
# convert to dataframe
ae_df = pd.DataFrame(ae)
ae_df = ae_df.loc[~ae_df['user_name'].isin(['awriedl','jmcawood','mrenquis','cyvhuynh'])]
print(ae_df['user_name'].value_counts())
print(ae_df['user_name'].value_counts().sum())

# %%
len(ae_df['project_name'].unique())
# %%
idle_time_remove_thresh_in_seconds = 600

annot_time_filter_cols = ['user_name','response_time']
annot_time_df = ae_df.filter(annot_time_filter_cols).copy()
annot_time_df = annot_time_df.sort_values(['user_name','response_time'])
# add shifted column response_time_next
annot_time_df['response_time_next'] = annot_time_df.groupby(['user_name'])['response_time'].shift(-1,
                                                                                                 axis=0)
annot_time_df['response_time_diff'] = annot_time_df['response_time_next'] - annot_time_df['response_time']
annot_time_df['response_time_seconds'] = annot_time_df['response_time_diff'].dt.total_seconds()

# NOTE: Since we are measuring inter-annotation intervals, we lose on record per annotator 
annot_time_df = annot_time_df.dropna()

# group to get time stats
annot_time_grp = (annot_time_df.loc[annot_time_df['response_time_seconds'] < idle_time_remove_thresh_in_seconds]
              .groupby(['user_name'])
              .agg(
                  response_time_mean=('response_time_seconds','mean'),
                  response_time_95_ci=('response_time_seconds',mean_confidence_interval)
              ))

print(annot_time_grp)
print(annot_time_grp.mean())
# %%
