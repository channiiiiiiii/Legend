# -*- coding: utf-8 -*-
"""
🎮 JENNY'S LEGEND DAMAGOCHI SIMULATOR (v17.2)
메인 콘솔 실시간 논블로킹 라이브 루프 & 대시보드 UI
10대 신수 BST 리마스터, 잠재 혼 성장, 종족 전용 보물, 방어구 승급(+15 ★5), 21개 레이드 보스전 & 개발자 모드
"""

import sys
import time
import os
import random

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError) as e:
        print(f"[CONSOLE ENCODING ERROR] {type(e).__name__}: {e}", file=sys.stderr)
    import msvcrt
else:
    msvcrt = None

from save_manager import SaveManager
from pet import Pet
from species import SPECIES_DATABASE, Genetics, PERSONALITIES, SPECIES_SKILLS
from shop import Shop, Inventory, ITEMS_DATABASE, EXCLUSIVE_RELICS, ARMORS_DATABASE
from minigames import Minigames
from adventure import AdventureSystem, BOSS_DATABASE, RAID_DIFFICULTIES
from achievements import AchievementManager, ACHIEVEMENTS_LIST
from storage import StorageManager, PetMarket

ESC = "\033["
RESET = f"{ESC}0m"
BOLD = f"{ESC}1m"
GREEN = f"{ESC}32m"
YELLOW = f"{ESC}33m"
CYAN = f"{ESC}36m"
MAGENTA = f"{ESC}35m"
RED = f"{ESC}31m"
PINK = f"{ESC}95m"
GOLD = f"{ESC}93m"
WHITE = f"{ESC}97m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(f"{PINK}{BOLD}╔══════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{PINK}{BOLD}║        ✨💖 JENNY'S LEGEND DAMAGOCHI SIMULATOR v17.2 💖✨          ║{RESET}")
    print(f"{PINK}{BOLD}║         수석 비서 제니의 10대 신수 육성 & 21개 레이드 정복기        ║{RESET}")
    print(f"{PINK}{BOLD}╚══════════════════════════════════════════════════════════════════════╝{RESET}")

def render_dashboard(pet: Pet, inventory: Inventory, claimed_achievements: list, msg: str = ""):
    clear_screen()
    print_header()
    print(pet.get_current_art())
    print("─" * 68)

    status_tags = []
    if pet.is_sleeping:
        status_tags.append(f"{CYAN}[💤 수면중]{RESET}")
    if pet.is_sick:
        status_tags.append(f"{RED}[🤒 질병 감염]{RESET}")
    if pet.poops > 0:
        status_tags.append(f"{YELLOW}[💩 똥 x{pet.poops}]{RESET}")
    if getattr(pet, "affection", 50) >= 80:
        status_tags.append(f"{PINK}[💖 무한 신뢰]{RESET}")
    if getattr(pet, "transcend_level", 0) > 0:
        status_tags.append(f"{GOLD}[🌌 초월 Lv.{pet.transcend_level}]{RESET}")
    if not status_tags:
        status_tags.append(f"{GREEN}[✨ 최상 컨디션]{RESET}")

    b_stats = pet.get_battle_stats(inventory)
    shiny_badge = f"{GOLD}[✨ 극희귀 변이!]{RESET} " if getattr(pet, "is_shiny", False) else ""
    
    # 장비 장착 현황
    sp_key = getattr(pet, "species_key", "드래곤")
    r_lvl = b_stats.get("relic_level", 0)
    relic_str = f"{GOLD}🎴 보물: [{EXCLUSIVE_RELICS.get(sp_key, {}).get('name', '보물')} +{r_lvl}]{RESET}" if inventory.equipped_relic else f"{WHITE}🎴 보물: [미장착]{RESET}"
    
    a_lvl = b_stats.get("armor_level", 0)
    armor_str = f"{CYAN}🛡️ 방어구: [{ARMORS_DATABASE.get(inventory.equipped_armor['armor_id'], {}).get('name', '방어구')} +{a_lvl}]{RESET}" if inventory.equipped_armor else f"{WHITE}🛡️ 방어구: [미장착]{RESET}"
    
    p_info = PERSONALITIES.get(getattr(pet, "personality", "용맹함"), PERSONALITIES["용맹함"])
    
    print(f"{BOLD}{pet.emoji} {shiny_badge}[{pet.name}] | 종족: {pet.species_name} ({pet.tier}) | {' '.join(status_tags)}{RESET}")
    print(f"{CYAN}🔮 역할군: [{getattr(pet, 'role', '공격형')}]  └ {getattr(pet, 'role_desc', '')}{RESET}")
    print(f"{PINK}🎭 성격: {p_info['emoji']} [{p_info['name']}]  └ {p_info['desc']}{RESET}")
    print(f"{relic_str}   {armor_str}")
    print(f"{GOLD}🧬 5V 개체값: HP {pet.hp_iv} / ATK {pet.atk_iv} / DEF {pet.def_iv} / SPD {getattr(pet, 'spd_iv', 70)} / CRIT {getattr(pet, 'crit_iv', 70)}  [{pet.rank}]{RESET}")
    
    if pet.level >= 99:
        print(f"⭐ 레벨: {GOLD}Lv.99 만렙 (초월 Lv.{getattr(pet, 'transcend_level', 0)} / EXP: {pet.transcend_exp:,}/50,000){RESET}")
    else:
        print(f"⭐ 레벨: Lv.{pet.level}/99 (EXP: {pet.exp:,}/{pet.max_exp:,})")
        
    print("─" * 68)
    print(f"{BOLD}⚔️ [실시간 전투 스탯 - 포만감/행복도 실시간 반영]{RESET}")
    print(f"❤️  {BOLD}실제 체력 (HP):  {GREEN}{b_stats['max_hp']:,}{RESET}  | ⚔️ {BOLD}실제 공격력 (ATK): {RED}{b_stats['atk']:,}{RESET}")
    print(f"🛡️  {BOLD}실제 방어력 (DEF): {CYAN}{b_stats['def']:,}{RESET}  | ⚡ {BOLD}실제 스피드 (SPD): {YELLOW}{b_stats['spd']}{RESET}  | 💥 {BOLD}치명타 (CRIT): {PINK}{b_stats['crit']}{RESET}")
    print(f"🍚 컨디션: {b_stats['hunger_status_tag']} | 💖 심리: {b_stats['happy_status_tag']}")
    print(f"💰 보유 골드: {pet.coins:,}G | 🏆 보스 토벌: {pet.total_dungeon_clears}회 | 📜 달성 업적: {len(claimed_achievements)}/{len(ACHIEVEMENTS_LIST)}개")
    print("─" * 68)
    
    h_bar = pet.get_status_bar(pet.hunger)
    c_bar = pet.get_status_bar(pet.cleanliness)
    hp_bar = pet.get_status_bar(pet.happiness)
    e_bar = pet.get_status_bar(pet.energy)
    hl_bar = pet.get_status_bar(pet.health)
    aff_bar = pet.get_status_bar(pet.affection)
    ch_bar = pet.get_status_bar(pet.charm)
    
    print(f"🍚 포만감: [{h_bar}] {pet.hunger:3d}%    🧼 청결도: [{c_bar}] {pet.cleanliness:3d}%")
    print(f"💖 행복도: [{hp_bar}] {pet.happiness:3d}%    ⚡ 에너지: [{e_bar}] {pet.energy:3d}%")
    print(f"🏥 건강도: [{hl_bar}] {pet.health:3d}%")
    print(f"{PINK}{BOLD}❤️ 애정도: [{aff_bar}] {pet.affection:3d}%    ✨ 외모력: [{ch_bar}] {pet.charm:3d}점{RESET}")
    print("─" * 68)
    
    if msg:
        print(f"{MAGENTA}{BOLD}📢 [최신 소식]: {msg}{RESET}")
        print("─" * 68)

