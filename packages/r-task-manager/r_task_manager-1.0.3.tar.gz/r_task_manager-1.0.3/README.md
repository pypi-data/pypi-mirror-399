# RunMan

RunMan 是一个简单而强大的后台任务管理工具，支持运行脚本、查看日志、管理进程等功能。

## 功能特性

- 🚀 **后台运行脚本**：支持 Python 和 Shell 脚本的后台运行
- 📜 **日志管理**：自动记录日志，支持实时查看和历史查看
- 🏷️ **别名管理**：自动分配单字母别名，方便快速操作
- 🔄 **任务重启**：一键重启任务
- 👥 **多用户支持**：支持多用户环境（本地和 Docker）
- 🎯 **进程组管理**：kill 时自动终止所有子进程
- 📝 **命令历史**：记录最近运行的命令
- 🔍 **任务监控**：查看任务状态和运行时间

## 安装

```bash
pip install r-task-manager
```

### Windows/PowerShell 用户注意

PowerShell 默认有一个 `r` 别名（用于 `Invoke-History`），会与 `r-task-manager` 的命令冲突。

**临时解决方案（仅当前 PowerShell 窗口有效）：**
```powershell
Remove-Item Alias:r
```

**永久解决方案（推荐）：**
将以下内容添加到 PowerShell 配置文件（`$PROFILE`）：
```powershell
Remove-Item Alias:r -Force -ErrorAction SilentlyContinue
```

查看配置文件路径：
```powershell
$PROFILE
```

如果配置文件不存在，创建它：
```powershell
if (!(Test-Path -Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force
}
notepad $PROFILE
```

然后在文件中添加 `Remove-Item Alias:r -Force -ErrorAction SilentlyContinue` 并保存。

## 使用方法

### 基本命令

```bash
# 查看所有运行中的任务（默认）
r

# 启动 Python 脚本
r script.py

# 启动 Shell 脚本
r script.sh

# 启动脚本并传递参数
r script.py arg1 arg2

# 查看所有任务
r ls

# 终止任务（使用别名）
r kill a

# 查看任务日志
r log a
# 或简写
r l a

# 重启任务
r r a

# 查看任务详情
r watch a
# 或简写
r w a

# 显示命令历史
r a

# 初始化 .bashrc（添加常用别名）
r init

# 调试模式启动脚本
r debug script.py
```

### 目录跳转

```bash
# 方法1：加载 rcd 函数后使用
eval $(r func)
rcd a

# 方法2：直接使用
eval $(r cd a)

# 方法3：获取路径后跳转
cd $(R_PATH_ONLY=1 r cd a)
```

## 配置

RunMan 的配置文件默认存储在用户主目录下的 `.runman` 目录：

- `~/.runman/tasks/` - 任务配置文件
- `~/.runman/history.json` - 命令历史

### 自定义配置目录

你可以通过以下方式自定义配置目录位置：

**方法1：使用环境变量（推荐）**
```bash
# Linux/Mac
export RUNMAN_CONFIG_DIR=/path/to/your/config
r script.py

# Windows PowerShell
$env:RUNMAN_CONFIG_DIR = "C:\path\to\your\config"
r script.py
```

**方法2：使用命令行参数**
```bash
r --config-dir /path/to/your/config script.py
r --config-dir /path/to/your/config ls
```

**优先级：**
1. 命令行参数 `--config-dir`（最高优先级）
2. 环境变量 `RUNMAN_CONFIG_DIR`
3. 默认值 `~/.runman`（最低优先级）

## 许可证

MIT License

## 作者

dreamer

