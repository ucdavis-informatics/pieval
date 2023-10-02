"""
Author: Bill Riedl
Purpose: To delete a project from the pieval database
!RUN THIS ONLY IF YOU ARE SURE YOU WANT TO FULLY DELETE A PROJECT!
Please see docs/persistance.md for more information
"""

# imports and config
import argparse

# siblings
import app.mongo_common as mongo_common # some mongo helpers
import instance.config as config


parser = argparse.ArgumentParser()

parser.add_argument("--project_name", 
                    help="The name of the project you want to delete",
                    type=str,
                    required=True)


def main():
    args = parser.parse_args()
    project_name = args.project_name()
    print(f"Now deleting project data for {project_name}")

    mongo_client = mongo_common.get_mongo_client(config.MONGO_CONNECT_DICT)
    pv_db = mongo_client[config.DB_NAME]

    # delete project entry
    print("Deleting project entry")
    pv_db[config.PROJECT_COLLECTION_NAME].delete_one({'project_name':{'$eq':project_name}})

    # delete project data
    print("Deleting project data - you cannot recover from this!")
    pv_db[config.PROJECT_DATA_COLLECTION_NAME].delete_many({'project_name':{"$eq":project_name}})

    print("All Done - goodbye")

if __name__ == '__main__':
    main()