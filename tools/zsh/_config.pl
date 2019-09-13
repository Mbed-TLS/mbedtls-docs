#compdef config.pl config.py
## Completion for scripts/config.pl and scripts/config.pl in Mbed TLS.

_config_pl_symbols () {
  local -a identifiers
  #identifiers=("${(@f)$(_call_program get_symbols sed -n 's!^/*\**#define \(MBEDTLS_[0-9A-Z_a-z][0-9A-Z_a-z]*\).*!\1!p' $config_h)}")
  identifiers=("${(@f)$(sed -n 's!^/*\**#define \(MBEDTLS_[0-9A-Z_a-z][0-9A-Z_a-z]*\).*!\1!p' $config_h)}")
  _describe -t symbols 'config.h symbols' identifiers
}

_config_pl () {
  local context state state_descr line
  typeset -A opt_args
  local ret=0 config_h=$words[1]:h/../include/mbedtls/config.h
  local -a commands_with_descriptions
  commands_with_descriptions=(
    'baremetal:All features for bare metal platforms'
    'get:Get symbol value'
    'full:All features'
    'realfull:Uncomment all #define'\'''
    'set:Actvate symbol'
    'unset:Deactivate symbol'
  )
  _arguments \
    {'-f','--file'}'[file to edit]:file to edit:_files -g "*.h"' \
    {'-o','--force'}'[define symbol even if not present]' \
    '1:config.pl command:->command' \
    '*::config.pl commands:->param'
  case $state in
    (command)
      _describe -t commands 'config.pl command' commands_with_descriptions;;
    (param)
      case $words[1]:$CURRENT in
        ((get|set|unset):2) _call_function ret _config_pl_symbols;;
      esac;;
  esac
  return $ret
}

_config_pl "%@"

# Local Variables:
# mode: sh
# sh-shell: zsh
# End:

