import json
import requests
import logging

GBL_TOKEN_URL = "http://localhost:8080/auth/realms/master/protocol/openid-connect/token"
GBL_REALM_URL = "http://localhost:8080/auth/admin/realms"

#####################################################
# functions
#####################################################
def get_bearer_token(username, password, url, logger):
    token_header={"Content-Type":"application/x-www-form-urlencoded"}
    token_data = {
        'grant_type':'password',
        'client_id':'admin-cli',
        'username':username,
        'password':password
    }

    token_resp = requests.post(url, token_data, headers=token_header)
    logger.info(f"--- Token Request Status: {requests.status_codes._codes[token_resp.status_code]} ---")
    token_resp_dict = token_resp.json()
    access_token = token_resp_dict.get('access_token')

    return access_token

def build_realm(username, password, r_url, tok_url, realm_json_path, logger):
    access_token = get_bearer_token(username, password, tok_url, logger)
    
    with open(realm_json_path) as f:
        realm_data = json.load(f)

    # construct header and body
    realm_header={"Authorization":"bearer "+ access_token,
                  "Content-Type":"application/json"}
    # realm_body= {'rep':realm_data}

    realm_resp = requests.post(r_url, json=realm_data, headers=realm_header)
    logger.info(f"--- Realm Request Status: {requests.status_codes._codes[realm_resp.status_code]} ---")


def build_client(username, password, r_url, tok_url, client_json_path, logger):
    access_token = get_bearer_token(username, password, tok_url, logger)

    # client get/post url is a specification of the realm url
    make_client_url = r_url+'/pieval_realm/clients'
    header= {"Authorization":"bearer "+ access_token,
                "Content-Type":"application/json"}

    with open(client_json_path) as f:
        client_data = json.load(f)

    client_create_resp = requests.post(make_client_url, json=client_data, headers=header)
    logger.info(f"--- Client Request Status: {requests.status_codes._codes[client_create_resp.status_code]} --- ")

def build_user(username, password, r_url, tok_url, user_json_path, logger):
    access_token = get_bearer_token(username, password, tok_url, logger)

    make_users_url = r_url+'/pieval_realm/users'
    header= {"Authorization":"bearer "+ access_token,
                "Content-Type":"application/json"}

    with open(user_json_path) as f:
        user_data = json.load(f)

    user_create_resp = requests.post(make_users_url, json=user_data, headers=header)
    logger.info(f"--- User Request Status: {requests.status_codes._codes[user_create_resp.status_code]} --- ")


###  ############
# Run
###  ############
def run(username, password, r_url, tok_url,
        realm_json_path,
        client_json_path,
        user_json_path,
        logger):
    """
        Runnable function that does the configuration
    """
    # Step 1 - create a realm
    logger.info(f"Creating realm from {realm_json_path}")
    build_realm(username, password, r_url, tok_url, realm_json_path, logger)

    # Step 2 - Create client
    logger.info(f"Creating Client")
    build_client(username, password, r_url, tok_url, client_json_path, logger)
    
    # Step 3 - Create users
    logger.info(f"Creating pieval/pieval user")
    build_user(username, password, r_url, tok_url, user_json_path, logger)
    

#####################################################
# Main
#####################################################
def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.info("Auto-configuring KeyCloak for you!")

    # hard code params or possible swith to parser
    username='admin'
    password='admin'
    # Urls
    token_url = GBL_TOKEN_URL
    realm_url = GBL_REALM_URL

    # realm json
    realm_json_path = "docker_kc/resources/pieval_realm.json"
    client_json_path = "docker_kc/resources/pieval_client.json"
    user_json_path = "docker_kc/resources/pieval_user.json"

    logger.info("Calling Run")
    run(username, password, realm_url, token_url,
        realm_json_path,
        client_json_path,
        user_json_path,
        logger)


if __name__ == '__main__':
    main()