"""
Author: Bill Riedl
Date: 2023-08-24
Purpose: Establish skeleton mongo database for use by the pieval application.  Early
versions of this script will load the example data whether you like it or not.
"""

#########################################
# imports and config
#########################################
import numpy as np
import pandas as pd
from pymongo import UpdateOne, MongoClient

try:
    from mongo_common import print_collection_sizes, get_mongo_client
except ModuleNotFoundError:
    from src.mongo_common import print_collection_sizes, get_mongo_client


#########################################
# func defs
#########################################
def run(mongo_client):
    # Test client by reading out current database names
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
    

    # Step 1 - load up example data from csv files
    try:
        proj_classes_df = pd.read_csv('../example_database/project_classes.csv')
    except FileNotFoundError:
        proj_classes_df = pd.read_csv('example_database/project_classes.csv')

    try:
        proj_users = pd.read_csv('../example_database/project_users.csv')
    except FileNotFoundError:
        proj_users = pd.read_csv('example_database/project_users.csv')

    try:
        proj_df = pd.read_csv('../example_database/projects.csv')
    except FileNotFoundError:
        proj_df = pd.read_csv('example_database/projects.csv')

    # project data - the documents
    try:
        proj_data_df = pd.read_csv('../example_database/project_data.csv')
    except FileNotFoundError:
        proj_data_df = pd.read_csv('example_database/project_data.csv')
    # user information
    try:
        user_df = pd.read_csv('../example_database/user_details.csv')
    except:
        user_df = pd.read_csv('example_database/user_details.csv')

    #######################
    # project Data
    #######################
    print("Loading Projects")
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
    print(bulk_api_result_dict)

    #######################
    # project data
    #######################
    print("Loading Project Data")
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
    print(bulk_api_result_dict)


    ###########################
    # users
    ###########################
    print("Adding Users")
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
    print(bulk_api_result_dict)


#########################################
# main
#########################################
def main():
    print("Hi there!  I'm going to build out a mongo database for use with PieVal")

    # Pre -req stuff - Mongo Client
    local_connect_dict = {
        "host":"localhost",
        "port":27017,
        "user":'',
        "pass":'',
        "auth_source":''
    }
    mongo_client = get_mongo_client(local_connect_dict, tls_flag=False, tlsAllowInvalidCertificates=True)

    print("Calling Run!")
    run(mongo_client)
    


if __name__ == "__main__":
    main()