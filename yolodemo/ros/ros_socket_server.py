import json
import math
import socket
import threading
import time

import pymysql
import websocket

# 数据库配置
db_config = {
    "host": "192.168.1.197",
    "user": "qihe",
    "password": "3621676Abcd!",
    "database": "myDB",
    "port": 3306
}

ros_ws = None
current_client_conn = None
is_handling = False
current_station_index = -1
amcl_converged = False  # ➕ 标记AMCL是否已收教


# ---------- 数据库操作 ----------

def fetch_station_data():
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM my_station ORDER BY station_order")
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def quaternion_from_yaw(deg):
    rad = math.radians(deg)
    return {
        "x": 0.0,
        "y": 0.0,
        "z": math.sin(rad / 2),
        "w": math.cos(rad / 2)
    }


def get_station_pose(index):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM my_station WHERE station_order = %s", (index,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        z = row["station_z"]
        w = row["station_w"]
        yaw_rad = 2 * math.atan2(z, w)
        yaw_deg = math.degrees(yaw_rad)

        if -30 <= yaw_deg <= 30:
            quat = quaternion_from_yaw(0)
        elif 60 <= yaw_deg <= 120:
            quat = quaternion_from_yaw(90)
        elif yaw_deg >= 150 or yaw_deg <= -150:
            quat = quaternion_from_yaw(180)
        elif -120 <= yaw_deg <= -60:
            quat = quaternion_from_yaw(-90)
        else:
            quat = {"x": 0.0, "y": 0.0, "z": z, "w": w}

        return {
            "position": {
                "x": row["station_x"],
                "y": row["station_y"],
                "z": 0.0
            },
            "orientation": quat
        }
    return None


# ---------- TCP 逻辑 ----------

def send_json(conn, obj):
    try:
        message = json.dumps(obj, ensure_ascii=False) + "\n"
        conn.sendall(message.encode("utf-8"))
    except Exception as e:
        print(f"❌ 发送失败: {e}")


def handle_client(conn, addr):
    global current_client_conn
    current_client_conn = conn
    print(f"✅ 客户端连接: {addr}")

    try:
        stations = fetch_station_data()
        send_json(conn, {
            "current_station_index": current_station_index,
            "type": "station_list",
            "data": stations,
            "msg": "初始化站点数据",
            "success": True
        })

        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            print(f"📥 收到指令: {msg}")

            if msg.startswith("cmd:"):
                index = int(msg.split(":")[1])

                if not amcl_converged:
                    send_json(conn, {
                        "type": "cmd_reject",
                        "data": {"station": index},
                        "msg": "❌ 当前定位未收敛，导航命令已拒绝",
                        "success": False
                    })
                    print(f"⛔ 拒绝导航到站点 {index}：AMCL 未收敛")
                    continue

                send_json(conn, {
                    "type": "cmd_ack",
                    "data": {"station": index},
                    "msg": f"收到跳转指令：{index}",
                    "success": True
                })
                pose = get_station_pose(index)
                if pose:
                    publish_navigation_goal(pose, index)
                else:
                    print(f"❌ 未找到第 {index} 号站点")

            elif msg.startswith("turn:"):
                angle = int(msg.split(":")[1])
                send_json(conn, {
                    "type": "turn_ack",
                    "msg": f"开始旋转 {angle} 度",
                    "data": {},
                    "success": True
                })
                rotate_robot(angle, angular_speed=0.3)
            else:
                send_json(conn, {
                    "type": "error",
                    "msg": f"未知指令: {msg}",
                    "data": {},
                    "success": False
                })

    except Exception as e:
        print(f"❌ 客户端异常: {e}")
    finally:
        conn.close()
        print(f"❎ 客户端断开: {addr}")
        current_client_conn = None


def rotate_robot(angle_deg, angular_speed=0.5):
    """
    通用旋转函数。正角度表示逆时针，负角度表示顺时针（右转）
    """
    if angular_speed <= 0:
        print("❌ 错误：角速度必须为正值")
        return

    angle_rad = math.radians(abs(angle_deg))
    duration = angle_rad / angular_speed
    angular_z = -angular_speed if angle_deg < 0 else angular_speed

    print(f"🔁 开始旋转 {angle_deg}°，角速度={angular_speed:.2f} rad/s，预计耗时={duration:.2f} 秒")

    cmd_msg = {
        "op": "publish",
        "topic": "/cmd_vel",
        "msg": {
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": angular_z}
        }
    }

    stop_msg = {
        "op": "publish",
        "topic": "/cmd_vel",
        "msg": {
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
        }
    }

    start_time = time.time()
    while time.time() - start_time < duration:
        ros_ws.send(json.dumps(cmd_msg))
        time.sleep(0.1)

    ros_ws.send(json.dumps(stop_msg))
    print("✅ 旋转完成，已停止小车")


