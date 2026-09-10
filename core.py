# -*- coding: utf-8 -*-
"""核心功能：ADB、截圖、找圖、點擊、戰鬥、開箱、地圖輔助"""
import subprocess
import cv2
import numpy as np
import time
import random
import logging
import psutil
import shutil
import os
import sys
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import platform

import constants
import state

logger = logging.getLogger(__name__)

# 系統函數
def is_player_running():    #檢查mumu是否運行
    """檢查 Mumuplayer 是否正在運行"""
    # (state) global state.game_player
    for i in range(3):
        for proc in psutil.process_iter(['name']):
            name = proc.info['name'].lower()
            if name in ['mumunxdevice.exe', 'mumunxdevice', 'mumunydevice', 'mumuplayer']:
                logger.info("Mumuplayer正在運行")
                state.game_player = "mumuplayer"
                return True
    logger.info("沒有找到模擬器")
    return False
def start_game_player():
    """啟動 MuMu 的快捷方式 (wiz.lnk / wiz.command)"""
    now = time.time()
    if now - state.last_player_restart_time < 60:
        logger.warning(f"距離上次重啟模擬器不足 60 秒，跳過本次 start_game_player")
        return False

    state.last_player_restart_time = now

    if getattr(sys, 'frozen', False):
        script_dir = os.path.dirname(sys.executable)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. 先殺掉舊進程
    if platform.system() == 'Windows':
        subprocess.run(['taskkill', '/F', '/IM', 'mumunxdevice.exe'], check=False)
        wiz_path = os.path.join(script_dir, 'wiz.lnk')
    else:
        # Mac 實際進程名請再確認
        subprocess.run(['killall', '-9', 'MuMuNyxDevice'], check=False)
        subprocess.run(['pkill', '-9', '-f', 'MuMu'], check=False)
        wiz_path = os.path.join(script_dir, 'wiz.command')

    if not os.path.exists(wiz_path):
        logger.error(f"快捷方式未找到: {wiz_path}")
        return False

    try:
        logger.info(f"正在啟動遊戲模擬器: {wiz_path}")

        # 2. 只啟動一次
        if platform.system() == 'Windows':
            subprocess.Popen([wiz_path], shell=True)
        else:
            subprocess.Popen(['open', wiz_path])

        # 3. 等待進程出現
        wait_process_start = time.time()
        while time.time() - wait_process_start < 30:
            if is_player_running():
                logger.info("遊戲模擬器進程已偵測到")
                break
            time.sleep(2)
        else:
            raise Exception("遊戲模擬器進程啟動超時")

        # 4. 重連 ADB
        connected = False
        adb_count = 0
        wait_connect_start = time.time()
        while time.time() - wait_connect_start < 60:
            adb_count += 1
            logger.info(f"嘗試重連 ADB, 次數: {adb_count}")
            if connect_to_device():
                connected = True
                break
            time.sleep(5)

        if not connected:
            raise Exception("ADB 重連超時，無法繼續")

        logger.info("遊戲模擬器已啟動")
        game_restart()
        return True

    except Exception as e:
        logger.error(f"啟動遊戲模擬器失敗: {e}")
        return False
def check_requirements():   #檢查圖片包
    # (state) global state.image_dir
    # 動態設置圖像目錄路徑
    if getattr(sys, 'frozen', False):
        state.image_dir = os.path.join(os.path.dirname(sys.executable), 'images')
    else:
        state.image_dir = os.path.join(os.path.dirname(__file__), 'images')
    # 檢查圖像資料夾
    if not os.path.exists(state.image_dir):
        logger.error(f"圖像資料夾 {state.image_dir} 不存在")
        messagebox.showerror("錯誤", f"圖像資料夾 {state.image_dir} 不存在，請確保 images 資料夾與腳本或 exe 同級")
        exit(1)
    # 檢查 platform-tools 文件夾和 adb.exe
    if getattr(sys, 'frozen', False):
        adb_dir = os.path.join(os.path.dirname(sys.executable), 'platform-tools')
    else:
        adb_dir = os.path.join(os.path.dirname(__file__), 'platform-tools')
    adb_path = get_adb_path()
    if not os.path.exists(adb_dir):
        logger.error(f"platform-tools 資料夾 {adb_dir} 不存在")
        messagebox.showerror("錯誤", f"platform-tools 資料夾 {adb_dir} 不存在，請確保 platform-tools 資料夾與腳本或 exe 同級")
        exit(1)
    if not os.path.exists(adb_path):
        logger.error(f"ADB 可執行文件 {adb_path} 不存在")
        messagebox.showerror("錯誤", f"ADB 可執行文件 {adb_path} 不存在，請確保 platform-tools 資料夾中包含 adb程式")
        exit(1)
def connect_to_device():    #連接adb
    """
    嘗試連接 ADB 並確認設備 online。
    返回 True 如果成功，False 否則。
    """
    adb_path = get_adb_path()
    
    # 先執行 connect
    connect_cmd = f'"{adb_path}" connect {constants.ADB_HOST}:{state.adb_port}'
    try:
        result_connect = subprocess.run(connect_cmd, shell=True, capture_output=True, text=True)
        output_connect = result_connect.stdout.strip().lower()
        if result_connect.stdout:
            logger.info(f"ADB connect 輸出: {result_connect.stdout.strip()}")
        
        if result_connect.returncode != 0 or "connected" not in output_connect:
            logger.warning("ADB connect 未成功，繼續檢查 devices")
            return False  # connect 失敗，但不 raise，讓呼叫者重試
    except Exception as e:
        logger.error(f"ADB connect 異常: {e}")
        return False
    
    # 再檢查 devices 確保 online
    devices_cmd = f'"{adb_path}" -s {constants.ADB_HOST}:{state.adb_port} devices'
    try:
        result_devices = subprocess.run(devices_cmd, shell=True, capture_output=True, text=True)
        output_devices = result_devices.stdout.strip()
        if result_devices.stdout:
            logger.info(f"ADB devices 輸出: {output_devices}")
        
        if 'device' in output_devices and 'offline' not in output_devices:
            logger.info(f"ADB 設備 {constants.ADB_HOST}:{state.adb_port} 已 online")
            return True
        else:
            logger.warning("ADB 設備仍 offline 或 unauthorized")
            return False
    except Exception as e:
        logger.error(f"ADB devices 檢查異常: {e}")
        return False
def get_adb_port(): #讀取adb port
    """顯示彈出窗口以獲取 ADB 端口"""
    # (state) global state.adb_port
    dialog = tk.Tk()
    dialog.title("輸入 ADB 端口")
    dialog.geometry("300x150")
    dialog.resizable(False, False)

    label = tk.Label(dialog, text="請輸入 ADB 端口 (默認 5555):")
    label.pack(pady=10)

    port_var = tk.StringVar(value="5555")  # 默認值為 5555
    entry = tk.Entry(dialog, textvariable=port_var, width=20)
    entry.pack(pady=10)

    def submit():
        # (state) global state.adb_port
        try:
            port = port_var.get().strip()
            logger.info(f"用戶輸入的端口: '{port}'")  # 添加這行來檢查輸入值
            if port.isdigit() and 1024 <= int(port) <= 65535:
                state.adb_port = int(port)
                dialog.destroy()
            else:
                messagebox.showerror("錯誤", "請輸入有效的端口號 (1024-65535)")
        except Exception as e:
            messagebox.showerror("錯誤", f"無效輸入: {e}")

    button = tk.Button(dialog, text="確認", command=submit)
    button.pack(pady=10)

    dialog.mainloop()
    if state.adb_port is None:
        logger.error("未提供有效的 ADB 端口，退出程序")
        exit(1)
def game_restart():
    """重啟遊戲（優化版：修正 P_start2 重複點擊問題 + 用 ADB 啟動）"""
    # (state) global state.bs_restarted, state.image_restart, state.image_stage, state.script_choice, state.battle_mode, state.freeze_screen_check_time

    state.bs_restarted = True
    if state.freeze_screen_check_time is not None:
        state.freeze_screen_check_time = time.time() + 90   # 給重啟後較長的寬限期

    # 階段式等待清單（避免點完還繼續找）
    stage1_list = ["P_start1", "P_start2", "P_download"]          # 啟動畫面
    stage2_list = ["P_autobattle_inactive", "P_autobattle_inactive0", 
                   "P_autobattle_inactive1", "P_exit", "P_chest_open"]  # 已進入遊戲

    if state.image_restart:
        for image in state.image_restart:
            if image not in stage2_list:
                stage2_list.append(image)
        logger.info(f"額外等待圖片: {state.image_restart}")

    clicked_start1 = False
    clicked_start2 = False
    start_time = time.time()
    timeout = 180          # 最多等 3 分鐘

    logger.info("開始 game_restart 流程")

    while time.time() - start_time < timeout:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止 game_restart")
            return False

        # 優先找 stage1（啟動畫面）
        check = find_image(stage1_list, log=False, remedial=False)
        if check:
            name = check[0]
            if name == "P_start1" and not clicked_start1:
                click_image("P_start1")
                clicked_start1 = True
                time.sleep(4)
                continue
            elif name == "P_start2" and not clicked_start2:
                click_image("P_start2", timeout=3)
                clicked_start2 = True
                logger.info("已點擊 P_start2，進入等待進入遊戲階段")
                time.sleep(8)          # 多等一點，避免畫面還沒跳走
                continue
            elif name == "P_download":
                logger.info("需要下載資料，點擊下載")
                click_image("P_download", timeout=3)
                time.sleep(5)
                continue

        # 已經點過 start2 後，改找 stage2
        if clicked_start2 or clicked_start1:
            check2 = find_image(stage2_list, log=False, remedial=False)
            if check2:
                name2 = check2[0]
                logger.info(f"偵測到已進入遊戲畫面: {name2}")
                if name2 in ["P_autobattle_inactive", "P_autobattle_inactive0", "P_autobattle_inactive1"]:
                    tap(450, 50, "點擊取消遊戲暫停")
                    if state.battle_mode == "自動戰鬥":
                        click_image(["P_autobattle_inactive", "P_autobattle_inactive0", "P_autobattle_inactive1"])
                elif state.image_restart and name2 in state.image_restart:
                    if state.image_stage == "click":
                        click_image(state.image_restart)
                logger.info("閃退自動重啟步驟完成")
                return True

        time.sleep(1.5)

    logger.error("game_restart 超時，無法進入遊戲")
    return False
