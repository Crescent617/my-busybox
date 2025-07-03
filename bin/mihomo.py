#!/usr/bin/env python3

"""
mihomo.py 是一个无任何第三方py包依赖 Python 脚本，用于管理 Clash 配置文件、订阅更新和代理切换。
该脚本包括以下主要功能：
1. 下载订阅文件并与本地配置文件进行合并。
2. 自动下载 UI 组件和 MaxMind 地理数据库文件。
3. 测试代理节点的延迟并切换至最佳节点。
4. 提供 CLI 接口供用户操作。

依赖项：
- yq 和 git: 用于 YAML 合并及 UI 下载。

使用方法：
请确保设置环境变量 `CLASH_SUB_URL` 或在命令行中指定订阅 URL。
运行脚本时：
`python3 mihomo.py <commands>`
您可以通过以下命令来查看支持的全部功能：
`python3 mihomo.py --help`
"""

import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal

from minifire import fire_like

# ==== 配置部分 ====
PROXY_SELECTOR = re.compile(r"香港|新加坡|台湾|日本")  # 代理节点选择规则
TARGET_GROUP = "🔰国外流量"  # Clash 策略组名称
TEST_DELAY_URL = "http://google.com"  # 用于测试代理节点延迟的 URL

# ==== 日志设置 ====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ==== 常量定义 ====
MIHOMO_DIR = Path(os.getenv("MIHOMO_DIR") or "~/.config/mihomo").expanduser()
MIHOMO_DIR.mkdir(parents=True, exist_ok=True)  # 创建配置目录
DEFAULT_CONFIG = (Path(__file__).parent / "data" / "mihomo_default.yaml").read_text()
CUSTOM_RULES = (Path(__file__).parent / "data" / "mihomo_rules.yaml").read_text()
CLASH_HOST = "http://0.0.0.0:9090"  # Clash 控制台地址
SECRET = ""  # Clash 的 API 密钥，如果需要，请填写。

# ==== 函数定义 ====
def run_cmd(cmd: str, check=True):
    """运行命令行指令，并捕获输出"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        logger.error(f"命令执行失败: {cmd}")
        logger.error(result.stderr)
        sys.exit(1)
    return result.stdout.strip()

def download_config(sub_url: str):
    """下载订阅配置并合并为 Clash 的配置文件"""
    if not sub_url:
        logger.error("请设置 SUB_URL")
        sys.exit(1)

    logger.info("下载订阅中...")

    config_file = MIHOMO_DIR / "config.yaml"

    # 使用临时文件夹进行配置处理
    with tempfile.TemporaryDirectory() as temp_dir:
        p = Path(temp_dir)

        sub_config = p / "sub.yaml"
        default_config = p / "config_default.yaml"
        rules_file = p / "rules.yaml"

        # 写入默认配置与规则
        default_config.write_text(DEFAULT_CONFIG)
        rules_file.write_text(CUSTOM_RULES)

        try:
            # 下载订阅文件
            urllib.request.urlretrieve(sub_url, sub_config)
        except Exception as e:
            logger.error(f"下载订阅失败: {e}")
            sys.exit(1)

        # 检查是否正确下载了 proxies 字段
        try:
            output = run_cmd(f"yq -r '.proxies' {sub_config}")
            if not output:
                raise Exception("订阅 proxies 字段为空")
        except Exception as e:
            logger.error(f"解析订阅失败或无 proxies: {e}")
            sys.exit(1)

        logger.info("合并配置文件...")
        merged_yaml = run_cmd(
            f"yq eval-all 'select(fi == 0) *+ select(fi == 1) * select(fi == 2)' {rules_file} {sub_config} {default_config}"
        )
        config_file.write_text(merged_yaml)

def download_ui():
    """下载 UI 组件"""
    ui_dir = MIHOMO_DIR / "ui"
    if ui_dir.exists():
        logger.info("UI 已存在，跳过下载")
        return
    logger.info("下载 UI...")
    run_cmd(
        f"git clone https://github.com/metacubex/metacubexd.git -b gh-pages --depth 1 {ui_dir}"
    )

def download_mmdb():
    """下载 MaxMind MMDB 文件"""
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
def test_delay(proxy_name: str):
    encoded = urllib.parse.quote(proxy_name.encode(), safe="")
    url = build_url(
        f"/proxies/{encoded}/delay",
        {"timeout": 5000, "url": TEST_DELAY_URL},
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
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

class Cli:
    """CLI 命令行控制类"""
    def __init__(self, sub_url: str = "", dir=MIHOMO_DIR):
        self.mihomo_dir = Path(dir).expanduser()
        self.sub_url = (
            sub_url
            or load_json(self.mihomo_dir / "subconfig.json").get("sub_url")
            or os.getenv("CLASH_SUB_URL")
        )

    def download(self, file: Literal["config", "ui", "mmdb", "all"]):
        """下载配置、UI 或 mmdb 文件"""

        sub_url = self.sub_url
        if not sub_url:
            raise ValueError("请设置环境变量 CLASH_SUB_URL")
        actions = {
            "config": lambda: download_config(sub_url),
            "ui": download_ui,
            "mmdb": download_mmdb,
            "all": lambda: (download_config(sub_url), download_ui(), download_mmdb()),
        }
        actions[file]()

    def update_sub(self):
        """更新订阅"""
        self.download("config")

    def run(self):
        """运行 Mihomo"""
        logger.info("启动 mihomo...")
        run_cmd(f"mihomo -d {self.mihomo_dir}")

    def proxy(self, show: bool = False, auto: bool = False):
        """切换代理节点"""
        proxies = get_proxies()

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(test_delay, proxy): proxy for proxy in proxies}
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

    def healthcheck(self):
        req = urllib.request.Request(TEST_DELAY_URL)
        try:
            urllib.request.urlopen(req, timeout=10)
            logger.info("ping 测试成功，网络连接正常")
        except Exception as e:
            logger.error(f"ping 失败: {e}... 尝试切换代理")
            self.proxy(auto=True)


if __name__ == "__main__":
    try:
        fire_like(Cli)
    except Exception as e:
        logger.error(f"发生错误: {str(e)[:50]}")
        sys.exit(1)