def hatch_egg_animation() -> Pet:
    clear_screen()
    print_header()
    print(f"{GOLD}{BOLD}✨ [신비한 10대 신수의 알이 도착했습니다!] ✨{RESET}\n")
    print("      .---.")
    print("     /  ?  \\   (호랑이, 사자, 늑대, 드래곤, 불사조, 현무, 구미호, 그리핀, 기린, 바하무트)")
    print("    |  ? ?  |  2% 확률로 [극희귀 변이 이로치]가 탄생합니다!")
    print("     \\_____/   10대 성격과 5V 개체값이 랜덤 부여됩니다.\n")
    
    input("👉 [Enter] 키를 눌러 알을 깨트리세요... ")
    print("\n🐣 알에 금이 가기 시작합니다... 찌익-!")
    time.sleep(0.5)
    print("💥 파자자작-!! 눈부신 전설의 빛이 뿜어져 나옵니다!")
    time.sleep(0.8)
    
    new_pet = Pet()
    print(f"\n{GREEN}{BOLD}🎉 축하합니다! [{new_pet.emoji} {new_pet.name}]이(가) 세상에 태어났습니다!{RESET}")
    p_inf = PERSONALITIES[new_pet.personality]
    print(f"{PINK}🎭 성격: {p_inf['emoji']} [{p_inf['name']}] - {p_inf['desc']}{RESET}")
    print(f"{GOLD}🧬 개체값 총합: {new_pet.total_iv}/500 [{new_pet.rank}]{RESET}")
    input("\n👉 [Enter] 키를 눌러 게임을 시작하세요...")
    return new_pet

def handle_storage_and_market(pet: Pet, inventory: Inventory, meta_data: dict) -> tuple[Pet, str]:
    while True:
        clear_screen()
        print_header()
        storage_pets = StorageManager.load_storage()
        print(f"{BOLD}🏛️ [명예의 전당 보관소 & 왕실 경매소] (현재 보관: {len(storage_pets)}마리){RESET}\n")
        print("1. 🏛️ 현재 신수 명예의 전당에 영구 보관하고 새 알 부화하기")
        print("2. 💎 현재 신수 왕실 경매소에 매각하고 거액의 골드 획득하기")
        print("3. 📜 명예의 전당 보관 목록 조회하기")
        print("0. 🔙 메인 메뉴로 돌아가기")

        sel = input("\n👉 선택: ").strip()
        if sel == "0":
            return pet, "보관소 메뉴를 종료했습니다."
        elif sel == "1":
            confirm = input(f"\n⚠️ [{pet.name}]을(를) 보관하고 새 알을 부화하시겠습니까? (y/N): ").strip().lower()
            if confirm == "y":
                suc, msg = StorageManager.store_pet(pet)
                if suc:
                    new_pet = hatch_egg_animation()
                    SaveManager.save(new_pet.to_dict(), inventory.to_dict(), meta_data)
                    return new_pet, msg
                else:
                    return pet, msg
        elif sel == "2":
            price = PetMarket.calculate_sell_price(pet)
            print(f"\n👑 왕실 감정 결과: [{pet.name}]의 경매 가치는 {GOLD}{price:,}G{RESET} 입니다.")
            confirm = input("⚠️ 정말로 매각하시겠습니까? (y/N): ").strip().lower()
            if confirm == "y":
                suc, msg, earned_gold = PetMarket.sell_pet(pet)
                if suc:
                    new_pet = hatch_egg_animation()
                    new_pet.coins += earned_gold
                    SaveManager.save(new_pet.to_dict(), inventory.to_dict(), meta_data)
                    return new_pet, msg
                else:
                    return pet, msg
        elif sel == "3":
            clear_screen()
            print_header()
            print(f"{BOLD}📜 [명예의 전당 영구 보관 신수 목록]{RESET}\n")
            if not storage_pets:
                print("보관된 신수가 없습니다.")
            else:
                for idx, p_dict in enumerate(storage_pets, 1):
                    print(f"[{idx}] {p_dict.get('emoji', '🐾')} {p_dict.get('name')} | Lv.{p_dict.get('level')} (초월 Lv.{p_dict.get('transcend_level', 0)}) | 개체값 [{p_dict.get('rank')}]")
            input("\n[Enter] 키를 누르면 돌아갑니다...")

