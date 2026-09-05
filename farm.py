# -*- coding: utf-8 -*-
"""各關卡 / 周回腳本 Farm_* """
import time
import logging
from tkinter import messagebox

import constants
import state
import core

logger = logging.getLogger(__name__)

# 方便呼叫 core 函式（保持原腳本寫法接近）
find_image = core.find_image
click_image = core.click_image
wait_image = core.wait_image
check_image = core.check_image
tap = core.tap
swipe = core.swipe
press_key = core.press_key
goMap = core.goMap
exitMap = core.exitMap
goToMark = core.goToMark
goToDungeon_check = core.goToDungeon_check
map_click = core.map_click
swipe_map = core.swipe_map
open_chest = core.open_chest
find_chest = core.find_chest
find_chest_auto = core.find_chest_auto
find_chest_process = core.find_chest_process
find_chest_fixed = core.find_chest_fixed
battle_skill = core.battle_skill
health_check = core.health_check
heal = core.heal
bag = core.bag
inn_rest = core.inn_rest
inn_check = core.inn_check
general_inn_mode = core.general_inn_mode
rest_check = core.rest_check
reteam = core.reteam
reteam_pre = core.reteam_pre
revive_main = core.revive_main
revive_npc = core.revive_npc
common_reaction = core.common_reaction
handle_loop = core.handle_loop
image_stability = core.image_stability
waitVanish = core.waitVanish
check_abnormality = core.check_abnormality
check_reconnect = core.check_reconnect
store_equip = core.store_equip
switch_wheel = core.switch_wheel
exitLog = core.exitLog
random_delay = core.random_delay
ch2_pre = core.ch2_pre
ch4_pre = core.ch4_pre
rock_pre = core.rock_pre
comment_check = core.comment_check
take_screenshot = core.take_screenshot
findAll = core.findAll
find_region = core.find_region
waitBattleVanish = core.waitBattleVanish
force_stop_game = core.force_stop_game
start_game_app = core.start_game_app
game_restart = core.game_restart

