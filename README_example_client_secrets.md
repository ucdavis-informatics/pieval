**client_secrets.json**  
This is another secrets file, also in the instance/ folder that must be created for each deployment.  All values must be updated for your deployment.  It's structure is presented below:
```json
{
    "web": {
        "issuer": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3",
        "auth_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/auth",
        "client_id": "<Unique client id - defined in keycloak>",
        "client_secret": "<unique key value here>",
        "redirect_uris": [
            "<url where app is hosted>"
        ],
        "userinfo_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/userinfo",
        "token_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/token",
        "token_introspection_uri": "https://kc01.ri.ucdavis.edu/auth/realms/CDI3/protocol/openid-connect/token/introspect"
    }
}
```