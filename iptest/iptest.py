# python version 3.7
# 融合脚本：先检查网关，如果失败则重启；网关通后执行 IP 检测和邮件通知

import socket
import sys
import subprocess
import os
import datetime
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from urllib.request import urlopen

# --- 网关检查配置 ---
GATEWAY_IP = "192.168.9.1"  # <--- 请修改为您网络的网关IP地址
PING_COUNT = 5              # 尝试ping的次数
SUDO_REBOOT = True          # 是否使用sudo执行reboot命令
# -------------------

# --- IP检测和邮件配置 ---
LOG_DEBUG_EN = 1  # 1-开启调试打印， 0-关闭

# 第三方 SMTP 服务
mail_host = "smtp.qq.com"           # SMTP服务器
mail_user = "your_email@example.com"        # 用户名
mail_pass = "your_smtp_password"      # 授权密码，非登录密码

sender = 'your_email@example.com'         # 发件人邮箱(最好写全, 不然会失败)
receivers = ['recipient@example.com']     # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

title = '[NAS]ip地址变更'         # 邮件主题
content = ''                       # 邮件内容
# -------------------

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "gateway_check.log")  # 日志文件路径


def log_message(message):
    """记录带时间戳的日志消息"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + '\n')


def Log(fmt):
    if LOG_DEBUG_EN:
        print(fmt)


# 发送email
def sendEmail():
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = "{}".format(sender)
    message['To'] = ",".join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)


# 获取当前时间并格式化
def getLastDate():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# 使用Phy自带库获取当前IP地址并切片 在windows好用，但在linux不行
def getipv6():
    host_ipv6 = []
    host_ipv4 = []
    ips = socket.getaddrinfo(socket.gethostname(), 80)
    for ip in ips:
        Log(ip)
        if ip[0] == 2:
            host_ipv4.append(ip[4][0])

        # 2408 中国联通
        # 2409 中国移动
        # 240e 中国电信
        if ip[0] == 23 and ip[4][0].startswith('24'):
            host_ipv6.append(ip[4][0])
    return host_ipv6, host_ipv4


# 使用网络服务api接口获取当前IP地址并切片 ，windows和linux都好用
def getipv6_url():
    url_ipv6 = []
    rets = subprocess.getoutput('curl http://ifconfig.io')
    ret_list = rets.split('\n')
    Log("last list=%s" % ret_list[-1])
    if ret_list[-1].startswith('24'):
        url_ipv6.append(ret_list[-1])
    return url_ipv6


def ping_host(host, count=1):
    """
    尝试ping指定主机
    :param host: 目标主机IP或域名
    :param count: ping的包数量
    :return: bool, True表示成功，False表示失败
    """
    try:
        # 构建ping命令
        cmd = ["ping", "-c", str(count), host]

        # 执行命令并捕获结果
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,  # 丢弃标准输出
            stderr=subprocess.DEVNULL,  # 丢弃错误输出
            timeout=10  # 设置超时时间
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


def check_gateway():
    """检查网关是否可达，不可达则重启系统"""
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


def check_ip_and_notify():
    """检查IP地址变化并发送邮件通知"""
    # 获取IPv6地址
    now_ip6 = getipv6_url()

    Log("ipv6=%s" % now_ip6)

    if now_ip6 == []:
        print("未获取到ip6地址,退出脚本.\r\n")
        return  # 退出IP检测部分，但不影响脚本整体

    # 获取IP记录文件路径
    filename = os.path.join(SCRIPT_DIR, 'myip6.txt')

    Log("filename=%s" % filename)

    if os.path.exists(filename):
        with open(filename) as f:  # 默认模式为'r'，只读模式
            ip6_old = f.read()  # 读取文件全部内容
            Log("ip6_old = [%s]\r\n" % ip6_old)
    else:
        print("<%s>不存在.\r\n" % filename)
        ip6_old = ''

    with open(filename, 'w') as f:  # 如果filename不存在会自动创建
        f.writelines(now_ip6[0])

    if now_ip6[0] == ip6_old:
        print("ip6没有变更 = [%s]" % ip6_old)
    else:
        global content
        content = f"IPv6 Address: [{now_ip6[0]}]"
        sendEmail()


def main():
    """主函数：先检查网关，通过后执行IP检测"""
    # 第一步：检查网关
    check_gateway()

    # 第二步：网关检查通过，执行IP检测和邮件通知
    check_ip_and_notify()


if __name__ == "__main__":
    main()
