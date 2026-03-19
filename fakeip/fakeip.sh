#!/bin/bash

# 设置代理变量（与 Clash 设置匹配）
export CLASH_IP="192.168.9.102"
export PROXY_PORT_HTTP="7899"      # HTTP(S) 代理端口
export PROXY_PORT_SOCKS5="7898"    # SOCKS5 代理端口
export PROXY_PORT_MIXED="7897"     # 混合代理端口（可选）

# 设置 HTTP/HTTPS 代理
export http_proxy="http://$CLASH_IP:$PROXY_PORT_HTTP"
export https_proxy="http://$CLASH_IP:$PROXY_PORT_HTTP"
export HTTP_PROXY="http://$CLASH_IP:$PROXY_PORT_HTTP"
export HTTPS_PROXY="http://$CLASH_IP:$PROXY_PORT_HTTP"

# 设置 SOCKS5 代理
export all_proxy="socks5://$CLASH_IP:$PROXY_PORT_SOCKS5"
export ALL_PROXY="socks5://$CLASH_IP:$PROXY_PORT_SOCKS5"

# 可选：设置混合代理（如果脚本支持）
# export http_proxy="http://$CLASH_IP:$PROXY_PORT_MIXED"
# export https_proxy="http://$CLASH_IP:$PROXY_PORT_MIXED"

# 输出当前代理设置
echo "✅ Linux 临时代理已开启！"
echo "----------------------------------------"
echo "代理地址: $CLASH_IP:$PROXY_PORT_HTTP"
echo "HTTP 代理: http://$CLASH_IP:$PROXY_PORT_HTTP"
echo "HTTPS 代理: http://$CLASH_IP:$PROXY_PORT_HTTP"
echo "SOCKS5 代理: socks5://$CLASH_IP:$PROXY_PORT_SOCKS5"
echo "----------------------------------------"
echo "📌 注意：此代理设置是临时的，仅对："
echo "1. 当前终端会话"
echo "2. 从此终端启动的程序"
echo "3. 重启后自动失效"
echo "----------------------------------------"
echo "🧪 验证代理是否生效:"
echo "  curl -s --connect-timeout 5 http://httpbin.org/ip"
echo ""
echo "🔧 关闭代理（当前终端内）:"
echo "  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY"
echo "  git config --global --unset http.proxy"
echo "  git config --global --unset https.proxy"