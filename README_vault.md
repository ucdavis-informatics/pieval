# Vault for PieVal
[Vault](https://www.vaultproject.io) is an excellent secrets as a service technology from Hasicorp.  A full introduction to vault is outside the scope of these docs.  However, hashicorp has a great [Getting Started](https://learn.hashicorp.com/tutorials/vault/getting-started-install) guide.

For the purposes of this documentation, we will assume you have a running instance of vault and understand that a vault secret is a set of key:value pairs that can be accessed securely.  It is purely a way of distributing secrets from a central location rather and creating instances of secrets at the edge with each app.  Within PieVal, vault is used exclusively to serve up SQL database connection details like:
1. Database type - Oracle or MSSQL
1. Database connection parameters such as
    - URL
    - Driver
1. Database connection secrets such as
    - Username
    - Password

## Structure of a Database Secret in Vault
This can be anything.  Here is what we use.  It's a little different depending on the RDBMS type.  Out of the box we support Oracle and MSSQL.  

**Oracle Secret Structure**  
```json
{
  "dbtype": "oracle",  
  "password": "\<password\>",  
  "tns": "\<Name in tnsnames.ora\>",  
  "url": "\<OPTIONAL - Value of connection descriptor in tnsnames.ora\>",  
  "username": "\<username\>"  
}  
```
 
**Oracle Secret Example**  
```json
{  
  "dbtype": "oracle",  
  "password": "awesome_password",  
  "tns": "db_tns",  
  "url": "(DESCRIPTION =(ADDRESS = (PROTOCOL = TCP)(HOST = db_host.ucdavis.edu)(PORT = 1521))(CONNECT_DATA =(SERVER = DEDICATED)(SERVICE_NAME = db_tns)))",  
  "username": "awesome_user"  
}
```


**MSSQL secret structure**
```json
{  
  "db": "\<db_name\>",  
  "dbtype": "mssql",  
  "driver": "\<driver name\>",  
  "fqdn": "\<fully qualified domain name\>",  
  "password": "\<password\>",  
  "port": "\<port db service listens on\>",  
  "server": "\<short server name\>",  
  "username": "\<username\>"  
}  
```

**MSSQL secret example**  
```json
{  
  "db": "db_name",  
  "dbtype": "mssql",   
  "driver": "{ODBC Driver 17 for SQL Server}",  
  "fqdn": "db_host.ucdavis.edu",  
  "password": "awesome_password",  
  "port": "1433",  
  "server": "db_host",  
  "username": "awesome_user"  
}
```

## Accessing Vault Secrets
Accessing vault is token based.  There are two major types of tokens to be aware of:
1. Standard Tokens - these expire after a set period of time.  They are nice for development since they are easy to issue but, using them in production cna gor annoying since you must remember to update the token before expiration or secret access will be denied.
1. App Role Tokens - These also expire but only if a period of inactivity onger than the defined interval passes by.  These are good in situations for when you want access to remain as long as there is utilization.  However, if utilization stops, access will expire after a set period of time.  This a nice safety net knowing that an otherwise open portal to your system will close on it's own even if you forget about it.

## Creating a Vault approle token for pieval
The process to create an approle token for pieval is a little involved.  

### Step 1 - create a vault policy specific to the application
this policy should follow the paradigm of minimum access, meaning only give the set of abilities necessary to function.  For pieval, this means reading a very select few database secrets.  Here is an example Pieval Vault Policy.  You can use this after updating \<your database path\>
```text
path "<your database path>" {
  capabilities = ["read", "list"]
}

# Allow tokens to look up their own properties
path "auth/token/lookup-self" {
  capabilities = ["read"]
}

# Allow tokens to renew themselves
path "auth/token/renew-self" {
  capabilities = ["update"]
}

# Allow tokens to revoke themselves
path "auth/token/revoke-self" {
  capabilities = ["update"]
}

# Allow a token to look up its own capabilities on a path
path "sys/capabilities-self" {
  capabilities = ["update"]
}

# Allow a token to look up its resultant ACL from all policies. This is useful
# for UIs. It is an internal path because the format may change at any time
# based on how the internal ACL features and capabilities change.
path "sys/internal/ui/resultant-acl" {
  capabilities = ["read"]
}

# Allow a token to renew a lease via lease_id in the request body; old path for
# old clients, new path for newer
path "sys/renew" {
  capabilities = ["update"]
}

path "sys/leases/renew" {
  capabilities = ["update"]
}

# Allow looking up lease properties. This requires knowing the lease ID ahead
# of time and does not divulge any sensitive information.
path "sys/leases/lookup" {
  capabilities = ["update"]
}

# Allow a token to manage its own cubbyhole
path "cubbyhole/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Allow a token to wrap arbitrary values in a response-wrapping token
path "sys/wrapping/wrap" {
  capabilities = ["update"]
}

# Allow a token to look up the creation time and TTL of a given
# response-wrapping token
path "sys/wrapping/lookup" {
  capabilities = ["update"]
}

# Allow a token to unwrap a response-wrapping token. This is a convenience to
# avoid client token swapping since this is also part of the response wrapping
# policy.
path "sys/wrapping/unwrap" {
  capabilities = ["update"]
}

# Allow general purpose tools
path "sys/tools/hash" {
  capabilities = ["update"]
}

path "sys/tools/hash/*" {
  capabilities = ["update"]
}

path "sys/tools/random" {
  capabilities = ["update"]
}

path "sys/tools/random/*" {
  capabilities = ["update"]
}
```

### Step 2 - Create the approle and obtain its accessor values
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

### Step 3
Inject the role id values into instance/config.py in the vault config section!

## Running Vault
If you don't run vault but would like to, vault officially suports docker images.  So, if you have downloaded this app, run it in development mode using docker, you can pretty easily extend that model to include a docker image for vault and wire into it.