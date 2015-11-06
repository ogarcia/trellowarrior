# TrelloWarrior

Tool to sync Taskwarrior projects with Trello boards.

## Requeriments

### In Taskwarrior

First for all you need configure some UDAs in Taskwarrior to store some
Trello data. This is very, very, very important. If you dont have the UDAs
configured before run TrelloWarrior you'll destroy your Taskwarrior tasks
data.

To set UDAs in Taskwarrior simply edit `.taskrc` and add the following
lines.

```
# UDAs
uda.trelloid.type=string
uda.trelloid.label=Trello ID
uda.trellolistname.type=string
uda.trellolistname.label=Trello List Name
```

The first UDA `trelloid` is used to store the Trello Card ID and establish
an equivalence between Trello Cards and Taskwarrior Tasks.

The second UDA `trellolistname` is used to determine the Trello List where
the Card/Task is stored.

### For TrelloWarrior

#### Prepare environ

For run TrelloWarrior you need to install [tasklib][1] and [py-trello][2].
TrelloWarrior uses this python helpers to comunicate with Taskwarrior and
Trello.

You can use you package system to install it, but the easy form is use
a Python 2.7 Virtualenv.

```sh
virtualenv2 trw
. trw/bin/activate
pip install tasklib
pip install py-trello
```

Note that in several distributions the Virtualenv executable is called
simply `virtualenv` instead `virtualenv2`.

[1](https://github.com/robgolding63/tasklib)
[2](https://github.com/sarumont/py-trello)

#### Get the keys

TrelloWarrior access to Trello via API. You need generate an access token
for it.

First go to: https://trello.com/app-key to get your API Key and API Secret.

In a bash compatible shell, run the following exports to config (configure
with your data).

```sh
export TRELLO_API_KEY="your_api_key"
export TRELLO_API_SECRET="your_api_secret"
export TRELLO_NAME="trellowarrior"
export TRELLO_EXPIRATION="30days"
```

Note: You can set the `TRELLO_EXPIRATION` to `1hour`, `1day`, `30days`,
`never`. We recomend use `30days` for tests and `never` for daily use.

Run now the trello util into Virtualenv to get token and token secret.

```sh
python trw/lib/python2.7/site-packages/trello/util.py
```

This return some like this.

```
Request Token:
    - oauth_token        = 1c5ad394834dde42a7655437ab3e0060
    - oauth_token_secret = dffc3a62622ef450028f685406bceacc

Go to the following link in your browser:
https://trello.com/1/OAuthAuthorizeToken?oauth_token=1c5ad334134dde46a8659437ab3e0069&scope=read,write&expiration=30days&name=trellowarrior
Have you authorized me? (y/n)
```

You must visit the link to authorize the token. This gives you a pin like
this.

```
You have granted access to your Trello information.

To complete the process, please give this verification code:

  17894a35a2f745c3a184cf8e4bb5f1f9
```

Respond yes, and insert the pin.

```
What is the PIN? 17894a35a2f745c3a184cf8e4bb5f1f9
Access Token:
    - oauth_token = 0469c6271416af6eae10123fdae0afc1135e9082bb0b5ba87b2f8a1db9d7f0b1
    - oauth_token_secret = a978b159692cfc315377790669ac99a0

You may now access protected resources using the access tokens above.
```

Finaly you have access tokens to put in TrelloWarrior config file.

