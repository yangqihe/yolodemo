# import serial
# import time
#
# def send_modbus_read_command(port="COM3", baudrate=19200):
#     # 打开串口
#     ser = serial.Serial(port=port, baudrate=baudrate, bytesize=8, parity='E', stopbits=1, timeout=1)
#
#     # Modbus RTU 读取线圈指令（你抓到的数据）
#     # 站号1，功能码01，起始地址0x00C8（200），读取40个位（0x0028），CRC = BD EA
#     request = bytes.fromhex("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
#     request = bytes.fromhex("01 01 00 C8 00 28 BD EA")
#     request = bytes.fromhex("00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
#     #1号通
#     request = bytes.fromhex("01 01 05 02 00 00 00 00 e8 92")
#     #request = bytes.fromhex("01 04 00 00 00 04 F1 C9")
#     #request = bytes.fromhex("01 01 05 00 00 00 00 00 91 52")
#     #176 25/05/2025 10:44:51 IRP_MJ_WRITE DOWN  01 05 00 c9 ff 00 5c 04  ...?.\. 8 8 COM8
#
#     print("发送 Modbus 请求:", request.hex(" ").upper())
#     ser.write(request)
#
#     # 接收响应
#     time.sleep(0.1)  # 等待数据返回
#     response = ser.read(ser.in_waiting or 1)
#     if response:
#         print("收到响应:", response.hex(" ").upper())
#     else:
#         print("未收到设备响应，可能未连接或地址/波特率不对")
#
#     ser.close()
#
# if __name__ == "__main__":
#     send_modbus_read_command(port="COM3", baudrate=19200)



import serial
import time

def send_modbus_command(ser, request_hex):
    """发送单个 Modbus 请求，并接收响应"""
    request = bytes.fromhex(request_hex)
    print("\n发送 Modbus 请求:", request.hex(" ").upper())
    ser.write(request)

    # 等待响应
    time.sleep(0.1)  # 根据设备响应时间调整
    response = ser.read(ser.in_waiting or 1)
    if response:
        print("收到响应:", response.hex(" ").upper())
    else:
        print("未收到设备响应，可能未连接或地址/波特率不对")

def send_modbus_read_command(port="COM3", baudrate=19200):
    """打开串口，并顺序发送多个 Modbus 请求"""
    try:
        # 打开串口（偶校验）
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='E',  # 偶校验
            stopbits=1,
            timeout=1   # 超时1秒
        )

        # 定义要发送的多个 Modbus 请求（按顺序执行）
        # modbus_requests = [
        #     "01 01 00 C8 00 28 BD EA",  # 请求1：读取线圈（地址200，40个位）
        #     "01 01 05 02 00 00 00 00 E8 92",  # 请求2：自定义命令
        #     "01 04 00 00 00 04 F1 C9",  # 请求3：读取输入寄存器（地址0，4个寄存器）
        #     "01 05 00 C9 FF 00 5C 04",  # 请求4：写单个线圈（地址201，ON）
        # ]

        # modbus_requests = [
        #     "01 01 00 C8 00 28 BD EA",  # 请求1：读取线圈（地址200，40个位）
        #     "01 01 05 02 00 00 00 00 E8 92",  # 请求2：自定义命令
        #     "01 04 00 00 00 04 F1 C9",  # 请求3：读取输入寄存器（地址0，4个寄存器）
        #     "01 05 00 C9 FF 00 5C 04",  # 请求4：写单个线圈（地址201，ON）
        # ]

        modbus_requests = [
            "01 01 00 C8 00 28 BD EA",  # 请求1：读取线圈（地址200，40个位）
            "01 01 05 04 00 00 00 00 60 92",  # 请求2：自定义命令
            "01 04 00 00 00 04 F1 C9",  # 请求3：读取输入寄存器（地址0，4个寄存器）
            "01 05 00 C9 FF 00 5C 04",  # 请求4：写单个线圈（地址201，ON）
        ]

        # 逐个发送请求
        for req_hex in modbus_requests:
            send_modbus_command(ser, req_hex)
            time.sleep(0.2)  # 每个请求之间间隔0.2秒（防止设备处理不过来）

    except serial.SerialException as e:
        print(f"串口错误: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("\n串口已关闭")

if __name__ == "__main__":
    send_modbus_read_command(port="COM3", baudrate=19200)