import socket
import threading
import pymysql
import json

db_config = {
    "host": "172.17.190.165",
    "user": "yangqihe",
    "password": "3621676Ab!",
    "database": "myDB",
    "port": 3306
}

def fetch_station_data():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM my_station ORDER BY station_order")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

def send_json(conn, obj):
    message = json.dumps(obj, ensure_ascii=False) + "\n"
    conn.sendall(message.encode('utf-8'))

import time

def handle_client(conn, addr):
    print(f"✅ 客户端连接: {addr}")
    try:
        # 发送站点列表
        station_data = fetch_station_data()
        send_json(conn, {
            "type": "station_list",
            "data": station_data,
            "msg": "初始化站点数据",
            "success": True,
            "current_station_index":0
        })

        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            print(f"📥 收到指令: {msg}")

            if msg.startswith("cmd:"):
                index = msg.split(":")[1]

                # 立即回一个 ack
                send_json(conn, {
                    "type": "cmd_ack",
                    "data": {"station": index},
                    "msg": f"收到跳转指令：{index}",
                    "success": True
                })

                # 5 秒后模拟到达
                def simulate_arrival():
                    time.sleep(5)
                    try:
                        send_json(conn, {
                            "type": "arrived",
                            "data": {"station": index},
                            "msg": f"已到达 {index} 号站",
                            "success": True
                        })
                        print(f"✅ 已模拟到达 {index} 号站")
                    except Exception as e:
                        print(f"❌ 发送到达消息失败: {e}")

                threading.Thread(target=simulate_arrival, daemon=True).start()

            else:
                send_json(conn, {
                    "type": "error",
                    "msg": f"未知指令: {msg}",
                    "data": {},
                    "success": False
                })
    except Exception as e:
        print(f"❌ 异常: {e}")
    finally:
        conn.close()
        print(f"❎ 客户端断开: {addr}")

def start_server(host='0.0.0.0', port=5001):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"🚀 TCP JSON 服务器已启动: {host}:{port}")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("🛑 手动中断")
    finally:
        server.close()

if __name__ == '__main__':
    start_server()


