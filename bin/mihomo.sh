#!/bin/bash

set -euo pipefail

MIHOMO_DIR="${HOME}/.config/mihomo"
mkdir -p "${MIHOMO_DIR}"

config_tmpl=$(
  cat <<EOF
port: 7890
socks-port: 7891
redir-port: 7892
allow-lan: true
mode: rule
log-level: warning
external-controller: '0.0.0.0:9090'
secret: ''
external-ui: /home/hrli/.config/mihomo/ui
EOF
)

# Function to check and download the config file
download_config() {
  default_config="${MIHOMO_DIR}/config_default.yaml"
  echo "$config_tmpl" >"${default_config}"

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

  # merge config_tmpl and sub_config
  yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' "${sub_config}" "${default_config}" >"${config_file}"
}

# Function to download the UI
download_ui() {
  ui_dir="${MIHOMO_DIR}/ui"
  if [ ! -d "${ui_dir}" ]; then
    echo "[+] 下载 UI..."
    git clone https://github.com/metacubex/metacubexd.git -b gh-pages --depth 1 "${ui_dir}"
  else
    echo "[+] UI 已存在，跳过下载"
  fi
}

# Function to download the mmdb file
download_mmdb() {
  mmdb_path="${MIHOMO_DIR}/Country.mmdb"
  if [[ -f /etc/clash/Country.mmdb ]]; then
    echo "[+] 检测到系统已安装 mmdb 文件，跳过下载"
    rm "$mmdb_path"
    ln -s /etc/clash/Country.mmdb "$mmdb_path"
    return
  fi

  temp_path="${MIHOMO_DIR}/Country.mmdb.temp"
  if [ ! -f "${temp_path}" ]; then
    echo "[+] 下载 mmdb 文件..."
    curl -m 10 -L -H "User-Agent: Clash" -o "${temp_path}" "https://cdn.jsdelivr.net/gh/Dreamacro/maxmind-geoip@release/Country.mmdb"
    if [ $? -ne 0 ]; then
      echo "[x] 下载 mmdb 文件失败"
      exit 1
    fi
    # rename to Country.mmdb
    mv "${temp_path}" "${mmdb_path}"
  fi
}

system-proxy-open() {
  # 跳过 localhost 相关流量，避免死循环
  sudo iptables -t nat -A OUTPUT -d 127.0.0.1 -j RETURN

  # 跳过本地代理程序（比如 mihomo）的进程流量（假设 UID 为 123）
  # sudo iptables -t nat -A OUTPUT -m owner --uid-owner 123 -j RETURN

  # 重定向其他 TCP 流量到 redir 端口
  sudo iptables -t nat -A OUTPUT -p tcp -j REDIRECT --to-ports 7892
}

system-proxy-close() {
  # 清除之前的规则
  sudo iptables -t nat -F OUTPUT
  sudo iptables -t nat -F PREROUTING
}

# Main function to start the script
run() {
  echo "[+] 启动 mihomo..."
  mihomo -d "${MIHOMO_DIR}"
}

while getopts "D:P:R" opt; do
  case "$opt" in
  D) # Download
    case "$OPTARG" in
    config) download_config $CLASH_SUB_URL ;;
    ui) download_ui ;;
    mmdb) download_mmdb ;;
    all)
      download_config $CLASH_SUB_URL
      download_ui
      download_mmdb
      ;;
    *) echo "无效选项: -D $OPTARG" ;;
    esac
    ;;
  P) # System Proxy
    case "$OPTARG" in
    o)
      system-proxy-open
      ;;
    c)
      system-proxy-close
      ;;
    *)
      echo "无效选项: -P $OPTARG"
      ;;
    esac
    ;;
  R) # Run
    run
    ;;
  esac
done
