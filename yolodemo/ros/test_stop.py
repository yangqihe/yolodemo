import websocket
import json

def pause_amcl_updates():
    # 建立连接到 rosbridge_server
    try:
        ws = websocket.create_connection("ws://192.168.1.197:9090", timeout=5)
    except Exception as e:
        print("❌ 无法连接到 rosbridge:", e)
        return

    # 组合 payload：设置 resample_interval、update_min_d、update_min_a
    payload = {
        "op": "call_service",
        "service": "/amcl/set_parameters",
        "args": {
            "config": {
                "ints": [
                    {
                        "name": "resample_interval",
                        "value": 1000000
                    }
                ],
                "doubles": [
                    {
                        "name": "update_min_d",
                        "value": 999.0
                    },
                    {
                        "name": "update_min_a",
                        "value": 999.0
                    }
                ]
            }
        },
        "id": "pause_amcl_full"
    }

    # 发送请求
    ws.send(json.dumps(payload))
    print("✅ 已发送暂停参数，等待反馈...")

    # 接收反馈
    result = ws.recv()
    print("📩 反馈结果:", result)

    ws.close()

if __name__ == "__main__":
    pause_amcl_updates()
