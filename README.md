# my-busybox

一个实用脚本与小工具集合，用于提升日常开发与运维效率：网络加速、Git 辅助、tmux/终端工具、系统信息、压力测试等。

> 注：本仓库会不定期调整脚本与结构，请以本文档为准。欢迎提 Issue/PR！

## 目录结构

```
my-busybox/
├── bin/                      # 可直接加入 PATH 的脚本
│   ├── ai                    # 通过 Goose CLI 快速调用 AI
│   ├── cht.sh                # 连接 cht.sh 的命令行速查
│   ├── dict.sh               # 命令行英汉词典（有道）
│   ├── gcl-gh.sh             # GitHub 仓库克隆加速（ghproxy）
│   ├── git-mkbak             # 为当前分支创建备份分支
│   ├── gwtsw.sh              # git worktree 快速切换（fzf）
│   ├── launchctl-fzf.sh      # macOS launchctl 服务管理（fzf）
│   ├── minifire.py           # 迷你版 Fire 风格 CLI 适配器
│   ├── motd.sh               # 开机/登录信息展示（可选集成 todo/更新数等）
│   ├── osc                   # OSC52 远程终端复制
│   ├── proxy-toggle.sh       # 快速切换 HTTP(S) 代理（支持 MY_PROXY）
│   ├── quick-git-cp.py       # Git cherry-pick 增强（可从 PR 拆取并建 PR）
│   ├── tmux-tools.py         # tmux 常用工具（目前支持 list-panes）
│   ├── wget-gh.sh            # GitHub 单文件下载加速（ghproxy）
│   └── data/
│       ├── mihomo_default.yaml
│       └── mihomo_rules.yaml
├── script/
│   └── mem_stress_test.sh    # 内存压力测试（stress-ng）
└── template/
    └── mihomo.template.yaml  # Mihomo 配置模板（示例）
```

与旧版 README 的差异：
- 移除了 mihomo/ 目录与 mihomo.sh 的说明，改为提供模板与数据文件。
- 新增工具：ai、gwtsw.sh、launchctl-fzf.sh、git-mkbak、minifire.py、mem_stress_test.sh 等。

## 安装与快速开始

1) 克隆仓库
```
git clone https://github.com/yourusername/my-busybox.git
```

2) 赋予执行权限（首次）
```
chmod +x my-busybox/bin/*
chmod +x my-busybox/script/* 2>/dev/null || true
```

3) 将 bin 目录加入 PATH（建议）
```
# bash
echo 'export PATH="$PATH:$HOME/my-busybox/bin"' >> ~/.bashrc
# zsh
echo 'export PATH="$PATH:$HOME/my-busybox/bin"' >> ~/.zshrc
```
然后重新加载 shell 配置或开新终端：
```
source ~/.bashrc  # 或 ~/.zshrc
```

## 依赖说明

- 通用：
  - git、curl、wget、python3、bash
- 可选/按功能：
  - fzf：gwtsw.sh、launchctl-fzf.sh 需要
  - gh（GitHub CLI）：quick-git-cp.py 的 PR 相关能力需要
  - tmux：tmux-tools.py 需要（仅使用 tmux 时）
  - fastfetch：motd.sh 用于展示系统信息
  - boxes：motd.sh 渲染盒子框（可选）
  - todo.sh：motd.sh 读取待办（可选）
  - pup：dict.sh 解析网页（需安装命令行 HTML 解析工具 pup）
  - stress-ng：script/mem_stress_test.sh 需要（Linux）
  - Arch Linux 的 checkupdates：motd.sh 可显示系统可更新包数量（可选）
  - macOS：launchctl（系统自带），配合 launchctl-fzf.sh 使用
  - Goose CLI：ai 脚本使用（https://github.com/block/goose 或你自己的安装方式）

## 工具说明与示例

### 网络与代理
- proxy-toggle.sh
  - 功能：快速开启/关闭 HTTP(S)/ALL 代理；默认 http://localhost:7890；可通过环境变量 MY_PROXY 覆盖。
  - 用法（推荐以 source 方式修改当前会话环境变量）：
    ```
    source proxy-toggle.sh
    # 或临时覆盖默认代理
    MY_PROXY=http://127.0.0.1:1080 source proxy-toggle.sh
    ```
- gcl-gh.sh / wget-gh.sh
  - 功能：通过 ghproxy 加速 GitHub 仓库克隆/文件下载。
  - 示例：
    ```
    gcl-gh.sh https://github.com/owner/repo.git
    wget-gh.sh https://raw.githubusercontent.com/owner/repo/branch/path/to/file
    ```

