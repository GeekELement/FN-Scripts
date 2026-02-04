import subprocess
import sys
import time
import os
from datetime import datetime

# --- 配置区域 ---
GATEWAY_IP = "192.168.9.1"  # <--- 请修改为您网络的网关IP地址
PING_COUNT = 3              # 尝试ping的次数
SUDO_REBOOT = True          # 是否使用sudo执行reboot命令 (推荐设置为 True)
# -----------------

# 获取脚本所在目录，日志文件保存在同级目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "gateway_check.log")  # 日志文件路径


def log_message(message):
    """记录带时间戳的日志消息"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')


def ping_host(host, count=1):
    """
    尝试ping指定主机
    :param host: 目标主机IP或域名
    :param count: ping的包数量
    :return: bool, True表示成功，False表示失败
    """
    try:
        # 构建ping命令
        # -c count (Linux), -n count (Windows)
        # 我们假设在类Unix系统（如Linux）上运行NAS
        cmd = ["ping", "-c", str(count), host]
        
        # 执行命令并捕获结果
        # timeout参数确保命令不会无限期挂起
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,  # 丢弃标准输出
            stderr=subprocess.DEVNULL,  # 丢弃错误输出
            timeout=10  # 设置超时时间，例如10秒
        )
        # 如果返回码为0，则认为ping成功
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        log_message(f"WARNING: Ping command timed out for {host}.")
        return False
    except FileNotFoundError:
        log_message("FATAL ERROR: 'ping' command not found.")
        sys.exit(1)
    except Exception as e:
        log_message(f"FATAL ERROR during ping: {e}")
        sys.exit(1)


def main():
    """主函数"""
    if not ping_host(GATEWAY_IP, PING_COUNT):
        # ping失败，记录日志并准备重启
        log_message(f"ERROR: Failed to ping gateway {GATEWAY_IP} after {PING_COUNT} attempts. Rebooting now...")
        
        reboot_cmd = []
        if SUDO_REBOOT:
            # 检查sudo命令是否存在
            try:
                subprocess.run(["which", "sudo"], check=True, stdout=subprocess.PIPE)
            except subprocess.CalledProcessError:
                log_message("FATAL ERROR: 'sudo' command not found. Cannot proceed with reboot.")
                sys.exit(1)
            
            reboot_cmd = ["sudo", "-n", "/sbin/reboot"]
        else:
            # 直接使用reboot命令 (脚本本身需以root权限运行)
            reboot_cmd = ["/sbin/reboot"]

        try:
            # 执行重启命令
            subprocess.run(reboot_cmd, check=True)
            log_message("Reboot command issued successfully.")
        except subprocess.CalledProcessError as e:
            log_message(f"FATAL ERROR: Failed to execute reboot command. Command: {' '.join(reboot_cmd)}, Error: {e}")
            sys.exit(1)
        except FileNotFoundError:
            log_message(f"FATAL ERROR: Reboot binary not found at {' '.join(reboot_cmd)}. Check path and permissions.")
            sys.exit(1)
    else:
        log_message(f"Success: Gateway {GATEWAY_IP} is reachable.")


if __name__ == "__main__":
    main()