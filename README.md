## Requeriments

Create virtualenv

```sh
pip install tasklib
pip install py-trello
```

Go to: https://trello.com/app-key to get API Key and API Secret.

Run exports to config (configure with your data):

```sh
export TRELLO_API_KEY="your_api_key"
export TRELLO_API_SECRET="your_api_secret"
export TRELLO_NAME="trellowarrior"
export TRELLO_EXPIRATION="30days"
```

Run from venv to get token and token secret:

```sh
python lib/python2.7/site-packages/trello/util.py
```

This return some like this:

```
Request Token:
    - oauth_token        = 1c5ad394834dde42a7655437ab3e0060
    - oauth_token_secret = dffc3a62622ef450028f685406bceacc

Go to the following link in your browser:
https://trello.com/1/OAuthAuthorizeToken?oauth_token=1c5ad334134dde46a8659437ab3e0069&scope=read,write&expiration=30days&name=trellowarrior
Have you authorized me? (y/n)
```

You must visit the link to auth the token. This gives you a pin like this:

```
You have granted access to your Trello information.

To complete the process, please give this verification code:

  17894a35a2f745c3a184cf8e4bb5f1f9
```

Respond yes, and insert the pin:

```
What is the PIN? 17894a35a2f745c3a184cf8e4bb5f1f9
Access Token:
    - oauth_token = 0469c6271416af6eae10123fdae0afc1135e9082bb0b5ba87b2f8a1db9d7f0b1
    - oauth_token_secret = a978b159692cfc315377790669ac99a0

You may now access protected resources using the access tokens above.
```

Finaly you have access tokens to put in python vars.
