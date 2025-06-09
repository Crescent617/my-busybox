#!/bin/bash

set -e

# 默认 scope 为 system
SCOPE="system"
UID=$(id -u)

# 参数解析
while [[ $# -gt 0 ]]; do
  case "$1" in
  --scope)
    SCOPE="$2"
    shift 2
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
  exec sudo "$0" --scope system
fi

# 设置 launchctl domain
if [[ "$SCOPE" == "gui" ]]; then
  DOMAIN="gui/$UID"
else
  DOMAIN="system"
fi

# 获取服务列表
SERVICES=$(launchctl list | awk 'NR>1 {print $3}' | sort | uniq)

if [ -z "$SERVICES" ]; then
  echo "No launchctl services found in scope [$SCOPE]"
  exit 1
fi

# 选择服务
SELECTED=$(echo "$SERVICES" | fzf --prompt="[$SCOPE] Select a service: ")

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
