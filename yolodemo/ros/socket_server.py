import socket
import threading
import time
from datetime import datetime
import pymysql

HOST = '0.0.0.0'
PORT = 5000
DB_CONFIG = {
    'host': '172.17.190.165',
    'user': 'yangqihe',
    'password': '3621676Ab!',
    'database': 'test',
    'port': 3306,
    'autocommit': True
}

sleep_time = 5

active_connections = []
db_conn = None
db_cursor = None

def init_db_connection():
    global db_conn, db_cursor
    try:
        db_conn = pymysql.connect(**DB_CONFIG)
        db_cursor = db_conn.cursor()
        print(f"[{now()}] ✅ 数据库连接成功")
    except Exception as e:
        print(f"[{now()}] ❗ 数据库连接失败: {e}")

def get_record_count():
    global db_conn, db_cursor
    try:
        db_cursor.execute("SELECT COUNT(*) FROM employees")
        return db_cursor.fetchone()[0]
    except (pymysql.err.OperationalError, pymysql.err.InterfaceError):
        print(f"[{now()}] ⚠️ 连接失效，重连数据库...")
        init_db_connection()
        return 0
    except Exception as e:
        print(f"[{now()}] ❗ 查询失败: {e}")
        return 0

def handle_client(conn, addr):
    print(f"[{now()}] 🔌 客户端连接: {addr}")
    conn.settimeout(10)
    active_connections.append(conn)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode('utf-8').strip()
            if msg.upper() != 'PING':
                print(f"[{now()}] 📨 来自 {addr}: {msg}")

            if msg.upper() == 'PING':
                conn.sendall(now().encode('utf-8'))

            elif msg.startswith('CMD:'):
                command = msg[4:]
                if command == 'READ_SENSOR':
                    conn.sendall(f"[{now()}] RESP:SENSOR=25.5\n".encode('utf-8'))
                else:
                    conn.sendall(f"[{now()}] RESP:UNKNOWN_COMMAND {command}\n".encode('utf-8'))

            elif msg.lower() == 'quit':
                conn.sendall(b"RESP:BYE\n")
                break

            else:
                conn.sendall(b"RESP:INVALID_FORMAT\n")

    except socket.timeout:
        print(f"[{now()}] ⚠️ 客户端空闲超时断开: {addr}")
    except Exception as e:
        print(f"[{now()}] ❗ 客户端异常断开: {addr} - {e}")
    finally:
        conn.close()
        if conn in active_connections:
            active_connections.remove(conn)
        print(f"[{now()}] ❎ 客户端断开: {addr}")

def monitor_database():
    init_db_connection()
    while True:
        if not active_connections:
            print(f"[{now()}] 💤 无客户端连接，暂停查询")
            time.sleep(sleep_time)
            continue

        start = time.time()
        count = get_record_count()
        print(f"[{now()}] 📊 当前记录数: {count}")

        if count > 10:
            print(f"[{now()}] 🚨 记录超过 10，向所有客户端发送 CMD:ACTION")
            for conn in active_connections[:]:
                try:
                    conn.sendall(b"CMD:ACTION\n")
                except Exception as e:
                    print(f"[{now()}] ❗ 发送失败，移除连接: {e}")
                    active_connections.remove(conn)

        elapsed = time.time() - start
        time.sleep(max(0, sleep_time - elapsed))  # 控制周期

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[{now()}] 🚀 服务器启动监听 {HOST}:{PORT}")

    threading.Thread(target=monitor_database, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
