#!/bin/bash

# fakeip_clear.sh
# 用于清除 fakeip.sh 设置的环境变量代理（仅当前终端会话有效）

echo "正在关闭 Linux 临时代理设置..."

# 清除所有相关的代理环境变量
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY
unset all_proxy
unset ALL_PROXY
unset no_proxy
unset NO_PROXY

# 如果之前通过 git config 设置过代理，也一并清除（全局配置）
git config --global --unset http.proxy  2>/dev/null || true
git config --global --unset https.proxy 2>/dev/null || true

echo "----------------------------------------"
echo "✅ 代理已关闭（当前终端）"
echo ""
echo "当前代理状态检查："
echo "http_proxy  = ${http_proxy:-未设置}"
echo "https_proxy = ${https_proxy:-未设置}"
echo "all_proxy   = ${all_proxy:-未设置}"
echo ""
echo "验证网络（直连测试）："
echo "  curl -s --connect-timeout 5 http://httpbin.org/ip"
echo "  ping -c 3 8.8.8.8"
echo ""
echo "如果需要重新启用代理，请再次执行："
echo "  source fakeip.sh"
echo "----------------------------------------"