# VaultDweller
## This is the simplest client for quick work with vaultwarden.

### Installation
```sh 
pip install vaultdweller
```
### Usage
You can get credits by name or by ID.

The names of repositories, collections, and records are not unique in vaultWarden, only the IDs are unique.
Therefore, if you are searching by name and the name of the record is duplicated, the first one found will be returned.
In such cases, you can add the name of the collection and/or storage
There are synchronous and asynchronous search methods.

I tested on python 3.11, I think it will work on earlier versions,
maybe it will be necessary to fix the typing.

``` python
vault = VaultWarden(
    url=url,
    email=email,
    password=master_password,
    client_id=client_id,
    client_secret=client_secret,
    device_id=device_id,
)
by_id_async = await vault.get_creds_by_id('ea27e9e3-f4c0-45ca-afd3-f7e722303a4b')

by_name_async = await vault.creds_by_name('item_name_1')
by_name_sync = vault.creds_by_name_sync('item_name_2', collection='Collection_1')

# change password
await vault.change_password(by_name_async.item_id, 'new_password')

#generate new totp
by_name_async.get_current_totp()

```
### Results
```
username='some_user'
password='some_password'
topt='111111'                   # one time password
uri='https://localhost/Login'
custom_fields=None              # if you added custom field in item 
```

#### Requirements:
* pyotp>=2.9.0
* httpx>=0.28.1
* pycryptodome>=3.22.0
* hkdf>=0.0.3
