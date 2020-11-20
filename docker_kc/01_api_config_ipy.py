# %%
"""
    NOTE: Make sure KC docker container is running!  See README for deets
"""
import json
from run import create_app
import requests
import logging
from config_keycloak import (get_bearer_token,
                            GBL_TOKEN_URL,
                            GBL_REALM_URL)

logger = logging.getLogger(__name__)
logger.info("Logger configured")

username='admin'
password='admin'
tok_url = GBL_TOKEN_URL


# %% Creating a client over the API
# step 1 - manually create client in web console - SEE README, then download what that looks like.  Use this representation to create future clients
access_token = get_bearer_token(username, password, tok_url, logger)
print(f"Access token is {access_token}")

get_client_url = GBL_REALM_URL+'/apirealm/clients'
header= {"Authorization":"bearer "+ access_token,
              "Content-Type":"application/json"}

clients_resp = requests.get(get_client_url, headers=header)
print(clients_resp.status_code)
clients_dict_list = clients_resp.json()
print(len(clients_dict_list))

clients_dict_list

# %% Step 2 - using the client json just downloaded, use it to create a new client!
access_token = get_bearer_token(username, password, tok_url, logger)
print(f"Access token is {access_token}")

make_client_url = GBL_REALM_URL+'/apirealm/clients'
header= {"Authorization":"bearer "+ access_token,
              "Content-Type":"application/json"}

with open('resources/pieval_client_no_id.json') as f:
    client_data = json.load(f)

client_create_resp = requests.post(make_client_url, json=client_data, headers=header)
print(client_create_resp.status_code)



# %% Creating a user over the api
# Step 1 - create a user in the GUI, then download json and use for future users
access_token = get_bearer_token(username, password, tok_url, logger)
print(f"Access token is {access_token}")

get_users_url = GBL_REALM_URL+'/apirealm/users'
header= {"Authorization":"bearer "+ access_token,
              "Content-Type":"application/json"}

users_resp = requests.get(get_users_url, headers=header)
print(requests.status_codes._codes[users_resp.status_code][0])
users_dict_list = users_resp.json()
print(len(users_dict_list))

users_dict_list

# %% Using the data retreived above, now create the user!
access_token = get_bearer_token(username, password, tok_url, logger)
print(f"Access token is {access_token}")

make_users_url = GBL_REALM_URL+'/apirealm/users'
header= {"Authorization":"bearer "+ access_token,
              "Content-Type":"application/json"}

with open('resources/pieval_user.json') as f:
    user_data = json.load(f)

user_create_resp = requests.post(make_users_url, json=user_data, headers=header)
print(user_create_resp.status_code)

# %%
requests.status_codes._codes[201]