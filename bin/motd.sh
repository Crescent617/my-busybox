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

cmd_exists() {
  command -v "$1" &>/dev/null
  return $?
}

os_logo() {
  case $(uname -s) in
  Darwin)
    echo " "
    ;;
  Linux)
    echo " "
    ;;
  *)
    echo " "
    ;;
  esac
}

# ==== System Information ====
# fastfetch --logo small -s "break:os:cpu:gpu:memory:disk:uptime" 2>/dev/null
# if [ $? -ne 0 ]; then
#   mark_blue "$(os_logo) $(uptime)"
# fi
# echo ""

# ==== Package Updates ====
if cmd_exists checkupdates; then
  cur_file=/tmp/motd_checkupdates

  # not exist or older than 12 hours
  if [ ! -f "$cur_file" ] || [ "$(find "$cur_file" -mmin +720)" ]; then
    touch "$cur_file"
    UPDATES=$(checkupdates 2>/dev/null)
    NUM_UPDATES=$(echo "$UPDATES" | sed '/^$/d' | wc -l)
    if [ "$NUM_UPDATES" -gt 0 ]; then
      mark_cyan "󰮯 $NUM_UPDATES updates available."
    fi
  fi

fi

# ==== Todo List ====
if cmd_exists todo.sh; then
  # keep lines start with number
  title=$(mark_cyan "  TODO")
  todos="$(todo.sh list | awk '/^\x1b\[[0-9;]*m*[0-9]/')"
  if [ -z "$todos" ]; then
    todos="Nice! No todos today. 🤪"
  fi
  if cmd_exists boxes; then
    echo -e "$title\n--\n$todos" | boxes -d ansi-rounded
  else
    echo -e "$title\n--\n$todos"
  fi
fi
