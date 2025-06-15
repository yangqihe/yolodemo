import socket

# 配置服务端地址
server_ip = "192.168.1.197"   # 替换为目标服务端 IP
server_port = 1024           # 替换为目标服务端端口

# 创建 UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 要发送的数据
message = "Hello UDP Server".encode()

# 发送数据到服务端
client_socket.sendto(message, (server_ip, server_port))

# 接收服务端响应（可选）
response, addr = client_socket.recvfrom(1024)
print(f"收到服务端({addr})响应: {response.decode()}")

client_socket.close()
