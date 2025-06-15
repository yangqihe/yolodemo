import serial
import time

def crc16(data: bytes) -> bytes:
    """计算 Modbus RTU 的 CRC16 校验码"""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def parse_coil_response(response: bytes, total_bits=32):
    """解析读取线圈状态的响应，返回布尔列表"""
    if len(response) < 3:
        return []
    byte_count = response[2]
    data_bytes = response[3:3 + byte_count]
    bits = []
    for byte in data_bytes:
        for i in range(8):
            bits.append((byte >> i) & 1)
    return bits[:total_bits]

def send_modbus_command(ser, request_hex, parse_response=False):
    """发送单个 Modbus 请求，并可选解析响应"""
    request = bytes.fromhex(request_hex)
    print("\n发送 Modbus 请求:", request.hex(" ").upper())
    ser.write(request)

    time.sleep(0.1)
    response = ser.read(ser.in_waiting or 1)
    if response:
        print("收到响应:", response.hex(" ").upper())
        if parse_response:
            states = parse_coil_response(response)
            print("线圈状态（Y0~Y31）:")
            for i, state in enumerate(states):
                print(f"Y{i:02d} = {'ON' if state else 'OFF'}")
    else:
        print("未收到设备响应，可能未连接或地址/波特率不对")

def send_modbus_read_command(port="COM3", baudrate=19200):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='E',
            stopbits=1,
            timeout=1
        )

        modbus_requests = [
            # 读取32个开关状态（从0x00C8开始，对应线圈地址200）
            #"01 01 00 C8 00 20 3D EA",  # 功能码01，读取32个位，已验证CRC
            # 打开第一个开关（地址201 = 0x00C9）
            #"01 05 00 C9 FF 00 5C 04",  # 开启线圈
            "01 05 00 C9 00 00 1D F4",  # 关闭线圈
            #"01 05 00 CA FF 00 AC 04",  # 开启线圈
            #"01 05 00 CA 00 00 ED F4",  # 关闭线圈
            #"01 05 00 CB FF 00 FD C4",  # 开启线圈
            #"01 05 00 CB 00 00 BC 34",  # 关闭线圈
        ]

        for req_hex in modbus_requests:
            # 如果是读取状态，解析响应
            parse = req_hex.startswith("01 01")
            send_modbus_command(ser, req_hex, parse_response=parse)
            #time.sleep(5)

    except serial.SerialException as e:
        print(f"串口错误: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\n串口已关闭")

if __name__ == "__main__":
    send_modbus_read_command(port="COM3", baudrate=19200)
