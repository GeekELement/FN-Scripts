# python version 3.7
# 用python内置库稳定获取本机ipv6
# ipv6一般有多个，随便选一个就可以。一般就list里面第一个即可。
# 如果有多线运营商可以根据 不同前缀获取指定运营商的ipv6，不在意的话就用24开头确定ipv6
# 2408 中国联通
# 2409 中国移动
# 240e 中国电信
import socket
import sys
import subprocess

from urllib.request import urlopen

import os
import datetime

import smtplib
from email.header import Header
from email.mime.text import MIMEText

LOG_DEBUG_EN = 1 # 1-开启调试打印， 0-关闭



# 第三方 SMTP 服务
mail_host = "smtp.qq.com"           # SMTP服务器
mail_user = "your_email@example.com"  		# 用户名
mail_pass = "your_smtp_password"      # 授权密码，非登录密码

sender = 'your_email@example.com'    		# 发件人邮箱(最好写全, 不然会失败)
receivers = ['recipient@example.com']  	# 接收邮件，可设置为你的QQ邮箱或者其他邮箱

title = '[NAS]ip地址变更'         # 邮件主题
content = ''                       # 邮件内容

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
    host_ipv6=[]
    host_ipv4=[]
    ips=socket.getaddrinfo(socket.gethostname(),80)
    # print(ips)
    for ip in ips:
        Log(ip)
        # print("\r\n")
        # if ip[0][0].startswith('INET:'):
        #     print("ipv4地址\r\n")

        # if ip[0][0].startswith('INET6:'):
        #     print("ipv6地址\r\n")
        # if 'INET6:' in ip[0][0]:
        #     print("ipv6地址\r\n")

        if ip[0] == 2:
            host_ipv4.append(ip[4][0])

        #2408 中国联通
        #2409 中国移动
        #240e 中国电信
        if ip[0] == 23 and ip[4][0].startswith('24'):
            # print(ip)
            host_ipv6.append(ip[4][0])
    return host_ipv6,host_ipv4

# 使用网络服务api接口获取当前IP地址并切片 ，windows和linux都好用
def getipv6_url():
    url_ipv6=[]
    rets = subprocess.getoutput('curl http://ifconfig.io')
    # print("retult = " + rets + "\r\n")
    ret_list = rets.split('\n')
    # Log("list1=%s" %ret_list)
    Log("last list=%s" %ret_list[-1])
    if ret_list[-1].startswith('24'):
        url_ipv6.append(ret_list[-1])
    return url_ipv6

# now_ip6,now_ip4=getipv6()
now_ip6 = getipv6_url();

Log("ipv6=%s" %now_ip6)
# Log("ipv4=%s" %now_ip4)

if now_ip6 == []:
    print("未获取到ip6地址,退出脚本.\r\n")
    sys.exit()  # 退出当前程序，但不重启shell

# filename = 'myip6.txt'
# 获取当前脚本的路径
# script_dir = os.path.dirname(os.path.realpath(__file__))
# print(f"当前脚本所在路径: {script_dir}")

# 获取绝对路径 (在群晖Nas上运行时发现文件并不是创建在脚本所在目录，故改用绝对路径)
filename = os.path.dirname(os.path.realpath(__file__)) + '/' + 'myip6.txt'

Log("filename=%s" %filename)

if os.path.exists(filename):
    with open(filename) as f: # 默认模式为‘r’，只读模式
        ip6_old = f.read() # 读取文件全部内容
        Log("ip6_old = [%s]\r\n" %ip6_old)
else:
    print("<%s>不存在.\r\n" %filename)
    ip6_old = ''

with open(filename,'w') as f: # 如果filename不存在会自动创建， 'w'表示写数据，写之前会清空文件中的原有数据！
    f.writelines(now_ip6[0])

if now_ip6[0] == ip6_old:
    print("ip6没有变更 = [%s]" %ip6_old)
    sys.exit()  # 退出当前程序，但不重启shell
else:
    content = f"IPv6 Address: [{now_ip6[0]}]"
    sendEmail()

# print("end")