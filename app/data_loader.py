'''
Data Loader for pieval
'''
################################################################
# imports and config
################################################################
from pymongo import MongoClient

################################################################
# classes
################################################################
## #################
# Custom Exception Classes
## #################
class InvalidVaultTokenError(Exception):
    """Raised when token doesn't authenticate to vault."""

#########################################################################
## Mongo DB Data Loader
#########################################################################
class MongoDataLoader(object):
    """
    Data Access interface between pieval app and a mongo database
    """
    def __init__(self, mongo_connect_dict, db_name, user_collection_name, project_collection_name, 
                 project_data_collection_name, mongo_tls_flag=False, mongo_allow_invalid_certs=True,
                 image_dir = None):
        """
        initialize a data loader
        """
        self.mongo_client = get_mongo_client(mongo_connect_dict, 
                                             tls_flag=mongo_tls_flag,
                                             tlsAllowInvalidCertificates=mongo_allow_invalid_certs)
        self.pv_db = self.mongo_client[db_name]
        self.user_collection = self.pv_db[user_collection_name]
        self.project_collection = self.pv_db[project_collection_name]
        self.project_data_collection = self.pv_db[project_data_collection_name]
        # currently not in use but working to restore image functionality
        self.image_dir = image_dir

    def get_user_data(self):
        """
        obtains user data from mongo database
        """
        res_cursor = self.user_collection.find({})
        return list(res_cursor)
  
    def get_projects(self, user_name='', project_name=''):
        """
        obtains project list from mongo database
        Have this consume getProjectMetdata, Users, and Classes
        """
        find_clause = {}
        if project_name:
            find_clause['project_name'] = {"$eq":project_name}
        if user_name:
            find_clause['user_list'] = user_name

        res_cursor = self.project_collection.find(find_clause)
        return list(res_cursor)

    def get_project_data(self, project_name='', example_id=None, not_annotated_only=False):
        """
        obtains all data for a project - the substrate for annotation
        """
        find_clause = {}
        if project_name:
            find_clause['project_name'] = {"$eq":project_name}
        if example_id:
            find_clause['example_id'] = {"$eq":example_id}
        if not_annotated_only:
            find_clause["annots"] = {"$exists":False}
        res_cursor = self.project_data_collection.find(find_clause)
        return list(res_cursor)

    def update_example(self, example, extra_feature_dict):
        """
        appends extra feature dict on to example based on _id
        """
        _id = example['_id']
        self.project_data_collection.update_one({'_id':_id},{'$set':extra_feature_dict})

#########################################################################
# functions
#########################################################################
def get_data_loader(my_type, mongo_connect_dict, db_name, user_collection_name, project_collection_name, project_data_collection_name,logger=None,
                    mongo_tls_flag=False, mongo_allow_invalid_certs=True):
    logger.info("Obtaining a PieVal Data Loader with type {}".format(my_type))
    pv_dl = MongoDataLoader(mongo_connect_dict, db_name, user_collection_name, project_collection_name, project_data_collection_name,
                            mongo_tls_flag=mongo_tls_flag, mongo_allow_invalid_certs=mongo_allow_invalid_certs)
    return pv_dl


def get_mongo_client(mongo_connect_dict, tls_flag=True, tlsAllowInvalidCertificates=False):
    return MongoClient(host=mongo_connect_dict['host'],
                               port=int(mongo_connect_dict['port']),
                               username=mongo_connect_dict['user'],
                               password=mongo_connect_dict['pass'],
                               authSource=mongo_connect_dict['auth_source'],
                               tls=tls_flag,
                               tlsAllowInvalidCertificates=tlsAllowInvalidCertificates)