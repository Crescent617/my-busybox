#!/usr/bin/env python3

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal

from minifire import fire_like

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

if d := os.getenv("MIHOMO_DIR"):
    MIHOMO_DIR = Path(d)
else:
    MIHOMO_DIR = Path.home() / ".config" / "mihomo"
    MIHOMO_DIR.mkdir(parents=True, exist_ok=True)

# Clash 配置
CLASH_HOST = "http://0.0.0.0:9090"  # Clash 控制台地址
SECRET = ""  # 如果有 secret，填入，比如 "abc123"
PROXY_SELECTOR = re.compile(r"香港|新加坡|台湾|日本")
TARGET_GROUP = "🔰国外流量"


DEFAULT_CONFIG = """
port: 7890
socks-port: 7891
# redir-port: 7892
allow-lan: true
mode: rule
log-level: warning
# log-level: info
external-controller: '0.0.0.0:9090'
secret: ''

tun:
  enable: true
  stack: system # system / gvisor，mac 上推荐 system
  dns-hijack:
    - any:53
    - tcp://any:53
  auto-route: true # 自动配置路由
  auto-detect-interface: true
  route-exclude-address:
    - 100.64.0.0/10
    - fd7a:115c:a1e0::/48
dns:
  enable: true
  listen: 0.0.0.0:53
  enhanced-mode: fake-ip
  fake-ip-range: 198.18.0.1/16
  fake-ip-filter:
    - '*.local'
    - 'localhost'
    - 'dns.google'
    - '+.lan'
    - '+.internal'
    - 'time.*'
    - "*.tailscale.com"
    - "tailscale.com"
    - "log.tailscale.net"
    - "ts.net" # Tailscale 的短域名
  nameserver:
    - https://doh.pub/dns-query
    - https://dns.alidns.com/dns-query
  fallback:
    - https://1.1.1.1/dns-query
  fallback-filter:
    geoip: true
    geoip-code: CN
    # geosite:
    #   - gfw
    ipcidr:
      - 240.0.0.0/4
    domain:
      - '+.google.com'
      - '+.facebook.com'
      - '+.youtube.com'
  nameserver-policy:
    "+.<tailnet-name>.ts.net": "100.100.100.100"
external-ui: ui
"""

CUSTOM_RULES = """
rules:
  # {{tailscale
  - PROCESS-NAME,tailscale,DIRECT
  - PROCESS-NAME,tailscaled,DIRECT
  - IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
  - IP-CIDR,fd7a:115c:a1e0::/48,DIRECT,no-resolve  # Tailscale IPv6
  # }}
"""

required_cmds = ["mihomo", "yq", "git"]


