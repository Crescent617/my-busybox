# my-busybox

一个实用工具集合，提供各种命令行工具和脚本，用于提高开发效率、简化网络操作和系统管理。

## 目录结构

```
my-busybox/
├── bin/                # 通用工具脚本
│   ├── cht.sh          # 命令行查询助手
│   ├── dict.sh         # 英文在线词典工具
│   ├── gcl-gh.sh       # GitHub克隆加速工具
│   ├── motd.sh         # 系统信息显示工具
│   ├── osc             # OSC52远程终端复制工具
│   ├── proxy-toggle.sh # HTTP代理快速切换工具
│   ├── quick-git-cp.py # Git cherry-pick增强工具
│   ├── tmux-tools.py   # tmux实用工具
│   └── wget-gh.sh      # GitHub文件下载加速工具
└── mihomo/             # Mihomo代理工具
    └── mihomo.sh       # Mihomo代理管理脚本
```

## 工具说明

### 网络工具

- **proxy-toggle.sh**: 快速开启/关闭HTTP代理，一键切换代理状态
- **gcl-gh.sh**: 通过ghproxy.cn加速GitHub仓库克隆
- **wget-gh.sh**: 通过ghproxy.cn加速GitHub文件下载
- **mihomo.sh**: 自动化管理Mihomo代理软件，包括订阅配置、UI界面和地理数据库

### 开发工具

- **cht.sh**: 查询命令行工具的使用说明和代码示例，连接至cht.sh在线服务
- **osc**: 支持在远程SSH会话中实现内容复制到本地剪贴板
- **quick-git-cp.py**: 增强的Git cherry-pick工具，简化从一个分支到另一个分支的提交迁移
- **tmux-tools.py**: tmux管理工具，提供了更易用的tmux操作命令

### 实用工具

- **dict.sh**: 命令行英文词典，通过有道词典查询单词释义
- **motd.sh**: 系统信息和通知显示工具，可展示系统状态、待办事项等

## 使用方法

1. 克隆此仓库到本地:
   ```
   git clone https://github.com/yourusername/my-busybox.git
   ```

2. 确保脚本有执行权限:
   ```
   chmod +x my-busybox/bin/*
   chmod +x my-busybox/mihomo/mihomo.sh
   ```

3. 建议将bin目录添加到PATH环境变量以方便使用:
   ```
   echo 'export PATH="$PATH:$HOME/my-busybox/bin"' >> ~/.bashrc
   # 或者对于zsh用户
   echo 'export PATH="$PATH:$HOME/my-busybox/bin"' >> ~/.zshrc
   ```

4. 重新加载shell配置或打开新终端:
   ```
   source ~/.zshrc
   ```

## 工具详细说明

### cht.sh
通过命令行查询编程语言、Shell命令等的用法和示例。
```
cht.sh python list comprehension
```

### dict.sh
命令行英文词典，快速查询单词。
```
dict.sh hello
```

### gcl-gh.sh
GitHub克隆加速。
```
gcl-gh.sh https://github.com/username/repo.git
```

### 其他工具

请查看各脚本的注释了解更多使用细节。

## 贡献

欢迎提交Issue和Pull Request来完善这个工具集！

## 许可证

MIT
