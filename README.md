# TrelloWarrior

Tool to sync Taskwarrior projects with Trello boards.

## Requirements

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
an equivalence between Trello Cards and Taskwarrior Tasks. Note that you
never, never, never, never, (period), should edit this field.

The second UDA `trellolistname` is used to determine the Trello List where
the Card/Task is stored. You can edit this field without problems to move
the task to another list.

### For TrelloWarrior

#### Prepare the environment

##### The easy way

Simply create a Python 2/3 virtualenv and install via pip:

```
virtualenv trw
. trw/bin/activate
pip install trellowarrior
```

##### By hand

For run TrelloWarrior you need to install
[tasklib](https://github.com/robgolding63/tasklib) and
[py-trello](https://github.com/sarumont/py-trello). TrelloWarrior uses these
Python helpers to comunicate with Taskwarrior and Trello.

You can use your package system to install it, but the best way is to use
a Python 2/3 virtualenv:

```sh
virtualenv trw
. trw/bin/activate
pip install tasklib
pip install py-trello
```

#### Get the keys

TrelloWarrior access to Trello via API. You need generate an access token
for it.

First go to: https://trello.com/app-key to get your API Key and API Secret.

Then call trellowarrior with the authenticate command :
```sh
trellowarrior.py -c path/to/your/configfile authenticate --api-key your_api_key --api-key-secret your_api_secret --trello-name TrelloWarrior --expiration 30days
```

If the config file already exist, an error will be printed and the command will stop without doing anything.

You can set the `TRELLO_EXPIRATION` to `1hour`, `1day`, `30days`,
`never`. We recomend use `30days` for tests and `never` for daily use.

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

The config file is now initialized with the needed configuration variables.

## Configuration

The TrelloWarrior config is very easy. There is a `trellowarrior.conf`
sample file that you can modify to set with your data.

You can place the config file with `trellowarrior.py`, in your home as
`~/.trellowarrior.conf` or `~/.config/trellowarrior/trellowarrior.conf`, or
set the configuration file path with `-c` or `--config` argument.

To synchronize trello and task warrior, simply call trellowarrior with the sync command

```sh 
trellowarrior.py sync
```

You can also add a list of project(s) to synchronize :

```sh 
trellowarrior.py sync project1 project2
```
 
### DEFAULT Section

In the `DEFAULT` section, it is mandatory to set your Trello API key and
token and, at least, one sync project.
The sync project corresponds to the following sections
that define the Taskwarrior project and Trello board equivalence.

* `taskwarrior_taskrc_location` Optional. Define where your *taskrc* file is located. Default: `~/.taskrc`
* `taskwarrior_data_location` Optional. Define where your *task* data dir is located. Default: `~/.task`

* `trello_api_key` MANDATORY. Your Trello Api Key.
* `trello_api_secret` MANDATORY. Your Trello Api Secret.
* `trello_token` MANDATORY. Your Trello Token.
* `trello_token_secret` MANDATORY. Your Trello Token Secret.

* `sync_projects` MANDATORY. Define what sections are loaded, separated by spaces.

### Project/Board Sections

The Project/Board sections are called from `sync_projects` and define the
equivalence between Taskwarrior and Trello.

* `tw_project_name` MANDATORY. The name of project in Taskwarrior.
* `trello_board_name` MANDATORY. The name of Trello Board.
* `trello_todo_list` Optional. The name of Trello list where new pending tasks are stored. Default: `To Do`
* `trello_doing_list` Optional. The name of Trello list for active tasks. Default: `Doing`
* `trello_done_list` Optional. The name of Trello list for done taks. Default: `Done`
* `tags_color` Optional. Mapping between taskwarrior tags and trello labels. Json encoded list of dict like : `[{"color": "blue", "name": "trellowarrior"}, {"color": "green", "name": "personal"}]`. Cannot have multiple labels with the same name and will remove not mapped ones.

## Equivalences

| Taskwarrior         | Trello        |
|---------------------|---------------|
| UDA: trelloid       | Card ID       |
| UDA: trellolistname | List Name     |
| Project             | Board Name    |
| Description         | Card Name     |
| Due                 | Card Due Date |
| Tag                 | Label         |

## Known limitations

The main objective of TaskWarrior is to be simple so it **doesn't manage
collisions**. The sync strategy is **last modified wins**, this means that if
you do a modification in Trello and later a modification in Taskwarrior,
TrelloWarrior does the sync and keeps the Taskwarrior data, because it is
the last touched.

You can have infinite lists in your Trello, but all of them are considered
as *pending*. You only can have one *doing* list and one *done* list, but
these lists can be configured.

If you have several boards with same name, TrelloWarrior always picks the
first one.

For now, only syncs *Title/Description*, *Due dates*, *Tags, and *Status*.
