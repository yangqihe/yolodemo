import websocket
import json
import time

# 是否正在处理中，防止重复触发
is_handling = False

def on_open(ws):
    print("✅ 已连接 ROS WebSocket")
    ws.send(json.dumps({
        "op": "subscribe",
        "topic": "/move_base/result"
    }))


def on_message(ws, message):
    global is_handling
    data = json.loads(message)
    if data.get("op") == "publish" and data.get("topic") == "/move_base/result":
        result = data["msg"]
        status_info = result.get("status", {})
        status_code = status_info.get("status", -1)
        status_text = status_info.get("text", "")
        goal_id = status_info.get("goal_id", {}).get("id", "")

        print(f"🎯 到站信息: status={status_info}, 描述={status_text}, goal_id={goal_id}")

        if status_code == 3 and not is_handling:
            is_handling = True
            print("🚏 小车已到站，执行暂停与等待...")
            #do_pause_and_resume(ws)
            is_handling = False



def do_pause_and_resume(ws):
    # 1. 暂停小车（发布零速度）
    ws.send(json.dumps({
        "op": "publish",
        "topic": "/cmd_vel",
        "msg": {
            "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
        }
    }))
    print("⏸ 已暂停小车，等待 30 秒...")
    time.sleep(30)

    # 2. 恢复导航（示例为继续前进，如需发布新导航目标可扩展）
    print("▶️ 30 秒结束，恢复前进中...")
    ws.send(json.dumps({
        "op": "publish",
        "topic": "/cmd_vel",
        "msg": {
            "linear": {"x": 0.2, "y": 0.0, "z": 0.0},
            "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
        }
    }))
    print("✅ 小车已恢复前进")


def on_close(ws, close_status_code, close_msg):
    print("🔌 连接关闭:", close_status_code, close_msg)


def on_error(ws, error):
    print("❌ 连接错误:", error)


# 启动 WebSocket 客户端
ws = websocket.WebSocketApp(
    "ws://192.168.1.197:9090",  # 改成你自己的 ROS WebSocket 地址
    on_open=on_open,
    on_message=on_message,
    on_close=on_close,
    on_error=on_error
)

ws.run_forever()
