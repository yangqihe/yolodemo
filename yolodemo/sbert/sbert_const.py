# local_huggingface_path = "D:/Github/yolodemo/model/huggingface/paraphrase-multilingual-MiniLM-L12-v2"
# local_whisper_path = "D:/Github/yolodemo/model/whisper/medium.pt"
# predict_threshold = 0.75

import os
import sys

def resource_path(relative_path):
    """兼容 PyInstaller 打包后的路径"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    # 回退一级，从 yolodemo/yolodemo 定位到 yolodemo/
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

local_huggingface_path = resource_path("model/huggingface/paraphrase-multilingual-MiniLM-L12-v2")
local_whisper_path = resource_path("model/whisper/medium.pt")

predict_threshold = 0.75

# ✅ 意图自然语言映射表
intent_to_natural_reply = {
    "extend_arm": "打开机械臂",
    "retract_arm": "收回机械臂",
    "extend_sensor": "伸出传感器",
    "retract_sensor": "收回传感器",
    "start_oxygen": "开始测量溶氧",
    "stop_oxygen": "停止测量溶氧",
    "start_ph": "开始测量PH值",
    "stop_ph": "停止PH检测",
    "open_camera": "打开相机",
    "take_photo": "拍照",
    "close_camera": "关闭相机",
    "detect_water_quality": "检测水质",
    "save_data": "保存数据",
}

control_templates = {
    # 机械臂控制
    "extend_arm": [
        "打开机械臂",
        "伸出机械臂", "把机械臂伸出来", "请伸出机械臂",
        "展开机械臂", "伸出机械手臂", "机械臂向前延伸",
        "启动机械臂伸出程序", "机械臂伸展到工作位置",
        "把机械臂完全展开", "让机械臂伸到最长",
        "机械臂展开准备", "请将机械臂伸出"
    ],
    "retract_arm": [
        "收回机械臂", "让机械臂退回来", "关闭机械臂",
        "缩回机械臂", "机械臂退回原位", "收起机械手臂",
        "机械臂完全收回", "让机械臂回到初始位置",
        "机械臂复位", "关闭机械臂并缩回",
        "机械臂收回待机", "请将机械臂收回"
    ],

    # 传感器控制
    "extend_sensor": [
        "打开传感器",
        "伸出传感器", "把传感器推出去", "请伸出传感器",
        "推出传感器模块", "传感器伸展到检测位置",
        "部署传感器", "激活并伸出传感器",
        "传感器探头伸出", "请将传感器伸出来"
    ],
    "retract_sensor": [
        "收回传感器", "关闭传感器", "让传感器回来",
        "传感器缩回", "收起传感器探头",
        "关闭传感器并收回", "传感器返回安全位置",
        "传感器复位", "停止传感器并收回"
    ],

    # 溶氧检测
    "start_oxygen": [
        "开始测量溶氧", "启动溶氧检测", "检测氧含量",
        "启动溶解氧检测", "开始监测氧气含量",
        "执行溶氧分析", "检测水中溶氧量",
        "请测量当前溶氧值", "开启溶氧传感器"
    ],
    "stop_oxygen": [
        "停止测量溶氧", "关闭溶氧检测", "结束氧气检测",
        "终止溶氧检测", "退出氧气测量模式",
        "溶氧传感器待机", "暂停氧气分析",
        "关闭溶氧测量", "停止氧含量检测"
    ],

    # PH检测
    "start_ph": [
        "开始测量PH值", "启动PH检测", "检测PH",
        "启动PH值检测", "测量当前酸碱度",
        "开始PH值分析", "检测溶液的PH值",
        "请校准并测量PH", "开启PH传感器"
    ],
    "stop_ph": [
        "停止PH检测", "关闭PH传感器", "取消PH测量",
        "结束PH检测", "关闭PH测量功能",
        "PH传感器休眠", "停止酸碱度监测","结束酸碱度监测","取消酸碱度监测",
        "退出PH检测模式", "暂停PH值检测"
    ],

    # 相机控制
    "open_camera": [
        "打开相机", "启动摄像头", "开启相机",
        "启动摄像功能", "开启图像采集",
        "相机准备就绪", "进入拍摄模式",
        "激活相机", "请打开摄像头"
    ],
    "take_photo": [
        "开始拍照", "拍照", "拍一张照片",
        "拍摄一张照片", "抓取当前画面",
        "执行拍照指令", "记录当前图像",
        "请拍照存档", "进行图像采集"
    ],
    "close_camera": [
        "关闭相机", "停止摄像", "关掉相机",
        "相机停止工作", "关闭图像采集",
        "退出拍摄模式", "相机进入待机",
        "关闭摄像设备", "请关闭相机"
    ],
    # 新增：数据保存指令
    "save_data": [
        "保存数据", "存储当前数据", "请保存检测结果",
        "记录数据", "将数据存档", "备份数据",
        "保存到数据库", "数据保存到文件",
        "保存实验数据", "存储测量结果",
        "请保存当前状态", "数据持久化"
    ],
    # 水质检测
    "detect_water_quality": [
        "开始检测水质", "检测水质", "请检测一下水质",
        "执行水质分析", "启动水质检测", "水质检测开始",
        "检测当前水质情况", "监测水体质量",
        "进行水质分析", "水质分析一下",
        "测一下水质", "检测一下水质参数",
        "启动水质参数监测", "请开始水质监测"
    ]
}