def handle_adventure_menu(pet: Pet, inventory: Inventory) -> str:
    while True:
        clear_screen()
        print_header()
        print(f"{BOLD}👑 [5대 레이드 보스 선택] | 현재 레벨: Lv.{pet.level} (초월 Lv.{getattr(pet, 'transcend_level', 0)}){RESET}\n")
        
        for b_id, b_info in BOSS_DATABASE.items():
            status = "🔓 도전 가능" if pet.level >= b_info["req_level"] else f"🔒 잠김 (필요: Lv.{b_info['req_level']})"
            print(f"[{b_id}] {b_info['emoji']} {b_info['name']} ({b_info['type']}) - {status}")
            print(f"    └ 고유 특성: 「{b_info['trait_name']}」 | {b_info['check_stat']}")
        print("\n[0] 메인 메뉴로 돌아가기")

        sel = input("\n👉 도전할 보스 번호 (1~5): ").strip()
        if sel == "0":
            return "레이드 메뉴를 종료했습니다."
        if not (sel.isdigit() and 1 <= int(sel) <= 5):
            continue
        
        boss_id = int(sel)
        target_boss = BOSS_DATABASE[boss_id]
        if pet.level < target_boss["req_level"]:
            print(f"\n🚫 레벨이 부족합니다! (필요 레벨: Lv.{target_boss['req_level']})")
            time.sleep(1.0)
            continue
        if pet.energy < target_boss["energy_cost"]:
            print(f"\n😫 에너지가 부족합니다! (필요 에너지: {target_boss['energy_cost']})")
            time.sleep(1.0)
            continue

        clear_screen()
        print_header()
        print(f"{BOLD}{target_boss['emoji']} [{target_boss['name']}] - 5단계 난이도 선택{RESET}\n")
        for diff_id, diff_info in RAID_DIFFICULTIES.items():
            req_lvl = target_boss["req_level"] + diff_info["req_lvl_add"]
            req_str = f"Lv.{req_lvl}+"
            print(f"[{diff_id}] {diff_info['name']} (요구: {req_str} | 스탯 ×{diff_info['stat_mult']} | EXP ×{diff_info['exp_mult']})")
            if diff_id == 5:
                print("    └ ⚠️ [고대 완전체 특성 발동!] (엔트 1%컷, 드래곤 25%반사, 이프리트 강화화상, 성운 35%추가타, 오메가 약자멸시)")
        print("\n[0] 보스 선택으로 돌아가기")

        diff_sel = input("\n👉 난이도 선택 (1~5): ").strip()
        if diff_sel == "0":
            continue
        if not (diff_sel.isdigit() and 1 <= int(diff_sel) <= 5):
            continue

        diff_id = int(diff_sel)
        req_lvl = target_boss["req_level"] + RAID_DIFFICULTIES[diff_id]["req_lvl_add"]
        if pet.level < req_lvl:
            print(f"\n🚫 해당 난이도에 필요한 레벨이 부족합니다! (요구: Lv.{req_lvl})")
            time.sleep(1.0)
            continue

        suc, res_msg = AdventureSystem.run_boss_raid(pet, inventory, boss_id, diff_id, interactive=True)
        return res_msg

