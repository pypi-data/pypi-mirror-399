#compdef iltero

_iltero_completion() {
  eval $(env _TYPER_COMPLETE_ARGS="${words[1,$CURRENT]}" _ILTERO_COMPLETE=complete_zsh iltero)
}

compdef _iltero_completion iltero
