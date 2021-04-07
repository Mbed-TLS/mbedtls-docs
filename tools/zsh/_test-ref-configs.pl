#compdef test-ref-configs.pl
## Completion for tests/test-ref-configs.pl in Mbed TLS.

_test_ref_configs_pl () {
  compadd $(sed -n '/%configs *=/,/;/ s/^ *'\''\([^'\'']*\)'\'' => {$/\1/p' $words[1])
}

_test_ref_configs_pl "%@"

# Local Variables:
# mode: sh
# sh-shell: zsh
# End:

