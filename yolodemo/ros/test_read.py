import serial

def crc16_modbus(data: bytes) -> bytes:
    """标准 Modbus CRC16 校验，POLY=0xA001，初始值0xFFFF，小端输出"""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x01:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')  # 低位在前

def build_read_coil_cmd(slave_id: int, start_addr: int, num_bits: int) -> bytes:
    """构造读取线圈命令（功能码01）"""
    cmd = bytearray()
    cmd.append(slave_id)
    cmd.append(0x01)  # 功能码：读取线圈状态
    cmd += start_addr.to_bytes(2, 'big')
    cmd += num_bits.to_bytes(2, 'big')
    cmd += crc16_modbus(cmd)
    return bytes(cmd)

def parse_coil_response(response: bytes, num_bits: int):
    """解析返回的线圈状态（按位展开）"""
    if len(response) < 3:
        return []
    byte_count = response[2]
    bit_list = []
    for byte in response[3:3 + byte_count]:
        for i in range(8):
            bit_list.append((byte >> i) & 0x01)
    return bit_list[:num_bits]

def read_coils(port="COM3", baudrate=19200, slave_id=1, start_addr=0x00C9, num_bits=32):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=8,
            parity='E',
            stopbits=1,
            timeout=1
        )

        # 构造命令
        cmd = build_read_coil_cmd(slave_id, start_addr, num_bits)
        print(f"发送指令：{cmd.hex(' ').upper()}")
        ser.write(cmd)

        # 接收响应
        response = ser.read(5 + (num_bits + 7) // 8)  # 5字节头 + 数据
        print(f"接收响应：{response.hex(' ').upper()}")

        # 解析状态
        states = parse_coil_response(response, num_bits)
        for i, state in enumerate(states):
            #print(f"Y{start_addr + i} = {'ON' if state else 'OFF'}")
            print(f"{i + 1}号桶 = {'ON' if state else 'OFF'}")

    except Exception as e:
        print(f"串口通信错误：{e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    # 示例：读取 Y0~Y31（起始地址 0x4800，共32位）
    read_coils(port="COM3", baudrate=19200, slave_id=1, start_addr=0x00C9, num_bits=32)
