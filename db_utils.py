import sqlalchemy
import urllib
import hvac

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
        print("I can start building your database")
        print("Obtaining connection")
        print("Getting secrets from vault")
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
        return pievalEngine
    else:
        print("Current datasource type is defined as file...no database to build!")
        return None