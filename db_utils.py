import sqlalchemy
import urllib
import logging
from piesafe import piesafe
piesafe.init_logging('example_log/setup')
logger = logging.getLogger(__name__)

def getOraDBEngine(inUsername, inPassword, inURL):
    '''
    Returns sqlalchemy database engine, specific to database type
    Oracle and MSSQL only current supported platforms
    '''
    ORAEngineConString = 'oracle+cx_oracle://{}:{}@{}'.format(inUsername,
                                                              inPassword,
                                                              inURL)
    ORAEngine = sqlalchemy.create_engine(ORAEngineConString, pool_size=100)

    # update NLS format for this session
    O_CON = ORAEngine.raw_connection()
    O_CURSOR = O_CON.cursor()
    O_CURSOR.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")

    return ORAEngine


def getMSSQLEngine(inDriver, inServer, inDb, inUsername, inPassword):
    # Setting up connection string using params:
    # Adding PORT seems to make no difference
    # 'PORT=' + myPort + ';' \
    conString = 'DRIVER=' + inDriver + ';' \
            'SERVER=' + inServer + ';' \
            'DATABASE=' + inDb + ';' \
            'UID=' + inUsername + ';' \
            'PWD=' + inPassword + ';' \
            'Trusted_Connection=No;'

    # URL encode the connection string
    conString = urllib.parse.quote_plus(conString)

    # Create the connection engine object
    MSSQLEngine = sqlalchemy.create_engine('mssql+pyodbc:///?odbc_connect=%s' % conString)
    return MSSQLEngine


def get_db_connection(config):
    if config.DATASOURCE_TYPE == 'db':
        logger.info("I can start building your database")
        logger.info("Obtaining connection")
        logger.info("Getting secrets from vault")
        #vaultClient = hvac.Client(url=config.VAULT_SERVER)
        vaultClient = piesafe.init_vault(None,
                                         vault_token=config.VAULT_TOKEN,
                                         vault_server=config.VAULT_SERVER
                                         # vault_role_id=config.VAULT_ROLE_ID,
                                         # vault_secret_id=config.VAULT_SECRET_ID
                                         )

        pieval_secret = vaultClient.read(config.DATASOURCE_LOCATION)
        logger.info("creating sqlalchemy engine")
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
        return pievalEngine
    else:
        logger.info("Current datasource type is defined as file...no database to build!")
        return None

def create_backup(pieval_engine, metadata):
    con = pieval_engine.raw_connection()
    curs = con.cursor()
    for table,_ in metadata.table_dict.items():
        try:
            drop_sql = """drop table pieval_backup.{}""".format(table)
            curs.execute(drop_sql)
        except Exception as e:
            logger.error("There was an error dropping the table!!")
            logger.error(e)
        try:
            ins_sql = """select * into pieval_backup.{} from pieval.{}""".format(table,table)
            curs.execute(ins_sql)
            curs.commit()
        except Exception as e:
            logger.error("There was a problem backing up the table!!")
            logger.error(e)
    curs.close()
    con.close()