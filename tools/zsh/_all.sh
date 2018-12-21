#compdef all.sh
## Completion for tests/scripts/all.sh in Mbed TLS.

_all_sh () {
  local components line opt spec specs
  components=()
  specs=()
  for line in "${(@M)${(@f)$(_call_program help $words[1] --help)}:# #-*}"; do
    line=${line##[ ]##}
    opt=(${(s:|:)${line%%[= ]*}})
    spec=
    line=${line#"${line%%[= ]*}"}
    if [[ $line == \=* ]]; then
      spec=":${${line#\=}%% *}:"
      if [[ $spec == ":<"*">:" ]]; then
        spec=":${${spec#??}%??}:"
      fi
      case $spec in
        *_dir_path:) spec="${spec}_dirs";;
        *_path:) spec="${spec}_files -g \"*(.*)\"";;
      esac
    elif [[ $opt[1] == '-s' || $opt[1] == '--seed' ]]; then
      spec=":seed:"
    fi
    line=${line##[^ ]#[ ]##}
    spec="[$line]${spec}"
    specs+=($^opt$spec)
    if ((${#${(M)opt:#--list-components}})); then
      components=("${(@M)${(@f)$(_call_program list-components $words[1] --list-components)}}")
    fi
  done
  if (($#components)); then
    specs+=("*:component:($components)")
  fi
  _arguments : $specs
}

_all_sh "%@"

# Local Variables:
# mode: sh
# sh-shell: zsh
# End:

