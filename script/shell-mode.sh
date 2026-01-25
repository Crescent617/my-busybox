#!/usr/bin/env zsh

typeset -g MODE=0

# 1. 切换模式的函数
toggle-mode() {
  if [[ $MODE -eq 0 ]]; then
    MODE=1
    zle -M -- "-- CLAUDE CODE --"
  else
    MODE=0
    zle redisplay
  fi
}

# 2. 包装回车键的函数
accept-line() {
  if [[ $MODE -eq 1 ]]; then
    # 如果输入框不为空，则重写命令
    if [[ -n "$BUFFER" ]]; then
      # 将当前缓冲区内容包裹在 claude '...' 中
      # 使用 ${(q)BUFFER} 可以自动处理输入内容中的单引号转义，防止脚本崩溃
      BUFFER="claude ${(q)BUFFER}"
    fi
    
    # 执行完后重置模式
    MODE=0
    zle -M -- ""
  fi
  # 执行原生的回车操作
  zle .accept-line
}

zle -N toggle-mode
zle -N accept-line accept-line
bindkey '\ea' toggle-mode
