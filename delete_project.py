##################################################
# imports and config
##################################################
import click

# siblings
import instance.config as config
import example_database.table_metadata as metadata
from db_utils import get_db_connection


##################################################
# functions
##################################################
@click.command(name='delete_project')
@click.option("--project_name","-pn","project_name",
              required=True,
              help="Name of the project to delete")
def delete_project(project_name):
    print(f"I'm going to delete this {project_name} project for you!")
    print("Getting pieval database connection (based on parameters in instance/config)")
    pieval_engine = get_db_connection(config)

    print("First - creating a backup for you!!")
    create_backup(pieval_engine)

    proceed = input("Are you sure you want to delete the {} project [y/n]:")
    if proceed == 'y':
        print("Now deleting your project")
        do_delete_project(pieval_engine, project_name)
    else:
        print("You chose to cancel...goodbye")


def do_delete_project(pieval_engine, project_name):
    con = pieval_engine.raw_connection()
    curs = con.cursor()
    for table, _ in metadata.table_dict.items():
        del_sql = """delete from pieval.{} where project_name = ?""".format(table)
        curs.execute(del_sql, [project_name])
    curs.commit()
    curs.close()
    con.close()

def create_backup(pieval_engine):
    con = pieval_engine.raw_connection()
    curs = con.cursor()
    for table,_ in metadata.table_dict.items():
        drop_sql = """drop table pieval_backup.{}""".format(table)
        ins_sql = """select * into pieval_backup.{} from pieval.{}""".format(table,table)
        curs.execute(drop_sql)
        curs.execute(ins_sql)
    curs.commit()
    curs.close()
    con.close()


if __name__ =="__main__":
    delete_project()