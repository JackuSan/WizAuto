# -*- coding: utf-8 -*-
"""
WizAuto 入口
打包: pyinstaller --noconfirm --onefile --windowed --add-data "platform-tools;platform-tools" --add-data "images;images" --name="WizAuto.v4.4.1" "main.pyw"
"""
import os
import sys
import logging
from datetime import datetime
import tkinter as tk

# 確保能 import 同目錄模組（打包後也適用）
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import constants
import state
import core
from gui import AutomationGUI

# ---------- 日誌 ----------
log_dir = os.path.join(BASE_DIR, "log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_filename = datetime.now().strftime("log_%Y%m%d%H%M%S.log")
log_path = os.path.join(log_dir, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s.%(msecs)03d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def preload_images():
    """檢查 images 目錄並預載模板"""
    image_dir = state.image_dir
    if getattr(sys, 'frozen', False):
        image_dir = os.path.join(BASE_DIR, 'images')
        state.image_dir = image_dir
    else:
        image_dir = os.path.join(BASE_DIR, 'images')
        if not os.path.exists(image_dir):
            image_dir = os.path.join(BASE_DIR, constants.DEFAULT_IMAGE_DIR)
        state.image_dir = image_dir

    if not os.path.exists(image_dir):
        logger.error(f"圖像目錄 {image_dir} 不存在")
        from tkinter import messagebox
        messagebox.showinfo("提示", "缺少 images 文件夾")
        sys.exit(1)

    missing = [name for name, file in constants.image_files.items()
               if not os.path.exists(os.path.join(image_dir, file))]
    if missing:
        logger.error(f"缺少圖像文件: {missing}")
        from tkinter import messagebox
        messagebox.showinfo("提示", f"缺少以下圖片:\n {missing}")
        sys.exit(1)

    import cv2
    for name, file in constants.image_files.items():
        path = os.path.join(image_dir, file)
        img = cv2.imread(path)
        if img is not None:
            state.preloaded_images[name] = img
        else:
            logger.error(f"無法預加載圖像: {path}")
    logger.info(f"已預載 {len(state.preloaded_images)} 張模板圖")


if __name__ == "__main__":
    # ADB 端口
    core.get_adb_port()
    core.is_player_running()
    preload_images()

    root = tk.Tk()
    app = AutomationGUI(root)
    state.app = app
    root.mainloop()
