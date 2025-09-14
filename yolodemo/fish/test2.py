# check_ports.py
import socket

ip = "169.254.121.10"
ports = [554, 8554, 10554]

for port in ports:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((ip, port))
        print(f"[OK] 端口 {port} 打开")
    except Exception as e:
        print(f"[FAIL] 端口 {port} 不通 ({e})")
    finally:
        sock.close()
