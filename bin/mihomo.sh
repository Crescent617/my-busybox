#!/bin/bash

set -euo pipefail

MIHOMO_DIR="${HOME}/.config/mihomo"
mkdir -p "${MIHOMO_DIR}"

config_tmpl=$(
  cat <<EOF
port: 7890
socks-port: 7891
redir-port: 7892
allow-lan: false
mode: rule
log-level: silent
external-controller: '0.0.0.0:9090'
secret: ''
external-ui: /home/hrli/.config/mihomo/ui
EOF
)

# Function to check and download the config file
download_config() {
  sub_config="${MIHOMO_DIR}/sub.yaml"
  config_file="${MIHOMO_DIR}/config.yaml"
  ui_dir="${MIHOMO_DIR}/ui"
  sub_url=$1
  # Check if SUB_URL is set
  if [ -z "$sub_url" ]; then
    echo "[x] 请设置 SUB_URL"
    exit 1
  fi
  echo "[+] 下载订阅中..."
  echo "$sub_url" >"${MIHOMO_DIR}/sub_url.txt"
  curl -m 10 -L -H "User-Agent: Clash" -o "${sub_config}" "${sub_url}"
  if [ $? -ne 0 ]; then
    echo "[x] 下载订阅失败"
    exit 1
  fi

  # add sub_config's proxies to config_tmpl
  echo "[+] 生成配置文件..."
  proxies=$(yq -r '.proxies' "${sub_config}")
  if [[ $? -ne 0 ]]; then
    echo "[x] 解析订阅失败"
    exit 1
  fi
  if [[ -z "$proxies" ]]; then
    echo "[x] 订阅文件中没有 proxies"
    exit 1
  fi

  echo "$config_tmpl" >"${config_file}"
  yq -i '.proxies = load("'$sub_config'").proxies' "${config_file}"
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
  download_config $CLASH_SUB_URL
  ;;
download_ui)
  download_ui
  ;;
download_mmdb)
  download_mmdb
  ;;
init)
  download_config $CLASH_SUB_URL
  download_ui
  download_mmdb
  ;;
*)
  echo "Usage: $0 {init|run|download_config|download_ui|download_mmdb}"
  exit 1
  ;;
esac