def check_reconnect(screenshot=None, similarity=0.7, check=True):    #檢查斷線
    """檢查並處理斷線對話框"""
    # (state) global state.paused
    if screenshot is None:
        take_screenshot()
    # 檢查 P_reconnect
    reconnect_result = find_image("P_reconnect", screenshot, log=False, reconnect=False)
    if not reconnect_result:
        logger.debug("未檢測到 P_reconnect，無斷線")
        return False
    (x, y) = reconnect_result[1]
    if x is None or y is None:
        logger.error("P_reconnect 坐標無效，跳過斷線處理")
        return False
    # 確認 P_reconnect_button 存在
    button_result = find_image("P_reconnect_button", screenshot, similarity=similarity, reconnect=False)
    if not button_result:
        logger.debug("未找到 P_reconnect_button，無斷線")
        return False
    (bx, by) = button_result[1]
    if bx is None or by is None:
        logger.error("P_reconnect_button 坐標無效，跳過斷線處理")
        return False
    logger.info(f"檢測到斷線：P_reconnect 在 ({x}, {y})，相似度高於 {similarity}")
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止斷線處理")
            return False
        if state.paused:
            logger.info("腳本暫停，等待恢復以處理斷線")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        tap(bx, by, "P_reconnect_button")
        time.sleep(5)
        new_screenshot = take_screenshot()
        if new_screenshot is None:
            logger.error("截圖失敗，無法驗證斷線畫面")
            return False
        if not find_image("P_reconnect", new_screenshot, similarity=similarity, reconnect=False):
            logger.info("斷線畫面已消失，重新連接成功")
            return True
        logger.warning(f"斷線畫面仍存在，重試 {attempt + 1}/{max_attempts}")
        attempt += 1
        screenshot = new_screenshot
    logger.error("多次嘗試後仍未解決斷線，終止處理")
    return False
def check_gameicon(screenshot=None, similarity=0.8):
    """檢查是否閃退出到模擬器桌面（有遊戲 icon），用 ADB 啟動取代點擊"""
    # (state) global state.paused
    if screenshot is None:
        take_screenshot()
    icon_result = find_image(["P_gameicon2", "P_gameicon3"], screenshot, log=False)
    if not icon_result:
        logger.debug("未檢測到 gameicon，無斷線")
        return False

    image_name, (x, y), sim = icon_result
    logger.info(f"檢測到 {image_name} 在 ({x}, {y})，相似度 {sim}，使用 ADB 啟動遊戲")
    
    # 改用 ADB 啟動，不再點擊 icon
    force_stop_game()          # 先確保乾淨
    start_game_app()
    game_restart()
    return True
def check_backtotitle(screenshot=None, similarity=0.8):
    """檢查是否閃退出模擬器頁面"""
    # (state) global state.paused
    if screenshot is None:
        take_screenshot()
    backtotitle_result = find_image("P_backtotitle", screenshot, log=False, reconnect=False)
    if not backtotitle_result:
        logger.debug("未檢測到 P_backtotitle，無返回標題")
        return False
    (x, y) = backtotitle_result[1]
    logger.info(f"檢測到P_backtotitle在 ({x}, {y})，相似度高於要求 {similarity}")
    tap(x,y, "P_backtotitle")
    game_restart()
    return True
def check_abnormality(sim=0.8):
    logger.info("斷線檢查")
    img = take_screenshot()          # 只截一次
    reconnect_result = find_image("P_reconnect", screenshot=img, similarity=sim, log=False, remedial=False)
    if reconnect_result:
        (x, y) = reconnect_result[1]
        button_result = find_image("P_reconnect_button", similarity=sim)
        (bx, by) = button_result[1]
        logger.info(f"檢測到斷線：P_reconnect 在 ({x}, {y})，相似度高於 {sim}")
        max_attempts = 10
        attempt = 0
        while attempt < max_attempts:
            if state.stop_event.is_set():
                logger.info("收到停止指令，終止斷線處理")
                return False
            if state.paused:
                logger.info("腳本暫停，等待恢復以處理斷線")
                while state.paused and not state.stop_event.is_set():
                    time.sleep(0.1)
            tap(bx, by, "P_reconnect_button")
            time.sleep(5)
            new_screenshot = take_screenshot()
            if new_screenshot is None:
                logger.error("截圖失敗，無法驗證斷線畫面")
                return False
            if not find_image("P_reconnect", similarity=sim):
                logger.info("斷線畫面已消失，重新連接成功")
                return True
            logger.warning(f"斷線畫面仍存在，重試 {attempt + 1}/{max_attempts}")
            attempt += 1
        logger.error("多次嘗試後仍未解決斷線，終止處理")
        return True
    gameicon_result = find_image(["P_gameicon2", "P_gameicon3"], screenshot=img, similarity=sim, log=False, remedial=False)
    if gameicon_result:
        image_name, (x, y), sim_val = gameicon_result
        logger.info(f"檢測到{image_name} 在 ({x}, {y})，相似度{sim_val}，改用 ADB 啟動")
        force_stop_game()
        start_game_app()
        game_restart()
        return True
    backtotitle_result = find_image("P_backtotitle", screenshot=img, similarity=sim, log=False, remedial=False)
    if backtotitle_result:
        image_name, (x, y), sim_result = backtotitle_result
        logger.info(f"檢測到{image_name} 在 ({x}, {y})，相似度{sim_result}高於要求 {sim}")
        tap(x,y, "返回標題")
        game_restart()
        return True
    return False
def get_adb_path(): 
    if hasattr(sys, 'frozen') and getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    adb_dir = os.path.join(base, 'platform-tools')
    
    if platform.system() == 'Windows':
        return os.path.join(adb_dir, 'windows', 'adb.exe')
    else:  # macOS / Linux
        return os.path.join(adb_dir, 'mac', 'adb')

# ADB 工具函數
def run_adb_command(command):   #執行adb指令
    """執行 ADB 命令並返回輸出，指定設備端口"""
    adb_path = get_adb_path()
    full_command = f'"{adb_path}" -s {constants.ADB_HOST}:{state.adb_port} {command}'
    for i in range(3):
        try:
            result = subprocess.run(full_command, shell=True, capture_output=True, text=True, check=True, timeout=5)
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            logger.warning(f"ADB 命令執行超時 (5秒): {command}，正在嘗試重試...")
            continue
        except subprocess.CalledProcessError as e:
            logger.error(f"ADB 命令執行失敗: {e}")
            logger.error(f"命令輸出: {e.stderr.strip()}")
            
            # 先嘗試恢復 ADB，而不是直接殺模擬器
            logger.warning("嘗試恢復 ADB 連線...")
            adb_path = get_adb_path()
            
            subprocess.run(f'"{adb_path}" kill-server', shell=True)
            time.sleep(1)
            subprocess.run(f'"{adb_path}" start-server', shell=True)
            time.sleep(2)
            
            if connect_to_device():
                logger.info("ADB 已恢復，不重啟模擬器")
                return None   # 讓上層決定要不要重試命令
            
            # 真的恢復失敗才檢查模擬器進程
            logger.error("ADB 恢復失敗，等待10秒觀察模擬器是否閃退")
            time.sleep(10)
            if not is_player_running():
                logger.info("遊戲模擬器確實關閉，嘗試重啟")
                start_game_player()
            else:
                logger.warning("模擬器進程仍在，但 ADB 無法連線，暫不重啟")
    else:
        return None
def take_screenshot(name=None, region=None):    #截圖
    """從設備捕獲螢幕截圖，改用純記憶體流方式，防止 Android 15 磁碟緩衝區爆滿"""
    # 控頻：非存檔截圖時，強制小休 0.2 秒（每秒最多截圖 5 次，大幅減輕 CPU 負載）
    if name is None:
        time.sleep(0.2)

    adb_path = get_adb_path()
    
    # 定義 full_command，透過管道流直接讀取二進制數據 (-p 代表 png 格式)
    full_command = f'"{adb_path}" -s {constants.ADB_HOST}:{state.adb_port} shell screencap -p'
    
    try:
        # 加上 5 秒超時，萬一 ADB 發生記憶體洩漏卡死，Python 會自動捕捉，而不會無限掛起塞爆 Windows
        result = subprocess.run(full_command, shell=True, capture_output=True, timeout=5)
        
        if result.returncode != 0 or not result.stdout:
            logger.error("ADB 記憶體截圖失敗，可能 ADB 服務暫時離線")
            return None
            
        # 將二進制數據轉換為 OpenCV 圖像
        if platform.system() == 'Windows':
            image_bytes = result.stdout.replace(b'\r\n', b'\n')
        else:
            image_bytes = result.stdout
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("無法解碼記憶體中的截圖數據")
            return None
            
        # 裁剪指定範圍
        if region:
            x, y, w, h = region
            img = img[y:y+h, x:x+w]
            if img.size == 0:
                logger.error(f"裁剪後圖像為空，region={region}")
                return None
                
        # 如果有傳入 name，代表需要存檔（例如隊伍排位截圖 P_char1 等）
        if name:
            local_path = os.path.join(state.image_dir, f"{name}.png")
            cv2.imwrite(local_path, img)
            logger.info(f"圖像已保存到: {local_path}")
            
        return img
        
    except subprocess.TimeoutExpired:
        logger.warning("【⚠️ 警告】截圖超時！檢測到 ADB 響應延遲，正在強制重啟 Python ADB 服務以釋放記憶體...")
        # 如果超時，主動斬斷卡死的 adb 進程，並重啟 adb server 進行自癒
        subprocess.run(f'"{adb_path}" kill-server', shell=True)
        time.sleep(2)
        subprocess.run(f'"{adb_path}" start-server', shell=True)
        return None
    except Exception as e:
        logger.error(f"捕獲螢幕截圖失敗: {e}")
        return None
def tap(x, y, name=None, log=True):  #點擊坐標
    """在設備上的指定坐標 (x, y) 模擬點擊"""
    run_adb_command(f"shell input tap {x} {y}")
    if log:
        logger.info(f"在({x}, {y})點擊，標記名:({name})")
    return True
def swipe(start_x, start_y, end_x, end_y, duration=500):    #滑動畫面
    """從 (start_x, start_y) 滑動到 (end_x, end_y)"""
    run_adb_command(f"shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}")
    logger.info(f"從 ({start_x}, {start_y}) 滑動到 ({end_x}, {end_y}) 速度為{duration}ms")
    time.sleep(1.5)
def force_stop_game():
    """用 ADB 強制停止遊戲 App（不關模擬器）"""
    logger.info(f"強制停止遊戲 App: {constants.GAME_PACKAGE}")
    run_adb_command(f"shell am force-stop {constants.GAME_PACKAGE}")
    time.sleep(2)
    return True
