# from PyQt5.QtWidgets import QDialog, QVBoxLayout
# from PyQt5.QtCore import Qt
#
# from ros.setting_page import SettingPage
#
#
# #from setting_page import SettingPage  # ✅ 正确引用
#
# class SettingWindow(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("调试页面")
#         self.setMinimumSize(1000, 860)
#         self.setWindowModality(Qt.ApplicationModal)
#
#         self.inner_widget = SettingPage()
#         layout = QVBoxLayout()
#         layout.addWidget(self.inner_widget)
#         self.setLayout(layout)
#
#         # ✅ 将 inner_widget 的信号转发出去
#         self.inner_widget.bucket_changed.connect(self.bucket_changed)
