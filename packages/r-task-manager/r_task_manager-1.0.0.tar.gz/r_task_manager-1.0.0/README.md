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
pip install runman
```

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

RunMan 的配置文件存储在用户主目录下的 `.runman` 目录：

- `~/.runman/tasks/` - 任务配置文件
- `~/.runman/history.json` - 命令历史

## 许可证

MIT License

## 作者

dreamer