def run_cmd(cmd: str, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        logger.error(f"命令执行失败: {cmd}")
        logger.error(result.stderr)
        sys.exit(1)
    return result.stdout.strip()


def download_config(sub_url: str):
    if not sub_url:
        logger.error("请设置 SUB_URL")
        sys.exit(1)

    logger.info("下载订阅中...")

    sub_config = MIHOMO_DIR / "sub.yaml"
    config_file = MIHOMO_DIR / "config.yaml"
    default_config = MIHOMO_DIR / "config_default.yaml"
    if not default_config.exists():
        default_config.write_text(DEFAULT_CONFIG)
    rules_file = MIHOMO_DIR / "config_with_rules.yaml"
    if not rules_file.exists():
        rules_file.write_text(DEFAULT_CONFIG + "\n" + CUSTOM_RULES)

    try:
        urllib.request.urlretrieve(sub_url, sub_config)
    except Exception as e:
        logger.error(f"下载订阅失败: {e}")
        sys.exit(1)

    # 检查是否有 proxies 字段
    try:
        output = run_cmd(f"yq -r '.proxies' {sub_config}")
        if not output:
            raise Exception("proxies 字段为空")
    except Exception as e:
        logger.error(f"解析订阅失败或无 proxies: {e}")
        sys.exit(1)

    logger.info("合并配置文件...")
    merged_yaml = run_cmd(
        f"yq eval-all 'select(fi == 0) *+ select(fi == 1) * select(fi == 2)' {rules_file} {sub_config} {default_config}"
    )
    config_file.write_text(merged_yaml)


def download_ui():
    ui_dir = MIHOMO_DIR / "ui"
    if ui_dir.exists():
        logger.info("UI 已存在，跳过下载")
        return
    logger.info("下载 UI...")
    run_cmd(
        f"git clone https://github.com/metacubex/metacubexd.git -b gh-pages --depth 1 {ui_dir}"
    )


def download_mmdb():
    mmdb_path = MIHOMO_DIR / "Country.mmdb"
    system_mmdb = Path("/etc/clash/Country.mmdb")
    if system_mmdb.exists():
        logger.info("检测到系统已安装 mmdb 文件，跳过下载")
        if mmdb_path.exists():
            mmdb_path.unlink()
        os.symlink(system_mmdb, mmdb_path)
        return

    temp_path = Path(tempfile.gettempdir()) / "Country.mmdb.temp"
    if not temp_path.exists():
        logger.info("下载 mmdb 文件...")
        url = "https://cdn.jsdelivr.net/gh/Dreamacro/maxmind-geoip@release/Country.mmdb"
        try:
            urllib.request.urlretrieve(url, temp_path)
        except Exception as e:
            logger.error(f"下载 mmdb 文件失败: {e}")
            sys.exit(1)
    os.rename(temp_path, mmdb_path)


# 构造带 secret 的 URL
def build_url(path, query=None):
    base = urllib.parse.urljoin(CLASH_HOST, path)
    query = query or {}
    if SECRET:
        query["secret"] = SECRET
    if query:
        return f"{base}?{urllib.parse.urlencode(query)}"
    return base


# 发送 GET 请求并返回 JSON
def http_get_json(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


# 发送 PUT 请求
def http_put_json(url, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode()


# 获取策略组下的所有节点名
def get_proxies():
    url = build_url("/proxies")
    data = http_get_json(url)
    proxies: dict[str, dict] = data.get("proxies", [])
    targets = []

    for name, proxy in proxies.items():
        if proxy.get("id") and proxy.get("name") and PROXY_SELECTOR.search(name):
            targets.append(proxy["name"])
    return targets


# 测试某个节点的延迟
def get_delay(proxy_name: str):
    encoded = urllib.parse.quote(proxy_name.encode(), safe="")
    url = build_url(
        f"/proxies/{encoded}/delay",
        {"timeout": 5000, "url": "http://www.gstatic.com/generate_204"},
    )
    try:
        data = http_get_json(url)
        return data.get("delay", float("inf"))
    except:
        return float("inf")


# 切换策略组使用的节点
def switch_proxy(proxy_name: str):
    encoded = urllib.parse.quote(TARGET_GROUP, safe="")
    url = build_url(f"/proxies/{encoded}")
    http_put_json(url, {"name": proxy_name})
    logger.info(f"✅ 已切换到节点：{proxy_name}")


def load_json(file_path: Path):
    """加载 JSON 文件"""
    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


class Cli:
    def __init__(self, sub_url: str = "", dir=MIHOMO_DIR):
        self.sub_url = sub_url
        self.mihomo_dir = Path(dir).expanduser()

    def download(self, file: Literal["config", "ui", "mmdb", "all"]):
        """下载配置、UI 或 mmdb 文件"""

        sub_url = (
            self.sub_url
            or load_json(self.mihomo_dir / "subconfig.json").get("sub_url")
            or os.getenv("CLASH_SUB_URL")
        )
        if not sub_url:
            raise ValueError("请设置环境变量 CLASH_SUB_URL")
        actions = {
            "config": lambda: download_config(sub_url),
            "ui": download_ui,
            "mmdb": download_mmdb,
            "all": lambda: (download_config(sub_url), download_ui(), download_mmdb()),
        }
        actions[file]()

    def run(self):
        """运行 Mihomo"""
        logger.info("启动 mihomo...")
        run_cmd(f"mihomo -d {self.mihomo_dir}")

    def healthcheck(self):
        """检查依赖"""
        logger.info("所有依赖已满足")
        missing_cmds = [cmd for cmd in required_cmds if not shutil.which(cmd)]
        if missing_cmds:
            logger.error(f"缺少依赖: {', '.join(missing_cmds)}")
            sys.exit(1)

    def proxy(self, show: bool = False, auto: bool = False):
        """切换代理节点"""
        proxies = get_proxies()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(get_delay, proxy): proxy for proxy in proxies}
            delays = {future.result(): proxy for future, proxy in futures.items()}
            if delays and auto:
                min_delay = min(delays.keys())
                best_proxy = delays[min_delay]
                logger.info(f"最佳节点: {best_proxy} (延迟: {min_delay} ms)")
                switch_proxy(best_proxy)

            elif show:
                logger.info("可用节点列表:")
                for d, proxy in sorted(delays.items()):
                    logger.info(f"{proxy} - 延迟: {d} ms")


if __name__ == "__main__":
    try:
        fire_like(Cli)
    except Exception as e:
        logger.error(f"发生错误: {str(e)[:50]}")
        sys.exit(1)
