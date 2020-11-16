# %%
# make sure the kc docker server is running!  See README for command
# %%
import json
import requests

# %%
# Obtain a token from KC in order to use the API to build realms/users
token_url = "http://localhost:8080/auth/realms/master/protocol/openid-connect/token"
token_header={"Content-Type":"application/x-www-form-urlencoded"}
token_data = {
    'grant_type':'password',
    'client_id':'admin-cli',
    'username':'admin',
    'password':'admin'
}

token_resp = requests.post(token_url, token_data, headers=token_header)
print(type(token_resp))
print(token_resp.status_code)
token_resp_dict = token_resp.json()
print(token_resp_dict)

access_token = token_resp_dict.get('access_token')
print('\n',f"My access token is: {access_token}")


# %%
# Creating a Realm over the API
#realm_url = "http://localhost:8080/auth/admin/realms"
realm_url = "http://localhost:8080/auth/admin/realms"
realm_header={"Authorization":"bearer "+ access_token,
              "Content-Type":"application/json"}
with open('simple_api_realm.json') as f:
    realm_data = json.load(f)

realm_body= {'rep':realm_data}

print(realm_data.keys())

# %% execute the realm creation
realm_resp = requests.post(realm_url, json=realm_data, headers=realm_header)
print(realm_resp.status_code)
# realm_resp_dict = realm_resp.json()
# print(realm_resp_dict)


# %%
# Reading a Realm over the API - requires that one be manually created first!!
get_realm_resp = requests.get(realm_url+'/myrealm', headers=realm_header)
print(get_realm_resp.status_code)
get_realm_resp_dict = get_realm_resp.json()
print(get_realm_resp_dict)


# %%
with open('myrealm.json','w') as out_f:
    json.dump(get_realm_resp_dict, out_f)
# %%
