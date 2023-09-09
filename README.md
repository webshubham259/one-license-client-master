# One License Client

- [One License Client](#one-license-client)
  - [Introduction](#introduction)
  - [How to use](#how-to-use)
    - [For Python](#for-python)
  - [Key Concepts](#key-concepts)
    - [Initialization](#initialization)
    - [Syncing](#syncing)
  - [Future scope](#future-scope)
  - [License](#license)

## Introduction

One License is solution for developers who want to distribute their offline solutions with an online licensing system. One Licensing Server is the online part of the solution that is responsible for creation, management and syncing of licenses. One License comprises of four modules:

| Description                                                          |
| -------------------------------------------------------------------- |
| The online server for storing and validating licenses                |
| A dashboard for interacting with the server                          |
| Script for integrating this licensing system into your own softwares |
| Intermediate client for preventing virtual machine frauds            |

## How to use

### For Python

1. Import `one_license_client`
2. At the start of your application initialize the client

```
l = OneLicenceClient({
    "server_url": "http://localhost:4000/api/v1",
    "product_id": "5edb10fecc150913cb7640f6",
    "version_id": "5edb1105cc150913cb7640f7",
    "license_id": "5edb1264cc150913cb7640f8",
})
```

3. At the end of every API call include `l.consume()`. This will either trigger an instant sync (if sync trigger is set to at every API call) or only increment the local API counter for a sync scheduled for later (if sync trigger is set to at interval).

Note:

- Get values of `server_url`, `product_id`, `version_id` and `license_id` from the online licensing sever
- View `demo.py` for sample usage.

## Key Concepts

### Initialization

When an object is created, it tries to activate the license based on the values passed in the constructor. If an error is received, the program crashes there itself. This error may be due to multiple reasons like:

- Invalid license values
- Unreachable API server
- Expired licenses
- Allowed activation count exceeded, etc

After the license is activated, the main program is allowed to run, and a sync script is started in a new thread.

### Syncing

The sync function keeps running throughout the program's lifetime in a separate thread. Its main function is to perform license syncing at specified interval. It also allows for retries before failing the program completely. These values are fetched from the online server. If the syncing fails, the whole program is programmed to crash.

## Future scope

- Add client scripts in more languages
- Enable client to send stats/report to the server

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
