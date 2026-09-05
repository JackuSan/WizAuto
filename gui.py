# -*- coding: utf-8 -*-
"""GUI 介面：AutomationGUI、日誌 Handler、超連結"""
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import logging
import json
import os
import webbrowser
import time
import constants
import state
import core
import farm

logger = logging.getLogger(__name__)

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.config(state='disabled')  # 設置為只讀

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.config(state='normal')
        if "使用前須知" in msg:
            self.text_widget.insert(tk.END, msg + '\n', 'warning')  # 用 tag
        else:
            self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)  # 自動滾動到最新日誌
        self.text_widget.config(state='disabled')

# 超連結部件
class HyperlinkManager:
    def __init__(self, text_widget):
        self.text = text_widget
        self.text.tag_configure("hyperlink", foreground="blue", underline=1)
        self.text.tag_bind("hyperlink", "<Enter>", self._enter)
        self.text.tag_bind("hyperlink", "<Leave>", self._leave)
        self.text.tag_bind("hyperlink", "<Button-1>", self._click)
        self.links = {}

    def add(self, url):
        self.links[url] = url
        return "hyperlink", url

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(tk.CURRENT):
            if tag == "hyperlink":
                url = self.links.get(self.text.tag_names(tk.CURRENT)[1])
                if url:
                    webbrowser.open(url)

