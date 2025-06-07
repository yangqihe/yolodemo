import serial
import serial.tools.list_ports
from datetime import datetime


def list_available_ports():
    """列出所有可用串口"""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("没有找到可用的串口设备")
        return []

    print("\n可用串口列表:")
    for i, port in enumerate(ports, 1):
        print(f"{i}. {port.device} - {port.description}")
    return ports


def select_port():
    """让用户选择要监听的串口"""
    ports = list_available_ports()
    if not ports:
        return None

    while True:
        try:
            choice = input("\n请选择要监听的串口编号(1-{})，或直接输入串口名称: ".format(len(ports)))
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(ports):
                    return ports[index].device
            elif choice.strip():
                return choice.strip()
        except:
            pass
        print("输入无效，请重新选择")


def get_baudrate():
    """获取波特率设置"""
    common_rates = [9600, 19200, 38400, 57600, 115200]
    print("\n常用波特率: " + ", ".join(map(str, common_rates)))

    while True:
        try:
            rate = input("请输入波特率(默认9600): ") or "9600"
            return int(rate)
        except ValueError:
            print("请输入有效的数字")


def get_display_mode():
    """选择显示模式"""
    while True:
        mode = input("\n显示模式: 1-文本模式, 2-十六进制模式 (默认1): ") or "1"
        if mode in ["1", "2"]:
            return mode == "2"  # True表示十六进制模式
        print("请输入1或2")


def get_log_setting():
    """获取日志设置"""
    choice = input("\n是否记录到日志文件? (y/n, 默认n): ") or "n"
    if choice.lower() == "y":
        return input("请输入日志文件路径(如plc_log.txt): ").strip()
    return None


def monitor_serial_port():
    """主监听函数"""
    print("=== PLC串口通信监听程序 ===")

    # 获取用户设置
    port = select_port()
    if not port:
        return

    baudrate = get_baudrate()
    hex_mode = get_display_mode()
    log_file = get_log_setting()

    # 连接串口
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
    except Exception as e:
        print(f"\n无法打开串口 {port}: {e}")
        return

    print(f"\n开始监听 {port} (波特率: {baudrate})...")
    print("按 Ctrl+C 停止监听\n")

    try:
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                # 根据模式显示数据
                if hex_mode:
                    display = ' '.join(f'{b:02X}' for b in data)
                else:
                    try:
                        display = data.decode('utf-8', errors='replace')
                        display = display.replace('\r', '\\r').replace('\n', '\\n')
                    except:
                        display = ' '.join(f'{b:02X}' for b in data) + " (解码失败)"

                # 输出到屏幕
                output = f"[{timestamp}] {display}"
                print(output)

                # 记录到文件
                if log_file:
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(output + '\n')

    except KeyboardInterrupt:
        print("\n监听已停止")
    finally:
        ser.close()


if __name__ == "__main__":
    try:
        monitor_serial_port()
    except Exception as e:
        print(f"程序出错: {e}")
    input("\n按Enter键退出...")