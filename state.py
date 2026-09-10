# -*- coding: utf-8 -*-
"""執行期可變狀態（所有模組透過 import state 共用同一份）"""
import threading

# 計數器
run_count = 0
chest_count = 0
enter_count = 0
tidy_count = 0
trap3_count = 0
trap3_click_count = 0
image_fail_count = 0
heal_period = 0
glant_count = 0
equip_count = 0
personality_count = 0

# 時間 / 相似度
current_time = 0.0
freeze_screen_check_time = 0.0
failed_image_sim = 0.0

# 模式與旗標
inn_mode = 1  # 不休息:0 野外補給:1 地城露營:2 標準房:3 豪華房:4
paused = False
is_running = False
trap_char_all_scared = False
trap_ar_indicator = False
revive_status = False
revived_bol = False
bs_restarted = False
restart_relocation = True
first_freeze_screen_check = True
freeze_check_status = False
list_update_status = True
last_round = False

stop_event = threading.Event()

# 運行時設定
chest_char = None
trap_mode = None
stage = None
adb_port = None
game_player = None
battle_mode = "自動戰鬥"
personality_action = None
personality_score = None
personality_choice = None
script_choice = None

target_checkpoint = None
image_restart = None
image_stage = None

chest_char_list = []
handle_loop_list = None
debuff_list = None
minimap_list = None
images_list = None
target_until = None
on9npc_list = []

preloaded_images = {}
image_dir = "./images/"

# GUI 實例（由 gui 設定）
app = None

# 卡死檢查輔助
freeze_high_sim_count = 0
last_player_restart_time = 0
