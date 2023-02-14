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
import pandas as pd
import sqlalchemy
import instance.config as config
import example_database.table_metadata as metadata
from db_utils import get_db_connection, create_backup
import logging
from piesafe import piesafe
piesafe.init_logging('example_log/setup')
logger = logging.getLogger(__name__)

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

parser.add_argument('--build_or_update',
                    help='If yes, include data in the csv files.  If no, exclude data from referenced csv files',
                    choices=['build', 'update'],
                    required=True)


#########################################################################
# functions
#########################################################################
def buildPievalDatabase(pievalEngine, destination_schema, example_data_dir, keep_example_data):
    for table, table_dict in metadata.table_dict.items():
        logger.info(f"Building table {table}")
        cur_file_path = os.path.join(example_data_dir, table_dict['filename'])
        logger.info(f"Current filepath is {cur_file_path}")
        cur_table_df = pd.read_csv(cur_file_path)

        # check to see if user wants to keep example data
        if keep_example_data == 'no':
            logger.info("Clearing example data")
            cur_table_df = cur_table_df[0:0]

        logger.info("Creating Table!")
        # create table in database
        cur_table_df.to_sql(name=table,
                            con=pievalEngine,
                            schema=destination_schema,
                            index=False,
                            dtype=table_dict['metadata'],
                            if_exists='replace')


def updatePievalDatabase(pievalEngine, destination_schema, example_data_dir, keep_example_data):
    """
    Use this function to update your existing pieval database
    This includes:
     - adding new tables
     - adding new columns to existing tables (columns are NEVER deleted - to be clear)
    """
    # see what tables are in DB now
    inspection = sqlalchemy.inspect(pievalEngine)
    cur_db_tables = inspection.get_table_names(schema=destination_schema)
    logger.info(cur_db_tables)

    for table, table_dict in metadata.table_dict.items():
        logger.info(f"Updating table {table}")
        cur_file_path = os.path.join(example_data_dir, table_dict['filename'])
        logger.info(f"Current filepath is {cur_file_path}")
        cur_table_df = pd.read_csv(cur_file_path)

        # check to see if user wants to keep example data
        if keep_example_data == 'no':
            logger.info("Clearing example data")
            cur_table_df = cur_table_df[0:0]

        # check if table exists in DB
        if table in cur_db_tables:
            # if yes, read it into memory and check to see if column sets are the same
            logger.info("Table exists - checking to see if columns match")
            cur_table_db = pd.read_sql(f"select * from {destination_schema}.{table}", pievalEngine)
            diff = set(list(cur_table_df)) - set(list(cur_table_db))
            if len(diff) > 0:
                logger.info("Need to add columns to table")
                for col in diff:
                    cur_table_db[col] = None
                # write updated table to DB
                cur_table_db.to_sql(name=table,
                                    con=pievalEngine,
                                    schema=destination_schema,
                                    index=False,
                                    dtype=table_dict['metadata'],
                                    if_exists='replace')
            else:
                logger.info(f"{table} is up to date - no updates required!")

        else:
            # if no - create the table
            logger.info("Creating Table!")
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
    logger.info("Builiding the pieval database")
    logger.info("parsing args")
    args = parser.parse_args()
    keep_example_data = args.keep_example_data
    example_data_dir = args.example_data_dir
    build_or_update = args.build_or_update

    if config.DATASOURCE_TYPE == 'db':
        logger.info("I can start building your database")
        logger.info("Obtaining connection")
        logger.info(
            f"Getting pieval database connection (based on parameters in instance/config) to {config.DATASOURCE_LOCATION}")
        pieval_engine = get_db_connection(config)

        if build_or_update == 'build':
            logger.info("Calling buildPievalDatabase")
            buildPievalDatabase(pieval_engine, config.DB_SCHEMA, example_data_dir, keep_example_data)
        elif build_or_update == 'update':
            logger.info("Creating Database backup before updating!")
            create_backup(pieval_engine, metadata)
            logger.info("Calling updatePievalDatabase")
            updatePievalDatabase(pieval_engine, config.DB_SCHEMA, example_data_dir, keep_example_data)
    else:
        logger.info("Current datasource type is defined as file...no database to build!")

    logger.info("I'm done")


if __name__ == '__main__':
    main()
