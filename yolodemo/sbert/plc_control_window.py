import sys
import serial
import serial.tools.list_ports
import struct
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QMessageBox, QScrollArea
)
from PyQt5.QtCore import QTimer


class PLCControlWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PLC 阀门控制界面")
        self.resize(1000, 600)

        self.valve_count = 32
        self.valve_states = [False] * self.valve_count
        self.serial_port = None
        self.plc_port = "COM3"

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 串口控制区
        port_layout = QHBoxLayout()
        self.port_input = QLineEdit(self.plc_port)
        self.save_button = QPushButton("保存串口")
        self.open_button = QPushButton("打开串口")
        self.close_button = QPushButton("关闭串口")
        self.read_button = QPushButton("读取状态")
        self.save_button.clicked.connect(self.save_port)
        self.open_button.clicked.connect(self.open_port)
        self.close_button.clicked.connect(self.close_port)
        self.read_button.clicked.connect(self.read_coil_status)

        port_layout.addWidget(QLabel("串口号:"))
        port_layout.addWidget(self.port_input)
        port_layout.addWidget(self.save_button)
        port_layout.addWidget(self.open_button)
        port_layout.addWidget(self.close_button)
        port_layout.addWidget(self.read_button)
        self.layout.addLayout(port_layout)

        # 阀门按钮区
        self.grid = QGridLayout()
        self.buttons = []
        for i in range(self.valve_count):
            btn = QPushButton(f"{i + 1}号关")
            btn.setStyleSheet("background-color: green; color: white;")
            btn.clicked.connect(lambda _, idx=i: self.toggle_valve(idx))
            self.grid.addWidget(btn, i // 8, i % 8)
            self.buttons.append(btn)

        scroll = QScrollArea()
        content = QWidget()
        content.setLayout(self.grid)
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        self.layout.addWidget(scroll)

        self.timer = QTimer()
        self.timer.timeout.connect(self.read_coil_status)

    def save_port(self):
        self.plc_port = self.port_input.text().strip()
        QMessageBox.information(self, "提示", f"串口号已保存为：{self.plc_port}")

    def open_port(self):
        try:
            self.serial_port = serial.Serial(
                port=self.plc_port,
                baudrate=19200,
                bytesize=8,
                parity=serial.PARITY_EVEN,
                stopbits=1,
                timeout=1
            )
            self.read_coil_status()
            self.timer.start(2000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"串口打开失败: {e}")

    def close_port(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.timer.stop()

    def toggle_valve(self, index):
        if not self.serial_port or not self.serial_port.is_open:
            QMessageBox.warning(self, "提示", "串口未打开")
            return

        if not self.valve_states[index] and sum(self.valve_states) >= 5:
            QMessageBox.warning(self, "提示", "手动开阀禁止同时开启超过 5 个阀门！")
            return

        address = 201 + index
        command = self.generate_write_command(address, not self.valve_states[index])
        self.serial_port.write(command)
        time.sleep(0.2)
        self.read_coil_status()

    def read_coil_status(self):
        if not self.serial_port or not self.serial_port.is_open:
            return

        request = [0x01, 0x01, 0x00, 0xC9, 0x00, 0x20]
        request += self.crc16(request)
        self.serial_port.write(bytearray(request))
        time.sleep(0.3)
        response = self.serial_port.read(9)

        if len(response) < 5:
            return

        byte_count = response[2]
        data = response[3:3 + byte_count]
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> i) & 0x01 == 1)

        if len(bits) >= self.valve_count:
            self.valve_states = bits[:self.valve_count]
            self.update_buttons()

    def update_buttons(self):
        for i, btn in enumerate(self.buttons):
            if self.valve_states[i]:
                btn.setText(f"{i + 1}号开")
                btn.setStyleSheet("background-color: red; color: white;")
            else:
                btn.setText(f"{i + 1}号关")
                btn.setStyleSheet("background-color: green; color: white;")

    def generate_write_command(self, address, turn_on):
        addr_high = (address >> 8) & 0xFF
        addr_low = address & 0xFF
        value = [0xFF, 0x00] if turn_on else [0x00, 0x00]
        base = [0x01, 0x05, addr_high, addr_low] + value
        crc = self.crc16(base)
        return bytearray(base + crc)

    def crc16(self, data):
        crc = 0xFFFF
        for b in data:
            crc ^= b
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return [crc & 0xFF, (crc >> 8) & 0xFF]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PLCControlWindow()
    window.show()
    sys.exit(app.exec_())
