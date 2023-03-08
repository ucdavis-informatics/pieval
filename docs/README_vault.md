# Vault for PieVal
[Vault](https://www.vaultproject.io) is an excellent secrets as a service technology from Hashicorp.  You can read more about the UCD implementation of it [here](https://repos.ri.ucdavis.edu/docs/ucd-techdocs/site/vault/)

Here are some brief instructions about how to create a durable approle token for the pieval application.

## Create the approle and obtain its accessor values
Create the approle
```shell script
vault write auth/approle/role/pieval_role policies="pieval_policy" period="192h"
```

Get the role id
```shell script
vault read auth/approle/role/pieval_role/role-id
```

Get the Secret id
```shell script
vault write -force auth/approle/role/pieval_role/secret-id
```

## Using your approle
Inject the role id values into instance/config.py in the vault config section!