def handle_potential_menu(pet: Pet, inventory: Inventory) -> str:
    while True:
        clear_screen()
        print_header()
        pot = getattr(pet, "potential_growth", {}) or {}
        print(f"{BOLD}🌱 [신수 5대 스탯 잠재 성장 각성소]{RESET}\n")
        print(f"🐾 신수: {GOLD}[{pet.name}]{RESET} ({pet.species_name} {pet.rank})")
        print(f"📜 혼(Soul)을 소모하여 5대 스탯을 각각 최대 +60.0%까지 확정 각성시킵니다.\n")
        
        stat_names = [("hp", "❤️ 체력"), ("atk", "⚔️ 공격력"), ("def", "🛡️ 방어력"), ("spd", "⚡ 스피드"), ("crit", "💥 치명타")]
        for idx, (k, name) in enumerate(stat_names, 1):
            val = pot.get(k, 0.0)
            step = int(round(val / 0.03))
            pct = int(round(val * 100))
            if step >= 20:
                nxt = "MAX (+60%)"
            else:
                nxt_s = step + 1
                sub_s = (nxt_s - 1) % 5 + 1
                req_c = [1, 4, 9, 16, 25][sub_s - 1]
                t_idx = (nxt_s - 1) // 5
                s_names = ["일반 혼", "고급 혼", "전설 혼", "신화 혼"]
                nxt = f"다음 +{int(round(nxt_s*3))}% (필요: {s_names[t_idx]} {req_c}개)"
            print(f" [{idx}] {name}: +{pct}% ({step}/20단계) | {nxt}")

        print(f"\n[보유 혼] ⚪일반: {inventory.items.get('soul_normal', 0)}개 | 🔵고급: {inventory.items.get('soul_hard', 0)}개 | 🟣전설: {inventory.items.get('soul_nightmare', 0)}개 | 🟡신화: {inventory.items.get('soul_mythic', 0)}개")
        print("[0] 🔙 돌아가기")

        sel = input("\n👉 각성할 스탯 번호: ").strip()
        if sel == "0":
            return "잠재 성장을 종료했습니다."
        idx_map = {"1": "hp", "2": "atk", "3": "def", "4": "spd", "5": "crit"}
        if sel in idx_map:
            suc, msg = pet.upgrade_potential(idx_map[sel], inventory)
            print(f"\n{msg}")
            time.sleep(1.2)

