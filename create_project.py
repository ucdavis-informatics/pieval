"""
Author: Bill Riedl
Purpose: To create a project in the pieval database from pre-existing JSON
Please see docs/persistance.md for more information
"""

# imports and config
import argparse
import json

from pymongo import UpdateOne

# siblings
import app.mongo_common as mongo_common # some mongo helpers
import instance.config as config

#########################################
# fxn defs
#########################################
def run(mongo_client, db_name, user_collection_name, project_collection_name, project_data_collection_name,
         json_data_dir=None):
    # Test client by reading out current database names
    print(mongo_client.list_database_names())
    if db_name in mongo_client.list_database_names():
        print("Database already exists")
        pv_db = mongo_client[db_name]
    else:
        print('Creating pv_db database')
        pv_db = mongo_client[db_name]
        pv_db.create_collection(user_collection_name)
        pv_db.create_collection(project_collection_name)
        pv_db.create_collection(project_data_collection_name)

    # Step 1 - load up example data from JSON files
    with open(json_data_dir+'/users.json','r', encoding='utf8') as user_json_in:
        user_dict_list = json.load(user_json_in)

    with open(json_data_dir+'/projects.json','r', encoding='utf8') as proj_json_in:
        proj_dict_list = json.load(proj_json_in)

    with open(json_data_dir+'/project_data.json','r', encoding='utf8') as proj_data_json_in:
        proj_data_dict_list = json.load(proj_data_json_in)

    #######################
    # project Data
    #######################
    proj_upserts = [UpdateOne({"_id": str(x.get('_id'))},
                        {"$set": x},
                        upsert=True) for x in proj_dict_list]
    bulk_res = pv_db[project_collection_name].bulk_write(proj_upserts)
    bulk_api_result_dict = bulk_res.bulk_api_result
    print(bulk_api_result_dict)

    #######################
    # project data
    #######################
    proj_data_upserts = [UpdateOne({"_id": str(x.get('_id'))},
                        {"$set": x},
                        upsert=True) for x in proj_data_dict_list]
    bulk_res = pv_db[project_data_collection_name].bulk_write(proj_data_upserts)
    bulk_api_result_dict = bulk_res.bulk_api_result
    print(bulk_api_result_dict)

    ###########################
    # users
    ###########################
    if user_dict_list:
        user_upserts = [UpdateOne({"_id": str(x.get('_id'))},
                            {"$set": x},
                            upsert=True) for x in user_dict_list]
        bulk_res = pv_db[user_collection_name].bulk_write(user_upserts)
        bulk_api_result_dict = bulk_res.bulk_api_result
        print(bulk_api_result_dict)
    else:
        print("No new users to upload!")

###################################################
# main
###################################################
parser = argparse.ArgumentParser()

parser.add_argument("--project_data_root_dir", 
                    help="The path to the project data directory with 3 files: projects.json, project_data.json, users.json",
                    type=str,
                    required=True)

def main():
    args = parser.parse_args()
    project_data_root_dir = args.project_data_root_dir()
    print(f"Now creating a project based on data from {project_data_root_dir}")

    mongo_client = mongo_common.get_mongo_client(config.MONGO_CONNECT_DICT)
    
    run(mongo_client, config.DB_NAME, config.USER_COLLECTION_NAME, config.PROJECT_COLLECTION_NAME, config.PROJECT_DATA_COLLECTION_NAME,
        json_data_dir=project_data_root_dir)
    
    print("All Done - goodbye")

if __name__ == '__main__':
    main()