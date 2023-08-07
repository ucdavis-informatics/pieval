"""
Author: Bill Riedl
Date: 2023-08-07
Purpose:  A script to load a fresh mongo database with pieval example data (from <projec_root>/example_database/*.csv).  App was
previously run against a SQL backend so CSV formatted example data files are retained.  This scripts loads them, reformats them
into JSON and loads them into Mongo
"""

# imports and config
# imports and config
import pandas as pd
from pymongo import UpdateOne
import numpy as np

# siblings
from mongo_common import print_collection_sizes, get_mongo_client

def run(mongo_client):
    # print the current structures in place - pv_db and collection names are hardcoded, whatevs
    print(mongo_client.list_database_names())
    if 'pv_db' in mongo_client.list_database_names():
        print("Database already exists")
        pv_db = mongo_client['pv_db']
        print_collection_sizes(pv_db)
    else:
        print('Creating pv_db database')
        pv_db = mongo_client['pv_db']
        pv_db.create_collection('projects')
        pv_db.create_collection('users')

    print("Loading data from CSV files")
    proj_classes_df = pd.read_csv('../example_database/project_classes.csv')
    proj_users = pd.read_csv('../example_database/project_users.csv')
    proj_df = pd.read_csv('../example_database/projects.csv')

    # project data - the documents
    proj_data_df = pd.read_csv('../example_database/project_data.csv')
    # user information
    user_df = pd.read_csv('../example_database/user_details.csv')

    print("wrangling and loading project metadata")
    proj_users_grp = (proj_users.groupby('project_name')
                  .agg(
                      user_list=('user_name',lambda x:list(x))
                      )
                    .reset_index()
                )

    proj_classes_grp = (proj_classes_df.groupby('project_name')
                    .agg(
                        class_list=('class',lambda x:list(x))
                        )
                        .reset_index()
                    )

    proj_final_df = pd.merge(proj_df, proj_users_grp, how='left', on='project_name')
    proj_final_df = pd.merge(proj_final_df, proj_classes_grp, how='left', on='project_name')
    proj_final_df['_id'] = proj_final_df['project_name']

    # write project data to mongo
    proj_dict_list = proj_final_df.to_dict(orient='records')
    for one_obj in proj_dict_list:
        for k,v in one_obj.items():
            if isinstance(v, (pd._libs.tslibs.nattype.NaTType)):
                one_obj[k] = None
            if (isinstance(v, float) and np.isnan(v)):
                one_obj[k] = None
            if isinstance(v, np.ndarray):
                one_obj[k] = v.tolist()

    proj_upserts = [UpdateOne({"_id": str(x.get('project_name'))},
                        {"$set": x},
                        upsert=True) for x in proj_dict_list]
    
    bulk_res = pv_db['projects'].bulk_write(proj_upserts)
    bulk_api_result_dict = bulk_res.bulk_api_result
    print("Loading project metadata results:")
    print(bulk_api_result_dict)

    print("Now loading Project Data")
    proj_data_df["_id"] = proj_data_df['project_name'] + '_' + proj_data_df['example_id'].astype(str)
    # write project data to mongo
    proj_data_dict_list = proj_data_df.to_dict(orient='records')
    for one_obj in proj_data_dict_list:
        for k,v in one_obj.items():
            if isinstance(v, (pd._libs.tslibs.nattype.NaTType)):
                one_obj[k] = None
            if (isinstance(v, float) and np.isnan(v)):
                one_obj[k] = None
            if isinstance(v, np.ndarray):
                one_obj[k] = v.tolist()

    proj_data_upserts = [UpdateOne({"_id": str(x.get('_id'))},
                        {"$set": x},
                        upsert=True) for x in proj_data_dict_list]
    
    bulk_res = pv_db['project_data'].bulk_write(proj_data_upserts)
    bulk_api_result_dict = bulk_res.bulk_api_result
    print("Project data loading results:")
    print(bulk_api_result_dict)

    print("Now loading User Data")
    user_df["_id"] = user_df['user_name']

    # write project data to mongo
    user_dict_list = user_df.to_dict(orient='records')
    for one_obj in user_dict_list:
        for k,v in one_obj.items():
            if isinstance(v, (pd._libs.tslibs.nattype.NaTType)):
                one_obj[k] = None
            if (isinstance(v, float) and np.isnan(v)):
                one_obj[k] = None
            if isinstance(v, np.ndarray):
                one_obj[k] = v.tolist()

    user_upserts = [UpdateOne({"_id": str(x.get('_id'))},
                        {"$set": x},
                        upsert=True) for x in user_dict_list]
    bulk_res = pv_db['users'].bulk_write(user_upserts)
    bulk_api_result_dict = bulk_res.bulk_api_result
    print("User Data loading results:")
    print(bulk_api_result_dict)


def main():
    print("Hello - I'll load some fake data into Mongo For you!")
    
    # namb a mongo client
    mongo_client = get_mongo_client({},local=True)
    run(mongo_client)   
    

if __name__ == '__main__':
    main()
    