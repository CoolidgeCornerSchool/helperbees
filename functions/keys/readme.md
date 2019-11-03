# `functions/keys/`

This folder contains two JSON files.

* `admins.json` - Contains the white list of admins.
  All admins are authenticated by Google login, so they
  must be either a gmail.com account or a gsuite domain account.
  To allow more users to be admins, edit this white list
  before deploying to the back end.


* `refresh.json` - Contains the refresh token, used to allow
sending email. This repo contains a dummy version. You'll need create
a real one before deploying.

See [install/setup_credentials/readme.md](../../install/setup_credentials/readme.md)
for instructions how to create this file.
