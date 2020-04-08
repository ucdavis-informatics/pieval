"""
CLI interface to mange pieval projects
"""
##################################################
# imports and config
##################################################
import click
import hvac
import pandas as pd
import sys

# siblings
import instance.config as config
import example_database.table_metadata as metadata
from db_utils import get_db_connection, create_backup


##################################################
# functions
##################################################
@click.command(name='create_project')
@click.option("--data_table","-dt","data_table",
              required=True,
              help="Name of the staged data table in the pieval_stage schema")
@click.option("--classes_table","-ct","classes_table",
              required=False,
              help="Name of the classes table in the pieval_stage schema")
@click.option("--proj_desc","-pd","proj_desc",
              required=True,
              help="Name of the staged data table in the pieval_stage schema")
@click.option("--proj_mode","-pm","proj_mode",
              required=True,
              type=click.Choice(['binary','multiclass']),
              default='binary',
              help="Project mode - binary or multiclass")
@click.option("--user","-u", "user_list",
              required=True,
              multiple=True,
              help="One or more users: example create_project.py -u user1 -u user2")
def create_project(data_table, classes_table, proj_desc, proj_mode, user_list):
    #########################
    # set up
    #########################
    print(f"Getting pieval database connection (based on parameters in instance/config) to {config.DATASOURCE_LOCATION}")
    pieval_engine = get_db_connection(config)
    print("Creating Backup in pieval_backup schema in case things go sideways")
    create_backup(pieval_engine, metadata)

    print("Loading staged data into memory")
    stage_data = get_project_staging_data(pieval_engine, data_table)
    project_name = stage_data['project_name'].unique()[0]
    print("-"*10,project_name,"-"*10)

    if proj_mode=='multiclass':
        classes = get_class_data(pieval_engine,classes_table)

    ##########################
    # Check 1 - does project data already exist for this project
    # if so, quit!
    ##########################
    print("Checking if data already exists")
    project_data_exists = check_project_data_exists(pieval_engine, project_name)
    if project_data_exists:
        print("There project already exists, remove it before continuing!!...quitting")
        sys.exit()

    ##########################
    # Provide summary and ask for permission to proceed
    ##########################
    print()
    print("="*100)
    print("-"*10,"Project Create Review","-"*10)
    print("=" * 100)
    print(f"Project name will be:     {project_name}")
    print(f"Project description:      {proj_desc}")
    print(f"Project Mode is:          {proj_mode}")
    print(f"User list:                {user_list}")
    print(f"Data will be loaded from: {data_table}")
    print(f"Project data record size: {stage_data.shape[0]}")
    print(f"Data will be loaded to {config.DATASOURCE_LOCATION}")
    print()
    proceed = input(f"Are you sure you want to proceed [y/n]")

    if proceed == 'y':
        print("Loading your project")
        # def insert project data
        insert_project_data(pieval_engine,stage_data)
        # def insert project users
        insert_project_users(pieval_engine, user_list, project_name)
        # def insert project
        insert_project(pieval_engine,project_name,proj_desc,proj_mode)
        if proj_mode == 'multiclass':
            print("Writting classed to db")
            insert_classes(pieval_engine, classes)
    else:
        print("You decided to halt insert...quitting")
        sys.exit()


def insert_project_data(pieval_engine, df, schema='pieval', data_table='project_data'):
    df.to_sql(data_table,
              pieval_engine,
              schema=schema,
              if_exists='append',
              index=False)

def insert_classes(pieval_engine, df, schema='pieval', data_table='project_classes'):
    df.to_sql(data_table,
              pieval_engine,
              schema=schema,
              if_exists='append',
              index=False)

def insert_project_users(pieval_engine, user_list, project_name):
    sql = "insert into pieval.project_users (project_name,user_name) values (?,?)"
    con = pieval_engine.raw_connection()
    curs = con.cursor()
    for user in user_list:
        curs.execute(sql, [project_name, user])
    curs.commit()
    curs.close()
    con.close()

def insert_project(pieval_engine, project_name, project_desc, project_mode='binary'):
    sql="insert into pieval.projects (project_name,project_description,project_mode) values (?,?,?)"
    con = pieval_engine.raw_connection()
    curs = con.cursor()
    curs.execute(sql, [project_name, project_desc, project_mode])
    curs.commit()
    curs.close()
    con.close()

def check_project_data_exists(pieval_engine, project_name):
    check = False
    sql_strings_dict = {'projects':"select count(*) from pieval.projects where project_name = ?",
                   'annotation_events':"select count(*) from pieval.annotation_events where project_name = ?",
                   'project_data':"select count(*) from pieval.project_data where project_name = ?",
                   'project_users':"select count(*) from pieval.project_users where project_name = ?",
                   'project_classes':"select count(*) from pieval.project_classes where project_name = ?"}
    for k,v in sql_strings_dict.items():
        count = pd.read_sql(v,
                    pieval_engine,
                    params=[project_name]).iloc[0].values[0]
        if count > 0:
            check=True
            print(f"There is data under this proeject name in {k}")

    return check

def get_class_data(pieval_engine, classes_table):
    sql = "select * from pieval_stage.{}".format(classes_table)
    classes = pd.read_sql(sql, pieval_engine)

    print("Ensuring columns are correct")
    # assert the expected columns are in place
    for k, v in metadata.project_classes_metadata.items():
        assert k in classes.columns

    assert len(classes.columns) == len(metadata.project_classes_metadata)

    assert classes['class'].is_unique

    return classes


def get_project_staging_data(pieval_engine, data_table, key_col="example_id"):
    """
    Obtains staging data and ensures its in a good format
    """
    sql = "select * from pieval_stage.{}".format(data_table)
    stage_data = pd.read_sql(sql, pieval_engine)

    print("Ensuring columns are correct")
    # assert the expected columns are in place
    for k,v in metadata.project_data_metadata.items():
        assert k in stage_data.columns

    # make sure there are no 'extra' columns
    assert len(stage_data.columns) == len(metadata.project_data_metadata)

    print(f"Ensuring {key_col} contains unique values")
    # make sure key_col is unique
    assert stage_data[key_col].is_unique

    return stage_data

##################################################
# main
##################################################
if __name__=='__main__':
    create_project()