def handle_dev_menu(pet: Pet, inventory: Inventory) -> str:
    """🛠️ 콘솔 개발자 및 관리자 자유 설정 에디터 (보안 잠금 연동)"""
    print_header()
    pin = input(f"\n🔒 {BOLD}관리자 보안 비밀번호를 입력하세요 (기본: 7777, 취소: 0):{RESET} ").strip()
    if pin == "0":
        return "개발자 모드 진입을 취소했습니다."
    if pin != "7777":
        return "🚫 관리자 비밀번호가 일치하지 않아 접근이 거부되었습니다."

    while True:
        clear_screen()
        print_header()
        b_stats = pet.get_battle_stats(inventory)
        pot = getattr(pet, "potential_growth", {}) or {}
        a_eq = inventory.equipped_armor
        a_str = f"{ARMORS_DATABASE[a_eq['armor_id']]['name']} +{a_eq['level']}{' ★' + str(a_eq.get('stars',0)) if a_eq.get('stars',0) else ''}" if a_eq else "미장착"
        r_eq = inventory.equipped_relic
        r_str = f"{pet.species_name}의 보물 +{r_eq['level']}" if r_eq else "미장착"

        print(f"{BOLD}🛠️ [신수키우기 개발자 & 관리자 완전 자유 설정 콘솔]{RESET}\n")
        print(f"🐾 현재 신수: {GOLD}[{pet.emoji} {pet.name}]{RESET} ({pet.species_name} {pet.rank} · Lv.{pet.level})")
        print(f"⚔️ 전투력: {CYAN}👑 {b_stats['combat_power']:,}{RESET} | 💰 골드: {GOLD}{pet.coins:,}G{RESET}")
        print(f"🌟 초월: Lv.{getattr(pet, 'transcend_level', 0)} | 💖 애정도: Lv.{pet.get_affection_state()[0]} ({getattr(pet, 'total_affection', 0)}/1000) | 🎭 성격: {getattr(pet, 'personality', '용맹함')}")
        print(f"🌱 잠재 성장: HP +{int(pot.get('hp', 0)*100)}% / ATK +{int(pot.get('atk', 0)*100)}% / DEF +{int(pot.get('def', 0)*100)}% / SPD +{int(pot.get('spd', 0)*100)}% / CRIT +{int(pot.get('crit', 0)*100)}%")
        print(f"🛡️ 방어구: {a_str} | 🎴 전용보물: {r_str}\n")
        
        print(" [1] 🐾 10대 신수 종족 직접 변경     [2] 🎭 10대 성격 직접 변경")
        print(" [3] 📈 레벨 직접 설정 (1~99)       [4] 🌌 초월 단계 직접 설정 (0~20)")
        print(" [5] 💖 애정도 수치 설정 (0~1000)   [6] 🌱 잠재 성장 % 설정 (0~60%)")
        print(" [7] 🛡️ 방어구 종류/강화/성급 설정   [8] 🎴 전용 보물 강화 설정 (0~10)")
        print(" [9] 🧬 IV 개체값 & 샤이니 설정     [10] 💰 골드 수치 직접 입력")
        print(" [11] 🍬 사탕 & 강화석 & 혼 지급    [12] 🏥 올스탯 풀회복 & 완치")
        print(" [13] 🚪 레이드 전체 관문 올해금    ")
        print("\n [🌟 난이도별 MAX 원클릭 프리셋]")
        print(" [14] ⚪ 노말 MAX (Lv.25 / 가죽+5 / 보물+2 / 잠재 15%)")
        print(" [15] 🔵 하드 MAX (Lv.50 / 수정+8 / 보물+5 / 잠재 30%)")
        print(" [16] 🟣 악몽 MAX (Lv.75 / 천계+11 / 보물+8 / 잠재 45%)")
        print(" [17] 🟡 신화 MAX (Lv.99 / 고대신+15 / 보물+10 / 잠재 60%)")
        print(" [18] 🌌 고대 MAX 종결 (Lv.99 / 고대신+15★5 / 보물+10 / 초월20 / 500IV / 샤이니)")
        print(" [0] 🔙 메인 메뉴로 돌아가기")

        sel = input("\n👉 실행할 커스텀 설정 번호: ").strip()
        if sel == "0":
            return "개발자 모드를 종료했습니다."
        elif sel == "1":
            print("\n[🐾 10대 신수 종족 선택]")
            sp_keys = list(SPECIES_DATABASE.keys())
            for idx, sp_k in enumerate(sp_keys, 1):
                d = SPECIES_DATABASE[sp_k]
                print(f" {idx}. {d['emoji']} {d['name']} ({d['tier']} · {d['role']})")
            sub_s = input("\n👉 변경할 종족 번호: ").strip()
            if sub_s.isdigit() and 1 <= int(sub_s) <= len(sp_keys):
                chosen_sp = sp_keys[int(sub_s)-1]
                suc, msg = pet.change_species(chosen_sp, inventory)
                print(f"\n{msg}")
                time.sleep(1.2)
        elif sel == "2":
            print("\n[🎭 10대 성격 선택]")
            p_keys = list(PERSONALITIES.keys())
            for idx, p_k in enumerate(p_keys, 1):
                d = PERSONALITIES[p_k]
                print(f" {idx}. {d['emoji']} {d['name']} - {d['desc']}")
            sub_p = input("\n👉 변경할 성격 번호: ").strip()
            if sub_p.isdigit() and 1 <= int(sub_p) <= len(p_keys):
                pet.personality = p_keys[int(sub_p)-1]
                print(f"\n🎭 신수의 성격이 [{pet.personality}](으)로 변경되었습니다!")
                time.sleep(1.0)
        elif sel == "3":
            val = input("👉 설정할 레벨 입력 (1~99): ").strip()
            if val.isdigit():
                pet.level = max(1, min(99, int(val)))
                pet.exp = 0
                pet.max_exp = pet.calc_req_exp(pet.level)
                print(f"\n📈 신수의 레벨이 Lv.{pet.level}로 설정되었습니다!")
                time.sleep(1.0)
        elif sel == "4":
            val = input("👉 설정할 초월 단계 입력 (0~20): ").strip()
            if val.isdigit():
                pet.transcend_level = max(0, min(20, int(val)))
                print(f"\n🌌 신수의 초월이 Lv.{pet.transcend_level}로 설정되었습니다!")
                time.sleep(1.0)
        elif sel == "5":
            val = input("👉 설정할 애정도 수치 입력 (0~1000): ").strip()
            if val.isdigit():
                pet.total_affection = max(0, min(1000, int(val)))
                pet.affection = pet.total_affection
                print(f"\n💖 애정도가 {pet.total_affection}/1000 으로 설정되었습니다!")
                time.sleep(1.0)
        elif sel == "6":
            val = input("👉 설정할 잠재 성장 % 입력 (0~60): ").strip()
            if val.isdigit():
                pct = max(0, min(60, int(val)))
                r_val = pct / 100.0
                pet.potential_growth = {"hp": r_val, "atk": r_val, "def": r_val, "spd": r_val, "crit": r_val}
                print(f"\n🌱 5대 스탯 잠재 성장이 +{pct}% 로 설정되었습니다!")
                time.sleep(1.0)
        elif sel == "7":
            print("\n[🛡️ 방어구 종류 선택]")
            a_keys = list(ARMORS_DATABASE.keys())
            for idx, a_k in enumerate(a_keys, 1):
                d = ARMORS_DATABASE[a_k]
                print(f" {idx}. {d['tier']} {d['name']}")
            sub_a = input("👉 방어구 번호: ").strip()
            if sub_a.isdigit() and 1 <= int(sub_a) <= len(a_keys):
                a_id = a_keys[int(sub_a)-1]
                lvl_in = input("👉 강화 수치 (0~15): ").strip()
                lvl = int(lvl_in) if lvl_in.isdigit() else 0
                star_in = input("👉 고대 성급 (0~5): ").strip()
                star = int(star_in) if star_in.isdigit() else 0
                inventory.equipped_armor = {
                    "armor_id": a_id,
                    "level": max(0, min(15, lvl)),
                    "stars": max(0, min(5, star)),
                    "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}
                }
                print(f"\n🛡️ 방어구가 [{ARMORS_DATABASE[a_id]['name']} +{lvl} ★{star}](으)로 설정되었습니다!")
                time.sleep(1.0)
        elif sel == "8":
            val = input("👉 전용 보물 강화 수치 (0~10): ").strip()
            if val.isdigit():
                if not inventory.equipped_relic:
                    inventory.equipped_relic = {"species": pet.species_key, "level": 0}
                inventory.equipped_relic["level"] = max(0, min(10, int(val)))
                print(f"\n🎴 전용 보물이 +{inventory.equipped_relic['level']}강으로 설정되었습니다!")
                time.sleep(1.0)
        elif sel == "9":
            pet.hp_iv = 100; pet.atk_iv = 100; pet.def_iv = 100; pet.spd_iv = 100; pet.crit_iv = 100
            pet.total_iv = 500
            pet.rank = "👑 PERFECT (완벽)"
            pet.is_shiny = not pet.is_shiny
            print(f"\n🧬 PERFECT 500 IV 적용 및 샤이니 변이: {'🌟 On' if pet.is_shiny else 'Off'}!")
            time.sleep(1.0)
        elif sel == "10":
            val = input("👉 보유 골드 수치 입력: ").strip()
            if val.isdigit():
                pet.coins = int(val)
                print(f"\n💰 골드가 {pet.coins:,}G로 설정되었습니다!")
                time.sleep(1.0)
        elif sel == "11":
            for c_id_name in ["small_candy", "super_candy", "mega_candy", "ancient_candy"]:
                inventory.add_item(c_id_name, 20)
            inventory.add_item("stone", 50)
            inventory.add_item("armor_stone", 50)
            inventory.add_item("relic_essence", 50)
            inventory.add_item("soul_normal", 55); inventory.add_item("soul_hard", 55)
            inventory.add_item("soul_nightmare", 55); inventory.add_item("soul_mythic", 55)
            print("\n🍬 모든 사탕 20개, 강화석 50개, 혼 풀세트(각 55개)가 가방에 지급되었습니다!")
            time.sleep(1.0)
        elif sel == "12":
            pet.health = 100; pet.stamina = 100; pet.energy = 100
            pet.hunger = 100; pet.cleanliness = 100; pet.happiness = 100
            pet.is_critically_injured = False; pet.is_sick = False; pet.is_sleeping = False
            print("\n🏥 신수의 모든 상태가 100% 회복되고 완치되었습니다!")
            time.sleep(1.0)
        elif sel == "13":
            pet.raid_clears = {"1": [1, 2, 3, 4], "2": [1, 2, 3, 4], "3": [1, 2, 3, 4], "4": [1, 2, 3, 4], "5": [1, 2, 3, 4, 5]}
            pet.boss_kills = {"5_1": 15, "5_2": 15, "5_3": 15, "5_4": 15, "5_5": 15}
            print("\n🚪 모든 레이드 관문 및 고대 15킬 토벌이 올클리어 처리되었습니다!")
            time.sleep(1.0)
        elif sel == "14":
            suc, p_msg = pet.apply_preset("normal", inventory)
            print(f"\n{p_msg}")
            time.sleep(1.2)
        elif sel == "15":
            suc, p_msg = pet.apply_preset("hard", inventory)
            print(f"\n{p_msg}")
            time.sleep(1.2)
        elif sel == "16":
            suc, p_msg = pet.apply_preset("nightmare", inventory)
            print(f"\n{p_msg}")
            time.sleep(1.2)
        elif sel == "17":
            suc, p_msg = pet.apply_preset("mythic", inventory)
            print(f"\n{p_msg}")
            time.sleep(1.2)
        elif sel == "18":
            suc, p_msg = pet.apply_preset("ancient", inventory)
            print(f"\n{p_msg}")
            time.sleep(1.2)

