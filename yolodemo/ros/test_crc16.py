def crc16_modbus(data: bytes) -> bytes:
    """标准 CRC-16/MODBUS 算法：POLY=0xA001, INIT=0xFFFF, 无反转, Little Endian"""
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')  # Modbus 是低位在前

# 示例验证
data = bytes.fromhex("01 05 00 C9 FF 00")
#data = bytes.fromhex("01 05 00 C9 00 00")
#data = bytes.fromhex("01 05 00 CA FF 00")
#data = bytes.fromhex("01 05 00 CA 00 00")
#data = bytes.fromhex("01 05 00 CB FF 00")
#data = bytes.fromhex("01 05 00 CB 00 00")
crc = crc16_modbus(data)
print("最终带CRC命令：", (data + crc).hex(" ").upper())
