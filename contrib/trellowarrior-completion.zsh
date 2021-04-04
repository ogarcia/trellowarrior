#compdef trellowarrior

typeset -A opt_args

_trellowarrior_commands() {
  local -a _commands
  _commands=(
    'sync:synchronize Trello and Taskwarrior'
    'auth:setup the authentication against Trello'
    'config:view or modify TrelloWarrior config'
    'version:show TrelloWarrior version'
  )
  _describe 'command' _commands
}

_trellowarrior_config_commands() {
  local -a _commands
  _commands=(
    'get:get a config value'
    'set:set new or modify a config value'
    'remove:remove a config value'
    'project:configure projects'
  )
  _describe 'command' _commands
}

_trellowarrior_config_project_commands() {
  local -a _commands
  _commands=(
    'list:list projects'
    'add:add new project'
    'modify:modify values of existing project'
    'show:show project configuration'
    'enable:enable existing project sync'
    'disable:disable existing project sync'
    'remove:remove existing project'
  )
  _describe 'command' _commands
}

_trellowarrior_config_project () {
  _arguments \
    '(-h --help)'{-h,--help}'[show help]' \
    '1: :_trellowarrior_config_project_commands' \
    '*:: :->config_project_args'

  case ${state} in
    config_project_args)
      case ${words[1]} in
        list)
          _arguments \
            '(-h --help)'{-h,--help}'[show help]'
          ;;
        add)
          _arguments \
            '(-h --help)'{-h,--help}'[show help]' \
            '--todo[to do list name]:todo' \
            '--doing[doing list name]:doing' \
            '--done[done list name]:done' \
            '--filter[Trello lists to filter on sync (separated by commas)]:filter' \
            '(-o --only-my-cards)'{-o,--only-my-cards}'[sync only cards assigned to me]' \
            '(-d --disabled)'{-d,--disabled}'[add project disabled]' \
            ':name: ' \
            ':taskwarrior: ' \
            ':trello: '
          ;;
        modify)
          _arguments \
            '(-h --help)'{-h,--help}'[show help]' \
            '--taskwarrior[project name in Taskwarrior]:taskwarrior' \
            '--trello[project name in Trello]:trello' \
            '--todo[to do list name]:todo' \
            '--doing[doing list name]:doing' \
            '--done[done list name]:done' \
            '--filter[Trello lists to filter on sync (separated by commas)]:filter' \
            '--only-my-cards[sync only cards assigned to me]:(yes no)' \
            ':name: '
          ;;
        show|enable|disable|remove)
          _arguments \
            '(-h --help)'{-h,--help}'[show help]' \
            ':name'
          ;;
      esac
      ;;
  esac
}

_arguments \
  '(-h --help)'{-h,--help}'[show help]' \
  '(-c --config)'{-c,--config}'[custom configuration file path]:configuration file:_files' \
  '(-v -vv --verbose)'{-v,-vv,--verbose}'[be verbose]' \
  '1: :_trellowarrior_commands' \
  '*:: :->args'

case ${words[1]} in
  sync)
    _arguments \
      '(-h --help)'{-h,--help}'[show help]' \
      '*::projects'
    ;;
  auth)
    _arguments \
      '(-h --help)'{-h,--help}'[show help]' \
      '--api-key[api key]:api_key' \
      '--api-key-secret[api key secret]:api_key_secret' \
      '--expiration[duration of authorization]:expiration:(1hour 1day 30days never)' \
      '--name[application name]:name'
    ;;
  config)
    _arguments \
      '(-h --help)'{-h,--help}'[show help]' \
      '1: :_trellowarrior_config_commands' \
      '*:: :->config_args'
    ;;
  version)
    _arguments \
      '(-h --help)'{-h,--help}'[show help]'
    ;;
esac

case ${state} in
  config_args)
    case ${words[1]} in
      get|remove)
        _arguments \
          '(-h --help)'{-h,--help}'[show help]' \
          ':option: '
        ;;
      set)
        _arguments \
          '(-h --help)'{-h,--help}'[show help]' \
          ':option: ' \
          ':value: '
        ;;
      project)
        _trellowarrior_config_project
        ;;
    esac
    ;;
esac