def handle_equipment_menu(pet: Pet, inventory: Inventory) -> str:
    while True:
        clear_screen()
        print_header()
        sp_key = getattr(pet, "species_key", "호랑이")
        
        cur_relic_str = f"{EXCLUSIVE_RELICS[sp_key]['name']} +{inventory.equipped_relic['level']}" if inventory.equipped_relic else "미장착"
        stars = inventory.equipped_armor.get("stars", 0) if inventory.equipped_armor else 0
        star_str = f" {'★' * stars}" if stars > 0 else ""
        cur_armor_str = f"{ARMORS_DATABASE[inventory.equipped_armor['armor_id']]['name']} +{inventory.equipped_armor['level']}{star_str}" if inventory.equipped_armor else "미장착"
        
        print(f"{BOLD}🛡️ [신수 장비 관리소] (보유 골드: {pet.coins:,}G){RESET}")
        print(f"🎴 장착 보물: {GOLD}[{cur_relic_str}]{RESET} (현재 성장 관문 상한: +{pet.get_relic_max_level()})")
        print(f"🛡️ 장착 방어구: {CYAN}[{cur_armor_str}]{RESET}")
        print(f"🌟 {sp_key}의 정수: {inventory.species_essences.get(sp_key, 0)}개 | 💎 강화석: {inventory.items.get('stone', 0) + inventory.items.get('armor_stone', 0)}개\n")
        
        print("1. 🎴 종족 전용 보물 장착 / 변경")
        print("2. 🛡️ 방어구 장착 / 변경")
        print("3. ✨ 종족 전용 보물 강화 (+1 ~ +10)")
        print("4. 🔨 방어구 강화 (+1 ~ +15)")
        print("5. 🌟 방어구 티어 승급 (가죽+5 ➔ 수정, 수정+8 ➔ 천계, 천계+11 ➔ 고대신)")
        print("6. 👑 고대 방어구 ★1~★5 100% 확정 별 승급")
        print("7. ♻️ 보유 보물 분해 (정수 추출)")
        print("8. 🌟 종족 전용 보물 제작 (정수 50개 + 20,000G)")
        print("0. 🔙 메인 메뉴로 돌아가기")

        sel = input("\n👉 선택: ").strip()
        if sel == "0":
            return "장비 관리를 종료했습니다."
        elif sel == "1":
            # 보물 장착
            suc, msg = inventory.equip_relic(sp_key)
            print(f"\n{msg}")
            time.sleep(1.0)
        elif sel == "2":
            # 방어구 장착
            if not inventory.armors_inventory:
                print("\n보유 중인 방어구가 없습니다. (레이드에서 파밍하세요!)")
                time.sleep(1.0)
                continue
            print(f"\n{BOLD}[보유 방어구 목록]{RESET}")
            for idx, a in enumerate(inventory.armors_inventory, 1):
                a_info = ARMORS_DATABASE[a["armor_id"]]
                opt_str = f" ({a['opt']['name']} +{int(a['opt']['val']*100)}%)" if a.get("opt") else ""
                print(f"[{idx}] {a_info['tier']} {a_info['name']} +{a['level']}{opt_str} - {a_info['desc']}")
            a_sel = input("\n👉 장착할 방어구 번호: ").strip()
            if a_sel.isdigit() and 1 <= int(a_sel) <= len(inventory.armors_inventory):
                suc, msg = inventory.equip_armor(int(a_sel) - 1)
                print(f"\n{msg}")
                time.sleep(1.0)
        elif sel == "3":
            # 보물 강화 (성장 관문 상한 연동)
            suc, msg, pet.coins = inventory.enhance_relic(pet.coins, max_allowed_lvl=pet.get_relic_max_level())
            print(f"\n{msg}")
            time.sleep(1.2)
        elif sel == "4":
            # 방어구 강화
            suc, msg, pet.coins = inventory.enhance_armor(pet.coins)
            print(f"\n{msg}")
            time.sleep(1.2)
        elif sel == "5":
            # 방어구 티어 승급
            suc, msg, pet.coins = inventory.promote_armor(pet.coins, pet=pet)
            print(f"\n{msg}")
            time.sleep(1.5)
        elif sel == "6":
            # 고대 성급 승급
            suc, msg, pet.coins = inventory.ascend_armor_star(pet.coins)
            print(f"\n{msg}")
            time.sleep(1.2)
        elif sel == "7":
            # 보물 분해
            if not inventory.relics_inventory:
                print("\n분해할 보물이 인벤토리에 없습니다.")
                time.sleep(1.0)
                continue
            print(f"\n{BOLD}[분해 가능한 보물 목록]{RESET}")
            for idx, r in enumerate(inventory.relics_inventory, 1):
                r_info = EXCLUSIVE_RELICS[r["species"]]
                print(f"[{idx}] {r_info['name']} +{r['level']}")
            d_sel = input("\n👉 분해할 보물 번호: ").strip()
            if d_sel.isdigit() and 1 <= int(d_sel) <= len(inventory.relics_inventory):
                suc, msg = inventory.dismantle_relic(int(d_sel) - 1)
                print(f"\n{msg}")
                time.sleep(1.0)
        elif sel == "8":
            # 보물 제작
            suc, msg, pet.coins = inventory.craft_relic(sp_key, pet.coins)
            print(f"\n{msg}")
            time.sleep(1.2)

