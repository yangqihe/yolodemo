import serial

def listen_serial(port='COM3', baudrate=9600):
    with serial.Serial(port, baudrate, timeout=5) as ser:
        print(f"开始监听 {port}...")
        while True:
            data = ser.read(ser.in_waiting or 1)
            if data:
                print("收到串口数据:", data.hex(" "))

# 替换为实际串口号
listen_serial(port='COM14', baudrate=9600)
