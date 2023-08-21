from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import logging 

def do_del_current(mongo_connect_dict, mongo_db, mongo_collection, logger=None):
    # create mongo client
    mongo_client = get_mongo_client(mongo_connect_dict)

    my_mongo_db = mongo_client[mongo_db]
    my_mongo_col = my_mongo_db[mongo_collection]
    msg = f"Deleting {my_mongo_col.estimated_document_count()} Documents before loading new data"
    logger.info(msg) if logger else print(msg)

    # do the delete
    del_res = my_mongo_col.delete_many({})
    msg = f"Deleted {del_res.deleted_count} Documents from {mongo_db}.{my_mongo_col}"
    logger.info(msg) if logger else print(msg)

def log_bulk_write_results(mongo_host, mongo_port, mongo_user, mongo_pass, mongo_db, mongo_collection,
                           bulk_res_df,
                           mongo_log_collection=None,
                           logger=None):
    mongo_client = MongoClient(host=mongo_host,
                               port=mongo_port,
                               username=mongo_user,
                               password=mongo_pass,
                               authSource=mongo_db)
    my_mongo_db = mongo_client[mongo_db]
    my_mongo_col = my_mongo_db[mongo_collection]

    msg=f"Upserted: {bulk_res_df['upserted_len'].sum()}"
    logger.info(msg) if logger else print(msg)
    msg=f"NUpserted: {bulk_res_df['nUpserted'].sum()}"
    logger.info(msg) if logger else print(msg)
    msg=f"nMatched: {bulk_res_df['nMatched'].sum()}"
    logger.info(msg) if logger else print(msg)
    msg=f"nModified: {bulk_res_df['nModified'].sum()}"
    logger.info(msg) if logger else print(msg)
    msg=f"nRemoved: {bulk_res_df['nRemoved'].sum()}"
    logger.info(msg) if logger else print(msg)
    msg=f"Total document count: {my_mongo_col.estimated_document_count()}"
    logger.info(msg) if logger else print(msg)

    if mongo_log_collection:
        bulk_res_df['run_date'] = pd.to_datetime(datetime.now())
        msg=f"logging upload results to mongo in collection {mongo_log_collection}"
        logger.info(msg) if logger else print(msg)
        my_mongo_db[mongo_log_collection].insert_one(bulk_res_df.to_dict(orient='split'))

def get_mongo_client(mongo_connect_dict, tls_flag=True, tlsAllowInvalidCertificates=False):
    return MongoClient(host=mongo_connect_dict['host'],
                            port=int(mongo_connect_dict['port']),
                            username=mongo_connect_dict['user'],
                            password=mongo_connect_dict['pass'],
                            authSource=mongo_connect_dict['auth_source'],
                            tls=tls_flag,
                            tlsAllowInvalidCertificates=tlsAllowInvalidCertificates)


def print_collection_sizes(notes_db):
    for coll_name in notes_db.list_collection_names():
        if coll_name != 'system.views':
            if coll_name.startswith('v_'):
                print(f"VIEW      : {coll_name}                has {notes_db[coll_name].count_documents({})} documents")
            else:
                print(f"COLLECTION: {coll_name}                has {notes_db[coll_name].estimated_document_count()} documents")
        else:
            ...

def save_dicts_to_mongo(mongo_connect_dict, dest_db, col, dict_list):
    """
    Saves any list of dictionaries to Mongo
    Mostly used to save run steps to mongo.
    """
    mongo_client = get_mongo_client(mongo_connect_dict)
    my_dest_db = mongo_client[dest_db]
    my_dest_db[col].insert_many(dict_list)
    mongo_client.close()

def save_dict_to_mongo(mongo_connect_dict, dest_db, col, dict):
    """
    Saves an entire run to mongo.  This includes one or more run steps
    """
    mongo_client = get_mongo_client(mongo_connect_dict)
    my_dest_db = mongo_client[dest_db]
    my_dest_db[col].insert_one(dict)
    mongo_client.close()