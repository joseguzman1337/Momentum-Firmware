# Issue #2079: ED25519 support for U2F

**Original Issue:** [https://github.com/flipperdevices/flipperzero-firmware/issues/2079](https://github.com/flipperdevices/flipperzero-firmware/issues/2079)
**Author:** @exussum12
**Created:** 2022-12-02T13:07:50Z
**Labels:** Feature Request, USB

## Description

### Description of the feature you're suggesting.

Using the flipper zero as my private key for ssh I would expect 

`ssh-keygen -t ed25519-sk -f ~/.ssh/flipper.pub`


to generate a key in the same way 


`ssh-keygen -t ecdsa-sk -f ~/.ssh/flipper.pub`


does. (the ecdsa works as expected and I can ssh using this as the key) 


Output is currently 
```
Generating public/private ed25519-sk key pair.
You may need to touch your authenticator to authorize key generation.
Key enrollment failed: invalid format
````

the -vvv logs too

```
debug1: sshsk_enroll: using random challenge
debug1: sk_probe: 1 device(s) detected
debug1: sk_probe: selecting sk by touch
debug1: ssh_sk_enroll: using device /dev/hidraw9
debug1: ssh_sk_enroll: fido_dev_make_cred: FIDO_ERR_INVALID_ARGUMENT
debug1: sshsk_enroll: provider "internal" failure -1
debug1: ssh-sk-helper: Enrollment failed: invalid format
debug1: main: reply len 8
debug3: ssh_msg_send: type 5
debug1: client_converse: helper returned error -4
debug3: reap_helper: pid=72051
Key enrollment failed: invalid format

```


### Anything else?

_No response_

---
*This issue was automatically imported from the upstream Flipper Zero firmware repository.*