def start_game_app():
    """用 ADB 直接啟動遊戲（取代點擊 gameicon），失敗時先嘗試恢復 ADB"""
    logger.info(f"用 ADB 啟動遊戲: {constants.GAME_PACKAGE}")
    
    for attempt in range(3):
        result = run_adb_command(f"shell monkey -p {constants.GAME_PACKAGE} -c android.intent.category.LAUNCHER 1")
        if result is not None:
            time.sleep(3)
            return True
        
        logger.warning(f"start_game_app 第 {attempt+1} 次失敗，嘗試恢復 ADB")
        # 先嘗試救 ADB，而不是直接認定模擬器掛了
        adb_path = get_adb_path()
        
        subprocess.run(f'"{adb_path}" kill-server', shell=True)
        time.sleep(1)
        subprocess.run(f'"{adb_path}" start-server', shell=True)
        time.sleep(2)
        connect_to_device()
        time.sleep(2)
    
    logger.error("start_game_app 多次重試後仍然失敗")
    return False
def freeze_screen_check(mode=1):
    """
    卡死畫面檢測
    mode 1 = regular（受冷卻時間限制）
    mode 2 = ad hoc（強制檢查，無視冷卻，用於 harken_check 等）
    """
    if not hasattr(state, 'freeze_high_sim_count'):
        state.freeze_high_sim_count = 0

    state.current_time = time.time()

    # 第一次執行的初始化
    if state.first_freeze_screen_check:
        take_screenshot("P_screen_current")
        src = os.path.join(state.image_dir, "P_screen_current.png")
        dst = os.path.join(state.image_dir, "P_screen_previous.png")
        if os.path.exists(src):
            shutil.copy(src, dst)
        state.first_freeze_screen_check = False
        state.freeze_screen_check_time = state.current_time
        state.freeze_high_sim_count = 0
        return False

    # ===== 冷卻判斷（只對 mode=1 生效）=====
    if mode == 1:
        if state.freeze_screen_check_time is not None:
            if (state.current_time - state.freeze_screen_check_time) <= 25:
                return False

    # 開始真正檢查
    take_screenshot("P_screen_current")

    current_path = os.path.join(state.image_dir, "P_screen_current.png")
    previous_path = os.path.join(state.image_dir, "P_screen_previous.png")

    image_current = cv2.imread(current_path)
    image_previous = cv2.imread(previous_path)

    if image_current is None or image_previous is None:
        logger.warning("無法讀取 current/previous 截圖，跳過本次卡死檢查")
        state.freeze_screen_check_time = state.current_time
        return False

    # 黑畫面檢查
    dark_pixels = np.sum(image_current < 30)
    total_pixels = image_current.size
    dark_ratio = dark_pixels / total_pixels
    logger.info(f"目前畫面暗比例:{dark_ratio:.4%}")

    if dark_ratio >= 0.995 or dark_ratio == 0:
        logger.info("黑畫面/沒有畫面，先等待遊戲運行")
        state.freeze_screen_check_time = state.current_time
        state.freeze_high_sim_count = 0
        return False

    # 比對
    result = cv2.matchTemplate(image_current, image_previous, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    if max_val >= 0.995:
        state.freeze_high_sim_count += 1
        logger.warning(f"疑似卡死畫面，連續高相似度次數: {state.freeze_high_sim_count}，當前相似度 {max_val:.4f}")

        if state.freeze_high_sim_count >= 2:
            logger.info(f"確認卡死畫面（相似度 {max_val:.2f}），開始處理")
            # 保存 bug 圖方便之後分析
            shutil.copy(previous_path, "bug_previous.png")
            shutil.copy(current_path, "bug_current.png")

            try:
                force_stop_game()
                time.sleep(2)
                start_game_app()
                time.sleep(5)
            except Exception as e:
                logger.error(f"force-stop 失敗，改關模擬器: {e}")
                if platform.system() == 'Windows':
                        subprocess.run(['taskkill', '/F', '/IM', 'mumunxdevice.exe'], check=False)
                else:
                    # Mac MuMu 的進程名通常是 MuMuNyxDevice 或類似（需實際確認）
                    subprocess.run(['killall', '-9', 'MuMuNyxDevice'], check=False)

            state.freeze_screen_check_time = state.current_time
            state.freeze_high_sim_count = 0
            return True
        else:
            # 第一次疑似時，不要更新 freeze_screen_check_time
            # 讓它可以很快再檢查第二次，mode=2 也能正常累積
            return False
    else:
        # 畫面有變化，重置計數並更新 previous
        state.freeze_high_sim_count = 0
        logger.info(f"卡死畫面檢查通過，相似度 {max_val:.2f}，目標:{state.image_restart}")
        shutil.copy(current_path, previous_path)

    # 只有「確定結果」後才更新時間戳
    state.freeze_screen_check_time = state.current_time
    return False
def load_image(image_name):
    """從預加載字典加載圖像"""
    img = state.preloaded_images.get(image_name)
    if img is None:
        logger.error(f"無法從預加載字典加載圖像: {image_name}")
        return None
    return img.copy()
def find_image(image_list, screenshot=None, similarity=0.7, region=None, log=True, remedial=True, sim_print=False, 
               fail_log=False, reconnect=True, grayscale=True): #畫面上找圖片
    """在給定的螢幕截圖中使用模板匹配查找圖像, 成功返回 image_name, (center_x, center_y), similarity, 失敗返回None"""   
    # (state) global state.image_fail_count, state.freeze_screen_check_time, state.freeze_check_status, state.failed_image_sim, state.image_restart
    if log:
        logger.info(f"find_image開始, 目標{image_list}, 相似度{similarity}, 範圍{region}")
    if screenshot is None:
        screenshot = take_screenshot()
    if state.image_restart:
        state.image_restart = image_list
    # 檢查畫面卡死
    if state.freeze_check_status:
        if freeze_screen_check():
            start_game_player()
    # 將單個圖像名稱轉為列表以統一處理 
    if isinstance(image_list, str):
        find_image_list = [image_list]
    else:
        find_image_list = image_list[:]
    if remedial:
        find_image_list.append("P_reconnect")
        find_image_list.append("P_backtotitle")
        find_image_list.append("P_gameicon2")
        find_image_list.append("P_gameicon3")
    # 裁剪區域（如果指定）
    if region:
        x, y, w, h = region
        screenshot_crop = screenshot[y:y+h, x:x+w]
    else:
        screenshot_crop = screenshot
    for image_name in find_image_list:
        try:
            template = load_image(image_name)
            if template is None:
                continue
                        
            # 模板匹配
            result = cv2.matchTemplate(screenshot_crop, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            logger.debug(f"{image_name}相似度為{max_val:.2f}, 目標相似度為{similarity}")
            # 對比相似度
            if max_val >= similarity:
                template_h, template_w = template.shape[:2]
                center_x = max_loc[0] + template_w // 2
                center_y = max_loc[1] + template_h // 2
                if region:
                    center_x += x
                    center_y += y
                if log:
                    logger.info(f"在 ({center_x}, {center_y}) 找到 {image_name}，相似度 {max_val:.2f}")
                if image_name in ["P_gameicon2", "P_gameicon3"]:
                    """20260831
                    tap(center_x,center_y, "遊戲圖示")
                    game_restart()
                    continue
                    """
                    logger.info(f"find_image 偵測到 {image_name}，改用 ADB 啟動遊戲")
                    force_stop_game()
                    start_game_app()
                    # 關鍵：傳入一個 flag 或直接呼叫，但要避免再觸發 remedial
                    game_restart()
                    return None          # 或 continue，但最好直接 return，讓外層重新開始
                elif image_name == "P_reconnect" and reconnect:
                    check_reconnect()
                elif image_name == "P_backtotitle" and reconnect:
                    check_backtotitle()
                else:
                    state.image_fail_count = 0
                    return (image_name, (center_x, center_y), round(max_val,2))
            else:
                if fail_log:
                    if not image_name in ["P_reconnect", "P_gameicon2", "P_gameicon3", "P_backtotitle"]:
                        logger.info(f"沒有找到 {image_name}，最高相似度 {max_val:.2f}")
                if max_val > state.failed_image_sim:
                    state.failed_image_sim = max_val
        except Exception as e:
            logger.error(f"find_image 錯誤: {image_name}, {str(e)}")
            continue
    if sim_print:
        logger.info(f"{find_image_list}最高相似度 {state.failed_image_sim:.2f}")
    logger.debug(f"未找到任何匹配圖像: {image_list}")
    return None
def findAll(image_list, screenshot=None, similarity=0.7, region=None, log=True, radius_threshold=30):   #畫面上找特定圖片數量
    """在給定的螢幕截圖中使用模板匹配查找所有符合相似度的圖像，返回匹配的圖像數量, 沒有的話返回0"""
    # (state) global state.image_fail_count
    matches = []  # 儲存所有匹配結果 (image_name, center_x, center_y)
    if screenshot is None:
        #logger.info("沒有截圖, 自行截圖中")
        screenshot = take_screenshot()
    if isinstance(image_list, str):
        image_list = [image_list]  # 將單個圖像名稱轉為列表以統一處理
    for image_name in image_list:
        try:
            template = load_image(image_name)
            if template is None:
                continue
            # 轉為灰度圖像
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            # 裁剪區域（如果指定）
            if region:
                x, y, w, h = region
                screenshot_gray = screenshot_gray[y:y+h, x:x+w]
            # 模板匹配
            result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
            # 尋找所有高於相似度閾值的匹配
            locations = np.where(result >= similarity)
            template_h, template_w = template_gray.shape
            for pt in zip(*locations[::-1]):  # 迭代所有匹配位置
                center_x = pt[0] + template_w // 2
                center_y = pt[1] + template_h // 2
                if region:
                    center_x += x
                    center_y += y
                # 檢查新匹配點是否在已有匹配點的 5 像素半徑內
                skip = False
                for _, (existing_x, existing_y) in matches:
                    if (abs(center_x - existing_x) <= radius_threshold and 
                        abs(center_y - existing_y) <= radius_threshold):
                        skip = True
                        break
                if not skip:
                    matches.append((image_name, (center_x, center_y)))
                    if log:
                        logger.info(f"在 ({center_x}, {center_y}) 找到 {image_name}，相似度 {result[pt[1], pt[0]]:.2f}")
            if matches:  # 如果有匹配，重置失敗計數
                state.image_fail_count = 0
        except Exception as e:
            logger.error(f"findAll 錯誤: {image_name}, {str(e)}")
            continue
    if not matches:
        logger.debug(f"未找到任何匹配圖像: {image_list}")
    return len(matches)
def click_image(image_input, timeout=60.0, similarity=0.7, region=None, fail_count=True):    #點擊圖片
    """在螢幕上找到圖像並點擊，限時內執行, 成功返回image_name, 失敗返回None"""
    # (state) global state.paused, state.image_fail_count, state.image_restart, state.image_stage, state.failed_image_sim
    state.image_stage = "click"
    image_list = [image_input] if isinstance(image_input, str) else image_input
    state.image_restart = image_list
    state.failed_image_sim = 0.0
    start_time = time.time()
    logger.info(f"嘗試點擊 {image_list}, 超時{timeout}秒, 相似度要求{similarity}, 範圍 {region}")
    counter = 5
    while time.time() - start_time < timeout:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止點擊")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        screenshot = take_screenshot()
        if screenshot is None:
            logger.error("截圖失敗，跳過本次循環")
            time.sleep(1)
            continue
        counter -= 1
        if counter == 0:
            if check_abnormality():
                timeout +=60
                continue
            counter = 5
        result = find_image(image_list, screenshot, similarity, region, False)
        if result:
            image_name, (x, y), sim = result
            time.sleep(0.1)
            tap(x, y, image_name, log=False)
            logger.info(f"點擊 {image_name}，位置({x},{y})，相似度{sim}，耗時: {time.time() - start_time:.2f}秒")
            state.image_fail_count = 0
            state.image_restart = None
            return image_name
        time.sleep(0.1)
    else:
        logger.info(f"click_image等待超時，目標:{image_list}，最高相似度只有{state.failed_image_sim:.2f}")
    if fail_count:
        state.image_fail_count += 1
    if state.image_fail_count >= 5:
        exitLog("連續5次點擊/等待圖像超時, 退出腳本")
    state.image_restart = None
    logger.info(f"找圖失敗, 當前連續失敗次數{state.image_fail_count}")
    return False
def wait_image(image_input, timeout=60.0, similarity=0.7, region=None, fail_count=True): #等待圖片
    """等待圖像出現在螢幕上，限時內執行, 成功返回image_name, 失敗返回None"""
    # (state) global state.paused, state.image_fail_count, state.image_restart, state.image_stage, state.failed_image_sim
    state.image_stage = "wait"
    image_list = [image_input] if isinstance(image_input, str) else image_input
    state.image_restart = image_list
    state.failed_image_sim = 0.0
    start_time = time.time()
    logger.info(f"嘗試等待 {image_list}, 超時{timeout}秒, 相似度要求{similarity}, 範圍 {region}")
    counter = 5
    while time.time() - start_time < timeout:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止等待")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        screenshot = take_screenshot()
        if screenshot is None:
            logger.error("截圖失敗，跳過本次循環")
            time.sleep(1)
            continue
        counter -= 1
        if counter == 0:
            if check_abnormality():
                timeout +=60
                continue
            counter = 5
        result = find_image(image_list, screenshot, similarity, region, False)
        if result:
            image_name, (x, y), sim = result
            logger.info(f"等待到 {image_name}，位置({x},{y})，相似度{sim}，耗時: {time.time() - start_time:.2f}秒")
            state.image_restart = None
            return image_name
        time.sleep(0.1)
    else:
        logger.info(f"wait_image等待超時，目標:{image_list}，最高相似度只有{state.failed_image_sim:.2f}")
    if fail_count:
        state.image_fail_count += 1
    if state.image_fail_count >= 5:
        exitLog("連續5次點擊/等待圖像超時, 退出腳本")
    state.image_restart = None
    return None
def check_image(image_list, similarity=0.7, region=None):   #檢查圖片是否存在
    """檢查是否任一圖像出現,成功返回(bool, image_name), 失敗返回(bool, None)"""
    screenshot = take_screenshot()
    if screenshot is None:
        logger.error(f"截圖失敗，跳過 check_image({image_list}) 檢查")
        return (False, None)
    result = find_image(image_list, screenshot, similarity, region)
    if result:
        image_name= result[0]
        logger.info(f"check_image成功找到 {image_name}")
        return (True, image_name)
    else:
        logger.info(f"check_image沒有找到 {image_list}")
        return (False, None)
def find_region(image_name, screenshot=None, similarity=0.7, region=None):  #找尋圖片位置
    """在給定的螢幕截圖中使用模板匹配查找單一圖像, 成功返回 region(x, y, w, h), 失敗返回None"""
    # (state) global state.image_fail_count
    if screenshot is None:
        #logger.info("沒有截圖, 自行截圖中")
        screenshot = take_screenshot()
    try:
        template = load_image(image_name)
        # 轉為灰度圖像
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        # 裁剪區域（如果指定）
        if region:
            x, y, w, h = region
            screenshot_gray = screenshot_gray[y:y+h, x:x+w]
        # 模板匹配
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        #logger.info(f"{image_name}相似度為{max_val:.2f}, 目標相似度為{similarity}")
        # 對比相似度
        if max_val >= similarity:
            template_h, template_w = template_gray.shape
            if region:
                max_loc = (max_loc[0] + x, max_loc[1] + y)
            found_region = (max_loc[0], max_loc[1], template_w, template_h)
            logger.info(f"找到 {image_name}，相似度 {max_val:.2f}, 範圍({max_loc[0]}, {max_loc[1]}, {template_w}, {template_h})")
            state.image_fail_count = 0
            return found_region
    except Exception as e:
        logger.error(f"find_image 錯誤: {image_name}, {str(e)}")
    logger.debug(f"未找到任何匹配圖像: {image_name}")
    return None
def waitVanish(image_list, similarity=0.7, region=None, timeout=120):   #等待圖片消失
    """等待某一圖像消失"""
    logger.info(f"waitVanish開始, 目標{image_list}, 相似度要求{similarity}, 範圍{region}, 最長時限{timeout}秒")
    match_count = 0
    if isinstance(image_list, str):
        image_list = [image_list] 
    match = find_image(image_list, similarity=similarity, region=region, log=False)
    if match:
        logger.info(f"找到{image_list}，等待{image_list}消失")
    else:
        logger.info(f"沒有找到{image_list}")
        return False
    start_time = time.time()
    while time.time() - start_time < timeout:
        if match_count <= 3:
            time.sleep(0.01)
            match = find_image(image_list, similarity=similarity, region=region, log=False)
            if match:
                match_count = 0
            else:
                match_count += 1
        else:
            logger.info(f"{image_list}已消失，waitVanish完成")
            return True
    else:
        logger.info("waitVanish()等待超時")
        return False
def waitBattleVanish(similarity=0.7, region=None, timeout=120):   #等待戰鬥消失
    """等待某一圖像消失"""
    logger.info(f"waitBattleVanish開始, 相似度要求{similarity}, 範圍{region}, 最長時限{timeout}秒")
    image_list = ["P_fastbattle_active", "P_fastbattle_inactive"] 
    match = find_image(image_list, similarity=similarity, region=region, log=False)
    if match:
        logger.info(f"找到{image_list}，等待{image_list}消失")
    else:
        logger.info(f"沒有找到{image_list}")
        return False
    match_count = 0
    loop_count = 0
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        if match_count <= 3:
            time.sleep(0.01)
            match = find_image(image_list, similarity=similarity, region=region, log=False)
            if match:
                match_count = 0
            else:
                match_count += 1
            loop_count += 1
            if loop_count == 10:
                if find_image(constants.P_AUTOBATTLE_INACTIVE_LIST, log=False):
                    click_image(constants.P_AUTOBATTLE_INACTIVE_LIST)
                loop_count = 0
                check_reconnect()
        else:
            logger.info(f"沒有找到{image_list}")
            return False
    else:
        logger.info("waitBattleVanish()等待超時")
        return False
def image_stability(image, similarity=0.7, max_attempts=1, delay=0.1):  #檢查圖片穩定度
    """檢查圖像是否穩定出現"""
    # (state) global state.images_list, state.handle_loop_list
    if image == None:
        return False
    if state.images_list == None:
        search_list = state.handle_loop_list[:]
    else:
        search_list = state.images_list[:]
    logger.info(f"開始檢查 {image} 是否穩定出現，次數: {max_attempts}")
    for i in range(max_attempts):
        if image == "P_exit":
            if not find_image(search_list, similarity=similarity):
                logger.info(f"第 {i+1} 次檢查未找到 {image}，中斷檢查")
                return False
        else:
            if not find_image(image, similarity=similarity):
                logger.info(f"第 {i+1} 次檢查未找到 {image}，中斷檢查")
                return False
        time.sleep(delay)
    logger.info(f"{image} 連續檢查通過，確認穩定出現")
    return True

# 補給函數
def inn_rest(): #旅館休息
    """旅館休息"""
    # (state) global state.run_count, state.heal_period, state.inn_mode
    if (state.run_count+1)%state.heal_period == 0:
        logger.info(f"目前次數{state.run_count+1}次，補給間隔{state.heal_period}次，滿足條件進行補給")
        click_image("P_inn")
        click_image("P_inn_rest")
        if state.inn_mode == 3:
            click_image("P_inn_standardroom")
        elif state.inn_mode == 4:
            click_image("P_inn_richroom")
        click_image("P_inn_rest_confirm", similarity=0.8)
        click_image("P_inn_rest_dialog1")   
        time.sleep(1)  
        check = click_image(["P_inn_rest_bagrefill", "P_inn_rest_dialog2", "P_inn_rest_dialog3"], similarity=0.68)
        if check == "P_inn_rest_bagrefill":
            click_image(["P_inn_rest_dialog2", "P_inn_rest_dialog3"])
        for i in range(50):
            check = wait_image(["P_inn_leave","P_inn_levelup_skill","P_inn_levelup_close", "P_inn_levelup_next"])
            if check == "P_inn_leave":
                break
            elif check in ["P_inn_levelup_skill","P_inn_levelup_close", "P_inn_levelup_next"]:
                click_image(["P_inn_levelup_skill","P_inn_levelup_close", "P_inn_levelup_next"], timeout=3)
        click_image("P_inn_leave")
    else:
        logger.info(f"目前次數{state.run_count}次，補給間隔{state.heal_period}次，不用補給")
def bag(sim=0.7, outside=True):  #補充背包
    """補充背包"""
    click_image("P_bag_tidy", similarity=sim)
    click_image("P_bag_refill")
    match = wait_image(["P_bag_buybutton", "P_bag_refill_complete"])
    if match == "P_bag_buybutton":
        click_image("P_bag_buybutton")
    click_image("P_bag_refill_complete")
    if outside:
        wait_image(["P_town", "P_village", "P_worldMap"])
def heal(): #角色治癒
    """治癒角色"""
    logger.info("執行治癒角色")
    if find_image(["P_fastbattle_active", "P_fastbattle_inactive"]):
        logger.info("找到戰鬥畫面, 跳過治癒角色")
    tap(constants.L_heal_char[0], constants.L_heal_char[1], "constants.L_heal_char")
    if wait_image("P_heal_close", timeout=5):
        time.sleep(1.5)
        tap(constants.L_heal_button_main[0], constants.L_heal_button_main[1], "constants.L_heal_button_main")
        click_image("P_heal_confirm")
        time.sleep(5)
        click_image("P_heal_close")
        logger.info("執行治癒角色成功")
        return True
    else:
        click_image("P_heal_close", fail_count=False, timeout=2)
        logger.info("執行治癒角色失敗")
        return False
def health_check(): #檢查異常狀態
    # (state) global state.debuff_list
    if find_image(state.debuff_list, similarity=0.8, region=constants.R_char_dungeon[0], sim_print=True):
        heal()
def rest_check():   #地城補給檢查
    """檢查補給間隔進行補給"""
    # (state) global state.heal_period, state.run_count
    if (state.run_count+1)%state.heal_period == 0:
        logger.info(f"目前次數{state.run_count+1}次，補給間隔{state.heal_period}次，滿足條件進行補給")
        bag()
        time.sleep(1)
        heal()
        return True
    else:
        logger.info(f"目前次數{state.run_count+1}次，補給間隔{state.heal_period}次，不用補給")
    return False
def general_inn_mode(mode): #常規休息設定 #mode1是野外用; mode2是城市用
    """mode1是野外用; mode2是城市用"""
    # (state) global state.inn_mode, state.heal_period, state.run_count
    logger.info(f"當前次數:{state.run_count};回復間隔:{state.heal_period}")
    if not (state.run_count+1)%state.heal_period == 0:
        return False
    else:
        logger.info("符合條件, 執行回復")
    if state.inn_mode == 1:
        if mode == 1:
            rest_check()
        elif mode == 2:
            click_image("P_outside")
            rest_check()
            click_image(["P_town", "P_village", "P_worldMap"])
            inn_check()
    elif state.inn_mode == 3 or state.inn_mode ==4:
        if mode == 1:
            click_image(["P_town", "P_village", "P_worldMap"])
            inn_check()
            inn_rest()
            inn_check()
            click_image("P_outside")
        elif mode == 2:
            inn_rest()
def store_equip(equipment, similarity=0.72):
    #裝指定裝備放進倉庫
    # (state) global state.equip_count
    tap(159, 1317)  #左上1號角色
    click_image("P_charInfo_bag")
    wait_image("P_charInfo_itemlist")
    equip_temp = findAll(equipment, similarity=similarity)
    state.equip_count = state.equip_count + equip_temp
    logger.info(f"找到{equip_temp}件{equipment}")
    if equip_temp >0:
        for i in range(equip_temp):
            click_image(equipment)
            click_image("P_back_to_warehouse")
            time.sleep(2)
    click_image("P_heal_close")
    return True

# 戰鬥函數
def revive_npc():   #復活NPC
    # (state) global state.revive_status
    if not state.revive_status:
        exitLog("自動嘗試復活為False，中斷腳本")
    logger.info("發現NPC死亡，嘗試隨機復活")
    tap(450,800, "復活")
    for i in range(6):
        if not find_image(["P_battle_death_npc1", "P_battle_death_npc2"]):
            logger.info("NPC死亡復活畫面消失")
            time.sleep(2)
            check = wait_image(["P_fastbattle_active", "P_fastbattle_inactive", "P_battle_death_main", "P_battle_death_fire"], similarity=0.7)
            if check in ["P_battle_death_main", "P_battle_death_fire"]:
                revive_main()
            break
        random_delay(4)
        tap(450,800, "復活")
    return True
def revive_main():  #主角再起
    # (state) global state.revive_status, state.stage, state.revived_bol
    state.revived_bol = True
    if not state.revive_status:
        exitLog("沒有自動再起，中斷腳本")
    time.sleep(3)
    fire_count = findAll("P_battle_death_fire", similarity=0.75, region=(0, 0, 900, 800))
    logger.info(f"發現主角死亡，再起之火數量:{fire_count}")
    if  fire_count == 1:
        messagebox.showinfo("提示", "再起之火只餘下一個")
        exit(0)
    else:
        click_image("P_battle_death_main", similarity=0.6)
        time.sleep(2)

    return True
def reteam_pre():   #隊伍排位位置截圖
    logger.info("進行隊伍排位位置截圖")
    take_screenshot(name="P_char1", region=(24, 1270, 275, 30))     #中心點(162, 1285)
    take_screenshot(name="P_char2", region=(316, 1270, 275, 30))    #中心點(454, 1285)
    take_screenshot(name="P_char3", region=(602, 1270, 275, 30))    #中心點(740, 1285)
    take_screenshot(name="P_char4", region=(24, 1450, 275, 30))     #中心點(162, 1465)
    take_screenshot(name="P_char5", region=(316, 1450, 275, 30))    #中心點(454, 1465)
    take_screenshot(name="P_char6", region=(602, 1450, 275, 30))    #中心點(740, 1465)
    for i in range(1, 7):
        name = "P_char" + str(i)
        path = os.path.join(state.image_dir, name + ".png")
        img = cv2.imread(path)
        if img is not None:
            state.preloaded_images[name] = img
        else:
            logger.error(f"無法預加載圖像: {path}")
    return True
def reteam():   #隊伍企位檢查
    """檢查並重新排列角色到正確的 char_region"""
    char_region = {
        "char_box1": (10, 1255, 305, 60),
        "char_box2": (305, 1255, 305, 60),
        "char_box3": (590, 1255, 305, 60),
        "char_box4": (10, 1435, 300, 60),
        "char_box5": (305, 1435, 305, 60),
        "char_box6": (590, 1435, 305, 60),
    }
    char_center = {
        "P_char1": (162, 1285),
        "P_char2": (454, 1285),
        "P_char3": (740, 1285),
        "P_char4": (162, 1465),
        "P_char5": (454, 1465),
        "P_char6": (740, 1465),
    }
    char_mapping = {
    "char_box1": "P_char1",
    "char_box2": "P_char2",
    "char_box3": "P_char3",
    "char_box4": "P_char4",
    "char_box5": "P_char5",
    "char_box6": "P_char6",
    }
    tap(constants.L_reteam[0], constants.L_reteam[1], "隊伍整理")
    logger.info("開始檢查並重新排列角色")
    for box, expected_char in char_mapping.items():
        region = char_region[box]
        logger.info(f"檢查{box}")
        # 檢查所有可能的角色圖像
        screenshot = take_screenshot()
        for char_name in char_center.keys():
            result = find_image(char_name, screenshot=screenshot, region=region, remedial=False, log=False)
            if result:
                if char_name == expected_char:
                    logger.info(f"{box} 已包含正確角色 {char_name}")
                    break
                else:
                    logger.info(f"{box} 找到錯誤角色 {char_name}，應為 {expected_char}")
                    # 找到正確的目標區域
                    target_box = [k for k, v in char_mapping.items() if v == char_name][0]
                    start_x, start_y = char_center[char_name]
                    end_x, end_y = char_center[expected_char]
                    logger.info(f"拖拉 {char_name} 從 {box} ({start_x}, {start_y}) 到 {target_box} ({end_x}, {end_y})")
                    swipe(start_x, start_y, end_x, end_y, duration=500)
                    time.sleep(0.5)  # 等待拖拉完成
                    break
        else:
            logger.warning(f"{box} 未找到任何角色圖像")
    logger.info("角色重新排列完成")
    tap(constants.L_reteam[0], constants.L_reteam[1], "隊伍整理")
def battle_skill(enemy_list=None): #技能戰鬥
    """
    enemy_list 支援格式：
        None                          → 使用原本的網格點擊
        [(x, y), (x, y, "備註"), ...] → 依序點擊指定座標
    範例：
        battle_skill([(100, 200, "女妖"), (300, 400, "巨人")])
        battle_skill([(450, 850)])                 # 只有座標也可以
    """
    # ---------- 1. 資料驗證與正規化 ----------
    validated_enemies = None

    if enemy_list is not None:
        if not isinstance(enemy_list, (list, tuple)):
            logger.error(f"enemy_list 格式錯誤，應為 list/tuple，實際收到: {type(enemy_list)}")
            return False

        validated_enemies = []
        for idx, item in enumerate(enemy_list):
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                logger.error(f"enemy_list 第 {idx} 項格式錯誤，應為 (x, y) 或 (x, y, 備註)，實際: {item}")
                return False

            x, y = item[0], item[1]
            note = item[2] if len(item) >= 3 else f"敵人{idx+1}"

            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                logger.error(f"enemy_list 第 {idx} 項座標必須是數字，實際: x={x}, y={y}")
                return False

            validated_enemies.append((int(x), int(y), str(note)))

        logger.info(f"技能戰鬥目標敵人: {validated_enemies}")
    
    for i in range(100):
            match = wait_image(["P_battle_bar", "P_chest_open", "P_exit", "P_battle_death_main", "P_battle_death_npc1", "P_battle_death_npc2"], 
                               similarity=0.8)
            if match == "P_battle_bar":
                time.sleep(0.5)
                tap(553,1103, "右下技能")
                if click_image("P_aoe_confirm", timeout=1.5, fail_count=False):
                    if find_image("P_battle_noSPMP"):
                        click_image("P_battle_noSPMP")
                        click_image("P_battle_baseattack")
                if find_image("P_battle_detail", region=(0,0,900,1000)):
                    tap(453,1196,"2號角色")
                if validated_enemies is None:
                    for j in range (3):
                        for i in range(1,11):
                            if find_image(["P_battle_detail","P_battle_baseattack"], log=False):
                                tap(i*75, 800-j*50, log=False)
                            else:
                                break
                        else:
                            tap(899, 800 - j * 50, log=False)
                else:
                    for x, y, note in validated_enemies:
                        tap(x, y, note)
                        time.sleep(0.15)
            elif match == "P_chest_open":
                    open_chest()
            elif match == "P_exit":
                if image_stability("P_exit", max_attempts=1):
                    break
            elif match == "P_battle_death_main":
                revive_main()
                wait_image("P_exit")
                time.sleep(1)
                press_key("w")
            elif match in ["P_battle_death_npc1", "P_battle_death_npc2"]:
                revive_npc()
    return True

# 寶箱函數
def check_chest(map_name=None, check_region=None, forbidden_mode=True, map_similarity=0.7):   #小地圖找箱子
    # 定義禁止範圍 #constants.R_chest_map_region
    forbidden_regions = [
        (0, 627, 155, 267),   # 左側箭頭範圍
        (320, 1165, 260, 150), # 下側箭頭範圍
        (741, 631, 158, 214),  # 右側箭頭範圍
        (320, 193, 264, 172)   # 上側箭頭範圍
    ]
    logger.info(f"check_chest開始，限定位置:{map_name}，相似度{map_similarity}，範圍:{check_region}，四邊避箱:{forbidden_mode}")
    chest_result = map_name_list =  None
    if map_name:
        map_name_list = [map_name] if isinstance(map_name, str) else map_name
    if map_name_list:
        for map_area in map_name_list:
            chest_region = find_region(map_area)
            if chest_region:
                chest_result = find_image("P_chest", region=chest_region, similarity=map_similarity)
                if chest_result:
                    break
                else:
                    logger.info(f"{map_area}沒有找到箱子")
    else:
        chest_result = find_image("P_chest", region=check_region)
    if not chest_result:
        logger.info("所有位置沒有找到寶箱")
        return False  # 未找到寶箱
    (x, y) = chest_result[1]
    logger.info(f"找到寶箱，坐標({x}, {y})")
    if forbidden_mode:
        for x1, y1, w1, h1 in forbidden_regions:
            if x1 < x < x1 + w1 and y1 < y < y1 + h1:
                logger.info("寶箱坐標在禁止點擊範圍，跳過寶箱")
                return False
    click_image("P_chest", region=check_region)
    click_image(["P_automove","P_automove2"])
    return True  # 成功點擊寶箱
def find_chest(map=None, swipe_action=None, forbidden_mode=True, map_similarity=0.7):   #找箱子流程
    """尋找並打開寶箱"""
    # (state) global state.trap_char_all_scared
    logger.info("find_chest 開始")
    health_check()
    tap(constants.L_Minimap[0], constants.L_Minimap[1], "小地圖")
    time.sleep(1)
    if not find_image("P_minimap_close"):
        logger.info("沒有成功進入地圖畫面，中斷find_chest")
        return True
    if check_chest(map_name=map, forbidden_mode=forbidden_mode):
        time.sleep(1)
        if find_image("P_minimap_close"):
            logger.info("點擊auto_move失敗，退出重來")
            click_image("P_minimap_close")
            return True
        logger.info("find_chest 找到箱子, 開始前往")
        return True
    if swipe_action:
        swipe_list = [swipe_action] if isinstance(swipe_action, str) else swipe_action
        for action in swipe_list:
            if not find_image("P_minimap_close"):
                logger.info("沒有成功進入地圖畫面，中斷find_chest")
                return True
            swipe_map(action)
            if check_chest(map_name=map, forbidden_mode=forbidden_mode, map_similarity=map_similarity):
                logger.info("find_chest 找到箱子, 開始前往")
                return True
    click_image("P_minimap_close")
    logger.info("find_chest 沒有找到箱子")
    return False
def find_chest_fixed(map, forbidden_mode=True): #固定位置找箱子流程
    """打開地圖固定範圍尋找並打開寶箱"""
    # (state) global state.trap_char_all_scared
    logger.info(f"find_chest_fixed 開始, 範圍{map}")
    tap(constants.L_Minimap[0], constants.L_Minimap[1], "小地圖")
    time.sleep(1)
    minimap_result = find_image(["P_minimap_close"])
    if not minimap_result:
        logger.info("沒有成功進入地圖畫面，中斷find_chest_fixed")
        return True
    map_list = [map] if isinstance(map, str) else map
    for chestarea in map_list:
        if find_region(chestarea):
            result = check_chest(map_name=chestarea, forbidden_mode=forbidden_mode)
            if result:
                logger.info(f"{chestarea}找到箱子, 開始前往")
                return True
            else:
                logger.info(f"{chestarea}沒有找到箱子")
        else:
            logger.error(f"沒有找到{chestarea}")
    click_image("P_minimap_close")
    return False
def find_chest_process(map=None, direction=["left","down","right","up"], forbidden_mode=True): #流動找箱子
    # (state) global state.trap_char_all_scared, state.handle_loop_list
    direction_list = [direction] if isinstance(direction, str) else direction
    while state.trap_char_all_scared == False:
        match = wait_image(state.handle_loop_list)
        logger.info(f"找到匹配: {match}")
        if match == "P_exit":
            if image_stability("P_exit", max_attempts=2):
                if find_chest(map=map, swipe_action=direction_list, forbidden_mode=forbidden_mode, map_similarity=0.75):
                    #wait_image(["P_chest_open", "P_fastbattle_active", "P_fastbattle_inactive", "P_dungeon_suspicious_trader"])
                    waitVanish("P_exit")
                else:
                    logger.info("find_chest完結, 即將離開")
                    break
        else:
            common_reaction(match, None)  # state.stage=None，因為此處不依賴 state.stage
        time.sleep(0.5)
    else:
        logger.info("開箱角色全部開箱恐懼, 即將離開")
def find_chest_auto(heal_check=True):
    """利用自動找箱子功能找箱"""
    def auto_chest():
        if not find_image("P_autochest"):
            tap(761,320, "展開地圖功能")
        if click_image("P_autochest", timeout=3):
            if wait_image(["P_noChest", "P_noPath"], timeout=5, fail_count=False):
                logger.info("出現「沒有找到箱子或無法找到路徑」情況")
                return False
            else:
                logger.info("「自動找箱功能」找到箱子")
                return True    
    # (state) global state.trap_char_all_scared
    for i in range(20):
        if state.trap_char_all_scared == False:
            match = wait_image(state.handle_loop_list)
            logger.info(f"找到匹配: {match}")
            if match == "P_exit":
                if heal_check and image_stability("P_exit", max_attempts=1):
                    health_check()
                    if auto_chest():
                        waitVanish("P_exit", timeout=15)
                    else:
                        logger.info("auto_chest完結, 即將離開")
                        break
                else:
                    continue
            else:
                common_reaction(match, None)  # state.stage=None，因為此處不依賴 state.stage
            time.sleep(0.5)
        else:
            logger.info("開箱角色全部開箱恐懼, 即將離開")
            return True
    else:
        logger.info("已觸發15次開箱，提早完結")
        return True
def open_chest():   #開箱流程
    """打開寶箱並選擇角色"""
    # (state) global state.chest_count, state.chest_char, state.chest_char_list, state.trap_char_all_scared, state.trap_mode, state.trap_ar_indicator, state.target_until, state.on9npc_list
    if state.chest_count == 0:
        state.chest_char_list.clear()
        for digit in str(state.chest_char):
            index = int(digit)
            state.chest_char_list.append(constants.R_chest_char[index])
    logger.info("嘗試打開寶箱")
    click_image("P_chest_open")
    time.sleep(2)
    wait_image("P_chest_close")
    for i, region in enumerate(state.chest_char_list):
        logger.info(f"檢查第{i+1}個角色是否可開啟寶箱")
        if not find_image("P_chest_scaryIcon", similarity=0.7, region=region):
            logger.info(f"第{i+1}個角色無 P_chest_scaryIcon，點擊")
            tap(region[0] + region[2] // 2, region[1] + region[3] // 2, f"第{i+1}個開箱角色")
            check = wait_image(["P_chest_scary_dialog", "P_chest_trap", "P_chest_gain", "P_chest_ar"], similarity=0.65)
            if check == "P_chest_scary_dialog":
                click_image("P_chest_scary_dialog")
                time.sleep(1)
            elif check in ["P_chest_trap", "P_chest_gain", "P_chest_ar"]:
                break
        else:
            logger.info(f"第{i+1}個角色有 P_chest_scaryIcon，檢查下一個")
    else:
        click_image("P_chest_close", timeout=3)
        logger.info("全部開箱角色有 P_chest_scaryIcon無法開箱")
        state.trap_char_all_scared = True
        return False
    state.chest_count += 1
    try:
            state.app.chest_count_var.set(f"{state.chest_count}")
    except NameError:
        logger.warning("GUI 未初始化，無法更新 chest_count_var")
    if check == "P_chest_trap":
        if state.trap_mode == 1:
            trap1()
        elif state.trap_mode == 2:
            trap2()
        elif state.trap_mode == 3:
            trap3()
    logger.info("開始獲取寶箱物品")
    match_list = ["P_chest_gain", "P_chest_scary", "P_chest_ar", "P_exit"]
    until_list = []
    logger.info(f"state.target_until: {state.target_until}")
    for i in range(10):
        logger.info(f"第 {i+1} 次，檢查 {match_list}")
        match = wait_image(match_list, timeout=5)
        if match in ["P_chest_ar", "P_chest_scary", "P_chest_gain", "P_chest_lost"]:
            if match == "P_chest_ar":
                state.trap_ar_indicator = True
                for item in ["P_battle_death_main", "P_fastbattle_active", "P_fastbattle_inactive"]:
                    match_list.append(item)
                match_list.remove("P_exit")
            elif match == "P_chest_gain":
                match_list = ["P_chest_gain", "P_chest_lost", "P_exit", "P_chest_open", "P_fastbattle_active", "P_fastbattle_inactive"]
                if state.target_until:
                    until_list = [state.target_until] if isinstance(state.target_until, str) else state.target_until
                    for item in until_list:
                        if not item in match_list:
                            match_list.append(item)
            click_image(match_list, timeout=3, fail_count=False) #用match_list有機會點了P_exit!!
        elif match == "P_exit":
            if image_stability("P_exit", max_attempts=2):
                logger.info(f"匹配到P_exit，完成物品獲取")
                break
        elif match in until_list:
            if image_stability(until_list, max_attempts=2):
                logger.info(f"匹配到{until_list}，完成物品獲取")
                break
        elif match in ["P_chest_open", "P_fastbattle_active", "P_fastbattle_inactive"]:
            logger.info("檢測到開箱/戰鬥畫面，已完成物品獲取，中斷目前開箱流程")
            break
        elif match == "P_battle_death_main":
            logger.info("檢測到死亡畫面，已完成物品獲取，中斷目前開箱流程")
            break
        else:
            if state.on9npc_list: #防中途撞on9npc
                on9_check = find_image(state.on9npc_list)
                if on9_check:
                    common_reaction(on9_check[0], None)
        time.sleep(0.5)
    logger.info(f"open_chest 完成，當前 state.chest_count: {state.chest_count}")
    return True        
def trap1():    #放棄拆陷阱模式
    """關閉帶陷阱的寶箱"""
    logger.info("發現陷阱，state.trap_mode = 1")
    tap(constants.L_trap_exit[0], constants.L_trap_exit[1], "取消解除陷阱")
    logger.info("不打開帶陷阱的寶箱，退出")
def trap2():    #隨機拆陷阱模式
    """隨機移除陷阱"""
    logger.info("發現陷阱，state.trap_mode = 2")
    for i in range(5):
        tap(constants.L_trap_remove[0], constants.L_trap_remove[1], "解除陷阱")
        logger.info(f"移除陷阱嘗試: {i+1}")
        random_delay(4)
        if find_image(["P_chest_gain", "P_chest_scary", "P_chest_ar"], similarity=0.7):
            logger.info("[P_chest_gain, P_chest_scary, P_chest_ar]出現，結束循環")
            break
def trap3():    #測速拆陷阱模式 #未完成
    pass

# 跑圖函數
def comment_check():
    if find_image("P_comment1"):
        click_image("P_comment2")
        click_image("P_comment3")
        return True
    return False
def inn_check():    #城鎮檢查
    """檢查旅館對話框並處理意外對話框"""
    # (state) global state.paused
    for i in range(50):
        if comment_check():
            continue
        logger.info("在點擊 P_inn 前出現對話框")
        tap(450, 50, "畫面上方", log=False)
        time.sleep(1)
        if find_image("P_inn", similarity=0.7, log=False):
            image_stability("P_inn", max_attempts=1)
            logger.info("P_inn 出現")
            break
def common_reaction(match, stage): #基本動作處理
    """
    處理遊戲循環中特定圖像匹配的通用反應。
    參數:
        match (str): 匹配到的圖像標識符（如 'P_chest_open', 'P_fastbattle_active' 等）。
        state.stage (str): 當前階段（'Cmove', 'Exit' 或 None）。
    返回:
        bool: 如果執行了操作返回 True，否則返回 False。
    """
    def stage_check(stage):
        wait_image("P_exit", timeout=3)
        if state.stage == "Cmove":
            if find_image("P_Cmove", similarity=0.7):
                click_image("P_Cmove", timeout=3)
                return True
        elif state.stage == "Exit":
            if find_image("P_exit", similarity=0.7):
                click_image("P_exit", timeout=3)
                return True
    
    # (state) global state.bs_restarted, state.target_checkpoint, state.restart_relocation, state.trap_ar_indicator, state.battle_mode, state.personality_count, state.personality_action, state.personality_score, state.personality_choice
    #開箱流程
    if match == "P_chest_open":
        logger.info("處理 P_chest_open")
        open_chest()
        if state.trap_ar_indicator == True:
            stage_check(state.stage)
            state.trap_ar_indicator = False
        logger.info("command_reaction函數，開箱部份完成")
        return True
    #戰鬥流程
    elif match in ["P_fastbattle_active", "P_fastbattle_inactive"]:
        logger.info(f"處理戰鬥狀態: {match}")
        battle_status = True
        while battle_status == True:
            if find_image("P_fastbattle_inactive", similarity=0.8):
                click_image("P_fastbattle_inactive", similarity=0.8, timeout=3)
                pass
            if state.battle_mode == "自動戰鬥":
                if find_image(constants.P_AUTOBATTLE_INACTIVE_LIST,similarity=0.75):
                    click_image(constants.P_AUTOBATTLE_INACTIVE_LIST, timeout=3)
            elif state.battle_mode == "技能戰鬥":
                battle_skill()
            waitBattleVanish(similarity=0.75)
            time.sleep(3)
            check = find_image(["P_battle_death_npc1", "P_battle_death_npc2", "P_battle_death_main", "P_battle_death_fire"], similarity=0.9)
            if check:
                image = check[0]
                if image in ["P_battle_death_npc1", "P_battle_death_npc2"]:
                    revive_npc()
                elif image in ["P_battle_death_main", "P_battle_death_fire"]:
                    revive_main()      
                else:
                    logger.info("可能出現BUG了")
            else:
                battle_status = False
        logger.info("command_reaction函數，戰鬥部份完成")
        return True
    #閒置流程
    elif match == "P_exit":
        def target_checkpoint_check():
            if find_image(state.target_checkpoint):
                click_image(state.target_checkpoint)
                click_image("P_automove")
                return True
            return False
            
        logger.info(f"進入 P_exit 處理，state.bs_restarted:{state.bs_restarted} / state.restart_relocation::{state.restart_relocation}")
        if state.bs_restarted and state.restart_relocation:
            logger.info("模擬器曾重啟，重新找路中")
            state.bs_restarted = False
            tap(constants.L_Minimap[0], constants.L_Minimap[1], "小地圖")
            time.sleep(1)
            check = find_image(["P_minimap_close"])
            time.sleep(1)
            if target_checkpoint_check():
                return True
            else:
                for i in range(2):
                    for action in ["up", "left", "down", "right"]:
                        swipe_map(action)
                        time.sleep(0.5)
                        if target_checkpoint_check():
                            logger.info("找到目標checkpoint，前進中")
                            return True
                        time.sleep(0.5)
                else:
                    logger.info("沒有找到目標checkpoint")
        if image_stability("P_exit"):
            logger.info("P_exit 迴圈檢查通過")
            stage_check(state.stage)
        else:
            logger.info("未找到 P_exit，重新尋找匹配")
        return True
    #再起(應該是中陷阱死了)
    elif match == "P_battle_death_main":
        revive_main()
    #觸發敵人盯住你選項
    elif match == "P_battle_enemylookingatu":
        #還有個P_battle_fight選項是性格-1
        def good_action():
            # (state) global state.personality_count
            logger.info("面具人性格想變好，所以大發慈悲放過敵人")
            state.personality_count += 1
            click_image("P_battle_letthemgo", timeout=3)
            click_image(["P_battle_enemygone", "P_battle_dropsomething", "P_battle_enemywantfight"], timeout=3)
        def bad_action():
            # (state) global state.personality_count
            logger.info("面具人性格想變壞，所以戰鬥吧")
            state.personality_count -= 2
            click_image("P_battle_blindside", timeout=3)
        click_image("P_battle_enemylookingatu", timeout=3)
        logger.info(f"觸發性格變化選項，目前選項:{state.personality_choice}，目前性格變化程度:{state.personality_count}，目標性格變化程度{state.personality_score}")
        if state.personality_count <= state.personality_score:
            good_action()
        else:
            bad_action()
    #觸發可疑商人選項
    elif match == "P_dungeon_suspicious_trader":
        click_image("P_dungeon_suspicious_trader")
        temp_check = click_image(["P_dungeon_suspicious_trader_buy2000", "P_dungeon_suspicious_trader_lookgoods"])
        if temp_check == "P_dungeon_suspicious_trader_lookgoods":
            click_image("P_dungeon_suspicious_trader_buy2000")
        click_image("P_dungeon_gain")
        stage_check(state.stage)
    #觸發骨頭商人選項
    elif match == "P_dungeon_bone_trader":
        click_image("P_dungeon_bone_trader")
        check = click_image(["P_dungeon_bone_trader_buybone", "P_dungeon_bone_trader_dontbuy"])
        if check == "P_dungeon_bone_trader_buybone":
            click_image("P_dungeon_bone_trader_gotbone")
    #擋路NPC大全
    elif match in constants.ON9NPC_CLICK_LIST:
        click_image(constants.ON9NPC_CLICK_LIST)
    elif match == "P_ch1_on9npc2":
        click_image("P_ch1_on9npc2")
        click_image("P_ch1_on9npc2_option2", timeout=3)
    elif match == "P_ch1_on9npc3":
        click_image("P_ch1_on9npc3")    
    elif match == "P_ch2_on9npc2":
        click_image("P_ch2_on9npc2")
        click_image("P_ch2_on9npc2_option1")
    elif match == "P_ch2_on9npc3":
        click_image("P_ch2_on9npc3")
        click_image("P_ch2_on9npc3_2")
    elif match == "P_ch4_on9npc1":  #深雪盜賊
        click_image("P_ch4_on9npc1")
        click_image("P_ch4_on9npc1B")
    elif match == "P_ch4_on9npc2":  #拾骨者
        click_image("P_ch4_on9npc2")
        click_image("P_ch4_on9npc2_2", timeout=5)
        wait_image("P_ch4_on9npc2B")
        if find_image("P_ch4_on9npc2A"):
            click_image("P_ch4_on9npc2A")
        else:
            click_image("P_ch4_on9npc2B")
    elif match == "P_ch4_on9npc4":
        click_image("P_ch4_on9npc4")
        click_image("P_ch4_on9npc4B")
    elif match == "P_ch4_on9npc3":
        click_image("P_ch4_on9npc3")
        click_image("P_ch4_on9npc3A")
        click_image("P_ch4_on9npc3B")
    elif match == "P_GhostIsland_on9npc1":
        click_image("P_GhostIsland_on9npc1")
    elif match == "P_Cave_BigRock1":
        click_image("P_Cave_BigRock1")
        click_image("P_Cave_BigRock1_2")
    #閃退出homepage
    elif match == "P_gameicon2":
        click_image("P_gameicon2")
        game_restart()
    return False
def handle_loop(target, timeout=10000):   #動作處理loop
    """處理地圖循環，檢查目標圖像並執行操作, target支援list"""
    # (state) global state.stage, state.bs_restarted, state.images_list
    logger.info(f"進入 handle_loop，目標: {target}，時限:{timeout}秒")
    state.bs_restarted = False
    state.images_list = state.handle_loop_list[:]
    if isinstance(target, list):
        for item in range(len(target)):
            state.images_list.insert(item, target[item])
    else:
        state.images_list.insert(0, target)
    start_time = time.time()
    loop_counter = 1
    while time.time() - start_time <= timeout:
        loop_time = time.time()
        logger.info(f"handle_loop 計數: {loop_counter}，模擬器重啟記錄{state.bs_restarted}")
        match = wait_image(state.images_list, similarity=0.7)
        if match == None:
            loop_counter += 1
        logger.info(f"handle_loop 期間，目標: {target}，找到: {match}")
        if match == target or match in target:
            logger.info(f"找到目標 {target}")
            if image_stability(target):
                logger.info(f"確認找到 {target}，退出循環")
                return match
        elif common_reaction(match, state.stage):
            logger.info(f"common_reaction 處理 {match} 完成")
        logger.info(f"處理 handle_loop 操作，計數 +1，耗時: {time.time() - loop_time:.2f}秒")
        loop_counter += 1
        time.sleep(0.05)
    else:
        exitLog(f"耗時: {time.time() - loop_time:.2f}秒, handle_loop 超時，未找到 {target}")
    logger.info(f"完成 handle_loop，耗時: {time.time() - start_time:.2f}秒")
    state.images_list = None
    state.bs_restarted = False #重置bs_restarted, 準備流入下一次流程
    return False
def goMap(checkpoint, until, swipe_action=None, timeout=6000, relocation=True, goMap_similarity=0.7, heal_check=True, exit_check=False):  #前往指定位置
    """前往指定地圖檢查點, return matched until"""
    # (state) global state.stage, constants.R_char_dungeon, state.target_checkpoint, state.restart_relocation, state.minimap_list, state.handle_loop_list, state.target_until
    state.restart_relocation = relocation
    logger.info(f"goMap 開始，目標:{until}，swipe:{swipe_action}，超時:{timeout}，重啟定位:{relocation}")
    state.target_checkpoint = checkpoint
    state.target_until = until
    if state.minimap_list == None:
        state.minimap_list = state.handle_loop_list[:]
        state.minimap_list.insert(0, "P_minimap_close")
    if heal_check:
        health_check()
    for i in range(10):
        screenshot = take_screenshot()
        result = find_image(state.minimap_list, screenshot, similarity=0.73)
        if result:
            match = result[0]
            if match == "P_minimap_close":
                logger.info("找到 P_minimap_close，地圖界面檢查完成")
                break
            elif match == "P_exit":
                logger.info("找到 P_exit，點擊小地圖")
                tap(constants.L_Minimap[0], constants.L_Minimap[1], "小地圖")
                wait_image("P_minimap_close")
            elif match in state.handle_loop_list:
                logger.info(f"處理匹配: {match}")
                common_reaction(match, None)  # state.stage=None，因為此處不依賴後續點擊
            elif check_reconnect(screenshot):
                logger.info("處理斷線，繼續循環")
                continue
            elif check_gameicon(screenshot):
                logger.info("處理閃退，繼續循環")
                continue
        time.sleep(0.05)
    else:
        exitLog("goMap打開小地圖超時")
    if not isinstance(swipe_action, list):
        swipe_action = [swipe_action]
    for action in swipe_action:
        if action:
            if len(action) == 5:
                start_x, start_y, start_w, start_h, duration = action
                swipe(start_x, start_y, start_w, start_h, duration)
            elif len(action) == 4:
                start_x, start_y, start_w, start_h = action
                swipe(start_x, start_y, start_w, start_h)
            else:
                exitLog("swipe_action變數數目不正確")
        for i in range(3):
            if find_image(checkpoint, similarity=goMap_similarity-i*0):
                click_image(checkpoint, timeout=3, similarity=goMap_similarity-i*0)
                if click_image("P_Cmove", timeout=3, similarity=0.65):
                    break
    logger.info(f"前往 {checkpoint}")
    if exit_check:
        if wait_image("P_noPath", timeout=3):
            logger.info("沒有找到路徑")
            click_image("P_minimap_close")
            return False
    state.stage = "Cmove"
    result = handle_loop(until, timeout)
    logger.info("goMap 完成")
    state.target_until = None
    if result:
        return result
    else:
        return False
def exitMap(until, timeout=6000, heal_check=True):    #離開地圖
    """退出地圖"""
    # (state) global state.stage, constants.R_char_dungeon, state.restart_relocation, state.target_until
    logger.info("exitMap 開始")
    state.target_until = until
    state.restart_relocation = False
    if heal_check:
        health_check()
    click_image("P_exit", timeout=5)
    state.stage = "Exit"
    result = handle_loop(until, timeout)
    logger.info("exitMap 完成")
    state.target_until = None
    if result:
        return result
    else:
        return False
def map_click():    #大地圖出門前檢查
    wait_image("P_inn")
    comment_check()
    if find_image("P_downlist"):
        click_image("P_downlist")
    click_image("P_map")
    wait_image(["P_map_scalebig", "P_map_scalesmall"])
def goToDungeon_check():    #地城前意志力檢查
    """檢查進入地城是否意志力低下"""
    time.sleep(1)
    if find_image("P_gotodungeon"):
        click_image("P_gotodungeon")
        return True
    return False
def swipe_map(direction):   #小地圖滑動
    """以上下左右路徑滑地圖"""
    swipe_path = {
        "left": (75, 400, 825, 400, 500),   #左移
        "up": (825, 400, 825, 1200, 500), #上移
        "right": (825, 1200, 75, 1200, 500), #右移
        "down": (75, 1200, 75, 400, 500),   #下移
    }
    if direction:
            direction_list = [direction] if isinstance(direction, str) else direction
            for action in direction_list:
                #find_image(["P_minimap_close"])
                time.sleep(0.5)
                start_x, start_y, end_x, end_y, duration = swipe_path[action]
                swipe(start_x, start_y, end_x, end_y, duration)
    return True
def goToMark(target=None, target_sim=0.6): #自動前往標記位置
    def auto_mark():
        if not find_image("P_automark"):
            tap(761,342, "展開地圖功能")
        if click_image("P_automark", timeout=3):
            if wait_image("P_noPath", timeout=3, fail_count=False):
                logger.info("出現「無法找到路徑」情況")
                return False
        return True
    # (state) global state.target_until
    if target:
        state.target_until = target if isinstance(target,list) else [target]
    try_time = 1
    match = None
    for i in range(try_time):
        logger.info(f"goToMark第{try_time}外圈, try_time:{try_time}")
        for i in range(20):
            logger.info(f"goToMark第{i}內圈")
            if target is not None and try_time>0:
                if find_image(target, similarity=target_sim, fail_log=True):
                    logger.info(f"到達{target}，auto_mark完結")
                    return True
            match = wait_image(state.handle_loop_list)
            logger.info(f"找到匹配: {match}")
            if match == "P_exit":
                if image_stability("P_exit", max_attempts=1):
                    health_check()
                    if auto_mark():
                        waitVanish("P_exit", timeout=5)
                    else:
                        logger.info("auto_mark完結")
                        return True
            else:
                common_reaction(match, None)  # state.stage=None，因為此處不依賴 state.stage
        time.sleep(0.5)
    else:
        logger.info(f"已觸發{try_time}次前往標記，提早完結")
        return True
def ch2_pre():
    # (state) global state.run_count, state.on9npc_list, state.handle_loop_list
    if state.run_count == 0:
        for i in range(4):
            name = "P_ch2_on9npc" + str(i+1)
            state.handle_loop_list.append(name)
            state.on9npc_list.append(name)
    logger.info(f"首次執行，增加所需變數，目前handle_loop_list:{state.handle_loop_list}")
def ch4_pre():
    # (state) global state.run_count, state.on9npc_list, state.handle_loop_list
    if state.run_count == 0:
        for i in range(4):
            name = "P_ch4_on9npc" + str(i+1)
            state.handle_loop_list.append(name)
            state.on9npc_list.append(name)
    logger.info(f"首次執行，增加所需變數，目前handle_loop_list:{state.handle_loop_list}")
def rock_pre():
    # (state) global state.run_count, state.on9npc_list, state.handle_loop_list
    if state.run_count == 0:
        for i in range(1):
            name = "P_Cave_BigRock" + str(i+1)
            state.handle_loop_list.append(name)
            state.on9npc_list.append(name)
    logger.info(f"首次執行，增加所需變數，目前handle_loop_list:{state.handle_loop_list}")
def harken_check(target): #哈肯卡死檢測
    """哈肯卡死檢測"""
    if not find_image("P_back"):
        click_image("P_buff")
    click_image("P_back")
    logger.info("哈肯卡死檢測開始")
    for i in range(5):
        if not wait_image(target,timeout=5):
            if freeze_screen_check(mode=2):
                return False
        else:
            break
    return True

# 其他函數
def press_key(key, duration=350):   #地城上下左右滑動
    """模擬 ADB 滑動(wasd)或暫停(sleep)操作"""
    swipe_map = {
        'w': (450, 800, 450, 750),
        's': (450, 800, 450, 850),
        'a': (450, 800, 250, 800),
        'd': (450, 800, 650, 800),
    }
    # 如果 key 是字符串，轉為單元素列表；如果已是列表，直接使用
    key_list = [key] if isinstance(key, str) else key

    # 統一用 for 循環處理鍵列表
    for i, k in enumerate(key_list):
        if k in swipe_map:
            x1, y1, x2, y2 = swipe_map[k]
            swipe(x1, y1, x2, y2, duration)  # 調用 swipe() 執行滑動
        elif k == 'sleep':
            time.sleep(0.5)
            logger.info("執行暫停 0.5 秒")
        else:
            logger.info(f"無效鍵：{k}")
def exitLog(message):   #中斷腳本
    """記錄錯誤日誌並退出程式"""
    logger.info(f"{message}")
    exit(0)
def random_delay(fixed=0.0):    #隨機延遲
    """在固定秒數加 0.2 到 2 秒之間引入隨機延遲"""
    delay = fixed + random.uniform(0.2, 2)
    logger.info(f"將隨機等待 {delay:.2f}秒")
    time.sleep(delay)
def switch_wheel(point, chapter, point_sim=0.7, final_click=True):    #切換詛咒之輪
    if find_image(point, similarity=point_sim):
        click_image(point, similarity=point_sim)
        if final_click:
            click_image("P_wheel_jump")
        return True
    #target_chapter = "P_wheel_ch" + str(chapter)
    for i in range(4):
        temp = "P_wheel_ch" + str(i+1)
        if find_image(temp):
            current_chapter = i+1
            logger.info(f"當前在第{current_chapter}章")
            if current_chapter > chapter:
                direction = "up"
            else:
                direction = "down"
    for i in range(5):
        if current_chapter < chapter:
            swipe(700, 900, 100, 900, 500) #右一格
            current_chapter +=1
            time.sleep(0.5)
        else:
            swipe(100, 900, 700, 900, 500) #左一格
            current_chapter -=1
            time.sleep(0.5)
        if current_chapter == chapter:
            break
    for i in range(4):
        if not find_image(point, similarity=point_sim):
            if direction == "down":
                swipe(450, 1200, 450, 400, 500)
            else:
                swipe(450, 400, 450, 1200, 500)
            time.sleep(0.5)
        else:
            click_image(point, similarity=point_sim)
            if final_click:
                click_image("P_wheel_jump")
            return True
def fish(): #釣魚
    return True