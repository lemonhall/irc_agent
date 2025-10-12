# IRC 服务器检查和配置脚本

echo "=== 检查 ngircd 服务状态 ==="
sudo systemctl status ngircd

echo -e "\n=== 检查 IRC 端口是否在监听 ==="
sudo netstat -tlnp | grep 6667 || sudo ss -tlnp | grep 6667

echo -e "\n=== 检查防火墙状态 (ufw) ==="
sudo ufw status

echo -e "\n=== 检查防火墙状态 (iptables) ==="
sudo iptables -L -n | grep 6667

echo -e "\n=== 服务器公网 IP ==="
curl -s ifconfig.me
echo ""

echo -e "\n=== 如果需要开放端口 ==="
echo "方案 1 (ufw):"
echo "  sudo ufw allow 6667/tcp"
echo ""
echo "方案 2 (iptables):"
echo "  sudo iptables -A INPUT -p tcp --dport 6667 -j ACCEPT"
echo "  sudo iptables-save"
