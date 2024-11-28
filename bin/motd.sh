#!/bin/bash

mark_red() {
  echo -e "\033[0;31m$1\033[0m"
}

mark_yellow() {
  echo -e "\033[0;33m$1\033[0m"
}

mark_green() {
  echo -e "\033[0;32m$1\033[0m"
}

mark_blue() {
  echo -e "\033[0;34m$1\033[0m"
}

mark_magenta() {
  echo -e "\033[0;35m$1\033[0m"
}

mark_cyan() {
  echo -e "\033[0;36m$1\033[0m"
}

mark_gray() {
  echo -e "\033[0;37m$1\033[0m"
}

command -v todo.sh &>/dev/null && todo.sh list && echo '---'

if command -v checkupdates &>/dev/null; then
  cur_file=/tmp/motd_checkupdates

  # not exist or older than 12 hours
  if [ ! -f "$cur_file" ] || [ "$(find "$cur_file" -mmin +720)" ]; then
    touch "$cur_file"
    UPDATES=$(checkupdates 2>/dev/null)
    NUM_UPDATES=$(echo "$UPDATES" | sed '/^$/d' | wc -l)
    if [ "$NUM_UPDATES" -gt 0 ]; then
      echo "󰮯 $NUM_UPDATES updates available." >"$cur_file"
    fi
  fi

  mark_cyan "$(cat $cur_file)"
fi

mark_blue " $(uptime)"