def handle_shop(pet: Pet, inventory: Inventory) -> str:
    while True:
        clear_screen()
        print_header()
        print(f"{BOLD}🛒 [24시 신수 편의점 & 강화 상점] (보유 골드: {pet.coins:,}G){RESET}\n")
        idx_map = {}
        for idx, (item_id, item_data) in enumerate(ITEMS_DATABASE.items(), 1):
            idx_map[str(idx)] = item_id
            print(f"[{idx}] {item_data['name']} - {item_data['price']:,}G")
            print(f"    └ {item_data['desc']}")
        print(f"\n[0] 상점 나가기")

        sel = input("\n👉 구매할 아이템 번호: ").strip()
        if sel == "0":
            return "상점을 나왔습니다."
        if sel in idx_map:
            item_id = idx_map[sel]
            count_input = input("👉 구매 수량 (기본 1개): ").strip()
            count = int(count_input) if count_input.isdigit() and int(count_input) > 0 else 1
            success, msg = Shop.buy_item(pet, inventory, item_id, count)
            print(f"\n{msg}")
            time.sleep(1.0)
            if success:
                return msg

def handle_inventory(pet: Pet, inventory: Inventory) -> str:
    while True:
        clear_screen()
        print_header()
        print(f"{BOLD}🎒 [인벤토리 (가방)]{RESET}\n")
        if not inventory.items:
            print("가방이 텅 비어 있습니다.")
            input("\n[Enter] 키를 누르면 돌아갑니다...")
            return "가방을 닫았습니다."
        
        idx_map = {}
        curr = 1
        for item_id, count in inventory.items.items():
            item_data = ITEMS_DATABASE.get(item_id, {"name": item_id, "desc": ""})
            idx_map[str(curr)] = item_id
            print(f"[{curr}] {item_data['name']} x{count}개")
            print(f"    └ {item_data['desc']}")
            curr += 1
            
        print(f"\n[0] 가방 닫기")
        sel = input("\n👉 사용할 아이템 번호: ").strip()
        if sel == "0":
            return "가방을 닫았습니다."
        if sel in idx_map:
            success, use_msg = Shop.use_item(pet, inventory, idx_map[sel])
            print(f"\n{use_msg}")
            time.sleep(1.0)
            if success:
                return use_msg

def get_input_with_timeout(timeout=2.5) -> str:
    if msvcrt is None:
        return input().strip()
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        if msvcrt.kbhit():
            ch = msvcrt.getch()
            try:
                return ch.decode('utf-8')
            except UnicodeDecodeError:
                continue
        time.sleep(0.05)
    return None

