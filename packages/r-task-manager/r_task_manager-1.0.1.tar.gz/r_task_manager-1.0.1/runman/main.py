"""
后台任务管理工具
用法:
  r                   查看任务（按用户分组，默认行为）
  r <脚本文件>         启动任务
  r ls                查看任务（按用户分组）
  r kill <别名>        通过别名终止任务
  r log <别名>         查看指定任务的日志（tail -f）
  r l <别名>           查看指定任务的日志（tail -f，log的简写）
  r r <别名>           重启任务（先kill，等待3秒，再启动）
  r watch <别名>       查看任务详情和最新10行日志
  r w <别名>           查看任务详情和最新10行日志（watch的简写）
  r cd <别名>          输出cd命令（配合eval可直接跳转）
  r c <别名>           输出cd命令（cd的简写，配合eval可直接跳转）
  r func               输出shell函数定义（eval $(r func)后可使用rcd命令）
  r a                  显示历史命令（最近50条）
  r debug <脚本文件>   调试模式启动脚本
"""

import os
import sys
import json
import subprocess
import argparse
import signal
import time
import re
import pwd
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Optional, Dict, List, Tuple

# 使用用户主目录下的配置目录
HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / ".runman"
TASK_DIR = CONFIG_DIR / "tasks"
HISTORY_FILE = CONFIG_DIR / "history.json"
DEBUG_MODE = False
MAX_HISTORY = 50

# ANSI颜色代码
COLOR_RESET = "\033[0m"
COLOR_BRIGHT_GREEN = "\033[92m"  # 翠绿色 - 当前环境正在运行
COLOR_LIGHT_GREEN = "\033[2;32m"  # 浅绿色 - 其他环境正在运行
COLOR_BLACK = "\033[90m"  # 黑色/深灰色 - 已停止


def log_debug(*args, **kwargs):
    """调试日志输出"""
    if DEBUG_MODE:
        print(f"🐛 [DEBUG] {' '.join(str(a) for a in args)}", file=sys.stderr, **kwargs)


def ensure_permissions():
    """确保任务目录权限（root用户时设置为777）"""
    TASK_DIR.mkdir(parents=True, exist_ok=True)
    if os.geteuid() == 0:
        try:
            os.chmod(TASK_DIR, 0o777)
            for file in TASK_DIR.glob("*.task"):
                os.chmod(file, 0o777)
        except Exception:
            pass


def get_user_info() -> str:
    """检测用户环境信息"""
    if os.path.exists("/.dockerenv") and os.path.getsize("/.dockerenv") > 0:
        # 在docker容器中
        container_name = os.environ.get("HOSTNAME") or os.environ.get("CONTAINER_NAME", "unknown")
        return f"docker:{container_name}"
    else:
        # 在host机器上
        # 优先使用环境变量，如果不存在则通过UID获取用户名
        username = os.environ.get("USER") or os.environ.get("USERNAME")
        if not username:
            try:
                # 使用进程的UID获取用户名，避免os.getlogin()在无终端环境下的问题
                username = pwd.getpwuid(os.getuid()).pw_name
            except (KeyError, AttributeError):
                username = "unknown"
        return f"local:{username}"


def is_process_running(pid: int) -> bool:
    """检查进程是否正在运行"""
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def format_runtime(start_time_str: str) -> str:
    """格式化运行时间显示"""
    if start_time_str == "unknown":
        return "unknown"
    
    try:
        # 解析启动时间
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.now()
        delta = current_time - start_time
        
        total_seconds = int(delta.total_seconds())
        
        if total_seconds < 0:
            return "0s"
        
        # 计算天、小时、分钟、秒
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # 格式化显示
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    except Exception:
        return "unknown"


