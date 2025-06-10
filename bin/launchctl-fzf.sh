#!/bin/bash

set -e

# if not exists FZF_DEFAULT_OPTS
if [[ -z "$FZF_DEFAULT_OPTS" ]]; then
  export FZF_DEFAULT_OPTS="\
      --color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8\
      --color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc\
      --color=marker:#b4befe,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8\
      --color=selected-bg:#45475a\
      --multi"
fi

# 默认 scope 为 system
SCOPE="system"
uid() {
  echo "$(id -u)"
}

ONLY_ALIVE="0"

# 参数解析
while [[ $# -gt 0 ]]; do
  case "$1" in
  --scope)
    SCOPE="$2"
    shift 2
    ;;
  --alive)
    echo "Only showing alive services"
    ONLY_ALIVE="1"
    shift
    ;;
  *)
    echo "Unknown option: $1"
    exit 1
    ;;
  esac
done

# 检查 scope 合法性
if [[ "$SCOPE" != "gui" && "$SCOPE" != "system" ]]; then
  echo "Invalid scope: $SCOPE (expected 'gui' or 'system')"
  exit 1
fi

# 如果是 system scope 且当前不是 root，则用 sudo 重新执行
if [[ "$SCOPE" == "system" && "$EUID" -ne 0 ]]; then
  echo "Elevating to root for system scope..."
  args="--scope system"
  if [[ "$ONLY_ALIVE" == "1" ]]; then
    args+=" --alive"
  fi
  exec sudo "$0" $args
fi

# 设置 launchctl domain
if [[ "$SCOPE" == "gui" ]]; then
  DOMAIN="gui/$(uid)"
else
  DOMAIN="system"
fi

cond=''
if [[ "$ONLY_ALIVE" == "1" ]]; then
  cond='$1 != "-"'
  echo "Only showing alive services in scope [$SCOPE]"
else
  cond='1 == 1'
fi

SERVICES=$(launchctl list | awk 'NR>1 && '"$cond"' {printf "%-50s\t %s\t %s\n", $3, $1, $2}' | sort -r | uniq)

if [ -z "$SERVICES" ]; then
  echo "No launchctl services found in scope [$SCOPE]"
  exit 1
fi

# 选择服务
SELECTED=$(echo "$SERVICES" | fzf --prompt="[$SCOPE] Select a service: " | awk '{print $1}')

if [ -z "$SELECTED" ]; then
  echo "No service selected."
  exit 1
fi

# 选择操作
ACTION=$(printf "status\nstart\nstop\nrestart\nkickstart" | fzf --prompt="Action for [$SELECTED]: ")

if [ -z "$ACTION" ]; then
  echo "No action selected."
  exit 1
fi

# 执行动作
case "$ACTION" in
start)
  echo "Starting $SELECTED in [$DOMAIN]..."
  launchctl start "$DOMAIN/$SELECTED"
  ;;
stop)
  echo "Stopping $SELECTED in [$DOMAIN]..."
  launchctl stop "$DOMAIN/$SELECTED"
  ;;
restart)
  echo "Restarting $SELECTED in [$DOMAIN]..."
  launchctl stop "$DOMAIN/$SELECTED"
  sleep 0.5
  launchctl start "$DOMAIN/$SELECTED"
  ;;
status)
  echo "Status for $SELECTED in [$DOMAIN]:"
  launchctl print "$DOMAIN/$SELECTED" 2>/dev/null || echo "Service not found or not running."
  ;;
kickstart)
  echo "Kickstarting $SELECTED in [$DOMAIN]..."
  launchctl kickstart -k "$DOMAIN/$SELECTED"
  ;;
*)
  echo "Unknown action: $ACTION"
  exit 1
  ;;
esac
