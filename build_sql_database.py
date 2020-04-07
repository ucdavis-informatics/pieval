'''
A script to build out the pieval database schema
pre-reqs:
working system level odbc connection
vault server/hvac based access for secrets from an app key
access to ucd-ri-dbutils
example csv files and a table_metadata.py file.  Examples packaged with repo in example_database/

dependencies:
sqlalchemy
rdbms specific python package
[cx_oracle, pyodbc, etc...]
'''
#########################################################################
# imports
#########################################################################
import argparse
import os
import hvac
import pandas as pd

import instance.config as config
import example_database.table_metadata as metadata

from db_utils import getMSSQLEngine, getOraDBEngine

#########################################################################
# globals
#########################################################################
# Evaluate for script arguments
parser = argparse.ArgumentParser(description='Pieval DB builder')
parser.add_argument('--example_data_dir',
                    help="The directory where the pieval example data csv files are saved",
                    default="example_database/")
parser.add_argument('--keep_example_data',
                    help='If yes, include data in the csv files.  If no, exclude data from referenced csv files',
                    choices=['yes', 'no'],
                    default='yes')


#########################################################################
# functions
#########################################################################
def buildPievalDatabase(pievalEngine, destination_schema, example_data_dir, keep_example_data):
    for table, table_dict in metadata.table_dict.items():
        print(f"Building table {table}")
        cur_file_path = os.path.join(example_data_dir, table_dict['filename'])
        print(f"Current filepath is {cur_file_path}")
        cur_table_df = pd.read_csv(cur_file_path)

        # check to see if user wants to keep example data
        if keep_example_data == 'no':
            print("Clearing example data")
            cur_table_df = cur_table_df[0:0]

        print("Creating Table!")
        # create table in database
        cur_table_df.to_sql(name=table,
                            con=pievalEngine,
                            schema=destination_schema,
                            index=False,
                            dtype=table_dict['metadata'],
                            if_exists='replace')


#########################################################################
# main
#########################################################################
def main():
    print("Builiding the pieval database")
    print("parsing args")
    args = parser.parse_args()
    keep_example_data = args.keep_example_data
    example_data_dir = args.example_data_dir
    if config.DATASOURCE_TYPE == 'db':
        print("I can start building your database")
        print("Obtaining connection")
        print("Getting secreats from vault")
        vaultClient = hvac.Client(url=config.VAULT_SERVER,
                                  token=config.VAULT_TOKEN)
        pieval_secret = vaultClient.read(config.DATASOURCE_LOCATION)

        print("creating sqlalchemy engine")
        pievalDBType = pieval_secret.get('data').get('dbtype')
        if pievalDBType == 'oracle':
            pievalUser = pieval_secret.get('data').get('username')
            pievalPass = pieval_secret.get('data').get('password')
            pievalURL = pieval_secret.get('data').get('url')
            pievalEngine = getOraDBEngine(pievalUser, pievalPass, pievalURL)
        elif pievalDBType == 'mssql':
            myUsername = pieval_secret.get('data').get('username')
            myPassword = pieval_secret.get('data').get('password')
            myServer = pieval_secret.get('data').get('server')
            myDriver = pieval_secret.get('data').get('driver')
            myDB = pieval_secret.get('data').get('db')
            pievalEngine = getMSSQLEngine(myDriver, myServer, myDB,
                                          myUsername, myPassword)

        print("Calling buildPievalDatabase")
        buildPievalDatabase(pievalEngine, config.DB_SCHEMA, example_data_dir, keep_example_data)
    else:
        print("Current datasource type is defined as file...no database to build!")

    print("I'm done")


if __name__ == '__main__':
    main()