def load_task_file(task_file: Path) -> Optional[Dict]:
    """加载任务配置文件"""
    try:
        with open(task_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def save_task_file(task_file: Path, task_info: Dict):
    """保存任务配置文件"""
    with open(task_file, 'w', encoding='utf-8') as f:
        json.dump(task_info, f, ensure_ascii=False, indent=2)
    ensure_permissions()


def assign_alias() -> str:
    """分配单字母别名（a-z，按启动顺序，可重用）"""
    all_aliases = [chr(i) for i in range(ord('a'), ord('z') + 1)]
    used_aliases = set()
    
    # 收集所有正在运行的任务的别名（只检查进程正在运行的任务）
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if task_info:
            pid = task_info.get("PID", 0)
            # 只收集正在运行的任务的别名
            if isinstance(pid, int) and is_process_running(pid):
                alias = task_info.get("ALIAS", "")
                if alias:
                    used_aliases.add(alias)
    
    # 找到第一个未使用的别名
    for alias in all_aliases:
        if alias not in used_aliases:
            return alias
    
    # 如果所有别名都被使用，返回空（理论上不会发生）
    return ""


def check_path_conflict(target: str) -> bool:
    """检查路径冲突（当前目录下的同名脚本）"""
    target_path = Path(target).resolve()
    target_basename = target_path.name
    target_dir = target_path.parent
    current_user_info = get_user_info()
    
    conflicts = []
    
    # 只检查当前运行环境下正在运行的任务
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if not task_info:
            continue
        
        task_user_info = task_info.get("USER_INFO", "")
        pid = task_info.get("PID", 0)
        
        # 只检查当前运行环境下的任务
        if task_user_info != current_user_info or not is_process_running(pid):
            continue
        
        running_target = task_info.get("TARGET", "")
        running_dir = task_info.get("WORKDIR", "")
        
        if running_target and running_dir:
            running_path = Path(running_target)
            running_basename = running_path.name
            running_dir_path = Path(running_dir)
            
            # 检查是否是同一目录下的同名脚本
            if running_dir_path == target_dir and running_basename == target_basename:
                conflicts.append((task_file, task_info))
    
    if conflicts:
        print("⚠️  发现当前目录下有同名脚本正在运行：")
        for task_file, task_info in conflicts:
            pid = task_info.get("PID", "unknown")
            alias = task_info.get("ALIAS", "unknown")
            target_path = task_info.get("TARGET", "unknown")
            print(f"   PID: {pid} | 别名: {alias} | 文件: {target_path}")
        print()
        
        print("请选择操作：")
        print("  1. 结束之前的程序并继续运行")
        print("  2. 继续运行当前程序（不结束之前的）")
        print("  3. 退出")
        print()
        
        while True:
            reply = input("请输入选项 (1/2/3): ").strip()
            if reply == '1':
                # 结束冲突的任务
                for task_file, task_info in conflicts:
                    pid = task_info.get("PID")
                    if pid and is_process_running(pid):
                        try:
                            os.kill(pid, signal.SIGTERM)
                            print(f"✅ 已终止任务 PID: {pid}")
                        except Exception:
                            pass
                    task_file.unlink(missing_ok=True)
                return True
            elif reply == '2':
                # 继续运行当前程序，不结束之前的
                print("✅ 将继续运行当前程序（之前的程序仍在运行）")
                return True
            elif reply == '3':
                # 退出
                print("❌ 已取消")
                return False
            else:
                print("❌ 无效选项，请输入 1、2 或 3")
    
    return True


def kill_by_alias(alias: str) -> bool:
    """通过别名终止任务（仅限当前运行环境），包括所有子进程"""
    current_user_info = get_user_info()
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if not task_info:
            continue
        
        task_user_info = task_info.get("USER_INFO", "")
        task_alias = task_info.get("ALIAS", "")
        pid = task_info.get("PID", 0)
        
        # 只操作当前运行环境下的任务
        if task_user_info == current_user_info and task_alias == alias and is_process_running(pid):
            pgid = task_info.get("PGID")
            print(f"🛑 正在终止任务 [别名: {alias}, PID: {pid}]", end="")
            if pgid:
                print(f", 进程组: {pgid}")
            else:
                print()
            
            try:
                # 优先使用进程组 kill（可以终止所有子进程）
                if pgid and hasattr(os, 'killpg'):
                    try:
                        os.killpg(pgid, signal.SIGTERM)
                        log_debug(f"使用 killpg 终止进程组 {pgid}")
                    except ProcessLookupError:
                        # 进程组不存在，回退到单个进程 kill
                        os.kill(pid, signal.SIGTERM)
                        log_debug(f"进程组不存在，回退到 kill PID {pid}")
                    except OSError as e:
                        # 其他错误（如权限问题），回退到单个进程 kill
                        log_debug(f"killpg 失败 ({e})，回退到 kill PID {pid}")
                        os.kill(pid, signal.SIGTERM)
                else:
                    # 向后兼容：没有 PGID 或系统不支持 killpg，使用原来的方式
                    os.kill(pid, signal.SIGTERM)
                    log_debug(f"使用 kill 终止进程 {pid}")
                
                # 等待进程结束
                for _ in range(10):
                    if not is_process_running(pid):
                        break
                    time.sleep(0.5)
                
                task_file.unlink(missing_ok=True)
                print("✅ 任务已终止（包括所有子进程）")
                return True
            except ProcessLookupError:
                # 进程已经不存在
                task_file.unlink(missing_ok=True)
                print("✅ 任务已终止（进程已不存在）")
                return True
            except Exception as e:
                print(f"❌ 终止任务失败: {e}")
                return False
    
    print(f"❌ 未找到别名为 '{alias}' 的运行中任务")
    return False


def log_by_alias(alias: str) -> bool:
    """通过别名查看任务日志（使用tail -f）"""
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if not task_info:
            continue
        
        task_alias = task_info.get("ALIAS", "")
        pid = task_info.get("PID", 0)
        logfile = task_info.get("LOGFILE", "")
        
        # 只查看当前运行环境下的任务
        if task_alias == alias:
            if not logfile or not Path(logfile).exists():
                print(f"❌ 日志文件不存在: {logfile}")
                return False
            
            print(f"📜 查看任务日志 [别名: {alias}, PID: {pid}]")
            print("----------------------------------------")
            print("(按 Ctrl+C 退出日志查看)")
            print("----------------------------------------")
            
            # 使用 tail -f 命令查看日志
            try:
                subprocess.run(["tail", "-f", logfile], check=False)
            except KeyboardInterrupt:
                print("\n(已退出日志查看)")
                return True
            except FileNotFoundError:
                # 如果系统没有 tail 命令，使用 Python 实现
                print("(使用 Python 实现日志跟踪)")
                try:
                    with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
                        # 先显示已有内容
                        content = f.read()
                        if content:
                            print(content, end='', flush=True)
                        
                        # 移动到文件末尾
                        f.seek(0, 2)
                        
                        while True:
                            line = f.readline()
                            if line:
                                print(line, end='', flush=True)
                            else:
                                if not is_process_running(pid):
                                    break
                                time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\n(已退出日志查看)")
                    return True
            except Exception as e:
                print(f"❌ 查看日志失败: {e}")
                return False
            
            return True
    
    print(f"❌ 未找到别名为 '{alias}' 的运行中任务")
    return False


def watch_by_alias(alias: str) -> bool:
    """通过别名查看任务详情和最新30行日志"""
    current_user_info = get_user_info()
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if not task_info:
            continue
        
        task_alias = task_info.get("ALIAS", "")
        task_user_info = task_info.get("USER_INFO", "")
        
        # 只查看当前运行环境下的任务
        if task_alias == alias and task_user_info == current_user_info:
            pid = task_info.get("PID", 0)
            target = task_info.get("TARGET", "unknown")
            workdir = task_info.get("WORKDIR", "unknown")
            logfile = task_info.get("LOGFILE", "")
            start_time = task_info.get("START_TIME", "unknown")
            
            # 检查进程状态
            is_running = isinstance(pid, int) and is_process_running(pid)
            runtime = format_runtime(start_time)
            
            # 打印任务详情
            print("=" * 60)
            print(f"📋 任务详情 [别名: {alias}]")
            print("=" * 60)
            print(f"别名:        {alias}")
            print(f"PID:         {pid}")
            print(f"状态:        {'✅ 运行中' if is_running else '⏹️ 已停止'}")
            print(f"目标文件:    {target}")
            print(f"工作目录:    {workdir}")
            print(f"启动时间:    {start_time}")
            print(f"运行时间:    {runtime}")
            print(f"日志文件:    {logfile}")
            print("=" * 60)
            
            # 打印最新30行日志
            if logfile and Path(logfile).exists():
                print()
                print("📜 最新10行日志：")
                print("-" * 60)
                try:
                    # 读取文件最后30行
                    with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # 获取最后30行
                        last_lines = lines[-10:] if len(lines) > 10 else lines
                        for line in last_lines:
                            print(line, end='')
                except Exception as e:
                    print(f"❌ 读取日志失败: {e}")
                print("-" * 60)
            else:
                print()
                print("⚠️  日志文件不存在或无法访问")
            
            return True
    
    print(f"❌ 未找到别名为 '{alias}' 的任务")
    return False


def cd_by_alias(alias: str, path_only: bool = False) -> bool:
    """通过别名获取任务的工作目录并输出目录路径或cd命令"""
    current_user_info = get_user_info()
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if not task_info:
            continue
        
        task_alias = task_info.get("ALIAS", "")
        task_user_info = task_info.get("USER_INFO", "")
        
        # 只查看当前运行环境下的任务
        if task_alias == alias and task_user_info == current_user_info:
            workdir = task_info.get("WORKDIR", "")
            
            if not workdir or workdir == "unknown":
                print(f"❌ 无法获取任务的工作目录", file=sys.stderr)
                return False
            
            workdir_path = Path(workdir)
            if not workdir_path.exists():
                print(f"❌ 工作目录不存在: {workdir}", file=sys.stderr)
                return False
            
            # 如果 path_only 为 True，只输出目录路径
            # 否则输出完整的 cd 命令（用于 eval）
            if path_only:
                print(str(workdir_path.resolve()))
            else:
                print(f"cd {workdir_path.resolve()}")
            return True
    
    print(f"❌ 未找到别名为 '{alias}' 的任务", file=sys.stderr)
    return False


def output_shell_function():
    """输出 shell 函数定义，用于直接跳转"""
    # 使用 sys.argv[0] 获取当前脚本路径（安装后会是 r 命令的路径）
    script_path = Path(sys.argv[0]).resolve()
    func_def = f"""# r cd 功能的 shell 函数
rcd() {{
    if [ -z "$1" ]; then
        echo "❌ 用法: rcd <别名>"
        return 1
    fi
    
    TARGET_DIR=$(R_PATH_ONLY=1 {script_path} cd "$1" 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$TARGET_DIR" ] && [ -d "$TARGET_DIR" ]; then
        cd "$TARGET_DIR"
        echo "✅ 已跳转到: $TARGET_DIR"
    else
        echo "❌ 跳转失败: 未找到别名为 '$1' 的任务或目录不存在"
        return 1
    fi
}}"""
    print(func_def)


def init_bashrc():
    """初始化 .bashrc，添加常用别名"""
    bashrc_path = Path.home() / ".bashrc"
    
    # 要添加的别名
    aliases_to_add = [
        "alias ll='ls -alF'",
        "alias la='ls -A'",
        "alias l='ls -CF'",
        "alias nv='nvidia-smi'",
        "alias py='python'",
    ]
    
    # 检查标记，避免重复添加
    marker_start = "# RunMan aliases - start"
    marker_end = "# RunMan aliases - end"
    
    try:
        # 读取现有内容
        if bashrc_path.exists():
            with open(bashrc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # 检查是否已经添加过
        if marker_start in content and marker_end in content:
            print("✅ .bashrc 中已包含 RunMan 别名，跳过添加")
            return True
        
        # 添加别名
        new_content = content
        if new_content and not new_content.endswith('\n'):
            new_content += '\n'
        
        new_content += f"\n{marker_start}\n"
        for alias in aliases_to_add:
            new_content += f"{alias}\n"
        new_content += f"{marker_end}\n"
        
        # 写入文件
        with open(bashrc_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 已成功添加别名到 .bashrc")
        print("📝 添加的别名：")
        for alias in aliases_to_add:
            print(f"   {alias}")
        print("\n💡 提示: 请运行 'source ~/.bashrc' 或重新打开终端使别名生效")
        return True
        
    except Exception as e:
        print(f"❌ 初始化 .bashrc 失败: {e}")
        return False


def restart_by_alias(alias: str) -> bool:
    """通过别名重启任务：先kill，sleep 3秒，再启动"""
    current_user_info = get_user_info()
    
    # 查找任务
    target_task_file = None
    target_task_info = None
    
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if not task_info:
            continue
        
        task_user_info = task_info.get("USER_INFO", "")
        task_alias = task_info.get("ALIAS", "")
        pid = task_info.get("PID", 0)
        
        # 只操作当前运行环境下的任务
        if task_user_info == current_user_info and task_alias == alias:
            target_task_file = task_file
            target_task_info = task_info
            break
    
    if not target_task_info:
        print(f"❌ 未找到别名为 '{alias}' 的任务")
        return False
    
    # 获取任务信息
    pid = target_task_info.get("PID", 0)
    pgid = target_task_info.get("PGID")
    target = target_task_info.get("TARGET", "")
    
    if not target or target == "unknown":
        print(f"❌ 无法获取任务文件路径")
        return False
    
    # 先kill任务（包括所有子进程）
    if isinstance(pid, int) and is_process_running(pid):
        print(f"🛑 正在终止任务 [别名: {alias}, PID: {pid}]", end="")
        if pgid:
            print(f", 进程组: {pgid}")
        else:
            print()
        try:
            # 优先使用进程组 kill（可以终止所有子进程）
            if pgid and hasattr(os, 'killpg'):
                try:
                    os.killpg(pgid, signal.SIGTERM)
                    log_debug(f"使用 killpg 终止进程组 {pgid}")
                except ProcessLookupError:
                    # 进程组不存在，回退到单个进程 kill
                    os.kill(pid, signal.SIGTERM)
                    log_debug(f"进程组不存在，回退到 kill PID {pid}")
                except OSError as e:
                    # 其他错误（如权限问题），回退到单个进程 kill
                    log_debug(f"killpg 失败 ({e})，回退到 kill PID {pid}")
                    os.kill(pid, signal.SIGTERM)
            else:
                # 向后兼容：没有 PGID 或系统不支持 killpg，使用原来的方式
                os.kill(pid, signal.SIGTERM)
                log_debug(f"使用 kill 终止进程 {pid}")
            
            # 等待进程结束
            for _ in range(10):
                if not is_process_running(pid):
                    break
                time.sleep(0.5)
            print("✅ 任务已终止（包括所有子进程）")
        except ProcessLookupError:
            # 进程已经不存在
            print("✅ 任务已终止（进程已不存在）")
        except Exception as e:
            print(f"⚠️  终止任务时出错: {e}")
    
    # 删除任务文件
    if target_task_file:
        target_task_file.unlink(missing_ok=True)
    
    # sleep 3秒
    print("⏳ 等待 3 秒...")
    time.sleep(3)
    
    # 重新启动任务
    print(f"🚀 正在重新启动任务 [别名: {alias}]")
    start_task(target)
    
    return True


def list_tasks_grouped():
    """按用户分组列出任务（表格格式，动态列宽）"""
    # 首先清理当前运行环境下已结束的任务
    current_user_info = get_user_info()
    for task_file in TASK_DIR.glob("*.task"):
        task_info = load_task_file(task_file)
        if task_info:
            task_user_info = task_info.get("USER_INFO", "")
            pid = task_info.get("PID", 0)
            # 只清理当前运行环境下的已结束任务
            if task_user_info == current_user_info and not is_process_running(pid):
                task_file.unlink(missing_ok=True)
    
    # 重新检查是否有任务文件
    task_files = list(TASK_DIR.glob("*.task"))
    if not task_files:
        print("📋 当前后台任务：")
        print("----------------------------------------")
        print("（暂无任务）")
        return
    
    # 按用户信息分组
    user_groups = defaultdict(list)
    
    for task_file in task_files:
        task_info = load_task_file(task_file)
        if not task_info:
            continue
        
        pid = task_info.get("PID", 0)
        user_info = task_info.get("USER_INFO", "local:unknown")
        user_groups[user_info].append((task_file, task_info))
    
    if not user_groups:
        print("📋 当前后台任务：")
        print("----------------------------------------")
        print("（暂无任务）")
        return
    
    print("📋 当前后台任务（按用户分组）：")
    
    # 显示每个用户组的任务
    for user_info in sorted(user_groups.keys()):
        display_name = ""
        if user_info.startswith("local:"):
            username = user_info.split(":", 1)[1]
            display_name = f"local ({username})"
        elif user_info.startswith("docker:"):
            container_name = user_info.split(":", 1)[1]
            display_name = f"docker ({container_name})"
        else:
            display_name = user_info
        
        print()
        print(f"👤 用户: {display_name}")
        
        # 准备表格数据并计算最大宽度
        table_data = []
        max_filename_len = 10  # 最小宽度
        max_alias_len = 4
        max_pid_len = 8
        max_start_time_len = 19
        max_runtime_len = 15
        
        for task_file, task_info in user_groups[user_info]:
            alias = task_info.get("ALIAS", "")
            pid = task_info.get("PID", "unknown")
            start_time = task_info.get("START_TIME", "unknown")
            target = task_info.get("TARGET", "unknown")
            task_user_info = task_info.get("USER_INFO", "")
            
            # 如果别名为空，自动分配一个别名并保存
            if not alias or alias == "":
                # 收集所有任务文件中已使用的别名（包括所有用户组）
                used_aliases = set()
                for user_group_tasks in user_groups.values():
                    for _, ti_inner in user_group_tasks:
                        existing_alias = ti_inner.get("ALIAS", "")
                        if existing_alias:
                            used_aliases.add(existing_alias)
                
                # 找到第一个未使用的别名
                all_aliases = [chr(i) for i in range(ord('a'), ord('z') + 1)]
                for new_alias in all_aliases:
                    if new_alias not in used_aliases:
                        alias = new_alias
                        task_info["ALIAS"] = alias
                        save_task_file(task_file, task_info)
                        break
            
            # 提取文件名
            filename = Path(target).name if target != "unknown" else "unknown"
            
            # 计算运行时间和总秒数（用于排序）
            runtime = format_runtime(start_time)
            runtime_seconds = 0
            if start_time != "unknown":
                try:
                    start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    current_dt = datetime.now()
                    delta = current_dt - start_dt
                    runtime_seconds = int(delta.total_seconds())
                    if runtime_seconds < 0:
                        runtime_seconds = 0
                except Exception:
                    runtime_seconds = 0
            
            is_running = isinstance(pid, int) and is_process_running(pid)
            is_current_env = (task_user_info == current_user_info)
            
            # 根据状态和环境设置颜色和图标
            if is_running and is_current_env:
                color = COLOR_BRIGHT_GREEN
                status_icon = "✅"
            elif is_running:
                color = COLOR_LIGHT_GREEN
                status_icon = "✅"
            else:
                color = COLOR_BLACK
                status_icon = "⏹️"
            
            # 更新最大宽度
            max_filename_len = max(max_filename_len, len(filename))
            max_alias_len = max(max_alias_len, len(str(alias)))
            max_pid_len = max(max_pid_len, len(str(pid)))
            max_start_time_len = max(max_start_time_len, len(str(start_time)))
            max_runtime_len = max(max_runtime_len, len(runtime))
            
            table_data.append({
                'filename': filename,
                'alias': alias,
                'status_icon': status_icon,
                'color': color,
                'pid': pid,
                'start_time': start_time,
                'runtime': runtime,
                'runtime_seconds': runtime_seconds  # 用于排序
            })
        
        # 按运行时间排序（降序，运行时间最长的在前）
        table_data.sort(key=lambda x: x['runtime_seconds'], reverse=True)
        
        # 计算总宽度
        total_width = max_filename_len + max_alias_len + max_pid_len + max_start_time_len + max_runtime_len + 20  # 20为列间距和状态列
        separator = "-" * total_width
        
        print(separator)
        
        # 打印表头
        header = (f"{'文件名':<{max_filename_len}} "
                 f"{'别名':<{max_alias_len}} "
                 f"{'状态':<4} "
                 f"{'PID':<{max_pid_len}} "
                 f"{'启动时间':<{max_start_time_len}} "
                 f"{'运行时间':<{max_runtime_len}}")
        print(header)
        print(separator)
        
        # 表格内容
        for row in table_data:
            status_display = f"{row['status_icon']}"
            line = (f"{row['filename']:<{max_filename_len}} "
                   f"{row['alias']:<{max_alias_len}} "
                   f"{status_display:<4} "
                   f"{row['pid']:<{max_pid_len}} "
                   f"{row['start_time']:<{max_start_time_len}} "
                   f"{row['runtime']:<{max_runtime_len}}")
            print(f"{row['color']}{line}{COLOR_RESET}")
        
        print(separator)


def save_command_history(target: str):
    """保存命令历史（最多保留50条）"""
    try:
        # 加载现有历史
        history = []
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                history = []
        
        # 添加新记录
        target_path = Path(target).resolve()
        new_entry = {
            'target': str(target_path),
            'workdir': str(target_path.parent),
            'filename': target_path.name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 避免重复（如果路径相同，移除旧记录）
        history = [h for h in history if h.get('target') != new_entry['target']]
        
        # 添加到开头
        history.insert(0, new_entry)
        
        # 只保留最近50条
        history = history[:MAX_HISTORY]
        
        # 保存
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        # 确保权限
        if os.geteuid() == 0:
            try:
                os.chmod(HISTORY_FILE, 0o666)
            except Exception:
                pass
    except Exception:
        # 历史记录失败不影响主功能
        pass


def show_command_history():
    """显示命令历史（最近50条）"""
    try:
        if not HISTORY_FILE.exists():
            print("📜 命令历史：")
            print("----------------------------------------")
            print("（暂无历史记录）")
            return
        
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        if not history:
            print("📜 命令历史：")
            print("----------------------------------------")
            print("（暂无历史记录）")
            return
        
        print("📜 命令历史（最近50条）：")
        
        # 计算最大宽度
        max_filename_len = 10
        max_workdir_len = 20
        max_timestamp_len = 19
        
        for entry in history:
            filename = entry.get('filename', 'unknown')
            workdir = entry.get('workdir', 'unknown')
            timestamp = entry.get('timestamp', 'unknown')
            
            max_filename_len = max(max_filename_len, len(filename))
            max_workdir_len = max(max_workdir_len, len(workdir))
            max_timestamp_len = max(max_timestamp_len, len(timestamp))
        
        total_width = max_filename_len + max_workdir_len + max_timestamp_len + 10
        separator = "-" * total_width
        
        print(separator)
        
        # 表头
        header = (f"{'文件名':<{max_filename_len}} "
                 f"{'目录':<{max_workdir_len}} "
                 f"{'时间':<{max_timestamp_len}}")
        print(header)
        print(separator)
        
        # 内容
        for entry in history:
            filename = entry.get('filename', 'unknown')
            workdir = entry.get('workdir', 'unknown')
            timestamp = entry.get('timestamp', 'unknown')
            
            line = (f"{filename:<{max_filename_len}} "
                   f"{workdir:<{max_workdir_len}} "
                   f"{timestamp:<{max_timestamp_len}}")
            print(line)
        
        print(separator)
        
    except Exception as e:
        print(f"❌ 读取历史记录失败: {e}")


def cleanup_old_logs(workdir: Path, basename: str, keep_count: int = 3):
    """清理旧日志文件，只保留最新的几个"""
    try:
        # 查找所有匹配的日志文件：log_*_{basename}.log
        log_pattern = f"log_*_{basename}.log"
        log_files = list(workdir.glob(log_pattern))
        
        if len(log_files) <= keep_count:
            return
        
        # 按修改时间排序（最新的在前）
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # 删除超出保留数量的旧日志
        files_to_delete = log_files[keep_count:]
        for old_log in files_to_delete:
            try:
                old_log.unlink()
                log_debug(f"已删除旧日志: {old_log.name}")
            except Exception as e:
                log_debug(f"删除旧日志失败 {old_log.name}: {e}")
    except Exception as e:
        log_debug(f"清理旧日志时出错: {e}")


def start_task(target: str, extra_args: List[str] = None):
    """启动任务"""
    if extra_args is None:
        extra_args = []
    
    target_path = Path(target)
    if not target_path.exists():
        print(f"❌ 找不到文件: {target}")
        sys.exit(1)
    
    # 检查路径冲突
    if not check_path_conflict(target):
        sys.exit(1)
    
    # 保存命令历史
    save_command_history(target)
    
    # 获取绝对路径与目录
    abs_target = target_path.resolve()
    workdir = abs_target.parent
    basename = abs_target.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logfile = workdir / f"log_{timestamp}_{basename}.log"
    
    log_debug(f"ABS_TARGET={abs_target}")
    log_debug(f"WORKDIR={workdir}")
    log_debug(f"LOGFILE={logfile}")
    log_debug(f"EXTRA_ARGS={extra_args}")
    
    # 判断执行方式
    if abs_target.suffix == ".py":
        cmd = ["python3", "-u", str(abs_target)]
    elif abs_target.suffix == ".sh":
        cmd = ["bash", str(abs_target)]
    else:
        cmd = ["bash", str(abs_target)]
    
    # 追加额外参数
    if extra_args:
        cmd.extend(extra_args)
    
    print(f"🚀 正在后台运行: {' '.join(cmd)}")
    print(f"📜 日志文件: {logfile}")
    print("----------------------------------------")
    
    # 进入脚本所在目录执行，确保相对路径和日志正确
    try:
        with open(logfile, 'w', encoding='utf-8') as log_f:
            process = subprocess.Popen(
                cmd,
                cwd=str(workdir),
                stdout=log_f,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
        
        pid = process.pid
        log_debug(f"spawned PID: {pid}")
        
        # 等待一下确保进程启动
        time.sleep(1)
        
        # 检查进程是否还在运行
        if not is_process_running(pid):
            print(f"❌ 启动失败，进程已退出")
            sys.exit(1)
        
        # 获取进程组 ID（PGID）
        # 如果使用了 os.setsid()，进程组 ID 就是进程 ID
        # 但为了兼容性，我们使用 os.getpgid() 获取
        pgid = None
        try:
            if hasattr(os, 'getpgid'):
                pgid = os.getpgid(pid)
            else:
                # 如果没有 getpgid，假设 PGID 就是 PID（使用 setsid 时的情况）
                pgid = pid
        except Exception:
            # 如果获取失败，使用 PID 作为 PGID
            pgid = pid
        
        log_debug(f"PGID: {pgid}")
        
        # 清理旧日志（保留最新的3个，包括刚创建的）
        cleanup_old_logs(workdir, basename, keep_count=3)
        
        # 分配别名和获取用户信息
        alias = assign_alias()
        user_info = get_user_info()
        
        task_file = TASK_DIR / f"{pid}.task"
        task_info = {
            "PID": pid,
            "PGID": pgid,  # 保存进程组 ID
            "TARGET": str(abs_target),
            "WORKDIR": str(workdir),
            "LOGFILE": str(logfile),
            "START_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ALIAS": alias,
            "USER_INFO": user_info
        }
        
        save_task_file(task_file, task_info)
        
        print(f"✅ 已在后台运行（PID: {pid}, 别名: {alias}）")
        print("🔍 实时输出：")
        
        # 实时显示日志（类似tail -f）
        try:
            # 等待日志文件生成
            for _ in range(10):
                if logfile.exists():
                    break
                time.sleep(0.5)
            
            if logfile.exists():
                # 先显示已有内容
                try:
                    with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if content:
                            print(content, end='', flush=True)
                except Exception:
                    pass
                
                # 然后跟踪新内容
                try:
                    with open(logfile, 'r', encoding='utf-8', errors='ignore') as f:
                        # 移动到文件末尾
                        f.seek(0, 2)
                        
                        while True:
                            line = f.readline()
                            if line:
                                print(line, end='', flush=True)
                            else:
                                if not is_process_running(pid):
                                    break
                                time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\n(已停止跟踪日志，任务仍在后台运行)")
            else:
                print("(日志尚未生成)")
        except Exception as e:
            if DEBUG_MODE:
                print(f"日志跟踪错误: {e}", file=sys.stderr)
    
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        if DEBUG_MODE:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """主函数"""
    global DEBUG_MODE
    
    parser = argparse.ArgumentParser(
        description="后台任务管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
用法示例:
  %(prog)s                   查看所有运行中的任务（默认）
  %(prog)s script.py         启动Python脚本
  %(prog)s script.sh         启动Shell脚本
  %(prog)s ls                查看所有运行中的任务
  %(prog)s kill a            终止别名为'a'的任务
  %(prog)s log a             查看别名为'a'的任务日志
  %(prog)s l a               查看别名为'a'的任务日志（log的简写）
  %(prog)s r a               重启别名为'a'的任务
  %(prog)s watch a           查看别名为'a'的任务详情和最新10行日志
  %(prog)s w a               查看别名为'a'的任务详情和最新10行日志（watch的简写）
  eval $(%(prog)s func)      加载rcd函数（只需执行一次）
  rcd a                      直接跳转到别名为'a'的任务目录（需先执行上一步）
  eval $(%(prog)s cd a)      直接跳转到别名为'a'的任务目录
  eval $(%(prog)s c a)        直接跳转到别名为'a'的任务目录（cd的简写）
  %(prog)s a                 显示历史命令（最近50条）
  %(prog)s init              初始化 .bashrc，添加常用别名
  %(prog)s debug script.py   调试模式启动脚本
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        help='命令: 脚本文件路径, ls, kill, log, 或 debug'
    )
    parser.add_argument(
        'arg',
        nargs='*',
        help='参数: kill/log时提供别名, debug时提供脚本文件, 或脚本的额外参数'
    )
    
    args = parser.parse_args()
    
    ensure_permissions()
    
    # 如果没有提供命令，默认执行 ls
    if not args.command:
        list_tasks_grouped()
        sys.exit(0)
    
    # 处理 kill 命令
    if args.command == "kill":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r kill <别名>")
            sys.exit(1)
        success = kill_by_alias(args.arg[0])
        sys.exit(0 if success else 1)
    
    # 处理 log 命令（兼容旧用法）
    if args.command == "log":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r log <别名>")
            sys.exit(1)
        success = log_by_alias(args.arg[0])
        sys.exit(0 if success else 1)
    
    # 处理 l 命令（新用法，代替 log）
    if args.command == "l":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r l <别名>")
            sys.exit(1)
        success = log_by_alias(args.arg[0])
        sys.exit(0 if success else 1)
    
    # 处理 r 命令（重启任务）
    if args.command == "r":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r r <别名>")
            sys.exit(1)
        success = restart_by_alias(args.arg[0])
        sys.exit(0 if success else 1)
    
    # 处理 watch 命令（查看任务详情和最新日志）
    if args.command == "watch":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r watch <别名>")
            sys.exit(1)
        success = watch_by_alias(args.arg[0])
        sys.exit(0 if success else 1)
    
    # 处理 w 命令（watch的简写）
    if args.command == "w":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r w <别名>")
            sys.exit(1)
        success = watch_by_alias(args.arg[0])
        sys.exit(0 if success else 1)
    
    # 处理 func 命令（输出 shell 函数定义）
    if args.command == "func":
        output_shell_function()
        sys.exit(0)
    
    # 处理 init 命令（初始化 .bashrc）
    if args.command == "init":
        success = init_bashrc()
        sys.exit(0 if success else 1)
    
    # 处理 cd 命令（跳转到任务目录）
    if args.command == "cd":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r cd <别名>", file=sys.stderr)
            print("💡 提示:", file=sys.stderr)
            print("   方法1: eval $(r func) 后使用 rcd <别名> 直接跳转", file=sys.stderr)
            print("   方法2: eval $(r cd <别名>) 直接跳转", file=sys.stderr)
            print("   方法3: cd $(R_PATH_ONLY=1 r cd <别名>) 获取路径后跳转", file=sys.stderr)
            sys.exit(1)
        # 检查是否设置了 R_PATH_ONLY 环境变量（只输出路径）
        path_only = os.environ.get("R_PATH_ONLY", "").lower() in ("1", "true", "yes")
        success = cd_by_alias(args.arg[0], path_only=path_only)
        sys.exit(0 if success else 1)
    
    # 处理 c 命令（cd的简写）
    if args.command == "c":
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r c <别名>", file=sys.stderr)
            print("💡 提示:", file=sys.stderr)
            print("   方法1: eval $(r func) 后使用 rcd <别名> 直接跳转", file=sys.stderr)
            print("   方法2: eval $(r c <别名>) 直接跳转", file=sys.stderr)
            print("   方法3: cd $(R_PATH_ONLY=1 r c <别名>) 获取路径后跳转", file=sys.stderr)
            sys.exit(1)
        # 检查是否设置了 R_PATH_ONLY 环境变量（只输出路径）
        path_only = os.environ.get("R_PATH_ONLY", "").lower() in ("1", "true", "yes")
        success = cd_by_alias(args.arg[0], path_only=path_only)
        sys.exit(0 if success else 1)
    
    # 处理 a 命令（显示历史）
    if args.command == "a":
        show_command_history()
        sys.exit(0)
    
    # 处理 ls 命令
    if args.command == "ls":
        list_tasks_grouped()
        sys.exit(0)
    
    # 处理 debug 命令
    if args.command == "debug":
        DEBUG_MODE = True
        print("⚙️ Debug 模式已启用")
        if not args.arg or len(args.arg) == 0:
            print("❌ 用法: r debug <脚本文件> [额外参数...]")
            sys.exit(1)
        # args.arg[0] 是脚本文件，args.arg[1:] 是额外参数
        extra_args = args.arg[1:] if len(args.arg) > 1 else []
        start_task(args.arg[0], extra_args=extra_args)
        sys.exit(0)
    
    # 处理启动任务（将命令视为脚本文件路径）
    # args.arg 是额外参数列表
    extra_args = args.arg if args.arg else []
    start_task(args.command, extra_args=extra_args)


if __name__ == "__main__":
    main()