### Git 辅助
- git-mkbak
  - 功能：为当前分支创建备份分支 `<current>-bak`；若已存在可用 -f 强制覆盖。
  - 示例：
    ```
    git-mkbak        # 创建备份分支
    git-mkbak -f     # 强制重新创建备份分支
    ```
- gwtsw.sh
  - 功能：fzf 选择并切换到已存在的 git worktree 目录。
  - 示例：
    ```
    gwtsw.sh
    ```
- quick-git-cp.py
  - 功能：简化 cherry-pick 流程，支持从当前分支取最近 n 个提交或从 PR 抽取；可选创建新分支、push、并一键建 PR（需 gh）。
  - 示例：
    ```
    # 用法 1：从当前分支拿最近 2 个提交，切到目标分支并创建新分支再推送
    quick-git-cp.py --onto-branch origin/release/x.y -n 2 --create-new-branch --push

    # 用法 2：从 PR 123 的提交进行 cherry-pick，并创建 PR 到目标分支
    quick-git-cp.py --onto-branch origin/release/x.y --create-new-branch --create-pr --from-pr 123
    ```

### 终端与系统
- cht.sh
  - 功能：连接 https://cht.sh 查询命令/语言速查。
  - 注意：当前实现仅使用第一个参数，如需包含空格，请整体加引号并使用 cht.sh 的路径格式。
  - 示例：
    ```
    cht.sh tar
    cht.sh "python/list comprehensions"
    ```
- dict.sh
  - 功能：命令行英汉词典（有道），自动合并多行释义。
  - 示例：
    ```
    dict.sh hello
    dict.sh "machine learning"
    ```
- osc
  - 功能：通过 OSC52 在远程 SSH 会话中复制文本到本地剪贴板。
  - 说明：终端与中间层（如 tmux/ssh）需开启 OSC52 支持。
  - 示例：
    ```
    echo "copy this" | osc
    osc "copy this too"
    ```
- tmux-tools.py
  - 功能：tmux 工具集合，目前支持 list-panes。
  - 示例：
    ```
    tmux-tools.py list-panes
    ```
- motd.sh
  - 功能：展示系统信息（fastfetch）、可选展示待办（todo.sh）与可更新包数量（Arch 的 checkupdates）。
  - 示例：
    ```
    motd.sh
    ```
- launchctl-fzf.sh（macOS）
  - 功能：基于 fzf 的 launchctl 服务管理；支持 --scope gui|system，--alive 仅显示存活服务。
  - 示例：
    ```
    # GUI 用户域
    launchctl-fzf.sh --scope gui
    # System 域（脚本会自动提权）
    launchctl-fzf.sh --scope system --alive
    ```
- sudousrbin
  - 功能：以 sudo 执行指定命令（通过 which 解析绝对路径）。
  - 示例：
    ```
    sudousrbin systemctl status sshd
    sudousrbin brew update
    ```

### 其他
- ai
  - 功能：通过 Goose CLI 进行一次性对话/问答（无会话保存，-q 静默，-t 传入文本）。
  - 示例：
    ```
    ai "写一个 Python 快排"
    ```
- minifire.py
  - 功能：极简的 Fire 风格 CLI 适配器，便于将函数或类快速映射为命令行接口。
  - 使用方式：作为库导入，在你的脚本中调用。
  - 示例：
    ```python
    # demo.py
    from bin.minifire import fire_like

    class Greeter:
        def __init__(self, name: str = "world"):
            self.name = name
        def hello(self, times: int = 1):
            for _ in range(times):
                print(f"hello {self.name}")

    if __name__ == "__main__":
        fire_like(Greeter)
    ```
    运行：`python3 demo.py --name Alice hello --times 2`
- script/mem_stress_test.sh（Linux）
  - 功能：使用 stress-ng 在限定时间内尽可能占用可用内存进行压力测试。
  - 默认：持续 300 秒，占用约 90% 可用内存。
  - 风险提示：请谨慎使用，避免在关键生产环境直接运行。

### 配置与模板
- template/mihomo.template.yaml 与 bin/data/*.yaml 为 Mihomo 的示例模板与规则/默认配置，可按需参考改造到你的环境。仓库不再包含 mihomo.sh 管理脚本。

## 常见问题
- 执行提示 command not found？请确认已将 `bin/` 加入 PATH 并打开新终端或 `source` 配置文件。
- 某些功能没有输出？检查可选依赖是否已安装（见“依赖说明”）。
- cht.sh 查询包含空格？请使用引号并遵从 `cht.sh/<path>` 的结构。

## 贡献
欢迎通过 Issue/PR 反馈需求与改进建议。

## 许可证
MIT