# GUI 控制界面
class AutomationGUI:
    def __init__(self, root):
        # (state) global state.app  # 定義全局 state.app 變量
        state.app = self  # 將當前實例賦值給 state.app
        self.root = root
        self.root.title(f"Jacku小精靈-Wizardry Variants Daphne Automation v{constants.VERSION} [ADB port:{state.adb_port}]")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        self.is_running = False
        self.target_count = 0
        self.healperiod_count = 1
        self.script_thread = None
        
        # ====================== 6×4 表格佈局 ======================
        self.table_frame = tk.Frame(root)
        self.table_frame.pack(pady=8, padx=10, anchor="w", fill="x")

        # === 關鍵：欄位間距控制 ===
        # 欄位 0,1,2,3 對應：腳本 | 選單 | 目標 | 輸入
        self.table_frame.grid_columnconfigure(0, weight=0, minsize=50)  # 標籤欄
        self.table_frame.grid_columnconfigure(1, weight=1, minsize=150)  # 輸入欄
        self.table_frame.grid_columnconfigure(2, weight=0, minsize=50)  # 標籤
        self.table_frame.grid_columnconfigure(3, weight=1, minsize=150)  # 輸入欄
        self.table_frame.grid_columnconfigure(4, weight=0, minsize=50)  # 標籤
        self.table_frame.grid_columnconfigure(5, weight=1, minsize=150)  # 輸入欄

        # 統一寬度設定
        COMBO_WIDTH = 20
        ENTRY_WIDTH = 23
        LABEL_DISPLAY_WIDTH = 23
        
        # ------------------ 行 0 ------------------
        tk.Label(self.table_frame, text="腳本:").grid(row=0, column=0, sticky="w", padx=2, pady=3)
        self.script_choice = tk.StringVar()
        self.script_combobox = ttk.Combobox(self.table_frame, textvariable=self.script_choice,
                                            values=["皇女7000g刷錢", 
                                                    "第二章第一街B1F周回雜物",
                                                    "第二章船二周回雜物", 
                                                    "第三章第七區周回巨人", 
                                                    "第四章B1F周回雜物",
                                                    "第四章B4F周回雪山兇鳥帽",
                                                    "第四章B6F周回雜物",
                                                    "第四章B7F周回雜物",
                                                    "第四章B7F無限周回雜物",
                                                    "第四章B10F雪巨人",
                                                    #"擊退敵方勢力",
                                                    "擊退敵方勢力(固定開技版)",
                                                    "別離洞窟周回雜物",
                                                    "百花之庭周回雜物",
                                                    "白堊狼穴周回雜物",
                                                    "鬼啼島周回雜物",
                                                    "治癒師洞B3F周回雜物",
                                                    #"陽炎洞窟長征金箱", 
                                                    "陽炎洞窟B1F簡易周回雜物",
                                                    #"陽炎洞窟B1F右上打怪周回雜物", 
                                                    #"牛牛洞重置任務刷一隻牛",
                                                    "牛牛洞刷精靈甲", 
                                                    "土之洞窟周回雜物", 
                                                    "火之洞窟周回雜物", 
                                                    "風之洞窟周回雜物",
                                                    "光之洞窟周回雜物",
                                                    "水之洞窟周回雜物",
                                                    "怨嗟洞窟刷蠍子女遺物周回", 
                                                    "怨嗟洞窟周回",
                                                    "懸賞令周回(蠍子女)",
                                                    "懸賞令周回(牛頭人)",
                                                    "懸賞令周回(沉穩的騙子布洛克)",
                                                    "爐壺靈廟周回",
                                                    #"沙華魚人洞窟B2F雜物周回",
                                                    #"沙華魚人洞窟B3F雜物周回(修女線)",
                                                    #"金礦石任務(第三章)",
                                                    "旅館不停休息", 
                                                    "FF11_B1F周回雜物",
                                                    "FF11_B2F周回雜物", 
                                                    "FF11_B5F周回雜物", 
                                                    "FF11_B5F周回標記",
                                                    "FF11_B2F周回挖礦",
                                                    "測試腳本"],
                                            state="readonly", width=COMBO_WIDTH)
        self.script_combobox.set("")
        self.script_combobox.grid(row=0, column=1, sticky="w", padx=2, pady=3)
        self.script_combobox.bind("<<ComboboxSelected>>", self.validate_script)

        tk.Label(self.table_frame, text="目標次數:").grid(row=0, column=2, sticky="w", padx=2, pady=3)
        self.entry_target = tk.Entry(self.table_frame, width=ENTRY_WIDTH)
        self.entry_target.grid(row=0, column=3, sticky="w", padx=2, pady=3)
        self.entry_target.bind("<KeyRelease>", self.validate_target)

        tk.Label(self.table_frame, text="休息模式:").grid(row=0, column=4, sticky="w", padx=2, pady=3)
        self.inn_choice = tk.StringVar()
        self.inn_combobox = ttk.Combobox(self.table_frame, textvariable=self.inn_choice,
                                        values=["不休息", "野外補給", "地城露營", "標準房", "豪華房"], state="readonly", width=COMBO_WIDTH)
        self.inn_combobox.set("標準房")
        self.inn_combobox.grid(row=0, column=5, sticky="w", padx=2, pady=3)
        
        # ------------------ 行 1 ------------------
        tk.Label(self.table_frame, text="開箱模式:").grid(row=1, column=0, sticky="w", padx=2, pady=3)
        self.trap_choice = tk.StringVar()
        self.trap_combobox = ttk.Combobox(self.table_frame, textvariable=self.trap_choice,
                                        values=["放棄解除陷阱箱", "隨機解除陷阱箱", "測速解除陷阱箱(未完成不要選)"],
                                        state="readonly", width=COMBO_WIDTH)
        self.trap_combobox.set("隨機解除陷阱箱")
        self.trap_combobox.grid(row=1, column=1, sticky="w", padx=2, pady=3)

        tk.Label(self.table_frame, text="開箱角色順序:").grid(row=1, column=2, sticky="w", padx=2, pady=3)
        self.entry_chest_char = tk.Entry(self.table_frame, width=ENTRY_WIDTH)
        self.entry_chest_char.insert(0, "")
        self.entry_chest_char.grid(row=1, column=3, sticky="w", padx=2, pady=3)
        self.entry_chest_char.bind("<KeyRelease>", self.validate_chest_char)

        tk.Label(self.table_frame, text="補給隔離:").grid(row=1, column=4, sticky="w", padx=2, pady=3)
        self.entry_healperiod = tk.Entry(self.table_frame, width=ENTRY_WIDTH)
        self.entry_healperiod.insert(0, "1")
        self.entry_healperiod.grid(row=1, column=5, sticky="w", padx=5, pady=3)
        self.entry_healperiod.bind("<KeyRelease>", self.validate_healperiod)

        # ------------------ 行 2 ------------------
        tk.Label(self.table_frame, text="自動復活及再起:").grid(row=2, column=0, sticky="w", padx=2, pady=3)
        self.revive_var = tk.BooleanVar(value=True)
        self.check_revive = tk.Checkbutton(self.table_frame, variable=self.revive_var)
        self.check_revive.grid(row=2, column=1, sticky="w", padx=2, pady=3)
        
        tk.Label(self.table_frame, text="卡死檢查(測試):").grid(row=2, column=2, sticky="w", padx=2, pady=3)
        self.freeze_var = tk.BooleanVar(value=False)
        self.check_freeze = tk.Checkbutton(self.table_frame, variable=self.freeze_var)
        self.check_freeze.grid(row=2, column=3, sticky="w", padx=2, pady=3)
        
        tk.Label(self.table_frame, text="性格傾向:").grid(row=2, column=4, sticky="w", padx=2, pady=3)
        self.personality_choice = tk.StringVar()
        self.personality_combobox = ttk.Combobox(self.table_frame, textvariable=self.personality_choice,
                                        values=["保持不變", "善轉中立", "善轉惡", "中立轉善", "中立轉惡", "惡轉中立", "惡轉善"],
                                        state="readonly", width=COMBO_WIDTH)
        self.personality_combobox.set("保持不變")
        self.personality_combobox.grid(row=2, column=5, sticky="w", padx=2, pady=3)

        # ------------------ 行 3 ------------------
        tk.Label(self.table_frame, text="完成次數:").grid(row=3, column=0, sticky="w", padx=2, pady=3)
        self.current_count_var = tk.StringVar(value="0")
        self.label_current_count = tk.Label(self.table_frame, textvariable=self.current_count_var,
                                            width=LABEL_DISPLAY_WIDTH, anchor="w", relief="sunken", bg="#e0e0e0")
        self.label_current_count.grid(row=3, column=1, sticky="w", padx=2, pady=3)

        tk.Label(self.table_frame, text="當前寶箱數:").grid(row=3, column=2, sticky="w", padx=2, pady=3)
        self.chest_count_var = tk.StringVar(value="0")
        self.label_chest_count = tk.Label(self.table_frame, textvariable=self.chest_count_var,
                                        width=LABEL_DISPLAY_WIDTH, anchor="w", relief="sunken", bg="#e0e0e0")
        self.label_chest_count.grid(row=3, column=3, sticky="w", padx=2, pady=3)

        tk.Label(self.table_frame, text="戰鬥模式:").grid(row=3, column=4, sticky="w", padx=2, pady=3)
        self.battle_choice = tk.StringVar()
        self.battle_combobox = ttk.Combobox(self.table_frame, textvariable=self.battle_choice,
                                        values=["自動戰鬥", "技能戰鬥"],
                                        state="readonly", width=COMBO_WIDTH)
        self.battle_combobox.set("自動戰鬥")
        self.battle_combobox.grid(row=3, column=5, sticky="w", padx=2, pady=3)
        self.battle_combobox.bind("<<ComboboxSelected>>", self.validate_battle)

        # ====================== 按鈕區 ======================
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=1)

        self.button_pause = tk.Button(self.button_frame, text="暫停", command=self.pause_script, state="disabled", width=10)
        self.button_pause.pack(side=tk.LEFT, padx=15)

        self.button_resume = tk.Button(self.button_frame, text="繼續", command=self.resume_script, state="disabled", width=10)
        self.button_resume.pack(side=tk.LEFT, padx=15)

        self.button_stop = tk.Button(self.button_frame, text="中斷", command=self.stop_script, state="disabled", width=10)
        self.button_stop.pack(side=tk.LEFT, padx=15)

        self.button_run = tk.Button(self.button_frame, text="執行", command=self.run_script, state="disabled", width=10)
        self.button_run.pack(side=tk.LEFT, padx=15)
        
        self.button_last = tk.Button(
            self.button_frame, text="最後一輪", command=self.last_round_script,
            state="disabled", width=10
        )
        self.button_last.pack(side=tk.LEFT, padx=15)

        """
        # ====================== 日誌顯示 ======================
        self.log_text = scrolledtext.ScrolledText(self.root, width=110, height=20, wrap=tk.WORD, state='disabled')
        self.log_text.pack(pady=10, padx=10, fill="both", expand=True)
        self.log_text.tag_config('warning', foreground='red')

        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))

        # 重要：加到 root，不要只加到 gui logger
        root_logger = logging.getLogger()
        if not any(isinstance(h, TextHandler) for h in root_logger.handlers):
            root_logger.addHandler(text_handler)

        # ====================== 檢查與連接 ======================
        core.check_requirements()
        core.connect_to_device()
        if not core.run_adb_command("devices"):
            logger.error("未找到 ADB 設備。請確保設備已連接到 127.0.0.1:5555 並啟用 USB 調試或 TCP/IP 模式。")
            logger.error("解決方法：")
            logger.error("1. 運行 'adb connect 127.0.0.1:5555'")
            logger.error("2. 檢查 'adb devices' 是否顯示 '127.0.0.1:5555 device'")
            self.root.after(0, lambda: messagebox.showerror("錯誤", "未找到 ADB 設備，請檢查連接後重啟應用"))
            self.root.destroy()
            return
        else:
            logger.info("ADB連接passed")

        # ====================== 日誌顯示 ======================
        self.log_text = scrolledtext.ScrolledText(self.root, width=110, height=20, wrap=tk.WORD, state='disabled')
        self.log_text.pack(pady=10, padx=10, fill="both", expand=True)  # 先 pack 日誌

        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('[%(asctime)s.%(msecs)03d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(text_handler)

        # ====================== 彩蛋宣傳 ======================
        self.social_frame = tk.Frame(root)
        self.social_frame.pack(side=tk.BOTTOM, pady=5, fill=tk.X)  # 直接放最底

        self.social_text = tk.Text(self.social_frame, height=2, font=(15), wrap="none")
        self.social_text.pack()
        hyperlink = HyperlinkManager(self.social_text)
        self.social_text.insert(tk.END, "Youtube", hyperlink.add("https://www.youtube.com/channel/UCr4NlCWbXKPBOJCNzhgzRSQ"))
        self.social_text.insert(tk.END, ": JackuSan遊戲之旅 | 每星期一三五晚上9-12點直播打機 | 歡迎來掛台聊天支持作者")
        self.social_text.insert(tk.END, "\n")
        self.social_text.insert(tk.END, "Discord", hyperlink.add("https://discord.gg/gsrCpdeEnT"))
        self.social_text.insert(tk.END, ": 歡迎進來聊天和提出建議")
        self.social_text.config(state="disabled")
        """
        # ====================== 彩蛋宣傳（先 pack 到底部）======================
        self.social_frame = tk.Frame(self.root)
        self.social_frame.pack(side=tk.BOTTOM, pady=5, fill=tk.X)

        self.social_text = tk.Text(
            self.social_frame, height=2, font=("", 11), wrap="none",
            relief="flat", bg=self.root.cget("bg"), borderwidth=0
        )
        self.social_text.pack(fill=tk.X, padx=10)
        hyperlink = HyperlinkManager(self.social_text)
        self.social_text.insert(tk.END, "Youtube", hyperlink.add("https://www.youtube.com/channel/UCr4NlCWbXKPBOJCNzhgzRSQ"))
        self.social_text.insert(tk.END, ": JackuSan遊戲之旅 | 每星期一三五晚上9-12點直播打機 | 歡迎來掛台聊天支持作者")
        self.social_text.insert(tk.END, "\n")
        self.social_text.insert(tk.END, "Discord", hyperlink.add("https://discord.gg/gsrCpdeEnT"))
        self.social_text.insert(tk.END, ": 歡迎進來聊天和提出建議")
        self.social_text.config(state="disabled")

        # ====================== 日誌顯示（只有一個；掛 root 才能收到 core/farm）======================
        self.log_text = scrolledtext.ScrolledText(
            self.root, width=110, height=18, wrap=tk.WORD, state="disabled"
        )
        self.log_text.pack(pady=8, padx=10, fill="both", expand=True)
        self.log_text.tag_config("warning", foreground="red")

        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(
            logging.Formatter("[%(asctime)s.%(msecs)03d] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )
        root_logger = logging.getLogger()
        if not any(isinstance(h, TextHandler) for h in root_logger.handlers):
            root_logger.addHandler(text_handler)

        # ====================== 檢查與連接 ======================
        core.check_requirements()
        core.connect_to_device()
        if not core.run_adb_command("devices"):
            logger.error("未找到 ADB 設備。請確保設備已連接到 127.0.0.1:5555 並啟用 USB 調試或 TCP/IP 模式。")
            logger.error("解決方法：")
            logger.error("1. 運行 'adb connect 127.0.0.1:5555'")
            logger.error("2. 檢查 'adb devices' 是否顯示 '127.0.0.1:5555 device'")
            self.root.after(0, lambda: messagebox.showerror("錯誤", "未找到 ADB 設備，請檢查連接後重啟應用"))
            self.root.destroy()
            return
        else:
            logger.info("ADB連接passed")
        # ====================== 開場白 ======================
        logger.info("歡迎使用JackuSan製作的腳本")
        logger.info("此腳本免費使用，不定期更新")
        logger.info("希望會有更多人玩《辟邪除妖》這個遊戲，不被枯燥的刷裝生活勸退")
        logger.info("想多謝作者的話，可以訂閱作者的Youtube頻道，讓作者開心一下")
        logger.info("【重要警告】執行腳本前請仔細閱讀Google Drive的「使用前須知」")
        logger.info("【重要警告】執行腳本前請仔細閱讀Google Drive的「使用前須知」")
        logger.info("【重要警告】執行腳本前請仔細閱讀Google Drive的「使用前須知」")
        
        #呼叫讀取設定
        self.load_settings()
        
        #綁定視窗關閉事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    def save_settings(self):
        """將 GUI 選項儲存到 config.json"""
        data = {
            "trap_choice": self.trap_choice.get(),
            "entry_target": self.entry_target.get(),
            "inn_choice": self.inn_choice.get(),
            "state.script_choice": self.script_choice.get(),
            "entry_healperiod": self.entry_healperiod.get(),
            "revive_var": self.revive_var.get(),
            "freeze_var": self.freeze_var.get(),
            "battle_choice": self.battle_choice.get(),
            "entry_chest_char": self.entry_chest_char.get(),
        }
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    def load_settings(self):
        """啟動時讀取設定"""
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "trap_choice" in data: self.trap_choice.set(data["trap_choice"])
                    
                    if "entry_target" in data: 
                        self.entry_target.delete(0, tk.END)
                        self.entry_target.insert(0, data["entry_target"])
                        
                    if "inn_choice" in data: self.inn_choice.set(data["inn_choice"])
                    if "state.script_choice" in data: self.script_choice.set(data["state.script_choice"])
                    
                    if "entry_healperiod" in data: 
                        self.entry_healperiod.delete(0, tk.END)
                        self.entry_healperiod.insert(0, data["entry_healperiod"])
                        
                    if "revive_var" in data: self.revive_var.set(data["revive_var"])
                    if "freeze_var" in data: self.freeze_var.set(data["freeze_var"])
                    if "battle_choice" in data: self.battle_choice.set(data["battle_choice"])
                    
                    if "entry_chest_char" in data: 
                        self.entry_chest_char.delete(0, tk.END)
                        self.entry_chest_char.insert(0, data["entry_chest_char"])
                        
                    self.validate_target(None)
            except Exception as e:
                print(f"載入設定失敗: {e}")
    def on_closing(self):
        """關閉視窗時自動儲存"""
        self.save_settings()
        self.root.destroy()
    def validate_script(self, event): #選擇劇本後的使用提示
        script_map = constants.script_remainder
        script = self.script_choice.get()
        inn_list = script_map[script]["旅館"]
        logger.info(f"==========已選擇腳本「{script}」==========")
        logger.info(f"支援休息模式: {inn_list}")
        logger.info(f"腳本起點: {script_map[script]["起點"]}")
        logger.info(f"異常狀態: {script_map[script]["異常狀態"]}")
        if "提示" in script_map.get(script, {}):
            tips_len = len(script_map[script]["提示"])
            for i in range(tips_len):
                logger.info(f"提示{script_map[script]["提示"][i]}")
        return True
    def validate_battle(self,event): #驗證戰鬥模式
        state.battle_mode = self.battle_choice.get()
        if state.battle_mode == "自動戰鬥":
            logger.info("已切換為自動戰鬥模式")
        elif state.battle_mode == "技能戰鬥":
            logger.info("已切換為技能戰鬥模式")
            logger.info("請注意技能只支援右下技能及無條件攻擊型技能")
        return True
    def validate_chest_char(self, event):   #驗證開箱角色
        """驗證開箱角色順序輸入: 最多6位數字, 1-6無重覆"""
        value = self.entry_chest_char.get()
        if len(value) > 6 or not value.isdigit():
            self.entry_chest_char.config(bg="pink")
            return False
        self.entry_chest_char.config(bg="white")
        return True
    def validate_target(self, event):   #驗證次數
        """驗證目標次數輸入"""
        try:
            value = self.entry_target.get()
            if value.strip() == "":
                self.button_run.config(state="disabled")
                return
            target = int(value)
            if target >= 1:
                self.target_count = target
                self.button_run.config(state="normal")
            else:
                self.button_run.config(state="disabled")
        except ValueError:
            self.button_run.config(state="disabled")
    def validate_healperiod(self, event):   #驗證回復隔離
        """驗證目標次數輸入"""
        try:
            value = self.entry_healperiod.get()
            if value.strip() == "":
                self.button_run.config(state="disabled")
                return
            healperiod = int(value)
            if healperiod >= 1:
                self.healperiod_count = healperiod
                self.button_run.config(state="normal")
            else:
                self.button_run.config(state="disabled")
        except ValueError:
            self.button_run.config(state="disabled")
    def pause_script(self): #暫停腳本
        """暫停腳本"""
        # (state) global state.paused
        state.paused = True
        logger.info("腳本已暫停")
        self.current_count_var.set(f"{state.run_count} (已暫停腳本)")
        self.button_pause.config(state="disabled")
        self.button_resume.config(state="normal")
        self.entry_healperiod.config(state="normal")
        self.entry_chest_char.config(state="normal")
        self.trap_combobox.config(state="readonly")
        self.button_run.config(state="disabled")
        self.button_stop.config(state="normal")
        self.button_pause.config(state="disabled")
        self.button_resume.config(state="normal")
    def resume_script(self):    #繼續腳本
        """繼續腳本"""
        # (state) global state.paused, state.trap_mode, state.heal_period
        if not self.validate_chest_char(None):
            messagebox.showerror("錯誤", "開箱角色順序無效，請輸入6位不重覆的1-6數字")
            return
        trap_map = {
            "放棄解除陷阱箱": 1,
            "隨機解除陷阱箱": 2,
            "測速解除陷阱箱": 3,
        }
        state.trap_mode = trap_map[self.trap_choice.get()]
        state.heal_period = self.healperiod_count
        state.paused = False
        logger.info("腳本已恢復運行")
        self.current_count_var.set(f"{state.run_count}")
        self.chest_count_var.set(f"{state.chest_count}")
        self.button_pause.config(state="normal")
        self.button_resume.config(state="disabled")
        self.entry_healperiod.config(state="disabled")
        self.entry_chest_char.config(state="disabled")
        self.trap_combobox.config(state="disabled")
        self.button_run.config(state="disabled")
        self.button_stop.config(state="normal")
        self.button_pause.config(state="normal")
        self.button_resume.config(state="disabled")
    def stop_script(self):  #中斷腳本
        """停止腳本"""
        # (state) global state.is_running, state.paused
        state.stop_event.set()
        state.paused = False
        logger.info("收到停止指令，腳本終止")
        def check_thread():
            if self.script_thread and self.script_thread.is_alive():
                self.root.after(100, check_thread)  # 每100ms檢查線程
            else:
                state.is_running = False
                self.button_last.config(state="disabled")
                self.button_pause.config(state="disabled")
                self.button_resume.config(state="disabled")
                self.button_stop.config(state="disabled")
                self.button_run.config(state="normal")
                self.entry_target.config(state="normal")
                self.entry_healperiod.config(state="normal")
                self.entry_chest_char.config(state="normal")
                self.check_revive.config(state="normal")
                self.battle_combobox.config(state="readonly")
                self.check_freeze.config(state="normal")
                self.script_combobox.config(state="readonly")  # 啟用腳本選擇
                self.personality_combobox.config(state="readonly")  # 啟用性格傾向選擇
                self.inn_combobox.config(state="readonly")  # 啟用旅館房間選擇
                self.trap_combobox.config(state="readonly")  # 啟用開箱模式選擇
                self.root.after(0, lambda: messagebox.showinfo("提示", "腳本已終止"))
        if self.script_thread:
            self.root.after(100, check_thread)
        else:
            check_thread()
    def last_round_script(self):
        if not state.is_running:
            return
        state.last_round = True
        logger.info(f"已設定「最後一輪」：目前這輪完成後停止（當前完成次數 {state.run_count}）")
        self.current_count_var.set(f"{state.run_count} (最後一輪)")
        self.button_last.config(state="disabled")      
    def run_script(self):   #執行腳本
        """執行腳本"""
        # (state) global state.is_running, state.run_count, state.trap_mode, state.chest_char, state.revive_status, state.inn_mode, state.freeze_check_status, state.chest_count, state.heal_period, state.battle_mode, state.personality_action, state.personality_score, state.personality_choice

        if state.is_running:
            return
        if not self.validate_chest_char(None):
            messagebox.showerror("錯誤", "開箱角色順序無效，請輸入6位不重覆的1-6數字")
            return
        trap_map = {
            "放棄解除陷阱箱": 1,
            "隨機解除陷阱箱": 2,
            "測速解除陷阱箱": 3,
        }
        state.trap_mode = trap_map[self.trap_choice.get()]
        personality_map = {
            "保持不變": {"action": "retain", "target" : 0}, 
            "善轉中立": {"action": "bad", "target" : -18}, 
            "善轉惡": {"action": "bad", "target" : -36}, 
            "中立轉善": {"action": "good", "target" : +18}, 
            "中立轉惡": {"action": "bad", "target" : -18}, 
            "惡轉中立": {"action": "good", "target" : 18}, 
            "惡轉善": {"action": "good", "target" : 36},
        }
        state.personality_choice = self.personality_choice.get()
        state.personality_action = personality_map[state.personality_choice]["action"]
        state.personality_score = personality_map[state.personality_choice]["target"]
        inn_map = {
            "不休息": 0,
            "野外補給": 1,
            "地城露營": 2,
            "標準房": 3,
            "豪華房": 4,
        }
        state.inn_mode = inn_map[self.inn_choice.get()]
        state.heal_period = int(self.entry_healperiod.get())
        state.revive_status = self.revive_var.get()
        state.battle_mode = self.battle_choice.get()
        state.freeze_check_status = self.freeze_var.get()
        state.chest_char = int(self.entry_chest_char.get())
        state.is_running = True
        state.stop_event.clear()
        state.last_round = False
        self.button_last.config(state="normal")
        self.button_run.config(state="disabled")
        self.button_stop.config(state="normal")
        self.button_pause.config(state="normal")
        self.button_resume.config(state="disabled")
        self.entry_target.config(state="disabled")
        self.entry_healperiod.config(state="disabled")
        self.entry_chest_char.config(state="disabled")
        self.check_revive.config(state="disabled") #禁止更改再起checkbox選擇
        self.battle_combobox.config(state="disabled")
        self.check_freeze.config(state="disabled") #禁止更改卡死畫面checkbox選擇
        self.script_combobox.config(state="disabled")  # 禁用腳本選擇
        self.personality_combobox.config(state="disabled")  # 禁用性格傾向選擇
        self.inn_combobox.config(state="disabled")  # 禁用旅館房間選擇
        self.trap_combobox.config(state="disabled")  # 禁用開箱模式選擇
        self.current_count_var.set("0")  # 開始執行時顯示 0
        self.chest_count_var.set("0")  # 開始執行時顯示 0
        self.script_thread = threading.Thread(target=self.run_script_thread)
        self.script_thread.start()
    def run_script_thread(self):
        """在線程中運行腳本"""
        def renew_var_whole():  #重置開局變數
            # (state) global state.handle_loop_list, state.debuff_list, state.run_count, state.chest_count, state.list_update_status, state.first_freeze_screen_check, state.revived_bol, state.minimap_list, state.freeze_screen_check_time, state.on9npc_list, state.personality_count, state.equip_count
            logger.info("執行腳本前先重置變數")
            state.handle_loop_list = constants.HANDLE_LOOP_LIST_START[:]
            state.minimap_list = state.freeze_screen_check_time = None
            state.on9npc_list = []
            state.debuff_list = constants.DEBUFF_LIST_START[:]
            state.run_count = state.chest_count = state.equip_count = state.personality_count = 0
            state.list_update_status = state.first_freeze_screen_check = True
            state.revived_bol = False
            state.last_round = False
            return
        def renew_var_round():  #重置每輪變數
            # (state) global state.trap_char_all_scared, state.bs_restarted, state.images_list, state.target_until
            state.images_list = state.target_until = None
            state.trap_char_all_scared = state.bs_restarted = False
            return
        
        # (state) global state.run_count, state.trap_char_all_scared, state.target_checkpoint, state.image_restart, state.bs_restarted, state.script_choice
        try:
            renew_var_whole()
            while state.run_count < self.target_count and not state.stop_event.is_set() and not state.last_round:
                state.script_choice = self.script_choice.get()
                state.target_checkpoint = state.image_restart = state.bs_restarted =  None
                logger.info(f"========開始第 {state.run_count + 1} 次循環，腳本:{state.script_choice}========")
                if self.script_choice.get() == "皇女7000g刷錢":
                    farm.Farm_7000g()
                elif self.script_choice.get() == "第二章第一街B1F周回雜物":
                    farm.Farm_ch2B1F()
                elif self.script_choice.get() == "第二章船二周回雜物":
                    farm.Farm_ch2B9F()
                elif self.script_choice.get() == "第三章第七區周回巨人":
                    farm.Farm_ch3B7F()
                elif self.script_choice.get() == "第四章B1F周回雜物":
                    farm.Farm_ch4B1F()
                elif self.script_choice.get() == "第四章B4F周回雪山兇鳥帽":
                    farm.Farm_ch4B4F()
                elif self.script_choice.get() == "第四章B6F周回雜物":
                    farm.Farm_ch4B6F()    
                elif self.script_choice.get() == "第四章B7F周回雜物":
                    farm.Farm_ch4B7F()  
                elif self.script_choice.get() == "第四章B7F無限周回雜物":
                    farm.Farm_ch4B7F_2() 
                elif self.script_choice.get() == "第四章B10F雪巨人":
                    farm.Farm_ch4B10F_SnowGlant()
                elif self.script_choice.get() == "擊退敵方勢力":
                    farm.Farm_expCH2()
                elif self.script_choice.get() == "擊退敵方勢力(固定開技版)":
                    farm.Farm_expCH2_2()
                elif self.script_choice.get() == "別離洞窟周回雜物":
                    farm.Farm_BrokeUpCave1()
                elif self.script_choice.get() == "百花之庭周回雜物":
                    farm.Farm_FlowerGarden1()
                elif self.script_choice.get() == "白堊狼穴周回雜物":
                    farm.Farm_WhiteWolf()
                elif self.script_choice.get() == "鬼啼島周回雜物":
                    farm.Farm_GhostIsland()
                elif self.script_choice.get() == "治癒師洞B3F周回雜物":
                    farm.Farm_HealerCave()
                elif self.script_choice.get() == "陽炎洞窟長征金箱":
                    farm.Farm_NinjaCave1()
                elif self.script_choice.get() == "陽炎洞窟B1F簡易周回雜物":
                    farm.Farm_NinjaCave2()
                elif self.script_choice.get() == "陽炎洞窟B1F右上打怪周回雜物":
                    farm.Farm_NinjaCave3()
                elif self.script_choice.get() == "牛牛洞重置任務刷一隻牛":
                    farm.Farm_CowCave1()
                elif self.script_choice.get() == "牛牛洞刷精靈甲":
                    farm.Farm_CowCave2()
                elif self.script_choice.get() == "土之洞窟周回雜物":
                    farm.Farm_EarthCave()
                elif self.script_choice.get() == "火之洞窟周回雜物":
                    farm.Farm_FireCave()
                elif self.script_choice.get() == "風之洞窟周回雜物":
                    farm.Farm_WindCave()
                elif self.script_choice.get() == "光之洞窟周回雜物":
                    farm.Farm_LightCave()
                elif self.script_choice.get() == "水之洞窟周回雜物":
                    farm.Farm_WaterCave()
                elif self.script_choice.get() == "怨嗟洞窟刷蠍子女遺物周回":
                    farm.Farm_ScorpionGirl()
                elif self.script_choice.get() == "怨嗟洞窟周回":
                    farm.Farm_GrudgeCave()
                elif self.script_choice.get() == "懸賞令周回(蠍子女)":
                    farm.Farm_bounty_ScorpionGirl()
                elif self.script_choice.get() == "懸賞令周回(牛頭人)":
                    farm.Farm_bounty_CowMan()
                elif self.script_choice.get() == "懸賞令周回(沉穩的騙子布洛克)":
                    farm.Farm_bounty_faker()
                elif self.script_choice.get() == "爐壺靈廟周回":
                    farm.Farm_2Wbone()
                elif self.script_choice.get() == "金礦石任務(第三章)":
                    farm.Farm_GoldOre()
                elif self.script_choice.get() == "沙華魚人洞窟B2F雜物周回":
                    farm.Farm_FireDragon_B2F()
                elif self.script_choice.get() == "沙華魚人洞窟B3F雜物周回(修女線)":
                    farm.Farm_FireDragon_B3F()
                elif self.script_choice.get() == "FF11_B5F周回雜物":
                    farm.Farm_FF11_B5F()
                elif self.script_choice.get() == "FF11_B5F周回標記":
                    farm.Farm_FF11_B5F_fixed()
                elif self.script_choice.get() == "FF11_B2F周回雜物":
                    farm.Farm_FF11_B2F()
                elif self.script_choice.get() == "FF11_B1F周回雜物":
                    farm.Farm_FF11_B1F()
                elif self.script_choice.get() == "FF11_B2F周回挖礦":
                    farm.Farm_FF11_B2F_mine()
                elif self.script_choice.get() == "旅館不停休息":
                    farm.inn_rest()
                    state.run_count+1 #因為原本腳本沒有
                elif self.script_choice.get() == "測試腳本":
                    farm.test()  
                else:
                    logger.error("未選擇有效腳本")
                    break
                self.current_count_var.set(f"{state.run_count}")  # 更新當前次數
                renew_var_round()
                time.sleep(1)
            if not state.stop_event.is_set():
                logger.info(f"已完成 {self.target_count} 次，腳本結束")
                self.root.after(0, lambda: messagebox.showinfo("提示", f"已完成 {self.target_count} 次"))
        except StopIteration:
            pass
        except Exception as e:
            error_msg = str(e)
            logger.error(f"腳本運行錯誤: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"腳本運行錯誤: {error_msg}"))
        finally:
            # (state) global state.is_running
            state.is_running = False
            self.root.after(0, lambda: self.stop_script())

# 啟動 GUI
