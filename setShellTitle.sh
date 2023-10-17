#!/bin/bash

function setShellTitle()
{
    PROMPT_COMMAND="echo -en \"\033]0;$@\a\""
    echo "Title set to $@"
}
