#!/bin/bash

set -euo pipefail

MIHOMO_DIR="${HOME}/.config/mihomo"
mkdir -p "${MIHOMO_DIR}"

# Function to check and download the config file
download_config() {
  config_file="${MIHOMO_DIR}/config.yaml"
  ui_dir="${MIHOMO_DIR}/ui"
  sub_url=$1
  # Check if SUB_URL is set
  if [ -z "$sub_url" ]; then
    echo "[x] 请设置 SUB_URL"
    exit 1
  fi
  echo "[+] 下载订阅中..."
  curl -m 10 -L -H "User-Agent: Clash" -o "${config_file}" "${sub_url}"
  yq -i ".external-ui = \"${ui_dir}\"" "${config_file}"
}

# Function to download the UI
download_ui() {
  ui_dir="${MIHOMO_DIR}/ui"
  if [ ! -d "${ui_dir}" ]; then
    echo "[+] 下载 UI..."
    git clone https://github.com/metacubex/metacubexd.git -b gh-pages --depth 1 "${ui_dir}"
  fi
}

# Function to download the mmdb file
download_mmdb() {
  mmdb_path="${MIHOMO_DIR}/Country.mmdb"
  if [ ! -f "${mmdb_path}" ]; then
    echo "[+] 下载 mmdb 文件..."
    curl -m 10 -L -H "User-Agent: Clash" -o "${mmdb_path}" "https://cdn.jsdelivr.net/gh/Dreamacro/maxmind-geoip@release/Country.mmdb"
  fi
}

# Main function to start the script
run() {
  echo "[+] 启动 mihomo..."
  mihomo -d "${MIHOMO_DIR}"
}

arg1="${1:-}"
case "${arg1}" in
run)
  run
  ;;
download_config)
  download_config $SUB_URL
  ;;
download_ui)
  download_ui
  ;;
download_mmdb)
  download_mmdb
  ;;
init)
  download_config $SUB_URL
  download_ui
  download_mmdb
  ;;
*)
  echo "Usage: $0 {init|run|download_config|download_ui|download_mmdb}"
  exit 1
  ;;
esac
