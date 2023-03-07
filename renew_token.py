import logging
import instance.config as config
from piesafe import piesafe
# get a handle to the logger
logger = logging.getLogger(__name__)


def renew_token():
    logger.info('Running scheduled token renewal...')
    piesafe.init_vault(None,
                       vault_server=config.VAULT_SERVER,
                       vault_role_id=config.VAULT_ROLE_ID,
                       vault_secret_id=config.VAULT_SECRET_ID)
    return


if __name__ == '__main__':
    renew_token()