def main():
    save_data = SaveManager.load()
    meta_data = {"play_count": 0, "claimed_achievements": []}
    last_msg = ""

    if save_data and save_data.get("pet"):
        pet = Pet(custom_data=save_data.get("pet"))
        inv_data = save_data.get("inventory", {})
        inventory = Inventory(inv_data)
        meta_data = save_data.get("meta", meta_data)
        elapsed_min = save_data.get("elapsed_minutes", 0)
        if elapsed_min > 0:
            offline_logs = pet.apply_offline_time(elapsed_min)
            last_msg = " | ".join(offline_logs) if offline_logs else f"선배님 어서오세요! ({elapsed_min:.1f}분 만에 재접속)"
        else:
            last_msg = "저장된 데이터를 완벽하게 불러왔습니다! 환영합니다 선배님 💕"
    else:
        pet = hatch_egg_animation()
        inventory = Inventory()
        SaveManager.save(pet.to_dict(), inventory.to_dict(), meta_data)
        last_msg = f"🎉 새로운 전설 신수 [{pet.name}]과(와)의 여정이 시작되었습니다!"

    claimed_achievements = meta_data.get("claimed_achievements", [])

    while True:
        tick_logs = pet.live_tick()
        if tick_logs:
            last_msg = " | ".join(tick_logs)

        ach_logs = AchievementManager.check_and_claim(pet, inventory, claimed_achievements)
        if ach_logs:
            last_msg = " | ".join(ach_logs)

        meta_data["claimed_achievements"] = claimed_achievements
        SaveManager.save(pet.to_dict(), inventory.to_dict(), meta_data)

        render_dashboard(pet, inventory, claimed_achievements, last_msg)
        last_msg = ""

        print(f"{BOLD}⚡ [실시간 조작 메뉴 - 숫자/단축키를 누르세요]:{RESET}")
        print(" [1] 🍚 밥주기          [2] 🧼 목욕/똥치우기    [3] 🌙 잠자기/깨우기")
        print(" [4] 🏋️ 훈련(레벨업)    [5] 🎮 미니게임(3종)    [6] 🛒 24시 상점")
        print(" [7] 🎒 가방(소모품)     [E] 🛡️ 장비 관리(강화)  [K] 🌱 잠재 성장(혼)")
        print(" [G] ✨ 털손질/미용     [P] ❤️ 쓰다듬기        [N] ✏️ 닉네임 변경")
        print(" [T] 👑 25개 보스 레이드 [H] 🏛️ 보관 & 판매소   [D] 🛠️ 개발자 모드")
        print(" [8] 💉 병원 치료       [9] 💾 저장 및 종료     [0] 🔄 완전 초기화")
        print(f"\n{CYAN}⏰ (키를 누르지 않아도 실시간으로 시간이 흐릅니다...){RESET}")

        action = get_input_with_timeout(timeout=2.5)
        if not action:
            continue

        action = action.strip().upper()

        if action == "1":
            success, msg = pet.feed("normal")
            last_msg = msg
        elif action == "2":
            success, msg = pet.clean()
            last_msg = msg
        elif action == "3":
            success, msg = pet.sleep_toggle()
            last_msg = msg
        elif action == "4":
            success, msg = pet.train()
            last_msg = msg
        elif action == "5":
            clear_screen()
            print_header()
            print(f"{BOLD}🎮 [미니게임 선택]{RESET}\n1. 숫자 맞추기  2. 가위바위보  3. 퀴즈  0. 취소")
            sub = input("\n선택: ").strip()
            if sub == "1":
                c, xp, m = Minigames.play_number_guess(pet)
                pet.coins += c
                pet.gain_exp(xp)
                last_msg = m
            elif sub == "2":
                c, xp, m = Minigames.play_rock_paper_scissors(pet)
                pet.coins += c
                pet.gain_exp(xp)
                last_msg = m
            elif sub == "3":
                c, xp, m = Minigames.play_quiz(pet)
                pet.coins += c
                pet.gain_exp(xp)
                last_msg = m
        elif action == "6":
            last_msg = handle_shop(pet, inventory)
        elif action == "7":
            last_msg = handle_inventory(pet, inventory)
        elif action == "E":
            last_msg = handle_equipment_menu(pet, inventory)
        elif action == "K":
            last_msg = handle_potential_menu(pet, inventory)
        elif action == "8":
            success, msg = pet.cure()
            last_msg = msg
        elif action == "G":
            success, msg = pet.groom()
            last_msg = msg
        elif action == "P":
            success, msg = pet.pet_animal()
            last_msg = msg
        elif action == "N":
            clear_screen()
            print_header()
            print(f"{BOLD}✏️ [신수 닉네임 변경]{RESET}")
            print(f"현재 신수 이름: {GOLD}[{pet.name}]{RESET}\n")
            new_n = input("👉 새로 지어줄 이름을 입력하세요 (취소는 0): ").strip()
            if new_n != "0" and new_n:
                suc, r_msg = pet.rename(new_n)
                last_msg = r_msg
            else:
                last_msg = "이름 변경을 취소했습니다."
        elif action == "T":
            last_msg = handle_adventure_menu(pet, inventory)
        elif action == "D":
            last_msg = handle_dev_menu(pet, inventory)
        elif action == "H":
            pet, last_msg = handle_storage_and_market(pet, inventory, meta_data)
        elif action == "9":
            SaveManager.save(pet.to_dict(), inventory.to_dict(), meta_data)
            clear_screen()
            print(f"\n{GREEN}{BOLD}💾 데이터가 안전하게 저장되었습니다! 안녕히 가세요 선배님~ 👋{RESET}\n")
            break
        elif action == "0":
            confirm = input("\n⚠️ 정말로 모든 세이브 데이터를 삭제하시겠습니까? (y/N): ").strip().lower()
            if confirm == "y":
                SaveManager.reset_save()
                return main()

if __name__ == "__main__":
    main()