def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5000))
    server.listen(5)
    print("🚀 TCP 服务器启动: 0.0.0.0:5000")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        server.close()


# ---------- ROS WebSocket ----------

def on_ros_open(ws):
    print("✅ 已连接 ROS WebSocket")

    ws.send(json.dumps({
        "op": "advertise",
        "topic": "/move_base/goal",
        "type": "move_base_msgs/MoveBaseActionGoal"
    }))

    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/move_base/result"
    }))

    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/amcl_pose"
    }))


def cancel_navigation_goal():
    ros_ws.send(json.dumps({
        "op": "publish",
        "topic": "/move_base/cancel",
        "msg": {
            "stamp": {"secs": 0, "nsecs": 0},
            "id": ""
        }
    }))
    print("🚫 已取消当前导航目标")


def stop_robot():
    ros_ws.send(json.dumps({
        "op": "publish",
        "topic": "/cmd_vel",
        "msg": {
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
        }
    }))
    clear_costmaps()
    print("⏹️ 已发送停止运动指令")


def on_ros_message(ws, message):
    global is_handling, amcl_converged
    data = json.loads(message)

    if data.get("topic") == "/amcl_pose":
        cov = data["msg"]["pose"]["covariance"]
        cov_x = cov[0]
        cov_y = cov[7]
        #print(cov_x)
        #print(cov_y)
        if cov_x < 0.4 and cov_y < 0.4:
            if not amcl_converged:
                amcl_converged = True
                print(f"✅ AMCL 收教：协方差 x={cov_x:.3f}, y={cov_y:.3f}")
                if current_client_conn:
                    send_json(current_client_conn, {
                        "type": "amcl_status",
                        "msg": "AMCL 已收教，可开始导航",
                        "data": {},
                        "success": True
                    })
        else:
            if amcl_converged:
                amcl_converged = False
                print(f"⚠️ AMCL 发散：协方差 x={cov_x:.3f}, y={cov_y:.3f}")
                cancel_navigation_goal()
                stop_robot()
                if current_client_conn:
                    send_json(current_client_conn, {
                        "type": "amcl_lost",
                        "msg": "❌ 导航过程中定位失效，已中断导航",
                        "data": {},
                        "success": False
                    })

    elif data.get("topic") == "/move_base/result":
        status = data["msg"].get("status", {})
        code = status.get("status", -1)
        goal_id = status.get("goal_id", {}).get("id", "")

        if code == 3 and not is_handling:
            is_handling = True
            print(f"🎯 到站成功: {goal_id}")
            if current_client_conn:
                send_json(current_client_conn, {
                    "type": "arrived",
                    "data": {"station": goal_id},
                    "msg": "已到达目标站点",
                    "success": True
                })
            time.sleep(3)
            clear_costmaps()
            is_handling = False


def clear_costmaps():
    ros_ws.send(json.dumps({
        "op": "call_service",
        "service": "/move_base/clear_costmaps",
        "args": {}
    }))
    print("🪑 已请求清除代价地图")


def on_ros_close(ws, code, msg):
    print(f"🔌 ROS WebSocket 关闭: {code}, {msg}")


def on_ros_error(ws, error):
    print(f"❌ ROS WebSocket 错误: {error}")


def publish_navigation_goal(pose, station_index):
    global current_station_index
    current_station_index = station_index
    now_secs = int(time.time())
    goal_id = f"goal_{station_index}_{now_secs}"

    goal_msg = {
        "header": {
            "seq": 0,
            "stamp": {"secs": 0, "nsecs": 0},
            "frame_id": "map"
        },
        "goal_id": {
            "stamp": {"secs": 0, "nsecs": 0},
            "id": goal_id
        },
        "goal": {
            "target_pose": {
                "header": {
                    "frame_id": "map",
                    "stamp": {"secs": 0, "nsecs": 0}
                },
                "pose": pose
            }
        }
    }

    ros_ws.send(json.dumps({
        "op": "publish",
        "topic": "/move_base/goal",
        "msg": goal_msg
    }))
    print(f"📤 已发布 ROS1 导航目标: {goal_msg}")


def start_ros_ws():
    global ros_ws
    while True:
        try:
            ros_ws = websocket.WebSocketApp(
                "ws://192.168.1.197:9090",
                on_open=on_ros_open,
                on_message=on_ros_message,
                on_close=on_ros_close,
                on_error=on_ros_error
            )
            ros_ws.run_forever(ping_interval=10, ping_timeout=5)
        except Exception as e:
            print(f"🔁 ROS WebSocket 自动重连中... 原因: {e}")
            time.sleep(3)


# ---------- 主程序 ----------

if __name__ == "__main__":
    threading.Thread(target=start_tcp_server, daemon=True).start()
    start_ros_ws()
