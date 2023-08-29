##################################################
# imports and config
##################################################
import click

# siblings
import instance.config as config
import example_database.table_metadata as metadata
from db_utils import get_db_connection, create_backup
import logging
from piesafe import piesafe
piesafe.init_logging('example_log/setup')
logger = logging.getLogger(__name__)


##################################################
# functions
##################################################
@click.command(name='delete_project')
@click.option("--project_name","-pn","project_name",
              required=True,
              help="Name of the project to delete")
def delete_project(project_name):

    print("Getting pieval database connection (based on parameters in instance/config)")
    pieval_engine = get_db_connection(config)

    print("First - creating a backup for you!!")
    create_backup(pieval_engine, metadata)

    print()
    print("=" * 100)
    print("-" * 10, "Project Delete Review", "-" * 10)
    print("=" * 100)
    print(f"I'm going to delete this {project_name} project for you!")
    proceed = input("Are you sure you want to proceed with the delete [y/n]:")
    if proceed == 'y':
        print("Now deleting your project")
        do_delete_project(pieval_engine, project_name)
    else:
        print("You chose to cancel...goodbye")


def do_delete_project(pieval_engine, project_name):
    con = pieval_engine.raw_connection()
    curs = con.cursor()
    for table, _ in metadata.table_dict.items():
        if 'user_details' != table:
            logger.info(f"Now deleting from {table}")
            del_sql = """delete from pieval.{} where project_name = ?""".format(table)
            curs.execute(del_sql, [project_name])
        else:
            logger.info(f"NOT deleting data from {table}")
    curs.commit()
    curs.close()
    con.close()


if __name__ =="__main__":
    delete_project()