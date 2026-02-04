# FN-Scripts

一些实用的NAS网络工具脚本集合。

## 脚本说明

### checkgateway
网关连通性检测脚本。当检测到网关无法访问时，自动重启NAS系统。

**功能：**
- Ping指定网关IP
- 自动重启NAS（可选sudo模式）
- 日志记录

**配置：**
编辑 `checkgateway.py` 中的配置区域：
```python
GATEWAY_IP = "192.168.9.1"  # 修改为你的网关IP
SUDO_REBOOT = True           # 是否使用sudo
```

**运行：**
```bash
python checkgateway.py
```

---

### iptest
IPv6地址监控脚本。获取本机IPv6地址并检测变更，变更时通过邮件通知。

**功能：**
- 获取本机IPv6地址
- 对比历史IP地址
- IP变更时发送邮件通知

**配置：**
编辑 `iptest.py` 中的邮件配置：
```python
mail_host = "smtp.qq.com"           # SMTP服务器
mail_user = "your_email@example.com"    # 你的邮箱
mail_pass = "your_smtp_password"        # SMTP授权码
sender = 'your_email@example.com'       # 发件人
receivers = ['recipient@example.com']   # 收件人
```

**运行：**
```bash
python iptest.py
```

---

## 定时任务配置 (Cron)

使用 cron 设置定时任务，自动运行脚本。

### 1. 编辑 crontab
```bash
crontab -e
```

### 2. 添加定时任务

**iptest - 每小时检查一次IP：**
```bash
0 * * * * cd /path/to/iptest && python3 iptest.py
```

**checkgateway - 每5分钟检测网关：**
```bash
*/5 * * * * cd /path/to/checkgateway && python3 checkgateway.py
```

### 3. 常用时间格式
| 格式 | 说明 |
|------|------|
| `* * * * *` | 每分钟 |
| `*/5 * * * *` | 每5分钟 |
| `0 * * * *` | 每小时 |
| `0 0 * * *` | 每天凌晨 |
| `0 0 * * 0` | 每周日 |

### 4. 查看定时任务
```bash
crontab -l
```

### 5. 重启 cron 服务
```bash
# Debian/Ubuntu
sudo service cron restart

# CentOS/RHEL
sudo systemctl restart crond
```

---

## 注意事项

1. `iptest.py` 和 `checkgateway.py` 中的敏感配置需要根据实际环境修改
2. 建议定期检查IP变更通知，确保网络正常运行
