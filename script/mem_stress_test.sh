#!/usr/bin/env bash

# 设定运行时长（单位：秒）
DURATION=300   # 5 分钟

# 可用内存大小（单位：MB）
AVAILABLE_MB=$(free -m | awk '/Mem:/ {print int($7 * 0.9)}')

echo "⏳ 开始使用 $AVAILABLE_MB MB 内存进行 $DURATION 秒测试..."
sleep 2

# 执行 stress-ng，使用 vm 子系统进行内存分配测试
stress-ng --vm 1 --vm-bytes "${AVAILABLE_MB}M" --timeout "${DURATION}"s --metrics-brief