def Farm_7000g():
    """皇女7000g刷錢"""
    # (state) global state.run_count, state.paused
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止皇女7000g刷錢")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_house"):
            exitLog("起點不正確, 請移到任一城鎮能看到荒屋")
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(2)
        switch_wheel("P_wheel_basement", 3, 0.8)
        wait_image("P_Minimap_ch3_B5F")
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        click_image("P_town")
        click_image("P_dialog_knight")
        inn_check()
        map_click()
        for i in range(2):
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(0.5)
        wait_image("P_chapter3")
        swipe(450, 800, 700, 800)
        click_image("P_chapter1")
        inn_check()
        click_image("P_guild")
        click_image("P_dialog_era")
        click_image("P_gonow")
        match = click_image(["P_oldplace", "P_dialog_listentoher"])
        if match == "P_dialog_listentoher":
            click_image("P_oldplace")
        click_image("P_dialog_goin")
        click_image("P_notonly")
        click_image(["P_uncle_left", "P_uncle_middle", "P_uncle_right"])
        click_image("P_dialog_uncle")
        click_image(["P_girl_left", "P_girl_middle", "P_girl_right"])
        click_image("P_dialog_girl")
        click_image(["P_grandpa_left", "P_grandpa_middle", "P_grandpa_right"])
        click_image("P_dialog_grandpa")
        click_image("P_dialog_why")
        click_image("P_dialog_leftherhere")
        click_image("P_dialog_auok")
        click_image("P_dialog_disagree")
        click_image("P_oldplace")
        click_image("P_dialog_emo")
        click_image("P_dialog_try", region=(423,960,60,60)) #指定範圍備免誤判
        click_image("P_dialog_lazydo")
        click_image("P_coin")
        click_image("P_on9princess")
        wait_image("P_house")
        state.run_count += 1
        earned = state.run_count * 7000
        logger.info(f"----------------次數: {state.run_count}, 收益: {earned}g----------------")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_BrokeUpCave1():
    """別離洞窟B3F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止別離洞窟B3F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_BrokeUpCave"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_BrokeUpCave")
        click_image("P_BrokeUpCave_B2F")
        goToDungeon_check()
        wait_image("P_Minimap_BrokeUpCave_B2F")
        goMap("P_BrokeUpCave_checkpoint1", "P_Minimap_BrokeUpCave_B3F")
        #find_chest_process()
        find_chest_auto()
        exitMap("P_back")
        click_image("P_back")
        wait_image("P_BrokeUpCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"別離洞窟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_WaterCave():
    """水之洞窟周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止水之洞窟周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_WaterCave"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_WaterCave")
        click_image("P_WaterCave_B1F")
        goToDungeon_check()
        wait_image("P_exit")
        if not goMap("P_CaveGoal", "P_WaterCave", swipe_action=(800, 1100, 100, 500, 500), exit_check=True):
            exitMap("P_WaterCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"水之洞窟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_LightCave():
    """光之洞窟周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止光之洞窟周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_LightCave"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_LightCave")
        click_image("P_LightCave_B1F")
        goToDungeon_check()
        wait_image("P_exit")
        goMap("P_LightCave_checkpoint1", "P_LightCave_minimap1")
        goMap("P_LightCave_checkpoint2", "P_LightCave_minimap2")
        find_chest_auto()
        exitMap("P_LightCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"光之洞窟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_EarthCave():
    """土之洞窟周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止土之洞窟周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FireCave"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_EarthCave")
        click_image("P_EarthCave_B1F", similarity=0.8)
        goToDungeon_check()
        wait_image("P_exit")
        find_chest_auto()
        goToMark()
        exitMap("P_EarthCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"土之洞窟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FireCave():
    """火之洞窟周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止火之洞窟周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FireCave"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_FireCave")
        click_image("P_FireCave_B1F", similarity=0.8)
        goToDungeon_check()
        wait_image("P_exit")
        if not goMap("P_CaveGoal", "P_FireCave", exit_check=True):
            exitMap("P_FireCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"火之洞窟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_WindCave():
    """風之洞窟周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止風之洞窟周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_WindCave"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_WindCave")
        click_image("P_WindCave_B1F", similarity=0.8)
        goToDungeon_check()
        wait_image("P_exit")
        if not goMap("P_CaveGoal", "P_WindCave", swipe_action=(100, 800, 800, 800, 500), exit_check=True):
            exitMap("P_WindCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"風之洞窟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_GoldOre():
    """限定金礦石任務(第三章)周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    def get_ore_check():
        if find_image("P_GoldOre_getOre"):
            click_image("P_GoldOre_getOre")
            click_image("P_GoldOre_Ore")
     
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止金礦石任務(第三章)周回")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch3_outside"):
            exitLog("起點不正確, 請移到第三章郊外")
        click_image("P_ch3_outside")
        click_image("P_ch3_B1F")
        wait_image("P_exit")
        goMap("P_GoldOre_checkpoint1", ["P_GoldOre_minimap1", "P_GoldOre_getOre"])
        get_ore_check()
        goMap("P_GoldOre_checkpoint2", ["P_GoldOre_minimap1", "P_GoldOre_getOre"], (75, 400, 825, 400, 500))
        get_ore_check()
        exitMap("P_back")
        click_image("P_back")
        wait_image("P_ch3_outside")
        state.run_count += 1
        logger.info(f"限定金礦石任務(第三章)周回完成，當前次數: {state.run_count}")
        time.sleep(1)
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_NinjaCave1():
    """陽炎洞窟長征金箱子"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    def battle_check():
        check = wait_image(["P_autobattle_active", "P_autobattle_active0", "P_autobattle_active1", 
                            "P_autobattle_inactive", "P_autobattle_inactive0", "P_autobattle_inactive1"])
        if check in ["P_autobattle_inactive", "P_autobattle_inactive0", "P_autobattle_inactive1"]:
            check = click_image(["P_autobattle_inactive", "P_autobattle_inactive0", "P_autobattle_inactive1"])
        time.sleep(1)
        if check in ["P_autobattle_active", "P_autobattle_inactive"]:
            waitVanish("P_autobattle_active")
        elif check in ["P_autobattle_active0", "P_autobattle_inactive0"]:
            waitVanish("P_autobattle_active0")
        elif check in ["P_autobattle_active1", "P_autobattle_inactive1"]:
            waitVanish("P_autobattle_active1")
    
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止陽炎洞窟長征金箱子周回")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_house"):
            exitLog("起點不正確, 請移到第一章城鎮")
        if state.inn_mode == 1 or state.inn_mode == 2:
            exitLog("此腳本不能使用「野外補給」或「地城露營」休息模式")
        click_image("P_house")
        click_image("P_wheel")
        time.sleep(2)
        click_image("P_wheel_special_request")
        click_image("P_wheel_special_request_NinjaCave")
        click_image("P_wheel_jump")
        time.sleep(1.5)
        click_image("P_wheel_special_request_confirm")
        click_image("P_ninjacave_dialog1")
        inn_check()
        click_image("P_guild")
        click_image("P_guild_request")
        click_image("P_guild_request_special")
        for i in range(3):
            R_request_ninjacave = find_region("P_guild_request_ninjacave")
            if R_request_ninjacave:
                break
            else:
                swipe(450, 1200, 450, 400, 500)
                time.sleep(1)
        click_image("P_guild_request_take", region=R_request_ninjacave)
        click_image("P_ninjacave_dialog2")
        click_image("P_guild_leave")
        inn_check()
        map_click()
        for i in range(2):
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "放大地圖")
            time.sleep(0.5)
        wait_image("P_chapter1")
        swipe(700, 800, 450, 800)
        check = find_image(["P_map_ninjacave", "P_map_scalebig", "P_map_scalesmall"])
        if check:
            image = check[0]
            if image == "P_map_ninjacave":
                click_image("P_map_ninjacave")
                goToDungeon_check()
            elif image in ["P_map_scalebig", "P_map_scalesmall"]:
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
                click_image("P_map_ninjacave")
                goToDungeon_check()
            else:
                logger.info("沒有找到忍洞或地圖縮小, 中bug了")
        click_image("P_ninjacave_dialog3")
        wait_image("P_exit")
        press_key("w")
        click_image("P_ninjacave_trapbutton")
        click_image("P_ninjacave_dialog4")
        goMap("P_ninjacave_checkpoint1", "P_ninjacave_minimap1", swipe_action=(825, 1200, 75, 1200, 500))
        goMap("P_ninjacave_checkpoint2", "P_ninjacave_dialog5")
        click_image("P_ninjacave_dialog5")
        battle_check()
        wait_image("P_ninjacave_minimap2")
        time.sleep(1)
        goMap("P_ninjacave_checkpoint3", "P_ninjacave_minimap3")
        goMap("P_ninjacave_checkpoint4", "P_ninjacave_minimap4")
        press_key("w")
        wait_image("P_ninjacave_minimap4B")
        image_stability("P_ninjacave_minimap4B", max_attempts=1)
        goMap("P_ninjacave_checkpoint6", "P_ninjacave_dialog6")
        click_image("P_ninjacave_dialog6")
        #click_image("P_ninjacave_dialog6_optionA") #選戰鬥
        #click_image("P_ninjacave_dialog6_optionA_after")
        click_image("P_ninjacave_dialog6_optionB")
        goMap("P_ninjacave_checkpoint5", "P_ninjacave_minimap5", swipe_action=(75, 1200, 825, 1200, 500))
        goMap("P_ninjacave_checkpoint6", "P_ninjacave_minimap6")
        goMap("P_ninjacave_checkpoint7", "P_ninjacave_minimap7")
        goMap("P_ninjacave_checkpoint8", "P_ninjacave_minimap8")
        goMap("P_ninjacave_checkpoint9", "P_ninjacave_minimap9", swipe_action=(825, 1200, 75, 1200, 500))
        press_key("w")  #可能出bug
        wait_image("P_ninjacave_minimap9B")
        image_stability("P_ninjacave_minimap9B", max_attempts=1)
        goMap("P_ninjacave_checkpoint10", "P_ninjacave_minimap10")
        goMap("P_ninjacave_checkpoint11", "P_ninjacave_minimap11")
        goMap("P_ninjacave_checkpoint12", "P_ninjacave_minimap12", swipe_action=(75, 1200, 825, 1200, 500))
        exitMap("P_ninjacave_dialog7")
        click_image("P_ninjacave_dialog7")
        click_image("P_ninjacave_dialog7_optionA")
        wait_image("P_ninjacave_minimap12B")
        goMap("P_ninjacave_checkpoint13", "P_ninjacave_dialog8")
        click_image("P_ninjacave_dialog8")
        click_image("P_ninjacave_dialog8_optionC")
        battle_check()
        click_image("P_ninjacave_dialog9")
        wait_image("P_ninjacave_minimap13")
        goMap("P_ninjacave_checkpoint14", "P_ninjacave_minimap14")
        goMap("P_ninjacave_checkpoint15", "P_ninjacave_minimap15")
        for i in range(1000):
            if find_image("P_ninjacave_minimap15_screen"):
                press_key("w")
                break
            else:
                press_key("d")
            time.sleep(0.5)
        press_key("w")
        wait_image("P_ninjacave_minimap15B")
        image_stability("P_ninjacave_minimap15B", max_attempts=1)
        goMap("P_ninjacave_checkpoint16", "P_ninjacave_minimap16")
        goMap("P_ninjacave_checkpoint17", "P_ninjacave_minimap17")
        press_key("w")
        wait_image("P_ninjacave_minimap17B")
        image_stability("P_ninjacave_minimap17B", max_attempts=1)
        goMap("P_ninjacave_checkpoint18", "P_ninjacave_minimap18")
        goMap("P_ninjacave_checkpoint19", "P_ninjacave_dialog10", swipe_action=(75, 1200, 75, 400, 500))
        click_image("P_ninjacave_dialog10")
        wait_image("P_ninjacave_minimap19")
        press_key("w")
        click_image("P_ninjacave_dialog11")
        wait_image("P_ninjacave_minimap19B")
        goMap("P_ninjacave_checkpoint20", "P_ninjacave_minimap20", swipe_action=(825, 1200, 75, 1200, 500))
        exitMap("P_map_ninjacave")
        time.sleep(1)
        tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
        time.sleep(1.5)
        swipe(450, 800, 700, 800)
        click_image("P_chapter1")
        general_inn_mode(mode=2)
        wait_image("P_house")
        state.run_count += 1
        logger.info(f"陽炎洞窟長征金箱子周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_NinjaCave2(): 
    """陽炎洞窟B1F簡易周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止陽炎洞窟B1F簡易周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        check = find_image(["P_map_ninjacave", "P_map_scalebig", "P_map_scalesmall"])
        if check:
            image = check[0]
            if image == "P_map_ninjacave":
                click_image("P_map_ninjacave")
                goToDungeon_check()
            elif image in ["P_map_scalebig", "P_map_scalesmall"]:
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
                click_image("P_map_ninjacave")
                goToDungeon_check()
            else:
                exitLog("起點不正確, 請移到大地圖看到「陽炎洞窟」的位置")
        else:
            exitLog("find_image沒有找到任何結果")
        wait_image("P_exit")
        find_chest_auto()
        exitMap("P_map_ninjacave")
        if (state.inn_mode == 3 or state.inn_mode == 4) and (state.run_count+1)%state.heal_period == 0:
            time.sleep(1)
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(1.5)
            swipe(450, 800, 700, 800)
            click_image("P_chapter1")
            inn_check()
            general_inn_mode(mode=2)
            map_click()
            for i in range(2):
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(0.5)
            wait_image("P_chapter1")
            swipe(700, 800, 450, 800)
            time.sleep(1)
            if not find_image("P_map_ninjacave"):
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
        wait_image("P_map_ninjacave")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_NinjaCave3():
    """陽炎洞窟B1F右上打怪周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止陽炎洞窟B1F右上打怪周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        check = find_image(["P_map_ninjacave", "P_map_scalebig", "P_map_scalesmall"])
        if check:
            image = check[0]
            if image == "P_map_ninjacave":
                click_image("P_map_ninjacave")
                goToDungeon_check()
            elif image in ["P_map_scalebig", "P_map_scalesmall"]:
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
                click_image("P_map_ninjacave")
                goToDungeon_check()
            else:
                exitLog("起點不正確, 請移到大地圖看到「陽炎洞窟」的位置")
        else:
            exitLog("find_image沒有找到任何結果")
        wait_image("P_exit")
        goMap("P_ninjacave_checkpoint3", "P_ninjacave_minimap3", swipe_action=(450, 600, 450, 1000,500), goMap_similarity=0.65)
        exitMap("P_map_ninjacave")
        if (state.inn_mode == 3 or state.inn_mode == 4) and (state.run_count+1)%state.heal_period == 0:
            time.sleep(1)
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(1.5)
            swipe(450, 800, 700, 800)
            click_image("P_chapter1")
            inn_check()
            general_inn_mode(mode=2)
            map_click()
            for i in range(2):
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(0.5)
            wait_image("P_chapter1")
            swipe(700, 800, 450, 800)
            time.sleep(1)
            if not find_image("P_map_ninjacave"):
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
        wait_image("P_map_ninjacave")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_CowCave1(): 
    """刷牛洞牛牛周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    def cow_battle():
        match = wait_image(["P_fastbattle_active", "P_fastbattle_inactive"])
        common_reaction(match, None)
        open_chest()
        wait_image("P_exit")

    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止牛洞牛牛周回")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_house"):
            exitLog("起點不正確, 請移到第一章城鎮")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(2)
        if find_image("P_wheel_ch3_heroback", similarity=0.8):
            click_image("P_wheel_ch3_heroback", similarity=0.8)
        else:
            if find_image("P_wheel_ch3"):
                swipe(100, 900, 700, 900, 500)
            elif find_image("P_wheel_ch1"):
                swipe(700, 900, 100, 900, 500)
            swipe(700, 900, 100, 900, 500)
            swipe(450, 1200, 450, 400, 500) #下拉
            time.sleep(1)
            swipe(450, 1200, 450, 400, 500)
            if find_image("P_wheel_ch3_heroback", similarity=0.8):
                click_image("P_wheel_ch3_heroback", similarity=0.8)
            else:
                exitLog("腳本中斷, 原因:沒有找到「凱旋」節點")
        click_image("P_wheel_karma")
        click_image("P_wheel_emo_before")    
        click_image("P_wheel_karma_close")
        click_image("P_wheel_jump")
        time.sleep(4)
        inn_check()
        map_click()
        for i in range(2):
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(0.5)
        wait_image("P_chapter3")
        swipe(450, 800, 700, 800)
        click_image("P_chapter1")
        inn_check()
        click_image("P_guild")
        click_image("P_guild_request")
        click_image("P_guild_request_special")
        for i in range(3):
            R_request_cowcave = find_region("P_guild_request_cowcave")
            if R_request_cowcave:
                break
            else:
                swipe(450, 1200, 450, 400, 500)
                time.sleep(1)
        click_image("P_guild_request_take", region=R_request_cowcave)
        click_image("P_cowcave_dialog1")
        click_image("P_cowcave_dialog2")
        click_image("P_cowcave_dialog3")
        inn_check()
        map_click()
        for i in range(2):
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(0.5)
        tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
        swipe(450, 400, 450, 1200, 500)
        click_image("P_map_cowcave")
        goToDungeon_check()
        wait_image("P_exit")
        if state.run_count == 0:
            reteam_pre()
        else:
            reteam()
        goMap("P_cowcave_checkpoint1", "P_cowcave_dialog4", swipe_action=(75, 400, 825, 1200, 500))
        click_image("P_cowcave_dialog4")
        wait_image("P_exit")
        reteam()
        press_key("w")
        cow_battle()
        wait_image("P_exit")
        reteam()
        exitMap("P_map_cowcave")
        tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
        click_image("P_chapter1")
        general_inn_mode(mode=2)
        wait_image("P_house")
        state.run_count += 1
        logger.info(f"刷牛洞牛牛周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_CowCave2():
    """刷精靈甲周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止精靈甲周回")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_house"):
            exitLog("起點不正確, 請移到第一章城鎮")
        if state.inn_mode == 1 or state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(2)
        switch_wheel("P_wheel_ch3_heroback", 3, final_click=False)
        click_image("P_wheel_karma")
        click_image("P_wheel_emo_before")    
        click_image("P_wheel_karma_close")
        click_image("P_wheel_jump")
        time.sleep(4)
        inn_check()
        map_click()
        for i in range(2):
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(1)
        wait_image("P_chapter3")
        swipe(450, 800, 700, 800)
        click_image("P_chapter1")
        inn_check()
        click_image("P_guild")
        if click_image(["P_guild_request", "P_guild_dialog_welcomeback"]) == "P_guild_dialog_welcomeback":
            click_image("P_guild_request")
        click_image("P_guild_request_special")
        for i in range(3):
            R_request_cowcave = find_region("P_guild_request_cowcave")
            if R_request_cowcave:
                break
            else:
                swipe(450, 1200, 450, 400, 500)
                time.sleep(1)
        click_image("P_guild_request_take", region=R_request_cowcave)
        click_image("P_cowcave_dialog1")
        click_image("P_cowcave_dialog2")
        click_image("P_cowcave_dialog3")
        inn_check()
        map_click()
        for i in range(2):
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(1)
        tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
        time.sleep(1)
        swipe(450, 400, 450, 1200, 500)
        time.sleep(1)
        click_image("P_map_cowcave")
        goToDungeon_check()
        wait_image("P_exit")
        if state.run_count == 0:
            reteam_pre()
        else:
            reteam()
        goMap("P_cowcave_checkpoint2", "P_cowcave_dialog4", swipe_action=(75, 400, 825, 1200, 500))
        click_image("P_cowcave_dialog4")
        goMap("P_cowcave_checkpoint2", "P_cowcave_minimap2")
        tap(constants.L_magnifier[0], constants.L_magnifier[1], "放大鏡")
        time.sleep(1)
        swipe(600, 400, 300, 800, 500)
        time.sleep(0.5)
        click_image("P_cowcave_mushroom1")
        click_image("P_cowcave_mushroom_get")
        wait_image("P_exit")
        reteam()
        destination = goMap("P_cowcave_checkpoint3", ["P_cowcave_dialog5", "P_cowcave_trade"])
        if destination == "P_cowcave_dialog5":
            click_image("P_cowcave_dialog5")
        herbs_get_count = 0
        while herbs_get_count <3:
            wait_image("P_cowcave_trade")
            if find_image("P_cowcave_herbs"):
                if find_image(["P_cowcave_holly", "P_cowcave_rock", "P_cowcave_sake"]):
                    click_image("P_cowcave_trade")
                    click_image("P_cowcave_trade_dialog1")
                    click_image("P_cowcave_herbs_get")
                    herbs_get_count += 1
                    if herbs_get_count < 3:
                        click_image("P_cowcave_trade_continue")
                    else:
                        click_image("P_cowcave_trade_end")
                        continue
            click_image("P_cowcave_tradeother")
            click_image("P_cowcave_trade_dialog2")
            wait_image("P_cowcave_trade_dialog3")
            tap(constants.L_fasttalking[0], constants.L_fasttalking[1], "快速對話")
            click_image("P_cowcave_trade_dialog3")
        wait_image("P_exit")
        reteam()
        goMap("P_cowcave_checkpoint4", "P_cowcave_minimap4")
        click_image("P_cowcave_mushroom2")
        click_image("P_cowcave_mushroom_get")
        wait_image("P_exit")
        reteam()
        goMap("P_cowcave_checkpoint5", "P_cowcave_minimap5", swipe_action=(450, 1060, 450, 530, 500), goMap_similarity=0.8)
        tap(constants.L_magnifier[0], constants.L_magnifier[1], "快速對話")
        time.sleep(1)
        swipe(300, 400, 600, 800, 500)
        click_image("P_cowcave_mushroom1")
        click_image("P_cowcave_mushroom_get")
        click_image("P_cowcave_mushroom_allget")
        wait_image("P_exit")
        reteam()
        exitMap("P_cowcave_dialog6")
        click_image("P_cowcave_dialog6")
        click_image("P_cowcave_dialog7")
        click_image("P_cowcave_dialog8")
        click_image("P_cowcave_dialog9")
        wait_image("P_exit")
        exitMap("P_map_cowcave")
        tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
        click_image("P_chapter1")
        inn_check()     
        click_image("P_guild")
        click_image("P_guild_request")
        click_image("P_guild_request_special")
        click_image("P_guild_request_completed")
        click_image("P_cowcave_dialog10")
        click_image("P_cowcave_dialog11")
        click_image("P_cowcave_dialog12")
        click_image("P_guild_leave")
        click_image("P_cowcave_dialog13")
        inn_check()
        if not find_image("P_downlist"):
            click_image("P_uplist")
            time.sleep(1.5)
        store_equip("P_equip_erumon_cloth")
        general_inn_mode(mode=2)
        wait_image("P_house")
        state.run_count += 1
        logger.info(f"刷精靈甲周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_expCH2():
    """刷經驗任務之第二章擊退敵方勢力"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.handle_loop_list, state.inn_mode
    def battle_handle():
        aoe_list = ["P_aoe_holy_special", "P_aoe_earth_special", "P_aoe_light", "P_aoe_dark", "P_aoe_fire", "P_aoe_earth", "P_aoe_nil"]
        special_list = ["P_aoe_holy_special", "P_aoe_earth_special"]
        for i in range(20):
            result = find_image(aoe_list)
            if result:
                match = result[0]
                if match in special_list:
                    aoe_list.remove(match)
                click_image(match)
                click_image("P_aoe_confirm")
            else:
                click_image("P_battle_wait")
            match = wait_image(["P_battle_bar", "P_expCH2_dialog2"])
            if match == "P_expCH2_dialog2":
                click_image("P_expCH2_dialog2")
                break
    
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch2_outside"):
            exitLog("起點不正確, 請移到第二章郊外看到「貿易水路」的位置")
        ch2_pre()
        click_image("P_ch2_outside")
        click_image("P_ch2_B7F")
        goToDungeon_check()
        wait_image("P_exit")
        goMap("P_expCH2_checkpoint1", ["P_expCH2_dialog1", "P_expCH2_dialog3"], swipe_action=(75, 1000, 825, 400, 500), relocation=False)
        click_image(["P_expCH2_dialog1", "P_expCH2_dialog3"])
        wait_image("P_battle_bar")
        battle_handle()
        click_image("P_expCH2_optionB")
        for i in range(2):
            wait_image("P_exit")
            time.sleep(1)
            goMap("P_expCH2_checkpoint1", ["P_expCH2_dialog1", "P_expCH2_dialog3"], relocation=False)
            click_image(["P_expCH2_dialog1", "P_expCH2_dialog3"])
            wait_image("P_battle_bar")
            battle_handle()
            click_image("P_expCH2_optionB")
        exitMap("P_back")
        click_image("P_back")
        click_image("P_town")
        inn_check()
        inn_rest()
        click_image("P_outside")
        wait_image("P_ch2_outside")
        state.run_count += 1
        logger.info(f"擊退敵方勢力周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_expCH2_2():
    """刷經驗任務之第二章擊退敵方勢力(無腦開右下技能版)"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.handle_loop_list, state.inn_mode
    def battle_handle():
        for i in range(20):
            time.sleep(1)
            tap(553,1103, "右下技能")
            click_image("P_aoe_confirm")
            match = wait_image(["P_battle_bar", "P_expCH2_dialog2"])
            if match == "P_expCH2_dialog2":
                click_image("P_expCH2_dialog2")
                break
    
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch2_outside"):
            exitLog("起點不正確, 請移到第二章郊外看到「貿易水路」的位置")
        if state.inn_mode == 0 or state.inn_mode == 1:
            exitLog("此腳本不能使用「不休息」或「野外補給」休息模式")
        ch2_pre()
        click_image("P_ch2_outside")
        click_image("P_ch2_B7F")
        goToDungeon_check()
        wait_image("P_exit")
        goMap("P_expCH2_checkpoint1", ["P_expCH2_dialog1", "P_expCH2_dialog3"], swipe_action=(75, 1000, 825, 400, 500), relocation=False)
        click_image(["P_expCH2_dialog1", "P_expCH2_dialog3"])
        wait_image("P_battle_bar")
        battle_handle()
        click_image("P_expCH2_optionB")
        for i in range(2):
            wait_image("P_exit")
            time.sleep(1)
            goMap("P_expCH2_checkpoint1", ["P_expCH2_dialog1", "P_expCH2_dialog3"], relocation=False)
            click_image(["P_expCH2_dialog1", "P_expCH2_dialog3"])
            wait_image("P_battle_bar")
            battle_handle()
            click_image("P_expCH2_optionB")
        wait_image("P_exit")
        goToMark(["P_back", "P_buff"])
        if not find_image("P_back"):
            click_image("P_buff")
        click_image("P_back")
        if state.inn_mode == 2:
            click_image("P_town")
            inn_check()
            map_click()
            for i in range(2):
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(0.5)
            click_image("P_chapter1")
            click_image("P_outside")
            click_image("P_ch1_outside")
            click_image("P_ch1_B7F")
            goToDungeon_check()
            wait_image("P_exit")
            goMap("P_ch1_B7F_checkpoint1", "P_onsen_rest")
            time.sleep(5)
            click_image("P_onsen_rest")
            click_image("P_onsen_dialog1")
            wait_image("P_exit")
            check = goMap("P_ch1_B7F_checkpoint2", ["P_back", "P_buff"], swipe_action=(100, 900, 700, 900, 500))
            if check == "P_buff":
                click_image("P_buff")
            click_image("P_back")
            click_image("P_town")
            inn_check()
            map_click()
            click_image("P_chapter2")
            inn_check()
            click_image("P_outside")
        else:
            general_inn_mode(mode=1)
        wait_image("P_ch2_outside")
        state.run_count += 1
        logger.info(f"擊退敵方勢力周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch2B9F():
    """第二章船二周回寶箱"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch2_outside"):
            exitLog("起點不正確, 請移到第二章郊外看到「貿易水路」的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        ch2_pre()
        click_image("P_ch2_outside")    
        click_image("P_ch2_B8F")
        goToDungeon_check()
        wait_image("P_exit")
        goMap("P_Farm_ch2B9F_checkpoint1", "P_Farm_ch2B9F_minimap1")     
        find_chest_process(map=["P_Farm_ch2B9F_chestarea1", "P_Farm_ch2B9F_chestarea2", "P_Farm_ch2B9F_chestarea3", 
                                "P_Farm_ch2B9F_chestarea4", "P_Farm_ch2B9F_chestarea5", "P_Farm_ch2B9F_chestarea6"], 
                           direction = None, forbidden_mode=False)
        exitMap(["P_back", "P_buff"])
        if not find_image("P_back"):
            click_image("P_buff")
        click_image("P_back")
        wait_image("P_ch2_outside")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"第二章船一周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch2B1F():
    """第二章第一街周回寶箱"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch2_outside"):
            exitLog("起點不正確, 請移到第二章郊外看到「貿易水路」的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        ch2_pre()
        click_image("P_ch2_outside")    
        time.sleep(0.5)
        if not find_image("P_ch2_B1F"):
            swipe(600, 800, 600, 1200, 300)
        click_image("P_ch2_B1F")
        goToDungeon_check()
        wait_image("P_exit")
        #find_chest_process()
        find_chest_auto()
        exitMap(["P_back", "P_buff", "P_ch2_outside"])
        check = find_image(["P_back", "P_buff", "P_ch2_outside"])
        if check:
            image = check[0]
            if image == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif image == "P_back":
                click_image("P_back")
            elif image == "P_ch2_outside":
                pass
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_ch2_outside")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"第二章一號街周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch3B7F():
    """第三章第七區刷巨人"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period, state.glant_count, state.debuff_list, state.list_update_status
    def battle_handle():
        for i in range(20):
            match = wait_image(["P_battle_bar", "P_chest_open", "P_exit", "P_battle_death_main", "P_battle_death_npc1", "P_battle_death_npc2"], 
                               similarity=0.8)
            if match == "P_battle_bar":
                time.sleep(0.5)
                tap(553,1103, "右下技能")
                if not click_image("P_aoe_confirm", timeout=2):
                    tap(450, 800, "巨人")
                    tap(722, 839, "巨人同排女妖")
                    tap(654, 703, "後排右女妖")
                    tap(250, 703, "後排左女妖")
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
    
    enemy = [(450, 800, "巨人"),(722, 839, "巨人同排女妖"),(654, 703, "後排右女妖"),(250, 703, "後排左女妖")]
    
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch3_outside"):
            exitLog("起點不正確, 請移到第三章郊外位置")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        if state.list_update_status == True:
            state.debuff_list.append("P_banSkill")
            logger.info(f"首次執行，增加所需變數，目前debuff_list:{state.debuff_list}")
            state.list_update_status = False
        click_image("P_ch3_outside")
        click_image("P_ch3_B7F")
        goToDungeon_check()
        wait_image("P_exit")
        time.sleep(1)
        press_key("a")
        time.sleep(0.5)
        logger.info("檢查是否出現巨人，需時約5秒")
        for i in range(5):
            if find_image(["P_ch3B7F_glant1", "P_ch3B7F_glant2"], similarity=0.85):
                logger.info("找到巨人, 準備戰鬥")
                glant_check = True
                break
        else:
            logger.info("沒有找到巨人, 離開地圖")
            glant_check = False
        run_count_bol = False
        if glant_check: #找到巨人前進及戰鬥
            health_check()
            swipe(450, 800, 450, 100,2000)
            fastbattle_check = wait_image(["P_fastbattle_active", "P_fastbattle_inactive"])
            if fastbattle_check == "P_fastbattle_inactive":
                click_image("P_fastbattle_inactive")
            state.glant_count += 1
            run_count_bol = True
            #battle_handle()
            battle_skill([(450, 850, "目標")])
        exitMap(["P_back", "P_buff"], heal_check=False)
        if not find_image("P_back"):
            click_image("P_buff")
        click_image("P_back")
        wait_image("P_ch3_outside")
        logger.info(f"state.glant_count: {state.glant_count}")
        if state.glant_count:
            if state.glant_count%state.heal_period == 0:
                general_inn_mode(mode=1)
                wait_image("P_ch3_outside")
                state.glant_count = 0
        if run_count_bol == True:
            state.run_count += 1
            logger.info(f"第三章第七區刷巨人周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch4B1F():
    """第四章B1F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止第四章B1F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch4_outside"):
            exitLog("起點不正確, 請移到第二章郊外看到「豪雪地帶」的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        ch4_pre()
        click_image("P_ch4_outside")    
        time.sleep(0.5)
        if not find_image("P_ch4_B0F"):
            swipe(600, 800, 600, 1200, 300)
        click_image("P_ch4_B0F")
        goToDungeon_check()
        wait_image("P_exit")
        goMap("P_ch4_B1F_checkpoint1", "P_ch4_B1F_minimap1", goMap_similarity=0.65)
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_ch4_outside")
        if (state.run_count+1)%state.heal_period == 0:
            general_inn_mode(mode=1)
        wait_image("P_village")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch4B4F():
    """第四章B4F周回雪山兇鳥帽"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period, state.equip_count
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止第四章B4F周回雪山兇鳥帽")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch4_outside"):
            exitLog("起點不正確, 請移到第二章郊外看到「豪雪地帶」的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        ch4_pre()
        click_image("P_ch4_outside")    
        click_image("P_ch4_B4F")
        goToDungeon_check()
        wait_image("P_exit")
        goToMark("P_ch4_B4F_minimap1")
        goToMark("P_ch4_B4F_minimap6")
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_ch4_outside")
        if (state.run_count+1)%state.heal_period == 0:
            store_equip("P_ch4_SnowHat")
            general_inn_mode(mode=1)
        wait_image("P_village")
        state.run_count += 1
        logger.info(f"已獲得{state.equip_count}件雪山兇鳥帽")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch4B6F():
    """第四章B6F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止第四章B6F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch4_outside"):
            exitLog("起點不正確, 請移到第二章郊外看到「豪雪地帶」的位置") 
        ch4_pre()
        click_image("P_ch4_outside")    
        time.sleep(0.5)
        click_image("P_ch4_B5F")
        goToDungeon_check()
        wait_image("P_exit")
        goMap("P_ch4_B6F_checkpoint1", "P_ch4_B6F_minimap1", goMap_similarity=0.65)
        wait_image("P_exit")
        goToMark("P_ch4_B6F_minimap2")
        if state.inn_mode == 2 and (state.run_count+1)%state.heal_period == 0:
            goToMark("P_onsen_rest")
            click_image("P_onsen_rest")
            time.sleep(5)
            click_image("P_onsen_rest2")
            click_image("P_onsen_dialog1")
            wait_image("P_exit")
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_ch4_outside")
        if (state.run_count+1)%state.heal_period == 0:
            general_inn_mode(mode=1)
        wait_image("P_village")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch4B7F():
    """第四章B7F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止第四章B7F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_ch4_outside"):
            exitLog("起點不正確, 請移到第四章郊外看到「豪雪地帶」的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        ch4_pre()
        click_image("P_ch4_outside")    
        time.sleep(0.5)
        click_image("P_ch4_B7F")
        goToDungeon_check()
        wait_image("P_exit")
        find_chest_auto()
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_ch4_outside")
        if (state.run_count+1)%state.heal_period == 0:
            general_inn_mode(mode=1)
        wait_image("P_village")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch4B7F_2():
    """第四章B7F無限周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止第四章B7F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if state.inn_mode != 0:
            exitLog("此腳本只能使用「不休息」休息模式")
        if state.run_count == 0:
            if not find_image("P_ch4_B7F_minimap2"):
                exitLog("起點不正確, 請移到第四章郊外看到「豪雪地帶」的位置") 
            ch4_pre()
        wait_image("P_exit")
        goToMark("P_ch4_B7F_minimap1")
        goToMark("P_ch4_B6F_minimap3")
        check = exitMap(["P_back", "P_buff", "P_ch4_B7F_inside"])
        if not find_image("P_back"):
            click_image("P_buff")
        else:
            click_image("P_ch4_B7F_inside")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ScorpionGirl():
    """怨嗟洞窟刷蠍子女遺物周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_GrudgeCave"):
            exitLog("起點不正確, 請移到第一章郊外看到「怨嗟洞窟」的位置")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_GrudgeCave")
        click_image("P_GrudgeCave_B4F")
        wait_image("P_exit")
        goMap("P_GrudgeCave_checkpoint1", "P_GrudgeCave_minimap1", swipe_action=(450, 600, 450, 900,500))
        time.sleep(1)
        exitMap("P_back")
        click_image("P_back")
        wait_image("P_GrudgeCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"怨嗟洞窟刷蠍子女遺物周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_GrudgeCave():
    """怨嗟洞窟周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_GrudgeCave"):
            exitLog("起點不正確, 請移到第一章郊外看到「怨嗟洞窟」的位置")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_GrudgeCave")
        click_image("P_GrudgeCave_B3F")
        wait_image("P_exit")
        goToMark()
        exitMap(["P_back"])
        click_image("P_back")
        wait_image("P_town")
        wait_image("P_GrudgeCave")
        general_inn_mode(mode=1)
        wait_image("P_town")
        state.run_count += 1
        logger.info(f"怨嗟洞窟刷蠍子女遺物周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_bounty_ScorpionGirl():
    """懸賞令周回(蠍子女)"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    def battle_handle():
        for i in range(20):
            match = wait_image(["P_battle_bar", "P_chest_open", "P_exit", "P_battle_death_main", "P_battle_death_npc1", "P_battle_death_npc2"], 
                               similarity=0.8)
            if match == "P_battle_bar":
                time.sleep(0.5)
                tap(553,1103, "右下技能")
                if not click_image("P_aoe_confirm", timeout=2, fail_count=False):
                    tap(300, 800, "左蠍女")
                    tap(600, 800, "右蠍女")
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
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_house"):
            exitLog("起點不正確, 請移到任一城鎮能看到荒屋")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(1)
        switch_wheel("P_wheel_saveduke", 3)
        wait_image("P_house")
        click_image("P_guild")
        click_image("P_bounty_dialog1")
        click_image("P_guild_request")
        wait_image("P_guild_request_special")
        if find_image("P_guild_bounty"):
            click_image("P_guild_bounty")
        else:
            swipe(530, 1408, 400, 1408, 500)
            click_image("P_guild_bounty")
        time.sleep(2)
        check = wait_image(["P_guild_bounty_close", "P_guild_bounty_back"])
        if check == "P_guild_bounty_close":
            click_image("P_guild_bounty_close")
        click_image("P_guild_bounty_back")
        click_image("P_guild_leave")
        time.sleep(1)
        inn_check()
        click_image("P_outside")
        click_image("P_ch1_outside")
        click_image("P_ch1_B2F")
        goToDungeon_check()
        wait_image("P_exit")
        if state.run_count == 0:
            reteam_pre()
        else:
            reteam()
        goToMark()
        check = exitMap(["P_back", "P_buff"], heal_check=False)
        if check == "P_buff":
            click_image("P_buff")
        click_image("P_back")
        wait_image("P_town")
        if state.inn_mode == 1:
            general_inn_mode(mode=1)
        click_image("P_town")
        inn_check()
        click_image("P_guild")
        click_image("P_guild_request")
        if find_image("P_guild_bounty"):
            click_image("P_guild_bounty")
        else:
            swipe(530, 1408, 400, 1408, 500)
            click_image("P_guild_bounty")
        click_image("P_guild_bounty_reward")
        click_image("P_guild_bounty_reward_close")
        click_image("P_guild_bounty_back")
        click_image("P_guild_leave")
        inn_check()
        if state.inn_mode == 3 or state.inn_mode ==4:
            general_inn_mode(mode=2)
        wait_image("P_house")
        state.run_count += 1
        logger.info(f"懸賞令周回(蠍子女)完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_bounty_CowMan():
    """懸賞令周回(牛頭人)"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_house"):
            exitLog("起點不正確, 請移到任一城鎮能看到荒屋")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(1)
        switch_wheel("P_wheel_saveduke", 3)
        wait_image("P_house")
        click_image("P_guild")
        click_image("P_bounty_dialog1")
        click_image("P_guild_request")
        wait_image("P_guild_request_special")
        if find_image("P_guild_bounty"):
            click_image("P_guild_bounty")
        else:
            swipe(530, 1408, 400, 1408, 500)
            click_image("P_guild_bounty")
        time.sleep(2)
        check = wait_image(["P_guild_bounty_close", "P_guild_bounty_back"])
        if check == "P_guild_bounty_close":
            click_image("P_guild_bounty_close")
        click_image("P_guild_bounty_back")
        click_image("P_guild_leave")
        time.sleep(1)
        inn_check()
        click_image("P_outside")
        click_image("P_ch1_outside")
        click_image("P_ch1_B5F")
        goToDungeon_check()
        wait_image("P_exit")
        if state.run_count == 0:
            reteam_pre()
        else:
            reteam()
        goToMark("P_bounty_cow_minimap")    
        #battle_handle()
        check = exitMap(["P_back", "P_buff"], heal_check=False)
        if check == "P_buff":
            click_image("P_buff")
        click_image("P_back")
        wait_image("P_town")
        if state.inn_mode == 1:
            general_inn_mode(mode=1)
        click_image("P_town")
        inn_check()
        click_image("P_guild")
        click_image("P_guild_request")
        if find_image("P_guild_bounty"):
            click_image("P_guild_bounty")
        else:
            swipe(530, 1408, 400, 1408, 500)
            click_image("P_guild_bounty")
        click_image("P_guild_bounty_reward")
        click_image("P_guild_bounty_reward_close")
        click_image("P_guild_bounty_back")
        click_image("P_guild_leave")
        inn_check()
        if state.inn_mode == 3 or state.inn_mode ==4:
            general_inn_mode(mode=2)
        wait_image("P_house")
        state.run_count += 1
        logger.info(f"懸賞令周回(蠍子女)完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_bounty_faker():
    """懸賞令周回(沉穩的騙子布洛克)"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.revived_bol
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_house"):
            exitLog("起點不正確, 請移到任一城鎮能看到荒屋")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        if state.run_count == 0:
            for i in range(3):
                name = "P_ch1_on9npc" + str(i+1)
                state.handle_loop_list.append(name)
            logger.info(f"首次執行，增加所需變數，目前handle_loop_list:{state.handle_loop_list}")
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(1)
        if find_image("P_wheel_saveduke", similarity=0.8):
            click_image("P_wheel_saveduke", similarity=0.8)
        else:
            if find_image("P_wheel_ch3"):
                swipe(100, 900, 700, 900, 500)
            elif find_image("P_wheel_ch1"):
                swipe(700, 900, 100, 900, 500)
            swipe(700, 900, 100, 900, 500)
            if find_image("P_wheel_saveduke", similarity=0.8):
                click_image("P_wheel_saveduke", similarity=0.8)
            else:
                exitLog("腳本中斷, 原因:沒有找到「營救公爵的委託」節點")
        click_image("P_wheel_jump")
        wait_image("P_house")
        click_image("P_guild")
        click_image("P_bounty_dialog1")
        click_image("P_guild_request")
        wait_image("P_guild_request_special")
        if find_image("P_guild_bounty"):
            click_image("P_guild_bounty")
        else:
            swipe(530, 1408, 400, 1408, 500)
            click_image("P_guild_bounty")
        time.sleep(2)
        check = wait_image(["P_guild_bounty_close", "P_guild_bounty_back"])
        if check == "P_guild_bounty_close":
            click_image("P_guild_bounty_close")
        click_image("P_guild_bounty_back")
        click_image("P_guild_leave")
        time.sleep(1)
        inn_check()
        click_image("P_outside")
        click_image("P_ch1_outside")
        click_image("P_ch1_B3F")
        goToDungeon_check()
        wait_image("P_exit")
        goMap(["P_bounty_faker_checkpoint1", "P_bounty_faker_checkpoint1B"], ["P_bounty_faker_dialog1", "P_bounty_faker_dialog4"], 
              swipe_action=[None, (600, 800, 300, 800, 500)], goMap_similarity=0.8)
        for i in range(10):
            if click_image(["P_bounty_faker_dialog1", "P_bounty_faker_dialog4"]):
                click_image("P_bounty_faker_dialog2")
                click_image("P_bounty_faker_dialog3")
            match = wait_image(["P_fastbattle_active", "P_fastbattle_inactive"])
            common_reaction(match, None)
            #wait_image("P_exit")
            if state.revived_bol:
                state.revived_bol = False
                press_key("w")
            else:
                wait_image("P_exit")
                break
        check = goMap("P_bounty_faker_checkpoint2", ["P_back", "P_buff"], swipe_action=[None, (300, 800, 600, 800, 500)])
        if check == "P_buff":
            click_image("P_buff")
        click_image("P_back")
        wait_image("P_town")
        if state.inn_mode == 1:
            general_inn_mode(mode=1)
        click_image("P_town")
        inn_check()
        click_image("P_guild")
        click_image("P_guild_request")
        if find_image("P_guild_bounty"):
            click_image("P_guild_bounty")
        else:
            swipe(530, 1408, 400, 1408, 500)
            click_image("P_guild_bounty")
        click_image("P_guild_bounty_reward")
        click_image("P_guild_bounty_reward_close")
        click_image("P_guild_bounty_back")
        click_image("P_guild_leave")
        inn_check()
        if state.inn_mode == 3 or state.inn_mode ==4:
            general_inn_mode(mode=2)
        wait_image("P_house")
        state.run_count += 1
        logger.info(f"懸賞令周回(沉穩的騙子布洛克)完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FlowerGarden1():
    """百花之庭周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        check = find_image(["P_map_FlowerGarden", "P_map_scalebig", "P_map_scalesmall"], similarity=0.75)
        if check:
            image = check[0]
            if image == "P_map_FlowerGarden":
                click_image("P_map_FlowerGarden", similarity=0.75)
                goToDungeon_check()
            elif image in ["P_map_scalebig", "P_map_scalesmall"]:
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
                click_image("P_map_FlowerGarden")
                goToDungeon_check()
            else:
                exitLog("起點不正確, 請移到大地圖看到「百花之庭」的位置")
        else:
            exitLog("find_image沒有找到任何結果")
        wait_image("P_exit")
        #find_chest_process()
        find_chest_auto()
        exitMap("P_map_FlowerGarden")
        if (state.inn_mode == 3 or state.inn_mode == 4) and (state.run_count+1)%state.heal_period == 0:
            time.sleep(1)
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(1.1)
            click_image("P_chapter1")
            inn_check()
            general_inn_mode(mode=2)
            map_click()
            for i in range(2):
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(0.5)
            wait_image("P_chapter1")
            time.sleep(1)
            if not find_image("P_map_FlowerGarden"):
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
        wait_image("P_map_FlowerGarden")
        state.run_count += 1
        logger.info(f"別離洞窟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_WhiteWolf():
    """白堊狼穴周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        check = find_image(["P_map_WhiteWolf", "P_map_scalebig", "P_map_scalesmall"], similarity=0.75)
        if check:
            image = check[0]
            if image == "P_map_WhiteWolf":
                click_image("P_map_WhiteWolf", similarity=0.75)
                click_image("P_map_WhiteWolf_B1F")
                goToDungeon_check()
            elif image in ["P_map_scalebig", "P_map_scalesmall"]:
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
                click_image("P_map_WhiteWolf")
                click_image("P_map_WhiteWolf_B2F")
                goToDungeon_check()
            else:
                exitLog("起點不正確, 請移到大地圖看到「白堊狼穴」的位置")
        else:
            exitLog("find_image沒有找到任何結果")
        wait_image("P_exit")
        if state.run_count == 0:
            reteam_pre()
        else:
            reteam()
        find_chest_auto()
        check = exitMap(["P_back", "P_worldMap"])
        if check:
            if check == "P_back":
                click_image("P_back")
            elif check == "P_worldMap":
                pass
            else:
                exitLog("沒有找到正確結果")
        logger.info(f"state.run_count: {state.run_count}, state.heal_period: {state.heal_period}, state.inn_mode: {state.inn_mode}")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                time.sleep(1)
                click_image("P_chapter4")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                wait_image("P_chapter4")
                swipe(300,800,600,800,500)
                time.sleep(1)
            elif state.inn_mode == 1 or state.inn_mode == 0:
                general_inn_mode(mode=1)
                click_image("P_worldMap")
        else:
            click_image("P_worldMap")
        wait_image("P_map_WhiteWolf")
        state.run_count += 1
        logger.info(f"白堊狼穴周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_GhostIsland(): 
    """鬼啼島B2F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止鬼啼島B2F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        if state.run_count == 0:
            for i in range(1):
                name = "P_GhostIsland_on9npc" + str(i+1)
                state.handle_loop_list.append(name)
            logger.info(f"首次執行，增加所需變數，目前handle_loop_list:{state.handle_loop_list}")
        check = find_image(["P_GhostIsland", "P_map_scalebig", "P_map_scalesmall"])
        if check:
            image = check[0]
            if image == "P_GhostIsland":
                click_image("P_GhostIsland")
                click_image("P_GhostIsland_B2F")
                goToDungeon_check()
            elif image in ["P_map_scalebig", "P_map_scalesmall"]:
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
                click_image("P_GhostIsland")
                click_image("P_GhostIsland_B2F")
                goToDungeon_check()
            else:
                exitLog("起點不正確, 請移到大地圖看到「鬼啼島」的位置")
        else:
            exitLog("find_image沒有找到任何結果")
        wait_image("P_exit")
        find_chest_auto()
        goToMark("P_back")
        click_image("P_back")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                wait_image(["P_map_scalebig", "P_map_scalesmall"])
                swipe(300,700,700,900,500)
                click_image("P_map_scalesmall")
                click_image("P_chapter3")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                wait_image("P_chapter3")
                click_image("P_map_scalebig")
                time.sleep(1)
                swipe(700,900,300,900,500)
                time.sleep(1)
            elif state.inn_mode == 1:
                general_inn_mode(mode=1)
                click_image("P_worldMap")
        else:
            click_image("P_worldMap")
        wait_image("P_GhostIsland")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_2Wbone():
    """爐壺靈廟周回"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止爐壺靈廟周回")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_2Wbone"):
            exitLog("起點不正確, 請移到爐壺靈廟前")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_2Wbone")
        goToDungeon_check()
        wait_image("P_2Wbone_minimap1")
        goMap("P_2Wbone_checkpoint1", "P_2Wbone_minimap2")
        goMap("P_2Wbone_checkpoint2", "P_2Wbone_minimap3")
        goMap("P_2Wbone_checkpoint3", "P_2Wbone_minimap4")
        exitMap("P_2Wbone")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                wait_image(["P_map_scalebig", "P_map_scalesmall"])
                click_image("P_map_scalesmall")
                click_image("P_chapter1")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                wait_image("P_chapter1")
                click_image("P_map_scalebig")
                time.sleep(1)
            elif state.inn_mode == 1 or state.inn_mode == 0:
                general_inn_mode(mode=1)
                click_image("P_worldMap")
        click_image("P_map_temple")
        wait_image("P_2Wbone")
        state.run_count += 1
        logger.info(f"爐壺靈廟周回完成，當前次數: {state.run_count}")
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FireDragon_B2F():
    "沙華魚人洞窟B2F雜物周回"
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止沙華魚人洞窟B2F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FireDragon"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_FireDragon")
        click_image("P_FireDragon_B2F", similarity=0.8)
        goToDungeon_check()
        wait_image("P_exit")
        health_check()
        find_chest_auto()
        goToMark("P_back")
        click_image("P_back")
        wait_image("P_FireDragon")
        if (state.run_count+1)%state.heal_period == 0:
            general_inn_mode(mode=1)
        wait_image("P_FireDragon")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FireDragon_B3F():
    "沙華魚人洞窟B3F雜物周回(修女線)"
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止沙華魚人洞窟B3F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FireDragon"):
            exitLog("起點不正確, 請移到第一章郊外")
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_FireDragon")
        click_image("P_FireDragon_B2F", similarity=0.8)
        goToDungeon_check()
        wait_image("P_exit")
        if state.run_count == 0:
            reteam_pre()
        else:
            reteam()
        goToMark("P_FireDragon_B3F_minimap3")
        exitMap("P_back")
        click_image("P_back")
        wait_image("P_FireDragon")
        if (state.run_count+1)%state.heal_period == 0:
            general_inn_mode(mode=1)
        wait_image("P_FireDragon")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_HealerCave(): 
    """治癒師洞B3F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止治癒師洞B3F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        check = find_image(["P_HealerCave", "P_map_scalebig", "P_map_scalesmall"])
        if check:
            image = check[0]
            if image == "P_HealerCave":
                click_image("P_HealerCave")
                click_image("P_HealerCave_B3F")
                goToDungeon_check()
            elif image in ["P_map_scalebig", "P_map_scalesmall"]:
                tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                time.sleep(2)
                click_image("P_HealerCave")
                click_image("P_HealerCave_B3F")
                goToDungeon_check()
            else:
                exitLog("起點不正確, 請移到大地圖看到「治癒師洞」的位置")
        else:
            exitLog("find_image沒有找到任何結果")
        wait_image("P_exit")
        if state.run_count == 0:
            reteam_pre()
        else:
            reteam()
        find_chest_auto()
        goToMark("P_back")
        click_image("P_back")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                click_image("P_chapter4")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                wait_image("P_chapter4")
                time.sleep(1)
            elif state.inn_mode == 1:
                general_inn_mode(mode=1)
                click_image("P_worldMap")
        else:
            click_image("P_worldMap")
        wait_image("P_HealerCave")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FF11_B5F():
    """FF11_B5F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止FF11_B5F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FF11_B5F"):
            exitLog("起點不正確, 請移到看到FF11_B5F的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_FF11_B5F")    
        goToDungeon_check()
        wait_image("P_exit")
        find_chest_auto()
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_FF11_B5F")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                wait_image("P_FF11Cave")
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(1.5)
                click_image("P_chapter1")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                time.sleep(1)
                if not find_image("P_FF11Cave"):
                    tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                    time.sleep(2)
                    swipe(450,600,450,1000,500)
                click_image("P_FF11Cave")
                time.sleep(1)
            elif state.inn_mode == 1 or state.inn_mode == 0:
                general_inn_mode(mode=1)
        wait_image("P_FF11_B5F")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FF11_B2F():
    """FF11_B2F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止FF11_B2F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FF11_B2F"):
            exitLog("起點不正確, 請移到看到FF11_B2F的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_FF11_B2F")    
        goToDungeon_check()
        wait_image("P_exit")
        find_chest_auto()
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_FF11_B5F")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                wait_image("P_FF11Cave")
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(1.5)
                click_image("P_chapter1")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                time.sleep(1)
                if not find_image("P_FF11Cave"):
                    tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                    time.sleep(2)
                    swipe(450,600,450,1000,500)
                click_image("P_FF11Cave")
                time.sleep(1)
            elif state.inn_mode == 1 or state.inn_mode == 0:
                general_inn_mode(mode=1)
        wait_image("P_FF11_B2F")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FF11_B1F():
    """FF11_B1F周回雜物"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止FF11_B1F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FF11_B1F"):
            exitLog("起點不正確, 請移到看到FF11_B1F的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_FF11_B1F")    
        goToDungeon_check()
        wait_image("P_exit")
        find_chest_auto()
        check = exitMap(["P_back", "P_buff", "P_FF11_B1F"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            elif check == "P_FF11_B1F":
                pass
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_FF11_B1F")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                wait_image("P_FF11Cave")
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(1.5)
                click_image("P_chapter1")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                time.sleep(1)
                if not find_image("P_FF11Cave"):
                    tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                    time.sleep(2)
                    swipe(450,600,450,1000,500)
                click_image("P_FF11Cave")
                time.sleep(1)
            elif state.inn_mode == 1 or state.inn_mode == 0:
                general_inn_mode(mode=1)
        wait_image("P_FF11_B1F")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FF11_B5F_fixed():
    """FF11_B5F周回標記"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止FF11_B5F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FF11_B5F"):
            exitLog("起點不正確, 請移到看到FF11_B5F的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        click_image("P_FF11_B5F")    
        goToDungeon_check()
        wait_image("P_exit")
        #goToMark("P_FF11_B5F_minimap1", target_sim=0.7)
        goToMark()
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_FF11_B5F")
        if (state.run_count+1)%state.heal_period == 0:
            if state.inn_mode == 3 or state.inn_mode == 4:
                click_image("P_worldMap")
                wait_image("P_FF11Cave")
                tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
                time.sleep(1.5)
                click_image("P_chapter1")
                inn_check()
                general_inn_mode(mode=2)
                map_click()
                time.sleep(1)
                if not find_image("P_FF11Cave"):
                    tap(constants.L_map_scalebig[0], constants.L_map_scalebig[1], "放大地圖")
                    time.sleep(2)
                    swipe(450,600,450,1000,500)
                click_image("P_FF11Cave")
                time.sleep(1)
            elif state.inn_mode == 1 or state.inn_mode == 0:
                general_inn_mode(mode=1)
        wait_image("P_FF11_B5F")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_FF11_B2F_mine():
    """FF11_B2F挖礦"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止FF11_B2F挖礦")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_FF11_B2F"):
            exitLog("起點不正確, 請移到看到FF11_B2F的位置") 
        click_image("P_FF11_B2F")    
        goToDungeon_check()
        wait_image("P_exit")
        goToMark(["P_FF11_ore","P_FF11_ore2"])
        if find_image("P_FF11_ore"):
            logger.info("有礦")
            for i in range(10):
                click_image("P_FF11_ore")
                click_image("P_FF11_get")
                check = wait_image(["P_FF11_ore","P_FF11_ore2"])
                if check == "P_FF11_ore2":
                    break
        else:
            logger.info("冇礦走人")
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        wait_image("P_FF11_B5F")
        if (state.run_count+1)%state.heal_period == 0:
            click_image("P_worldMap")
            click_image("P_FF11_village")
            inn_check()
            click_image("P_uplist")
            bag(sim=0.65, outside=False)
            click_image("P_downlist")
            click_image("P_map")
            click_image("P_FF11Cave")
        wait_image("P_FF11_B2F")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise
def Farm_ch4B10F_SnowGlant():
    """第四章B10F周回雪巨人"""
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode, state.heal_period
    enemy = [(450,850, "雪巨人")]
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止第四章B7F周回雜物")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        if not find_image("P_inn"):
            exitLog("起點不正確, 請移到任一章城鎮的位置") 
        if state.inn_mode == 2:
            exitLog("此腳本不能使用「地城露營」休息模式")
        ch4_pre()
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(2)
        switch_wheel("P_wheel_ch4_minerequest", 4)
        inn_check()
        click_image("P_house")
        click_image("P_wheel")
        wait_image("P_wheel_special_request")
        time.sleep(2)
        switch_wheel("P_wheel_ch4_thetruth", 4)
        inn_check()
        map_click()
        for i in range(2):
            tap(constants.L_map_scalesmall[0], constants.L_map_scalesmall[1], "縮小地圖")
            time.sleep(0.5)
        swipe(450, 800, 700, 800)
        tap(constants.L_map_scalebig[0],constants.L_map_scalebig[1], "放大地圖")
        time.sleep(1)
        click_image("P_chapter4")
        click_image("P_outside")
        click_image("P_ch4_outside")    
        time.sleep(0.5)
        click_image("P_ch4_B10F")
        goToDungeon_check()
        wait_image("P_exit")
        goToMark("P_ch4_B10F_minimap2")
        press_key("w")
        battle_skill([(450, 850, "目標")])
        goMap("P_ch4_B10F_checkpoint2", "P_ch4_B10F_until2", goMap_similarity=0.65)
        goMap("P_ch4_B10F_checkpoint3", "P_ch4_B10F_until3")
        exitMap(["P_buff", "P_back"])
        check = exitMap(["P_back", "P_buff"])
        if check:
            if check == "P_buff":
                click_image("P_buff")
                click_image("P_back")
            elif check == "P_back":
                click_image("P_back")
            else:
                exitLog("沒有找到正確結果")
        click_image("P_village")
        inn_check()
        inn_rest()
        wait_image("P_inn")
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise

def test():
    # (state) global state.run_count, state.paused, state.trap_char_all_scared, state.inn_mode
    try:
        if state.stop_event.is_set():
            logger.info("收到停止指令，終止測試腳本")
            raise StopIteration
        if state.paused:
            logger.info("腳本已暫停，等待繼續")
            while state.paused and not state.stop_event.is_set():
                time.sleep(0.1)
        #在此輸入
        
        state.run_count += 1
    except StopIteration:
        logger.info("主循環被中斷，腳本終止")
        raise

