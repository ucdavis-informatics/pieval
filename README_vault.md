## Creating a Vault approle for pieval
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