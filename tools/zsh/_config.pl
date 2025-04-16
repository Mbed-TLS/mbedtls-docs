#compdef config.pl config.py
## Completion for scripts/config.pl and scripts/config.py in Mbed TLS.

_config_pl_symbols () {
  local -a identifiers
  identifiers=("${(@f)$(_call_program _config_pl_symbols 'sed -n \
      -e '\''s!^/*\**#define \(MBEDTLS_[0-9A-Z_a-z][0-9A-Z_a-z]*\).*!\1!p'\'' \
      -e '\''s!^/*\**#define \(PSA_[0-9A-Z_a-z][0-9A-Z_a-z]*\).*!\1!p'\'' \
      $config_h')}")
  _describe -t symbols 'config.h symbols' identifiers
}

_config_pl () {
  local context state state_descr line
  typeset -A opt_args
  local ret=0 config_h
  config_h=($words[1]:h/../include/mbedtls/(mbedtls_|)config.h(N[1]))
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
  if (($+opt_args[--file])); then
    config_h=$opt_args[--file]
  elif (($+opt_args[-f])); then
    config_h=$opt_args[-f]
  fi
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

