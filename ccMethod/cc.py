import socket

# 获取计算机的主机名
host_name = socket.gethostname()

# 通过主机名获取以太网IP地址
ethernet_ip = socket.gethostbyname(host_name)

print(f"以太网IP地址: {ethernet_ip}")
