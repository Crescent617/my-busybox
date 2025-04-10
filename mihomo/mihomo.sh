#!/bin/bash

set -euo pipefail

# Function to check and download the config file
download_config() {
  if [ ! -f "${CONFIG_FILE}" ] || [ $((($(date +%s) - $(stat -c %Y "${CONFIG_FILE}")) / 86400)) -ge 14 ]; then
    echo "[+] 下载订阅中..."
    curl -L -H "User-Agent: Clash" -o "${CONFIG_FILE}" "${SUB_URL}"
  else
    echo "[!] 配置文件在14天内更新过，无需重新下载"
  fi
}

# Function to download the UI
download_ui() {
  if [ ! -d "${UI_DIR}" ]; then
    echo "[+] 下载 UI..."
    git clone https://github.com/metacubex/metacubexd.git -b gh-pages --depth 1 "${UI_DIR}"
    yq -i ".external-ui = \"${UI_DIR}\"" "${CONFIG_FILE}"
  fi
}

# Function to download the mmdb file
download_mmdb() {
  if [ ! -f "${MMDB_PATH}" ]; then
    echo "[+] 下载 mmdb 文件..."
    curl -L -H "User-Agent: Clash" -o "${MMDB_PATH}" "https://cdn.jsdelivr.net/gh/Dreamacro/maxmind-geoip@release/Country.mmdb"
  fi
}

# Main function to start the script
main() {
  # Check if SUB_URL is set
  if [ -z "${SUB_URL:-}" ]; then
    echo "[x] 请设置 SUB_URL 环境变量"
    exit 1
  fi

  # Configuration paths
  MIHOMO_DIR="${HOME}/.config/mihomo"
  CONFIG_FILE="${MIHOMO_DIR}/config.yaml"
  UI_DIR="${MIHOMO_DIR}/ui"
  MMDB_PATH="${MIHOMO_DIR}/Country.mmdb"

  # Create configuration directory if it doesn't exist
  mkdir -p "${MIHOMO_DIR}"

  # Download necessary files
  download_config
  download_ui
  download_mmdb

  # Start mihomo
  echo "[+] 启动 mihomo..."
  mihomo -d "${MIHOMO_DIR}"
}

# Execute main function
main
