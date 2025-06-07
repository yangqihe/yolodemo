import serial
import time
import crcmod

def calculate_crc(data_hex):
    """计算Modbus CRC16校验码（低字节在前）"""
    crc16 = crcmod.predefined.Crc("modbus")
    crc16.update(bytes.fromhex(data_hex))
    crc_hex = crc16.hexdigest().upper()
    return f"{crc_hex[2:]} {crc_hex[:2]}"  # 低字节在前

def send_close_command(port="COM3", baudrate=19200):
    try:
        # 配置串口（偶校验）
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='E',
            stopbits=1,
            timeout=1
        )

        # 1. 发送全零帧（复位）
        zero_frame = "00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
        print("\n发送全零帧（复位）:", zero_frame)
        ser.write(bytes.fromhex(zero_frame))
        time.sleep(0.5)  # 等待设备复位

        # 2. 发送关闭指令
        close_cmd = "01 01 05 00 00 00 00 00"  # 数据部分
        close_crc = calculate_crc(close_cmd)    # 计算CRC
        close_frame = f"{close_cmd} {close_crc}"
        print("发送关闭指令:", close_frame)
        ser.write(bytes.fromhex(close_frame))

        # 接收响应
        time.sleep(0.1)
        response = ser.read(ser.in_waiting or 1)
        if response:
            print("关闭响应:", response.hex(" ").upper())
        else:
            print("未收到响应，请检查设备状态")

    except serial.SerialException as e:
        print(f"串口错误: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    send_close_command(port="COM3", baudrate=19200)