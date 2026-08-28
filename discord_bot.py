# -*- coding: utf-8 -*-
"""
🤖 JENNY'S 신수키우기 DISCORD BOT (v18 Supabase + Render 통합)
1. 신수키우기 전용 채널(1채널/2채널 등) 일반 텍스트 채팅 엄격 차단 & 즉시 삭제 (Clean Chat)
2. 전투 전용 Thread 자동 생성 & 하이브리드 (버튼 + 채팅) 실시간 턴제 보스전
3. 10대 신수 4대 스킬 & 5대 보스 절대 특성 & 투명 가챠 확률표 연동
4. Supabase DB 세이브 + Render 무료 24시간 배포 지원
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import time
import sys
import asyncio
import random
from datetime import datetime

# 🌐 Render 배포용 .env 환경변수 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Render 환경에서는 대시보드 환경변수 사용

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

from pet import Pet, AFFECTION_LEVELS
from species import SPECIES_DATABASE, Genetics, PERSONALITIES, SPECIES_SKILLS
from shop import Shop, Inventory, ITEMS_DATABASE, EXCLUSIVE_RELICS, ARMORS_DATABASE, ARMOR_PROMOTION_TREE
from adventure import (
    AdventureSystem, BOSS_DATABASE, RAID_DIFFICULTIES, BOSS_DIALOGUES,
    get_boss_dialogue, get_recommended_cp, get_power_judgement, RECOMMENDED_COMBAT_POWERS,
    BOSS_SKILLS_DATABASE, choose_boss_action, DUNGEON_DATABASE, DUNGEON_DIFFICULTIES,
    calc_cp_deficit_penalty, FIRST_CLEAR_ARMORS, ANCIENT_BOSS_CORES, BOSS_STAT_TABLE
)
from achievements import AchievementManager, ACHIEVEMENTS_DATABASE
from storage import StorageManager, PetMarket
from save_backend import load_user_save, save_user_save, delete_user_save, get_backend_info, SAVE_BACKEND

CONFIG_FILE = os.path.join(PROJECT_ROOT, "bot_config.json")
SAVES_DIR = os.path.join(PROJECT_ROOT, "discord_saves")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

if not os.path.exists(SAVES_DIR):
    os.makedirs(SAVES_DIR, exist_ok=True)

SPECIES_KEY_TO_FOLDER = {
    "호랑이": "tiger",
    "사자": "lion",
    "늑대": "wolf",
    "드래곤": "dragon",
    "불사조": "phoenix",
    "현무": "turtle",
    "구미호": "fox",
    "그리핀": "griffin",
    "기린": "kirin",
    "바하무트": "bahamut"
}

# 🔒 개발자 모드 보안 잠금 시스템 (기본: 잠금 활성화)
DEV_MODE_LOCKED = True
DEV_ADMIN_PIN = "7777"

def get_growth_stage(level: int) -> int:
    if level >= 99:
        return 4
    elif level >= 70:
        return 3
    elif level >= 40:
        return 2
    return 1

def resolve_pet_image(species_key: str, level: int) -> tuple[str, str]:
    folder_name = SPECIES_KEY_TO_FOLDER.get(species_key, "dragon")
    stage = get_growth_stage(level)
    extensions = [".png", ".jpg", ".jpeg", ".webp"]
    
    # 1. 해당 단계(Stage 1~4) 성장 이미지 탐색
    for ext in extensions:
        stage_filename = f"{folder_name}_stage{stage}{ext}"
        stage_path = os.path.join(ASSETS_DIR, folder_name, stage_filename)
        if os.path.exists(stage_path):
            return stage_path, stage_filename
    
    # 2. 폴더 내 Stage 1/2 기본 이미지 폴백
    for ext in extensions:
        for fallback_stage in [1, 2, 3, 4]:
            fallback_filename = f"{folder_name}_stage{fallback_stage}{ext}"
            fallback_path = os.path.join(ASSETS_DIR, folder_name, fallback_filename)
            if os.path.exists(fallback_path):
                return fallback_path, fallback_filename
        
    # 3. assets 루트 대표 이미지 폴백
    for ext in extensions:
        root_filename = f"{folder_name}{ext}"
        root_path = os.path.join(ASSETS_DIR, root_filename)
        if os.path.exists(root_path):
            return root_path, root_filename

    return None, None

def resolve_boss_image(boss_id: int) -> tuple[str | None, str | None]:
    """👑 5대 레이드 보스 이미지 자동 탐색 (assets/bosses/ 및 다중 확장자/이름 지원)"""
    boss_key_map = {
        1: ["boss_1", "ent", "ancient_ent", "고대엔트", "엔트"],
        2: ["boss_2", "crystal_dragon", "dragon_boss", "크리스탈드래곤", "드래곤"],
        3: ["boss_3", "ifrit", "이프리트"],
        4: ["boss_4", "nebula_guardian", "nebula", "성운가디언", "가디언"],
        5: ["boss_5", "omega", "오메가"]
    }
    cand_names = boss_key_map.get(boss_id, [f"boss_{boss_id}"])
    extensions = [".png", ".jpg", ".jpeg", ".webp", ".PNG", ".JPG", ".JPEG", ".WEBP"]
    
    boss_dir = os.path.join(ASSETS_DIR, "bosses")
    
    # 1. assets/bosses/ 폴더 내부 탐색
    for name in cand_names:
        for ext in extensions:
            fn = f"{name}{ext}"
            p = os.path.join(boss_dir, fn)
            if os.path.exists(p):
                return p, fn
                
    # 2. assets/ 루트 폴더 탐색
    for name in cand_names:
        for ext in extensions:
            fn = f"{name}{ext}"
            p = os.path.join(ASSETS_DIR, fn)
            if os.path.exists(p):
                return p, fn
                
    return None, None

def get_pet_battle_quote(pet: Pet, p_hp: int, p_max_hp: int, had_crit: bool = False, is_boss_dead: bool = False) -> str:
    """🐾 신수 성격/종족/HP상황별 생생한 전투 대사 반환"""
    hp_r = p_hp / max(1, p_max_hp)
    pers = getattr(pet, "personality", "용맹함")
    sp = getattr(pet, "species_key", "호랑이")
    
    if is_boss_dead:
        quotes = {
            "용맹함": "우리가 해냈어! 정의와 힘의 승리다!",
            "냉철함": "계산대로의 결과군. 완벽한 토벌이었다.",
            "애교쟁이": "주인님! 제가 이겼어요! 쓰담쓰담 해주세요 헤헤💕",
            "도도함": "흥, 이 정도 상대는 당연한 결과야.",
            "호기심": "와아! 보스가 쓰러졌어! 정말 멋진 승부였어!"
        }
        return quotes.get(pers, "승리했습니다!")
    
    if hp_r <= 0.30:
        crisis_quotes = {
            "용맹함": "크윽... 아직 쓰러질 수 없어! 끝까지 싸운다!",
            "냉철함": "위험 수치 진입... 침착하게 빈틈을 노린다.",
            "애교쟁이": "으앙 아파요... 하지만 주인님을 위해 버텨낼게요!",
            "도도함": "감히 나를 이 지경으로 만들다니... 대가를 치르게 하마.",
            "호기심": "우와... 엄청 세다... 하지만 포기 안 해!"
        }
        return crisis_quotes.get(pers, "아직 포기할 수 없어!")
    
    if had_crit:
        crit_quotes = {
            "용맹함": "받아라! 혼신의 일격이다!",
            "냉철함": "약점을 정확히 꿰뚫었다.",
            "애교쟁이": "에잇! 엄청 세게 때려줬어요!",
            "도도함": "내 힘이 어때? 감탄하긴 일러.",
            "호기심": "제대로 맞았다! 기분 최고야!"
        }
        return crit_quotes.get(pers, "크리티컬 일격!")
    
    normal_quotes = {
        "구미호": "푸른 여우불이여, 적의 정기를 삼켜라!",
        "호랑이": "백수의 왕의 발톱 앞에 무릎 꿇어라!",
        "사자": "태양왕의 위엄을 똑똑히 보여주마!",
        "늑대": "바람보다 빠르게 적을 꿰뚫겠다.",
        "드래곤": "태초의 용의 숨결을 느껴보아라!",
        "불사조": "불멸의 화염은 결코 꺼지지 않는다!",
        "현무": "천하의 어떤 공격도 이 방패를 뚫을 수 없다.",
        "그리핀": "창공의 날개로 적을 내리꽂아주마!",
        "기린": "천명의 빛으로 어둠을 정화하리라.",
        "바하무트": "모든 것을 무로 되돌리는 파멸을 맞이하라."
    }
    return normal_quotes.get(sp, f"주인님 {pet.name}이(가) 최선을 다해 싸울게요!")

def load_token() -> str:
    """🔑 디스코드 봇 토큰 로드 (환경변수 우선 → bot_config.json 폴백)"""
    # 1. 환경변수 우선 (Render 배포 시 필수)
    env_token = os.environ.get("DISCORD_TOKEN", "").strip()
    if env_token:
        return env_token
    # 2. 로컬 개발용 bot_config.json 폴백
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                token = (
                    data.get("DISCORD_BOT_TOKEN") or 
                    data.get("TOKEN") or 
                    data.get("token") or 
                    data.get("bot_token") or 
                    ""
                )
                return token.strip()
        except Exception:
            pass
    return ""

def get_user_save_path(user_id: int) -> str:
    return os.path.join(SAVES_DIR, f"{user_id}.json")

def get_or_create_user_pet(user_id: int) -> tuple[Pet, Inventory, dict, str]:
    """💾 유저 세이브 로드 (save_backend 통합 인터페이스 사용)"""
    msg = ""
    data = load_user_save(str(user_id))
    
    if data is not None:
        try:
            pet = Pet(custom_data=data.get("pet"))
            inv = Inventory(data.get("inventory"))
            meta = data.get("meta", {"claimed_achievements": []})
            
            # 🎴 신수 탄생 시 종족 전용 보물 기본 획득 보장 (누락 방지)
            if inv.equipped_relic is None:
                inv.equipped_relic = {"species": pet.species_key, "level": 0}
                save_user_pet(user_id, pet, inv, meta)

            last_saved = data.get("last_saved_time", time.time())
            elapsed_min = (time.time() - last_saved) / 60.0
            if elapsed_min > 0.5:
                offline_logs = pet.apply_offline_time(elapsed_min)
                msg = f"⏳ 부재중 {elapsed_min:.1f}분 경과: " + " | ".join(offline_logs)
            return pet, inv, meta, msg
        except Exception as e:
            print(f"⚠️ 세이브 복원 에러 (user={user_id}): {e}")
    
    # 신규 유저 → 새 신수 생성
    pet = Pet()
    inv = Inventory()
    # 🎴 신수 탄생 시 종족 전용 보물 기본 획득 및 자동 장착
    inv.equipped_relic = {"species": pet.species_key, "level": 0}
    meta = {"claimed_achievements": []}
    save_user_pet(user_id, pet, inv, meta)
    shiny_str = " 🌟 [극희귀 변이]" if pet.is_shiny else ""
    msg = f"🎉 [{pet.name}]이(가) 신비한 알에서 부화했습니다! (🎴 전용 보물 기본 지급){shiny_str}"
    return pet, inv, meta, msg

def save_user_pet(user_id: int, pet: Pet, inv: Inventory, meta: dict) -> bool:
    """💾 유저 세이브 저장 (save_backend 통합 인터페이스 사용)"""
    payload = {
        "last_saved_time": time.time(),
        "pet": pet.to_dict(),
        "inventory": inv.to_dict(),
        "meta": meta
    }
    try:
        return save_user_save(str(user_id), payload)
    except Exception as e:
        print(f"❌ DB SAVE ERROR: user={user_id} / {e}")
        return False

def create_bar(val: int, max_val: int = 100, length: int = 8) -> str:
    filled = max(0, min(length, int((val / max(1, max_val)) * length)))
    return "█" * filled + "░" * (length - filled)

class UserActionQueue:
    """
    🚀 유저별 독립 비동기 큐 관리자 (Queue-based Action Dispatcher)
    - 동일 유저의 빠른 연속 클릭(광클) 시 세이브 데이터 덮어쓰기/경쟁 상태(Race Condition) 100% 방지
    - 유저별 독립 Lock과 큐를 통해 멀티유저 및 멀티채널 요청을 안전하게 직렬화/병렬 처리
    """
    def __init__(self):
        self._locks: dict[int, asyncio.Lock] = {}

    def get_lock(self, user_id: int) -> asyncio.Lock:
        if user_id not in self._locks:
            self._locks[user_id] = asyncio.Lock()
        return self._locks[user_id]

USER_ACTION_QUEUE = UserActionQueue()

def is_damagochi_channel(channel) -> bool:
    """신수키우기 1채널, 2채널 및 모든 서버 채널/DM에서 100% 자유롭게 작동하도록 완전 개방"""
    return True

def create_main_embed(user: discord.User, pet: Pet, inv: Inventory, action_msg="", include_image: bool = True, meta: dict = None) -> tuple[discord.Embed, discord.File]:
    if meta is None: meta = {}
    b_stats = pet.get_battle_stats(inv)
    sp_key = getattr(pet, "species_key", "호랑이")
    cur_stage = get_growth_stage(pet.level)
    stage_name_map = {1: "Stage 1 · 유년기", 2: "Stage 2 · 성장기", 3: "Stage 3 · 각성기", 4: "Stage 4 · 👑 초월 강림"}
    
    status_tags = []
    if getattr(pet, "is_dead", False): status_tags.append("☠️ 전사 (부활/새 알 필요)")
    if getattr(pet, "is_critically_injured", False): status_tags.append("💀 치명상 (치료 필요)")
    if pet.is_sleeping: status_tags.append("💤 수면중")
    if pet.is_sick: status_tags.append("🤒 질병")
    if pet.poops > 0: status_tags.append(f"💩 똥 x{pet.poops}")
    
    aff_lvl, _, _ = pet.get_affection_state()
    if aff_lvl == 10: status_tags.append("👑 절대적 유대")
    elif aff_lvl >= 7: status_tags.append("💙 깊은 유대")
    
    if getattr(pet, "transcend_level", 0) > 0: status_tags.append(f"🌌 초월 Lv.{pet.transcend_level}")
    shiny_badge = "🌟 [극희귀 변이] " if getattr(pet, "is_shiny", False) else ""
    sp_data = SPECIES_DATABASE.get(sp_key, {})
    mood_title = sp_data.get("mood_title", "✨ 「신수의 숨결」")
    
    cp_val = b_stats.get('combat_power', 1000)
    
    desc_header = f"**{stage_name_map[cur_stage]}** · {mood_title}\n👑 **종합 전투력:** `{cp_val:,}`"
    if status_tags:
        desc_header += f"\n{' · '.join(status_tags)}"

    eq_title = meta.get("equipped_title")
    title_str = f"🏷️ **【{eq_title}】**\n" if eq_title else ""

    embed = discord.Embed(
        title=f"{pet.emoji} {title_str}{user.display_name}님의 신수 · {shiny_badge}{pet.name}",
        description=desc_header,
        color=discord.Color.gold() if getattr(pet, "is_shiny", False) or "신화" in getattr(pet, "tier", "") else discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    img_path, img_filename = resolve_pet_image(sp_key, pet.level)
    file_attachment = None
    if img_path and os.path.exists(img_path):
        file_attachment = discord.File(img_path, filename=img_filename)
        embed.set_image(url=f"attachment://{img_filename}")

    # 1. ⚔️ 전투 스탯
    c_val = b_stats['crit']
    base_crit_rate = c_val / (c_val + 900.0)
    final_crit_rate = min(0.70, base_crit_rate + (0.15 if b_stats.get('effect') == 'crit' else 0.0))
    crit_rate_pct = int(final_crit_rate * 100)
    
    cur_live_hp = max(10, int(b_stats['max_hp'] * (pet.health / 100.0)))
    stat_block = (
        f"❤️ **HP**　 `{cur_live_hp:,} / {b_stats['max_hp']:,}`\n"
        f"⚔️ **ATK**　`{b_stats['atk']:,}`\n"
        f"🛡️ **DEF**　`{b_stats['def']:,}`\n"
        f"⚡ **SPD**　`{b_stats['spd']}`\n"
        f"💥 **CRIT** `{b_stats['crit']}` *({crit_rate_pct}%)*"
    )
    embed.add_field(name="⚔️ 전투 스탯", value=stat_block, inline=True)

    # 2. 💖 실시간 컨디션 & 10단계 애정도
    max_e = getattr(pet, "max_energy", 100)
    e_b = create_bar(pet.energy, max_e, 6)
    st_b = create_bar(getattr(pet, "stamina", 100), max_e, 6)
    h_b = create_bar(pet.hunger, 100, 6)
    hp_b = create_bar(pet.happiness, 100, 6)
    hl_b = create_bar(pet.health, 100, 6)
    
    # 💖 10단계 애정도 상태
    aff_lvl, aff_prog, aff_info = pet.get_affection_state()
    aff_b = create_bar(aff_prog, 100, 6)
    
    cond_block = (
        f"⚡ **생활** `{e_b}` {pet.energy}%\n"
        f"🔥 **모험** `{st_b}` {getattr(pet, 'stamina', 100)}%\n"
        f"🍚 **포만** `{h_b}` {pet.hunger}%\n"
        f"💖 **행복** `{hp_b}` {pet.happiness}%\n"
        f"🏥 **건강** `{hl_b}` {pet.health}%\n"
        f"❤️ **애정** `{aff_b}` **Lv.{aff_lvl}** {aff_prog}/100\n"
        f"　 └ _{aff_info['quote']}_"
    )
    embed.add_field(name="💖 신수 컨디션", value=cond_block, inline=True)

    # 3. 📈 성장 및 골드
    if pet.level >= 99:
        exp_b = create_bar(pet.transcend_exp, 50000, 8)
        exp_pct = int((pet.transcend_exp / 50000) * 100)
        lvl_line = f"**Lv.99 만렙** *(초월 Lv.{getattr(pet, 'transcend_level', 0)})* `[{exp_b}]` {exp_pct}%"
    else:
        exp_b = create_bar(pet.exp, pet.max_exp, 8)
        exp_pct = int((pet.exp / max(1, pet.max_exp)) * 100)
        lvl_line = f"**Lv.{pet.level} / 99** `[{exp_b}]` {exp_pct}%"

    growth_block = f"{lvl_line} · 💰 **골드:** `{pet.coins:,}G` · 👑 **토벌:** `{pet.total_dungeon_clears}회`"
    embed.add_field(name="📈 성장 정보", value=growth_block, inline=False)

    if action_msg:
        embed.add_field(name="📢 안내", value=f"✨ {action_msg}", inline=False)

    return embed, file_attachment

def create_detail_embed(user: discord.User, pet: Pet, inv: Inventory, meta: dict = None) -> discord.Embed:
    b_stats = pet.get_battle_stats(inv)
    sp_key = getattr(pet, "species_key", "호랑이")
    sp_data = SPECIES_DATABASE.get(sp_key, {})
    p_info = PERSONALITIES.get(getattr(pet, "personality", "용맹함"), PERSONALITIES["용맹함"])
    if meta is None: meta = {}
    
    embed = discord.Embed(
        title=f"📊 [{pet.name}] 상세 스탯 & 장비 분석",
        description=(
            f"종족: **{pet.emoji} {pet.species_name}** | 등급: `{getattr(pet, 'tier', '일반')}` | 무드: **{sp_data.get('mood_title', '기본')}**\n"
            f"🌟 **종족 고유 무드 효과:** `{sp_data.get('mood_desc', '표준 성장')}`"
        ),
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )

    # 1. ⚔️ 실시간 전투 스탯 & 전투력 (CP)
    crit_rate_pct = int(min(0.70, b_stats['crit'] / (b_stats['crit'] + 900.0)) * 100)
    stats_block = (
        f"• ❤️ **최대 체력 (HP):** `{b_stats['max_hp']:,}`\n"
        f"• ⚔️ **물리 공격력 (ATK):** `{b_stats['atk']:,}`\n"
        f"• 🛡️ **방어력 (DEF):** `{b_stats['def']:,}`\n"
        f"• ⚡ **스피드 (SPD):** `{b_stats['spd']:,}`\n"
        f"• 💥 **치명타 (CRIT):** `{b_stats['crit']:,}` (치명타율 `{crit_rate_pct}%`)\n\n"
        f"👑 **종합 전투력 (CP):** `👑 {b_stats['combat_power']:,} CP`"
    )
    embed.add_field(name="⚔️ 실시간 전투 스탯 (CP)", value=stats_block, inline=False)

    def get_iv_grade(v: int) -> str:
        if v >= 100: return "👑 PERFECT"
        elif v >= 95: return "⭐ 천재"
        elif v >= 80: return "💎 최상"
        elif v >= 60: return "✨ 우수"
        elif v >= 30: return "🟢 보통"
        else: return "⚫ 낮음"

    hp_v = getattr(pet, "hp_iv", 70); atk_v = getattr(pet, "atk_iv", 70)
    def_v = getattr(pet, "def_iv", 70); spd_v = getattr(pet, "spd_iv", 70); crit_v = getattr(pet, "crit_iv", 70)

    iv_block = (
        f"• ❤️ **HP (체력):** `{hp_v}` / 100 ({get_iv_grade(hp_v)})\n"
        f"• ⚔️ **ATK (공격):** `{atk_v}` / 100 ({get_iv_grade(atk_v)})\n"
        f"• 🛡️ **DEF (방어):** `{def_v}` / 100 ({get_iv_grade(def_v)})\n"
        f"• ⚡ **SPD (스피드):** `{spd_v}` / 100 ({get_iv_grade(spd_v)})\n"
        f"• 💥 **CRIT (치명타):** `{crit_v}` / 100 ({get_iv_grade(crit_v)})\n\n"
        f"📊 **IV 총합:** `{pet.total_iv} / 500` ──> **[{pet.rank}]**"
    )
    embed.add_field(name="🧬 5V 개체 잠재력 (IV)", value=iv_block, inline=True)

    trait_desc_map = {
        "fierce_atk": "공격적으로 몰아붙임 (ATK +12%, DEF -6%)",
        "brave_crisis": "HP 50% 이하 위기 시 (ATK +10%, DEF +10%)",
        "dodge_boost": "적 공격 10% 확률 완전 회피 (ATK -5%)",
        "agile_spd": "선공 및 질풍 연타 특화 (SPD +12%, HP -5%)",
        "prudent_def": "안정적인 철벽 탱커 (DEF +12%, SPD -8%)",
        "early_burst": "첫 3턴 ATK +15% 폭딜 (이후 -5%)",
        "gentle_regen": "턴 종료 시 최대 HP 2% 지속 회복 (CRIT -5%)",
        "calm_crit": "치명타 피해 2.2배 극대화 (CRIT +8%, HP -5%)",
        "arrogant_hunt": "자신보다 약한 적에게 피해 +15%",
        "indomitable": "치명타 피격 시 20% 확률 피해 50% 감소"
    }
    p_trait_key = p_info.get("battle_trait", "none")
    p_trait_detail = trait_desc_map.get(p_trait_key, p_info.get("desc", ""))

    pers_block = (
        f"**{p_info['emoji']} {p_info['name']}**\n"
        f"_{p_info['desc']}_\n\n"
        f"⚡ **고유 효과:**\n`{p_trait_detail}`"
    )
    embed.add_field(name="🎭 성격 & 고유 패시브", value=pers_block, inline=True)

    if inv and inv.equipped_relic:
        r_lvl = inv.equipped_relic["level"]
        r_data = EXCLUSIVE_RELICS.get(sp_key, {})
        relic_str = f"🎴 **{r_data.get('name', '전용 보물')} +{r_lvl}**\n└ {r_data.get('desc', '')}"
        if r_lvl >= 10:
            relic_str += f"\n└ 👑 **[전용 효과]** {r_data.get('special_10', '')}"
    else:
        relic_str = "`미장착 (던전/상점 획득)`"

    if inv and inv.equipped_armor:
        a_lvl = inv.equipped_armor.get("level", 0)
        a_stars = inv.equipped_armor.get("stars", 0)
        star_str = f" {'★' * a_stars}" if a_stars > 0 else ""
        a_data = ARMORS_DATABASE.get(inv.equipped_armor["armor_id"], {})
        opt_str = f" [✨ {inv.equipped_armor['opt']['name']} +{int(inv.equipped_armor['opt']['val']*100)}%]" if inv.equipped_armor.get("opt") else ""
        ancient_str = f"\n└ 🌌 **[고대 특효]** 「{a_data.get('ancient_passive', '')}」 {a_data.get('ancient_desc', '')}" if a_stars >= 5 else ""
        armor_str = f"🛡️ **{a_data.get('tier', '')} {a_data.get('name', '방어구')} +{a_lvl}{star_str}**{opt_str}\n└ {a_data.get('desc', '')}{ancient_str}"
    else:
        armor_str = "`미장착 (던전/레이드 파밍)`"

    equip_block = (
        f"{relic_str}\n\n"
        f"{armor_str}"
    )
    embed.add_field(name="🎒 장착 장비 분석", value=equip_block, inline=False)

    aff_lvl, aff_prog, aff_info = pet.get_affection_state()
    tot_aff = getattr(pet, "total_affection", getattr(pet, "affection", 0))
    tot_hatches = meta.get("total_hatches", 0)
    pre_used_str = "❌ 사용완료 (99렙 달성 시 환생 가능)" if meta.get("pre_99_hatch_used", False) else "⭕ 1회 가능 (Lv.1 전용)"
    next_info_str = f"다음 단계: Lv.{aff_lvl+1}" if aff_lvl < 10 else "👑 최고 유대 도달"
    t_lvl = getattr(pet, 'transcend_level', 0)
    t_str = f"x{t_lvl}★" if t_lvl > 0 else "0★"
    
    growth_state_block = (
        f"• ❤️ **애정도:** {aff_info['icon']} **Lv.{aff_lvl} · {aff_info['name']}** `{aff_prog} / 100` (총 누적: `{tot_aff} / 1000`)\n"
        f"  └ 📜 _{aff_info['quote']}_ ({aff_info['bonus']} / {next_info_str})\n"
        f"• ✨ **외모력 (Charm):** `{pet.charm}점` (경매 판매가 가산)\n"
        f"• 🌌 **초월 단계:** `Lv.{pet.level} {t_str}` (전 스탯 +{t_lvl}% 영구 보정)\n"
        f"• 🥚 **개인 누적 소환:** `{tot_hatches}회` | **초기 리롤 기회:** `{pre_used_str}`"
    )
    embed.add_field(name="🌟 장기 성장 및 소환 기록", value=growth_state_block, inline=False)

    return embed

def create_skills_embed(user: discord.User, pet: Pet, inv: Inventory) -> discord.Embed:
    """⚔️ 신수 4대 고유 전투 스킬 & 전용 보물 정보 상세 조회 Embed (v17.2)"""
    sp_skills = SPECIES_SKILLS.get(pet.species_key, {})
    relic_data = EXCLUSIVE_RELICS.get(pet.species_key, {})
    eq_relic = getattr(inv, "equipped_relic", None)
    relic_lvl = eq_relic.get("level", 0) if eq_relic else 0
    b_stats = pet.get_battle_stats(inv)

    embed = discord.Embed(
        title=f"⚔️ [{pet.name}] 4대 전투 스킬 & 전용 보물 정보",
        description=(
            f"🐾 종족: **{pet.emoji} {pet.species_name}** | 🌈 속성: **{pet.element}** | 🎭 성격: **{pet.personality}**\n"
            f"👑 **실시간 전투력:** `👑 {b_stats['combat_power']:,} CP`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    # 1. 기본기 1 & 2
    b1 = sp_skills.get("basic1", {"name": "기본 공격 1", "desc": "기본 공격"})
    b2 = sp_skills.get("basic2", {"name": "기본 공격 2", "desc": "기본 공격"})
    embed.add_field(
        name=f"🗡️ [기본기 1] {b1.get('name', '기본기 1')} (쿨타임: 없음)",
        value=f"• {b1.get('desc', '기본 공격')}",
        inline=False
    )
    embed.add_field(
        name=f"🗡️ [기본기 2] {b2.get('name', '기본기 2')} (쿨타임: 없음)",
        value=f"• {b2.get('desc', '기본 공격')}",
        inline=False
    )

    # 2. 고유기
    u_skill = sp_skills.get("unique", {"name": "고유기", "cooldown": 3, "desc": "특수 효과"})
    embed.add_field(
        name=f"✨ [고유기] {u_skill.get('name', '고유기')} (쿨타임: {u_skill.get('cooldown', 3)}턴)",
        value=f"• {u_skill.get('desc', '특수 공격/버프')}",
        inline=False
    )

    # 3. 궁극기
    ult = sp_skills.get("ultimate", {"name": "궁극기", "cooldown": 5, "desc": "필살기"})
    embed.add_field(
        name=f"👑 [궁극기] {ult.get('name', '궁극기')} (쿨타임: {ult.get('cooldown', 5)}턴)",
        value=f"• **{ult.get('desc', '초극대 필살 피해')}**",
        inline=False
    )

    # 4. 종족 전용 보물 & +10강 고유 패시브
    r_name = relic_data.get("name", f"{pet.species_name}의 보물")
    r_spec10 = relic_data.get("special_10", "고유 효과 없음")
    relic_val_str = f"• **현재 장착 상태:** `+{relic_lvl}강` / `+10강`"
    if relic_lvl >= 10:
        relic_val_str += f"\n• 🌟 **+10강 고유 패시브 개화:** `{r_spec10}`"
    else:
        relic_val_str += f"\n• 🔒 **+10강 달성 시 개화:** `{r_spec10}`"

    embed.add_field(
        name=f"🎴 [전용 보물] {r_name}",
        value=relic_val_str,
        inline=False
    )

    embed.set_footer(text="하단 [📊 상세 스탯으로] 버튼을 눌러 스탯 분석 화면으로 돌아갈 수 있습니다.")
    return embed

def create_gacha_rates_embed() -> discord.Embed:
    embed = discord.Embed(
        title="🎲 10대 신수 소환 공식 확률표",
        description="게임 내 모든 소환 확률은 100% 투명하게 공개됩니다.",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="🟢 일반 (Common) · 48%",
        value="• 🐯 **호랑이:** `16.00%`\n• 🦁 **사자:** `16.00%`\n• 🐺 **늑대:** `16.00%`",
        inline=False
    )
    embed.add_field(
        name="🔵 희귀 (Rare) · 34%",
        value="• 🐉 **드래곤:** `12.00%`\n• 🦅 **불사조:** `12.00%`\n• 🐢 **현무:** `10.00%`",
        inline=False
    )
    embed.add_field(
        name="🟣 영웅 (Heroic) · 12%",
        value="• 🦊 **구미호:** `7.00%`\n• 🪽 **그리핀:** `5.00%`",
        inline=False
    )
    embed.add_field(
        name="🟡 전설 (Legendary) · 5%",
        value="• 🦄 **기린:** `5.00%` *(전설 등장 시 100% 기린 확정!)*",
        inline=False
    )
    embed.add_field(
        name="🔴 신화 (Mythic) · 1%",
        value="• 🐲 **바하무트:** `1.00%` *(약 1/100의 최고 존엄 파괴신!)*",
        inline=False
    )
    embed.add_field(
        name="🌟 극희귀 변이 (Shiny) · 2%",
        value=(
            "소환 시 `2.00%` 확률로 4대 변이(태초/혼돈/혈월/천공 각 25%)가 발현됩니다.\n"
            "• 🌌 **변이 바하무트 전체 확률:** `0.02%` *(약 1 / 5,000)*\n"
            "• 👑 **특정 변이 바하무트 확률:** `0.005%` *(약 1 / 20,000)*\n"
            "• 🏆 **총 종족 확률 합계:** `100.00%`"
        ),
        inline=False
    )
    embed.set_footer(text="신수키우기 v1.0 💖 | 100% 공정 투명 확률")
    return embed

def create_lineage_embed(user: discord.User, pet: Pet, meta: dict) -> discord.Embed:
    """🧬 가문 혈통 계보 및 세대별 성장 히스토리 Embed (v12.1 통합)"""
    lineage_data = meta.get("lineage", {})
    gen_history = lineage_data.get("history", [])
    cur_gen = getattr(pet, "generation", 1)
    best_iv = lineage_data.get("best_total_iv", pet.total_iv)
    best_gen = lineage_data.get("best_generation", cur_gen)

    embed = discord.Embed(
        title=f"🧬 {user.display_name}님의 신수 혈통 계보도",
        description=f"👑 **현재 세대:** `제{cur_gen}세대` | 🐾 **현재 신수:** `[{pet.name}]` ({pet.species_name} {pet.rank})",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="🏆 역대 최고 가문 기록",
        value=f"• 🌟 **역대 최고 IV 총합:** `{best_iv} / 500` (제{best_gen}세대)\n• 🏛️ **누적 계승 세대:** `{len(gen_history) + 1}세대`",
        inline=False
    )

    if gen_history:
        lines = []
        for g in gen_history[-6:]: # 최근 6세대 계보
            s_tag = "✨ " if g.get("is_shiny") else ""
            lines.append(f"• **제{g['generation']}세대** | {s_tag}[{g['name']}] ({g['species']}) ──> IV `{g['total_iv']}/500` [{g['rank'].split()[0]}]")
        lines.append(f"• **제{cur_gen}세대 (현재)** | [{pet.name}] ({pet.species_name}) ──> IV `{pet.total_iv}/500` [{pet.rank.split()[0]}]")
        embed.add_field(name="📜 가문 세대별 계보도 (History)", value="\n".join(lines), inline=False)
    else:
        embed.add_field(
            name="📜 가문 세대별 계보도",
            value=f"• **제1세대 (태초의 시조)** | [{pet.name}] ({pet.species_name}) ──> IV `{pet.total_iv}/500` [{pet.rank.split()[0]}]\n*(Lv.99 만렙 달성 후 환생 시 다음 세대 계보가 영구 기록됩니다!)*",
            inline=False
        )

    embed.set_footer(text="신수키우기 v1.0 💖 | [🔙 메인으로] 버튼으로 복귀")
    return embed

def create_bag_embed(user: discord.User, pet: Pet, inv: Inventory) -> discord.Embed:
    """🎒 가방(인벤토리) 전체 상세 조회 Embed"""
    t_lvl = getattr(pet, 'transcend_level', 0)
    t_str = f" x{t_lvl}★" if t_lvl > 0 else ""
    
    embed = discord.Embed(
        title=f"🎒 {user.display_name}님의 신수 인벤토리 (가방)",
        description=f"💰 **보유 골드:** `{pet.coins:,}G` | 🐾 **신수:** `[{pet.name} Lv.{pet.level}{t_str}]`",
        color=discord.Color.teal(),
        timestamp=datetime.now()
    )

    # 1. 🍖 돌봄 아이템
    care_items = []
    for i_id, cnt in inv.items.items():
        if i_id in ["feed", "meat", "cake", "shampoo", "toy"] and cnt > 0:
            i_info = ITEMS_DATABASE.get(i_id, {})
            care_items.append(f"{i_info.get('emoji', '📦')} **{i_info.get('name', i_id)}:** `{cnt}개`")
    embed.add_field(name="🍖 돌봄 아이템", value="\n".join(care_items) if care_items else "`보유 아이템 없음`", inline=True)

    # 2. 🍬 성장 & 치료 아이템
    growth_items = []
    for i_id, cnt in inv.items.items():
        if i_id in ["small_candy", "super_candy", "mega_candy", "ancient_candy", "potion_atk", "potion_def", "potion_hp", "potion_spd", "potion_crit", "potion", "revive", "life_gem", "holy_water", "primordial_heart"] and cnt > 0:
            i_info = ITEMS_DATABASE.get(i_id, {})
            growth_items.append(f"• **{i_info.get('name', i_id)}:** `{cnt}개`")
    embed.add_field(name="🍬 성장 & 치료", value="\n".join(growth_items) if growth_items else "`보유 아이템 없음`", inline=True)

    # 3. 🔨 강화 & 레이드 고난도 재료
    mat_items = []
    if inv.items.get("stone", 0) > 0: mat_items.append(f"💎 **일반 강화석:** `{inv.items['stone']}개`")
    if inv.items.get("armor_stone", 0) > 0: mat_items.append(f"🔷 **방어구 강화석:** `{inv.items['armor_stone']}개`")
    if inv.items.get("relic_essence", 0) > 0: mat_items.append(f"🔮 **보물의 정수:** `{inv.items['relic_essence']}개`")
    if inv.items.get("nightmare_crystal", 0) > 0: mat_items.append(f"🟣 **악몽의 결정 (Nightmare):** `{inv.items['nightmare_crystal']}개`")
    if inv.items.get("mythic_core", 0) > 0: mat_items.append(f"🟡 **신화의 핵 (Mythic):** `{inv.items['mythic_core']}개`")
    if inv.items.get("ancient_core", 0) > 0: mat_items.append(f"🌑 **태고의 핵 (Ancient):** `{inv.items['ancient_core']}개`")
    embed.add_field(name="🔨 강화 & 고난도 레이드 재료", value="\n".join(mat_items) if mat_items else "`보유 재료 없음 (던전/레이드 파밍)`", inline=False)

    # 4. 🎴 보물 & 🛡️ 방어구 보관함
    relic_str = f"🎴 **장착 보물:** `🎴 {EXCLUSIVE_RELICS.get(pet.species_key, {}).get('name', '보물')} +{inv.equipped_relic['level']}`" if inv.equipped_relic else "🎴 **장착 보물:** `미장착`"
    if inv.equipped_armor:
        a_lvl = inv.equipped_armor.get("level", 0)
        a_stars = inv.equipped_armor.get("stars", 0)
        star_str = f" {'★' * a_stars}" if a_stars > 0 else ""
        a_name = ARMORS_DATABASE.get(inv.equipped_armor["armor_id"], {}).get("name", "방어구")
        armor_str = f"🛡️ **장착 방어구:** `🛡️ {a_name} +{a_lvl}{star_str}`"
    else:
        armor_str = "🛡️ **장착 방어구:** `미장착`"
    
    # 보유 중인 다른 방어구 목록
    other_armors = []
    for idx, a in enumerate(inv.armors_inventory):
        a_n = ARMORS_DATABASE.get(a.get("armor_id"), {}).get("name", "방어구")
        a_l = a.get("level", 0)
        a_s = a.get("stars", 0)
        s_txt = f" {'★'*a_s}" if a_s > 0 else ""
        other_armors.append(f"• `{a_n} +{a_l}{s_txt}`")
    other_txt = f"\n📦 **보관 중인 방어구 ({len(inv.armors_inventory)}개):** " + (", ".join(other_armors) if other_armors else "없음")
    
    embed.add_field(name="🎒 장비 장착 및 보관함", value=f"{relic_str}\n{armor_str}{other_txt}", inline=False)

    embed.set_footer(text="신수키우기 v1.0 💖 | [🔙 메인으로] 버튼으로 복귀")
    return embed

def create_shop_embed(user: discord.User, pet: Pet, inv: Inventory = None) -> discord.Embed:
    """🛒 24시 신수 편의 상점 Embed (v17.2)"""
    embed = discord.Embed(
        title="🛒 24시 신수 편의 상점",
        description=(
            f"💰 **보유 골드:** `{pet.coins:,}G`\n"
            f"*돌봄 사료, 성장 사탕, 치명상 방지 및 소생 아이템을 구매할 수 있습니다!*\n"
            f"_(💡 질병 및 기본 상처 치료는 메인의 `[💉 병원 치료]`를 이용해 주세요.)_"
        ),
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="🍖 돌봄 & 관리",
        value=(
            "• 🍖 **일반 사료:** `50G` (포만+30)\n"
            "• 🥩 **고급 고기:** `200G` (포만+50, 기력+20)\n"
            "• 🍰 **신수 케이크:** `500G` (포만+40, 행복+30)\n"
            "• 🧼 **신수 샴푸:** `150G` (청결+60, 외모+3)"
        ),
        inline=True
    )

    embed.add_field(
        name="🍬 성장 아이템",
        value=(
            "• 🍬 **작은 EXP 사탕:** `500G` (+150 EXP)\n"
            "• 🍭 **슈퍼 EXP 사탕:** `1,500G` (+500 EXP)\n"
            "• 💎 **생명의 보석:** `5,000G` (치명상 1회 자동 방어)\n"
            "• ━━━━━━━━━━━━━━"
        ),
        inline=True
    )

    embed.add_field(
        name="🌟 불사 & 소생 (치명상 완치)",
        value=(
            "• 🌟 **불사의 성수:** `3,000G` (치명상 즉시 완치 + 건강/기력 60%)\n"
            "• 🌌 **태초의 심장:** `10,000G` (치명상 즉시 완치 + 건강/기력 100% 풀충전)"
        ),
        inline=False
    )

    embed.set_footer(text="하단 아이템 버튼을 클릭하여 즉시 구매하세요! 💖")
    return embed

def create_potential_embed(user: discord.User, pet: Pet, inv: Inventory) -> discord.Embed:
    """🌱 신수 잠재 성장 각성소 Embed (v17.1)"""
    pot = getattr(pet, "potential_growth", {}) or {}
    embed = discord.Embed(
        title=f"🌱 {user.display_name}님의 신수 잠재 성장 각성소",
        description=(
            f"🐾 **신수:** `[{pet.name}]` ({pet.species_name} {pet.rank})\n"
            f"📜 **규칙:** 레이드에서 획득한 난이도별 혼을 소모하여 5대 스탯을 각각 최대 **+60.0%**까지 각성시킵니다!\n"
            f"• ⚪ **노말 (일반 혼):** `0% -> 15%` | 🔵 **하드 (고급 혼):** `15% -> 30%`\n"
            f"• 🟣 **악몽 (전설 혼):** `30% -> 45%` | 🟡 **신화 (신화 혼):** `45% -> 60%`\n"
            f"• **단계별 필요 혼:** `1개` ➔ `4개` ➔ `9개` ➔ `16개` ➔ `25개` (단계당 +3%)"
        ),
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    stat_names = [("hp", "❤️ 체력"), ("atk", "⚔️ 공격력"), ("def", "🛡️ 방어력"), ("spd", "⚡ 스피드"), ("crit", "💥 치명타")]
    lines = []
    for k, name in stat_names:
        val = pot.get(k, 0.0)
        step = int(round(val / 0.03))
        bar = create_bar(step, 20, 10)
        pct = int(round(val * 100))
        
        if step >= 20:
            next_info = "👑 MAX 달성 (+60%)"
        else:
            next_s = step + 1
            sub_s = (next_s - 1) % 5 + 1
            req_c = [1, 4, 9, 16, 25][sub_s - 1]
            t_idx = (next_s - 1) // 5
            s_names = ["일반 혼", "고급 혼", "전설 혼", "신화 혼"]
            next_info = f"다음: +{int(round(next_s*3))}% (필요: {s_names[t_idx]} {req_c}개)"
            
        lines.append(f"• **{name}:** `+{pct}%` `[{bar}]` ({step}/20단계) | _{next_info}_")

    embed.add_field(name="📊 현재 5대 스탯 잠재 성장 현황", value="\n".join(lines), inline=False)

    souls_info = (
        f"• ⚪ **일반 혼 (Normal):** `{inv.items.get('soul_normal', 0)}개`\n"
        f"• 🔵 **고급 혼 (Hard):** `{inv.items.get('soul_hard', 0)}개`\n"
        f"• 🟣 **전설 혼 (Nightmare):** `{inv.items.get('soul_nightmare', 0)}개`\n"
        f"• 🟡 **신화 혼 (Mythic):** `{inv.items.get('soul_mythic', 0)}개`"
    )
    embed.add_field(name="🎒 보유 중인 레이드 혼(Soul)", value=souls_info, inline=False)
    embed.set_footer(text="하단 버튼을 클릭하여 원하는 스탯을 즉시 각성하세요! 💖")
    return embed

def create_dev_embed(user: discord.User, pet: Pet, inv: Inventory) -> discord.Embed:
    """🛠️ 개발자 & 관리자 전용 디버그/치트 대시보드 Embed"""
    b_stats = pet.get_battle_stats(inv)
    pot = getattr(pet, "potential_growth", {}) or {}
    embed = discord.Embed(
        title=f"🛠️ [개발자 모드] {user.display_name}님의 관리자 콘솔",
        description=(
            f"👑 **현재 신수:** `[{pet.name}]` ({pet.species_name} {pet.rank} · Lv.{pet.level})\n"
            f"⚔️ **전투력:** `👑 {b_stats['combat_power']:,}` | 💰 **골드:** `{pet.coins:,}G`\n"
            f"🌟 **초월:** `Lv.{getattr(pet, 'transcend_level', 0)}` | 💖 **애정도:** `Lv.{pet.get_affection_state()[0]} ({getattr(pet, 'total_affection', 0)}/1000)`\n"
            f"🌱 **잠재:** HP +{int(pot.get('hp', 0)*100)}% / ATK +{int(pot.get('atk', 0)*100)}% / DEF +{int(pot.get('def', 0)*100)}% / SPD +{int(pot.get('spd', 0)*100)}% / CRIT +{int(pot.get('crit', 0)*100)}%\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ *원하는 치트/디버그 버튼을 클릭하여 스탯과 장비를 자유롭게 조작하세요!*"
        ),
        color=discord.Color.magenta(),
        timestamp=datetime.now()
    )

    embed.add_field(
        name="🎁 1. 재화 & 아이템 치트",
        value="• `[💰 골드 +100만]` : 1,000,000G 즉시 지급\n• `[🍬 사탕+강화석]` : 모든 사탕 20개 + 강화석 50개\n• `[🌱 혼 4종 세트]` : 노말/하드/악몽/신화 혼 각 50개",
        inline=False
    )
    embed.add_field(
        name="📈 2. 스탯 & 혈통 & 성장 치트",
        value="• `[📈 만렙(Lv.99)]` : 즉시 Lv.99 달성\n• `[🌌 초월 Lv.20]` : 즉시 최고 초월 달성\n• `[💖 애정 Max]` : 10단계(1,000) 달성\n• `[🌱 잠재 60% Max]` : 5대 스탯 풀각성\n• `[🧬 PERFECT 500]` : 올 100 IV + 샤이니 변이",
        inline=False
    )
    embed.add_field(
        name="🛡️ 3. 장비 & 종결 프리셋",
        value="• `[🛡️ 고대신 +15 ★5]` : 최고위 고대 방어구 장착\n• `[🎴 보물 +10]` : 전용 보물 풀강화 장착\n• `[👑 신수왕 완전체]` : 모든 스탯/장비/초월 원클릭 종결 세팅\n• `[🚪 레이드 올해금]` : 5대 보스 관문/칭호 올클리어 처리",
        inline=False
    )

    embed.set_footer(text="개발자 모드 활성화됨 · 원하는 기능을 원클릭으로 테스트하세요! 🛠️")
    return embed

def create_dev_species_embed(user: discord.User, pet: Pet) -> discord.Embed:
    """🐾 10대 신수 종족 즉시 선택 변경 Embed"""
    embed = discord.Embed(
        title="🐾 [개발자 모드] 10대 신수 종족 즉시 변경",
        description=(
            f"👑 **현재 신수:** `[{pet.name}]` ({pet.emoji} {pet.species_name} {pet.rank})\n"
            f"원하는 종족 버튼을 클릭하면 스탯, 종족 고유기, 전용 보물이 즉시 변경됩니다!"
        ),
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    for sp_k, sp_d in SPECIES_DATABASE.items():
        embed.add_field(
            name=f"{sp_d['emoji']} {sp_d['name']} ({sp_d['tier']})",
            value=f"• 역할: `{sp_d['role']}` | 속성: `{sp_d.get('element', '무속성')}`\n• 패시브: {sp_d['battle_passive_name']}",
            inline=True
        )
    embed.set_footer(text="하단 종족 버튼을 클릭하세요!")
    return embed

def create_dev_personality_embed(user: discord.User, pet: Pet) -> discord.Embed:
    """🎭 10대 성격 즉시 선택 변경 Embed"""
    embed = discord.Embed(
        title="🎭 [개발자 모드] 10대 성격 즉시 변경",
        description=f"👑 **현재 성격:** `{getattr(pet, 'personality', '용맹함')}`\n원하는 성격 버튼을 클릭하여 고유 전투 패시브를 즉시 적용하세요!",
        color=discord.Color.teal(),
        timestamp=datetime.now()
    )
    for p_k, p_d in PERSONALITIES.items():
        embed.add_field(name=f"{p_d['emoji']} {p_d['name']}", value=f"_{p_d['desc']}_", inline=True)
    embed.set_footer(text="하단 성격 버튼을 클릭하세요!")
    return embed

def create_dev_armor_embed(user: discord.User, inv: Inventory) -> discord.Embed:
    """🛡️ 방어구 즉시 장착 & 강화/성급 조작 Embed"""
    cur_a = inv.equipped_armor
    cur_str = f"{ARMORS_DATABASE[cur_a['armor_id']]['name']} +{cur_a['level']}" if cur_a else "미장착"
    embed = discord.Embed(
        title="🛡️ [개발자 모드] 방어구 직접 선택 & 강화 조작",
        description=f"🛡️ **현재 장착 방어구:** `{cur_str}`\n원하는 방어구를 즉시 장착하거나 강화 수치를 설정하세요!",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    for a_k, a_d in ARMORS_DATABASE.items():
        embed.add_field(name=f"🛡️ {a_d['tier']} {a_d['name']}", value=f"• {a_d['desc']}", inline=True)
    embed.set_footer(text="하단 버튼으로 방어구를 즉시 교체하세요!")
    return embed

def create_forge_embed(user: discord.User, pet: Pet, inv: Inventory) -> discord.Embed:
    """⚒️ 신수 장비 대장간 & 티어 승급소 전용 Embed (v16.3)"""
    t_lvl = getattr(pet, 'transcend_level', 0)
    t_str = f" x{t_lvl}★" if t_lvl > 0 else ""
    sp_key = getattr(pet, "species_key", "호랑이")
    max_relic = pet.get_relic_max_level()
    
    embed = discord.Embed(
        title="⚒️ [장비 대장간] 신수 장비 강화 & 티어 승급소",
        description=(
            f"🐾 **신수:** `[{pet.name} Lv.{pet.level}{t_str}]` | 💰 **보유 골드:** `{pet.coins:,}G`\n"
            f"🌲 **던전에서 강화 재료를 캐고, ⚔️ 레이드에서 승급 허가증을 획득하세요!**\n"
            f"🛡️ _(강화 실패 시에도 장비 파괴나 수치 하락은 0%입니다!)_"
        ),
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )

    # 1. 🎴 종족 전용 보물 현황 & 다음 강화 정보
    if inv.equipped_relic:
        r_lvl = inv.equipped_relic.get("level", 0)
        r_data = EXCLUSIVE_RELICS.get(sp_key, {})
        if r_lvl >= 10:
            relic_block = (
                f"🎴 **{r_data['name']} +10** `[MAX 완전 종결]`\n"
                f"└ 👑 **[종결 특효 활성화]** 「{r_data['special_10']}」\n"
                f"└ ✨ _Nightmare/Mythic 레이드를 통해 보물 최종 완성을 달성했습니다!_"
            )
        elif r_lvl >= max_relic:
            relic_block = (
                f"🎴 **{r_data['name']} +{r_lvl}** `[성장 관문 상한 도달]`\n"
                f"⚠️ 현재 보물 강화 상한: **+{max_relic}**\n"
                f"📜 _(다음 난이도 레이드 보스를 올클리어하여 +{min(10, max_relic+2 if max_relic<8 else 10)} 상한을 해금하세요!)_"
            )
        else:
            relic_rates = {0: 100, 1: 100, 2: 100, 3: 90, 4: 80, 5: 70, 6: 60, 7: 50, 8: 35, 9: 20}
            r_rate = relic_rates.get(r_lvl, 20)
            req_st = (r_lvl + 1) * 2
            req_es = (r_lvl + 1)
            req_nc = 1 if r_lvl == 8 else (2 if r_lvl == 9 else 0)
            req_g = 25000 if r_lvl == 8 else (35000 if r_lvl == 9 else (r_lvl + 1) * 2500)
            
            nc_txt = f" · 🟣 악몽의결정 `{req_nc}개`" if req_nc > 0 else ""
            relic_block = (
                f"🎴 **{r_data['name']} +{r_lvl}** ➔ **+{r_lvl+1}** `(성공률: {r_rate}% | 상한: +{max_relic})`\n"
                f"• 필요 재료: 💎 강화석 `{req_st}개` · 🔮 보물정수 `{req_es}개`{nc_txt}\n"
                f"• 필요 골드: 💰 `{req_g:,}G`\n"
                f"• +10 특효: 「{r_data['special_10']}」"
            )
    else:
        relic_block = "`장착 중인 전용 보물이 없습니다. (던전 탐험에서 완제품 파밍/제작)`"
    embed.add_field(name="🎴 [종족 전용 보물] (성장 관문 상한 연동)", value=relic_block, inline=False)

    # 2. 🛡️ 방어구 현황 & 다음 강화/승급 정보
    if inv.equipped_armor:
        a_id = inv.equipped_armor["armor_id"]
        a_lvl = inv.equipped_armor.get("level", 0)
        a_stars = inv.equipped_armor.get("stars", 0)
        star_str = f" {'★' * a_stars}" if a_stars > 0 else ""
        a_data = ARMORS_DATABASE.get(a_id, {})
        max_enh = a_data.get("max_enhance", 15)
        promo_info = ARMOR_PROMOTION_TREE.get(a_id)
        
        if a_lvl < max_enh:
            a_rates = {
                0: 100, 1: 100, 2: 100, 3: 95, 4: 90, 5: 85,
                6: 75, 7: 65, 8: 55, 9: 45,
                10: 35, 11: 25, 12: 18, 13: 12, 14: 8
            }
            a_rate = a_rates.get(a_lvl, 8)
            req_st = 12 if a_lvl == 10 else (15 if a_lvl == 11 else (18 if a_lvl == 12 else (22 if a_lvl == 13 else (25 if a_lvl == 14 else a_lvl + 1))))
            req_es = 6 if a_lvl == 10 else (8 if a_lvl == 11 else (10 if a_lvl == 12 else (12 if a_lvl == 13 else (15 if a_lvl == 14 else max(1, (a_lvl + 1) // 2)))))
            req_nc = 1 if a_lvl == 10 else (2 if a_lvl == 11 else (3 if a_lvl == 12 else 0))
            req_mc = 2 if a_lvl == 13 else (4 if a_lvl == 14 else 0)
            req_g = 20000 if a_lvl == 10 else (25000 if a_lvl == 11 else (30000 if a_lvl == 12 else (40000 if a_lvl == 13 else (50000 if a_lvl == 14 else (a_lvl + 1) * 1500))))
            
            mat_txt = f"💎 강화석 `{req_st}개` · 🔮 정수 `{req_es}개`"
            if req_nc > 0: mat_txt += f" · 🟣 악몽의결정 `{req_nc}개`"
            if req_mc > 0: mat_txt += f" · 🟡 신화의핵 `{req_mc}개`"
            
            armor_block = (
                f"🛡️ **{a_data['name']} +{a_lvl}** ➔ **+{a_lvl+1}** `(성공률: {a_rate}% | 최대 +{max_enh})`\n"
                f"• 필요 재료: {mat_txt}\n"
                f"• 필요 골드: 💰 `{req_g:,}G`\n"
                f"• 스펙: ❤️ HP `+{a_data.get('base_hp', 0)}` | 🛡️ DEF `+{a_data.get('base_def', 0)}`"
            )
        elif a_data.get("is_mythic", False) and a_stars < 5:
            next_star = a_stars + 1
            star_gold = {0: 30000, 1: 50000, 2: 70000, 3: 90000, 4: 120000}
            req_g = star_gold.get(a_stars, 120000)
            bonus_pct = {1: 6, 2: 12, 3: 18, 4: 24, 5: 30}.get(next_star, 30)
            
            armor_block = (
                f"🛡️ **{a_data['name']} +15{star_str}** ➔ **★{next_star} 승급** `(100% 확정 승급!)`\n"
                f"• 필요 재료: 🌑 고대 보스 전용 핵 or 태고의 핵 `1개` (Ancient 보스 토벌 보상)\n"
                f"• 필요 골드: 💰 `{req_g:,}G`\n"
                f"• 승급 효과: 고대 스탯 보너스 **+{bonus_pct}%**" + (f" & 🌌 **「{a_data.get('ancient_passive', '')}」 해금!**" if next_star == 5 else "")
            )
        elif a_data.get("is_mythic", False) and a_stars >= 5:
            armor_block = (
                f"🛡️ **{a_data['name']} +15 ★★★★★** `[완전 종결 달성!]`\n"
                f"└ 🌌 **[고대 특효 활성화]** 「{a_data.get('ancient_passive', '')}」: _{a_data.get('ancient_desc', '')}_\n"
                f"└ ✨ _Ancient 레이드를 50회 이상 정복하고 최고위 고대 방어구를 완성했습니다!_"
            )
        else:
            armor_block = (
                f"🛡️ **{a_data['name']} +{a_lvl}** `[MAX 풀강 달성!]`\n"
                f"📜 _(상위 난이도 레이드 보스를 토벌하여 다음 단계의 신규 방어구를 획득하세요!)_"
            )
    else:
        armor_block = "`장착 중인 방어구가 없습니다. (레이드 최초 토벌 또는 던전 파밍으로 획득)`"
    embed.add_field(name="🛡️ [방어구] (던전 강화 & 레이드 독립 획득)", value=armor_block, inline=False)

    # 3. 📦 현재 보유 강화 & 레이드 핵심 재료 요약
    st_tot = inv.items.get("stone", 0) + inv.items.get("armor_stone", 0)
    es_tot = inv.items.get("relic_essence", 0)
    nc_tot = inv.items.get("nightmare_crystal", 0)
    mc_tot = inv.items.get("mythic_core", 0)
    ac_tot = inv.items.get("ancient_core", 0)
    
    mat_summary = (
        f"💎 **강화석:** `{st_tot}개` | 🔮 **보물의 정수:** `{es_tot}개`\n"
        f"🟣 **악몽의 결정:** `{nc_tot}개` | 🟡 **신화의 핵:** `{mc_tot}개` | 🌑 **태고의 핵:** `{ac_tot}개`"
    )
    embed.add_field(name="📦 보유 강화 & 레이드 핵심 재료", value=mat_summary, inline=False)

    embed.set_footer(text="하단 버튼을 클릭하여 원하는 장비의 강화 및 승급을 진행하세요!")
    return embed

def create_dungeon_select_embed(user: discord.User, pet: Pet) -> discord.Embed:
    """🗺️ 4대 테마 던전 선택 Embed (v15.3)"""
    max_e = getattr(pet, "max_energy", 100)
    cur_s = getattr(pet, "stamina", 100)
    st_b = create_bar(cur_s, max_e, 6)
    
    embed = discord.Embed(
        title="🗺️ [던전 탐험] 4대 테마 던전 선택",
        description=(
            f"🔥 **현재 보유 모험 기력:** `{st_b}` **{cur_s}/{max_e}%**\n"
            f"도전할 테마 던전을 선택하세요! 던전 선택 후 **[🟢일반 / 🟣정예 / 🔴심연]** 난이도를 지정할 수 있습니다."
        ),
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    for d_id, d_data in DUNGEON_DATABASE.items():
        req_norm = d_data["req_lvl"][1]
        embed.add_field(
            name=f"{d_data['emoji']} {d_data['name']} (기본 입장: Lv.{req_norm}+)",
            value=(
                f"• 테마 특성: `{d_data['theme']}` | 기본 기력: `{d_data['energy_cost']}%/회`\n"
                f"• 기본 보상: `💰 {d_data['base_gold']:,}G` · `✨ {d_data['base_exp']:,} EXP`\n"
                f"• 환경 기믹: _{d_data['env_desc'][1]}_"
            ),
            inline=False
        )

    embed.set_footer(text="하단 던전 버튼을 클릭하여 난이도 선택으로 진행하세요!")
    return embed

def create_dungeon_diff_select_embed(user: discord.User, pet: Pet, inv: Inventory, dungeon_id: int) -> discord.Embed:
    """🏰 테마 던전 난이도 선택 Embed (v15.3)"""
    b_stats = pet.get_battle_stats(inv)
    p_cp = b_stats.get('combat_power', 1000)
    d_data = DUNGEON_DATABASE.get(dungeon_id, DUNGEON_DATABASE[1])
    
    max_e = getattr(pet, "max_energy", 100)
    cur_s = getattr(pet, "stamina", 100)
    st_b = create_bar(cur_s, max_e, 6)

    embed = discord.Embed(
        title=f"🏰 [{d_data['emoji']} {d_data['name']}] 난이도 선택",
        description=(
            f"⚔️ **내 신수 전투력:** `👑 {p_cp:,}` (Lv.{pet.level})\n"
            f"🔥 **보유 모험 기력:** `{st_b}` **{cur_s}/{max_e}%**\n"
            f"🌐 **테마:** `{d_data['theme']}` | 선택 시 **5회 연속 자동 탐험** 후 일괄 정산됩니다!"
        ),
        color=discord.Color.teal(),
        timestamp=datetime.now()
    )

    for diff_id, diff_info in DUNGEON_DIFFICULTIES.items():
        req_l = d_data["req_lvl"].get(diff_id, 1)
        rec_cp = d_data["rec_cp"].get(diff_id, 5000)
        e_cost = int(d_data["energy_cost"] * diff_info["energy_mult"])
        judge, judge_desc = get_power_judgement(p_cp, rec_cp, is_ancient=(diff_id == 3))
        
        relic_txt = ""
        relic_r = d_data.get("relic_rate", {}).get(diff_id, 0.0)
        if relic_r > 0:
            relic_txt = f" | 🎴 **전용보물 ({int(relic_r*100)}%)**"

        embed.add_field(
            name=f"{diff_info['name']} (Lv.{req_l}+) | 🎯 권장: `{rec_cp:,}` ({judge})",
            value=(
                f"• 기력 소모: `회당 {e_cost}%` (5회: `{e_cost*5}%`) | ✨ 숨겨진 방: `{int(diff_info['hidden_rate']*100)}%`\n"
                f"• 보상: Gold ×{diff_info['gold_mult']}, EXP ×{diff_info['exp_mult']}, 재료 ×{diff_info['mat_mult']}{relic_txt}\n"
                f"• 환경 효과: _{d_data['env_desc'].get(diff_id, '')}_"
            ),
            inline=False
        )

    embed.set_footer(text="하단 난이도 버튼을 클릭하면 5회 연속 고속 탐험이 시작됩니다!")
    return embed

BOSS_IMAGE_MAP = {
    1: os.path.join(PROJECT_ROOT, "assets", "bosses", "ancient_ent.png"),
    2: os.path.join(PROJECT_ROOT, "assets", "bosses", "crystal_dragon.png"),
    3: os.path.join(PROJECT_ROOT, "assets", "bosses", "ifrit.png"),
    4: os.path.join(PROJECT_ROOT, "assets", "bosses", "nebula.png"),
    5: os.path.join(PROJECT_ROOT, "assets", "bosses", "omega.png"),
}

def resolve_boss_image(boss_id: int) -> tuple[str | None, str]:
    """👑 보스 ID에 따른 이미지 파일 경로 및 파일명 반환"""
    path = BOSS_IMAGE_MAP.get(boss_id)
    if path and os.path.exists(path):
        return path, os.path.basename(path)
    return None, "boss.png"

def create_raid_diff_select_embed(user: discord.User, pet: Pet, inv: Inventory) -> tuple[discord.Embed, discord.File | None]:
    """👑 5대 레이드 난이도 선택 Embed (v17.2 난이도 우선 구조)"""
    b_stats = pet.get_battle_stats(inv)
    p_cp = b_stats.get('combat_power', 1000)
    
    embed = discord.Embed(
        title="👑 [보스 레이드] 도전 난이도 선택",
        description=(
            f"⚔️ **{pet.name}의 전투력:** `👑 {p_cp:,}` | 🐾 **신수 레벨:** `Lv.{pet.level}`\n"
            f"도전할 레이드 난이도를 선택해 주세요! 난이도 선택 후 해당 난이도의 토벌 보스를 확인 및 지정할 수 있습니다."
        ),
        color=discord.Color.dark_red(),
        timestamp=datetime.now()
    )

    clears = getattr(pet, "raid_clears", {})

    diff_req_lvls = {1: 1, 2: 30, 3: 50, 4: 70, 5: 99}
    diff_boss_counts = {1: "4대 보스", 2: "4대 보스", 3: "4대 보스", 4: "4대 보스", 5: "5대 보스 (🪐오메가 포함)"}

    for d_id, d_info in RAID_DIFFICULTIES.items():
        req_l = diff_req_lvls.get(d_id, 1)
        b_cnt = diff_boss_counts.get(d_id, "4대 보스")
        inj_text = f"💀 치명상 {int(d_info.get('injury_rate', 0)*100)}%" if d_info.get('injury_rate', 0) > 0 else "안전 (치명상 0%)"
        
        # 클리어 수
        c_list = clears.get(str(d_id), clears.get(d_id, []))
        c_cnt = len(set(c_list))
        tot_b = 5 if d_id == 5 else 4
        c_badge = f"✅ `{c_cnt}/{tot_b}` 정복" if c_cnt > 0 else f"❌ `0/{tot_b}` 미정복"

        embed.add_field(
            name=f"{d_info['name']} (입장: Lv.{req_l}+) | {c_badge}",
            value=(
                f"• 대상: `{b_cnt}` | 보상 배율: EXP ×{d_info['exp_mult']}, Gold ×{d_info['gold_mult']}\n"
                f"• 위험도: {inj_text}"
            ),
            inline=False
        )

    col_path = os.path.join(PROJECT_ROOT, "assets", "promo", "bosses_collection.jpg")
    file_att = None
    if os.path.exists(col_path):
        file_att = discord.File(col_path, filename="bosses_collection.jpg")
        embed.set_image(url="attachment://bosses_collection.jpg")

    embed.set_footer(text="하단 난이도 버튼을 클릭하여 토벌 보스 선택으로 진행하세요!")
    return embed, file_att

def create_raid_boss_select_embed(user: discord.User, pet: Pet, inv: Inventory, diff_id: int) -> tuple[discord.Embed, discord.File | None]:
    """👑 난이도별 레이드 보스 선택 Embed (v17.2 난이도별 보스 스펙 & 오메가 고대 전용 제한)"""
    b_stats = pet.get_battle_stats(inv)
    p_cp = b_stats.get('combat_power', 1000)
    diff_info = RAID_DIFFICULTIES.get(diff_id, RAID_DIFFICULTIES[1])
    
    embed = discord.Embed(
        title=f"👑 [{diff_info['name']}] 토벌 대상 보스 선택",
        description=(
            f"⚔️ **내 신수 전투력:** `👑 {p_cp:,}` (Lv.{pet.level})\n"
            f"🎁 **보상 배율:** `EXP ×{diff_info['exp_mult']}` · `Gold ×{diff_info['gold_mult']}`\n"
            f"토벌할 보스를 선택하면 **실시간 턴제 보스 레이드**가 즉시 시작됩니다!"
        ),
        color=discord.Color.red() if diff_id < 5 else discord.Color.gold(),
        timestamp=datetime.now()
    )

    clears = getattr(pet, "raid_clears", {})
    c_list = clears.get(str(diff_id), clears.get(diff_id, []))

    for b_id, b_info in BOSS_DATABASE.items():
        if b_id == 5 and diff_id < 5:
            continue # 🪐 오메가는 Ancient(고대) 전용!
        
        rec_cp = get_recommended_cp(b_id, diff_id)
        judge, judge_desc = get_power_judgement(p_cp, rec_cp, is_ancient=(diff_id == 5))
        
        # 👑 v17.2 정밀 보스 스펙 데이터베이스 연동
        stat_data = BOSS_STAT_TABLE.get(diff_id, {}).get(b_id, {})
        cur_hp = stat_data.get("hp", int(b_info["base_hp"] * diff_info["hp_mult"]))
        cur_atk = stat_data.get("atk", int(b_info["base_atk"] * diff_info["atk_mult"]))
        cur_def = stat_data.get("def", int(b_info["base_def"] * diff_info["def_mult"]))
        cur_spd = stat_data.get("spd", int(b_info["base_spd"] * diff_info["spd_mult"]))
        cur_crit = stat_data.get("crit", 100)

        is_cleared = b_id in c_list
        clear_str = "✅ `토벌 완료`" if is_cleared else "❌ `미토벌`"

        embed.add_field(
            name=f"{b_info['emoji']} {b_info['name']} | 🎯 권장: `{rec_cp:,}` ({judge})",
            value=(
                f"• 보스 스펙: ❤️ `{cur_hp:,}` | ⚔️ `{cur_atk:,}` | 🛡️ `{cur_def:,}` | ⚡ `{cur_spd:,}` | 💥 `{cur_crit}`\n"
                f"• 특성: 「`{b_info['trait_name']}`」 | 판정: *{judge_desc}* | 정복: {clear_str}\n"
                f"• _{b_info['desc']}_"
            ),
            inline=False
        )

    col_path = os.path.join(PROJECT_ROOT, "assets", "promo", "bosses_collection.jpg")
    file_att = None
    if os.path.exists(col_path):
        file_att = discord.File(col_path, filename="bosses_collection.jpg")
        embed.set_image(url="attachment://bosses_collection.jpg")

    embed.set_footer(text="하단 보스 버튼을 클릭하면 실시간 레이드가 즉시 시작됩니다!")
    return embed, file_att

def create_reincarnate_select_embed(user: discord.User, pet: Pet, meta: dict) -> discord.Embed:
    """🥚 환생의 의식 선택 Embed (동일 혈통 계승 vs 새로운 운명의 알)"""
    cur_gen = getattr(pet, "generation", 1)
    next_gen = cur_gen + 1 if pet.level >= 99 else 1
    
    embed = discord.Embed(
        title="🥚 [환생의 의식] 세대 계승 방식 선택",
        description=(
            f"👑 **현재 신수:** {pet.emoji} **{pet.name}** ({pet.species_name} · 제{cur_gen}대)\n"
            f"🧬 **개체 잠재력 (5V):** `{pet.rank}` (총합 IV `{pet.total_iv}/500`)\n"
            f"✨ **다음 세대:** `제{next_gen}대 혈통 강림`\n\n"
            f"환생하여 부화시킬 알의 방식을 선택해 주세요!"
        ),
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    embed.add_field(
        name="🧬 [동일 혈통 계승] (동일 종족 유지)",
        value=(
            f"• 부모 신수와 **동일한 종족({pet.species_name})**으로 부화합니다.\n"
            f"• 부모의 높은 개체값(IV)을 50% 확률로 100% 온전하게 물려받습니다.\n"
            f"• 단일 종족 명문 가문 육성 및 랭크 극대화에 유리합니다!"
        ),
        inline=False
    )
    embed.add_field(
        name="🎲 [새로운 운명의 알] (랜덤 종족 가챠)",
        value=(
            f"• 10대 신수 중 **새로운 종족**이 랜덤하게 부화합니다.\n"
            f"• 1% 확률 🔴 **신화 바하무트** 및 3% 🌟 **극희귀 황금 변이** 출현 가능!\n"
            f"• 새로운 종족의 4단계 진화 일러스트와 도감을 수집할 수 있습니다!"
        ),
        inline=False
    )
    
def create_hall_of_fame_embed(user: discord.User, meta: dict) -> discord.Embed:
    """🏛️ 명예의 전당 (전사한 영웅 신수 영구 보관소) Embed (v15.6)"""
    hall = meta.get("hall_of_fame", [])
    
    embed = discord.Embed(
        title="🏛️ [명예의 전당] 영원히 기억될 전장의 영웅들",
        description=(
            f"👑 **{user.display_name}**님과 함께 전장을 누비다 산화한 위대한 신수들의 영구 기록입니다.\n"
            f"신수들의 숭고한 희생과 업적은 이곳에 영원히 보존됩니다.\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.dark_gold(),
        timestamp=datetime.now()
    )
    
    if not hall:
        embed.add_field(
            name="🕊️ 기록된 전사 영웅 없음",
            value="아직 전사한 신수가 없습니다. 모든 신수들이 건강하고 안전하게 성장하고 있습니다! ✨",
            inline=False
        )
    else:
        for idx, entry in enumerate(reversed(hall[-10:]), 1):
            shiny_tag = "🌟 " if entry.get("is_shiny") else ""
            embed.add_field(
                name=f"{idx}. {shiny_tag}「{entry.get('name')}」 ({entry.get('species')} · {entry.get('rank')})",
                value=(
                    f"• 최종 레벨: `Lv.{entry.get('level', 1)}` | 성격: `{entry.get('personality', '용맹함')}`\n"
                    f"• 잠재력 IV: `{entry.get('total_iv', 350)}/500` | 토벌 수: `👑 {entry.get('boss_kills', 0)}회`\n"
                    f"• 최후의 전투: `[{entry.get('death_boss', '보스')}]` ({entry.get('death_difficulty', '고대')} 난이도)\n"
                    f"• 전사 일시: `{entry.get('death_date', '기록 없음')}`"
                ),
                inline=False
            )
            
    embed.set_footer(text="상점에서 [불사의 성수]나 [태초의 심장]을 사용하여 현재 전사한 신수를 소생시킬 수 있습니다.")
    return embed

def create_achievements_embed(user: discord.User, pet: Pet, meta: dict) -> discord.Embed:
    """🏆 업적 대시보드 Embed (v15.8)"""
    claimed = meta.get("claimed_achievements", [])
    tot_ach = len(ACHIEVEMENTS_DATABASE)
    cleared_cnt = len(claimed)
    pct = int((cleared_cnt / max(1, tot_ach)) * 100)
    score = meta.get("achievement_score", 0)
    eq_title = meta.get("equipped_title", "미장착")
    
    embed = discord.Embed(
        title=f"🏆 [{user.display_name}]님의 업적 & 칭호 대시보드",
        description=(
            f"👑 **장착 중인 칭호:** 🏷️ **【{eq_title}】**\n"
            f"🌟 **업적 총점:** `🏆 {score:,} 점`\n"
            f"📊 **달성률:** `✅ {cleared_cnt} / {tot_ach} ({pct}%)`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    
    cat_names = {
        "grow": "🐣 육성 & 성장",
        "affection": "💖 애정도 유대",
        "lineage": "🧬 혈통 & 잠재력",
        "transcend": "🌟 만렙 초월",
        "battle": "⚔️ 전투 & 보스 토벌",
        "equip": "🎴 보물 & 방어구 성급",
        "raid": "🔴 고난도 레이드 정복",
        "zenith": "👑 최종 졸업 엔드게임"
    }
    
    for cat_key, cat_title in cat_names.items():
        cat_achs = [a for a in ACHIEVEMENTS_DATABASE if a.get("category") == cat_key]
        c_done = len([a for a in cat_achs if a["id"] in claimed])
        c_tot = len(cat_achs)
        
        sample_list = []
        for a in cat_achs[:3]:
            is_c = "✅" if a["id"] in claimed else "🔒"
            sample_list.append(f"{is_c} **{a['name']}** (+{a['points']}점 · 🏷️_{a['title']}_)")
            
        embed.add_field(
            name=f"{cat_title} ({c_done}/{c_tot})",
            value="\n".join(sample_list) if sample_list else "업적 준비 중",
            inline=False
        )
        
    embed.set_footer(text="하단 [🏷️ 칭호 목록 & 장착] 버튼을 눌러 획득한 칭호를 변경할 수 있습니다.")
    return embed

def create_titles_embed(user: discord.User, meta: dict) -> discord.Embed:
    """🏷️ 보유 칭호 목록 및 장착 선택 Embed (v15.8)"""
    titles = meta.get("unlocked_titles", [])
    eq_title = meta.get("equipped_title", "미장착")
    
    embed = discord.Embed(
        title=f"🏷️ [{user.display_name}]님의 칭호 보관함",
        description=(
            f"👑 **현재 장착 중인 칭호:** 🏷️ **【{eq_title}】**\n"
            f"📦 **보유한 칭호 수:** `{len(titles)}개`\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    if not titles:
        embed.add_field(
            name="🔒 보유 중인 칭호 없음",
            value="아직 획득한 칭호가 없습니다! 던전, 레이드, 육성 업적을 달성하여 명예로운 칭호를 획득해 보세요! ✨",
            inline=False
        )
    else:
        title_lines = []
        for t in titles:
            tag = "🌟 [장착중] " if t == eq_title else "• "
            title_lines.append(f"{tag}**【{t}】**")
        embed.add_field(name="📜 획득한 칭호 목록", value="\n".join(title_lines), inline=False)
        
    embed.set_footer(text="하단 칭호 선택 버튼으로 원하는 칭호를 선택하여 프로필에 장착할 수 있습니다.")
    return embed

# 📖 JENNY'S LEGEND DAMAGOCHI SIMULATOR V17.2 공식 플레이어 가이드북 데이터
GUIDE_CHAPTERS = {
    1: {
        "title": "🎮 1. 입문 & 핵심 게임 루프",
        "description": "다마고치 RPG의 시작과 핵심 육성 순환 사이클 안내",
        "fields": [
            ("📌 기본 슬래시 명령어", "• `/다마고치` : 내 신수 대시보드 메인 콘솔 열기\n• `/가이드` : v17.2 공식 가이드북 열람\n• `/확률표` : 10대 신수 소환 확률표 확인\n• `/이름변경 [새이름]` : 신수 닉네임 변경\n• `/개발자인증 7777` : 관리자 모드 잠금/해제", False),
            ("🔄 핵심 게임 루프 사이클", "```\n신수 탄생 ➔ 돌보기/애정도 ➔ 던전 파밍(재료) ➔ 방어구/보물 강화\n➔ 레이드 4종 정복(허가증) ➔ 혼 투자 잠재 성장 ➔ 상위 장비 승급\n➔ Lv.99 만렙 달성 ➔ Ancient & 오메가 도전 ➔ 고대신 갑옷 ★5 완성!\n```", False),
            ("💡 한 줄 핵심 요약", "> **\"던전에서 강화하고, 레이드에서 승급하며, Ancient에서 증명한다!\"**", False)
        ]
    },
    2: {
        "title": "🐾 2. 10대 신수 종족값 (BST) & 4대 스킬",
        "description": "바하무트(800 BST) 기준 20% 간극 압축 리마스터 & 고유 스킬셋",
        "fields": [
            ("📊 10대 신수 종족값 (BST)", "• 🐺 **늑대 (665 BST):** 125/135/115/150/140 (표준 기준선/초고속 연타)\n• 🐯 **호랑이 (670 BST):** 115/165/110/130/150 (순수 물리화력 1위)\n• 🦁 **사자 (670 BST):** 155/130/150/115/120 (체력·방어 밸런서)\n• 🐢 **현무 (670 BST):** 175/110/175/90/120 (철벽 방어·탱커 1위)\n• 🐉 **드래곤 (690 BST):** 135/160/130/125/140 (고화력 원소 폭격)\n• 🦅 **불사조 (690 BST):** 145/135/125/140/145 (무한 재생 & 1회 부활)\n• 🦊 **구미호 (690 BST):** 120/150/115/150/155 (치명타 1위 & 정기 흡혈)\n• 🪽 **그리핀 (690 BST):** 130/145/120/160/135 (스피드 1위 & 선공 연타)\n• 🦄 **기린 (740 BST):** 150/150/145/150/145 (전설 올라운더 버퍼)\n• 🐲 **바하무트 (800 BST):** 160/160/160/160/160 (신화 종결 킬러)", False),
            ("⚔️ 전투 4대 스킬 시스템", "• **기본기 1 & 2:** 노쿨타임 주력기 (연타/관통/흡혈/디버프)\n• **고유기 (3~4턴 쿨):** 버프, 무적 방어막, 스탯 흡수 등 특수기\n• **궁극기 (5턴 쿨):** 180%~300% 초극대 파멸 피해 & 고유 부가효과", False)
        ]
    },
    3: {
        "title": "🧬 3. 개체값(IV), 10대 성격 & 5대 속성",
        "description": "선천적 재능과 성격/속성 시너지 빌드",
        "fields": [
            ("🧬 5대 개체값 (IV: 0~100)", "• HP / ATK / DEF / SPD / CRIT 각각 0~100\n• `IV 0 = ×1.00` ➔ `IV 100 = ×1.30 (+30% 스탯 증폭)`\n• 500 IV 만점 달성 시 👑 **PERFECT** 등급!\n• ⚠️ *IV는 돈으로 올릴 수 없으며, 혈통 환생을 통해 계승·육성합니다.*", False),
            ("🎭 10대 성격 패시브", "• 🔥 **사나움:** ATK +12%, DEF -6% (극딜러)\n• 🛡️ **용맹함:** HP 50% 이하 시 ATK/DEF +10%\n• ⚡ **민첩함:** SPD +12%, HP -5% (선공 연타)\n• 🧱 **신중함:** DEF +12%, SPD -8% (탱커)\n• 🎯 **냉정함:** CRIT +8%, 치명피해 +10%\n• 🌌 **불굴:** 피격 시 20% 확률로 피해 50% 반감", False),
            ("🌈 5대 원소 속성", "• 🔥 **화염:** 치명타율 +20% + 방어 관통\n• 🛡️ **수호:** 받는 모든 피해 25% 감소\n• ⚡ **질풍:** SPD 비례 최대 40% 1턴 2연타\n• 🌑 **암흑:** 가한 피해의 20% HP 흡혈\n• 🌿 **대지:** 최대 HP +25% + 매 턴 3% 지속 재생", False)
        ]
    },
    4: {
        "title": "🌱 4. 레벨 제한, 혼 4종 & 잠재 성장",
        "description": "레이드 난이도별 혼 파밍을 통한 +0% ~ +60% 확정 잠재 각성",
        "fields": [
            ("📈 레이드 관문과 레벨캡 해제", "• ⚪ 노말 미정복 시 ➔ **Lv.34에서 성장 정지**\n• 🔵 하드 미정복 시 ➔ **Lv.54에서 성장 정지**\n• 🟣 악몽 미정복 시 ➔ **Lv.74에서 성장 정지**\n• 🟡 신화 미정복 시 ➔ **Lv.94에서 성장 정지**\n• 🔴 고대(Ancient) ➔ **Lv.99 만렙 진입**", False),
            ("🌱 혼 4종과 잠재 성장 구간 (+0% ➔ +60% MAX)", "• ⚪ **일반 혼 (Normal):** 1~5단계 (+0% ➔ +15%)\n• 🔵 **고급 혼 (Hard):** 6~10단계 (+15% ➔ +30%)\n• 🟣 **전설 혼 (Nightmare):** 11~15단계 (+30% ➔ +45%)\n• 🟡 **신화 혼 (Mythic):** 16~20단계 (+45% ➔ +60% MAX)\n• ⚠️ *하위 혼으로 상위 구간을 뚫을 수 없습니다.*", False),
            ("💎 소모 비용 공식 ($n^2$ 스텝)", "• 각 티어 1~5단계: `1개, 4개, 9개, 16개, 25개` (스탯당 55개)\n• 5대 스탯 1개 티어 풀각성 = **275개 혼** (총 1,100개 필요)", False)
        ]
    },
    5: {
        "title": "🛡️ 5. 4대 던전, 방어구 승급 & 종족 보물",
        "description": "파괴 없는 강화 & 승급 시 강화 수치 100% 보존",
        "fields": [
            ("🌲 4대 테마 던전 (재료 농장)", "• 🌲 **요정 숲:** 초반 골드/경험치 파밍\n• 💎 **수정 동굴:** 일반/방어구 강화석 파밍\n• 🔥 **마그마 화산:** 보물의 정수 & 중후반 재료\n• 🌌 **심연의 균열:** 악몽의 결정 & 고난도 종결 재료", False),
            ("🛡️ 방어구 승급 트리 (강화 수치 계승!)", "• 🟢 **가죽 갑옷 (+5 풀강)** ➔ 🔵 **수정 갑옷 (+5 계승!)**\n• 🔵 **수정 갑옷 (+8 풀강)** ➔ 🟣 **천계 갑주 (+8 계승!)**\n• 🟣 **천계 갑주 (+11 풀강)** ➔ 🟡 **고대신의 갑옷 (+11 계승!)**\n• 🟡 **고대신의 갑옷 (+15 풀강)** ➔ 🔴 **고대 성급 (★1 ~ ★5)**\n• ⚠️ *강화 실패 시에도 장비 파괴/하락 없음!*", False),
            ("🎴 종족 전용 보물 (+10강 종결)", "• 탄생 시 종족 고유 전용 보물 +0강 기본 지급!\n• 노말(+3), 하드(+5), 악몽(+8), 신화(+10) 상한 확장\n• +10강 달성 시 종족별 고유 킬러 패시브 개화!", False)
        ]
    },
    6: {
        "title": "⚔️ 6. 5대 레이드 보스 공략 & 방어 태세",
        "description": "8~15턴 공방 사투 밸런스 & 보스별 맞춤 전략",
        "fields": [
            ("🌳 고대 엔트 (내구·회복)", "• 「불멸의 뿌리」 매 턴 체력 지속 회복\n• 공략: 강력한 단일 폭딜 및 방어 관통으로 회복량 상회 DPT 유지", False),
            ("💎 크리스탈 드래곤 (방어·반사)", "• 「절대 반사」 가한 피해의 일부를 플레이어에게 반사\n• 공략: 흡혈/회복 수단 확보 및 무작정 큰 한방 남발 자제", False),
            ("🔥 이프리트 (DPS 타임어택)", "• 「업화 누적」 매 턴 공격력 영구 광폭화 누적\n• 공략: 7턴 이내에 극딜·치명타로 빠르게 승부 (장기전 절대 불리)", False),
            ("☄️ 성운 가디언 (속도·시간 지배)", "• 「시간 지배」 플레이어 스탯 강탈 및 잃은 체력 시간 역행\n• 공략: 높은 SPD 확보, 상태이상 저항, 연속 폭딜", False),
            ("🛡️ 방어 태세 시스템", "• 보스가 필살기 준비 경고를 띄울 때 **[🛡️ 방어]** 선택!\n• 받는 최종 피해 -50% & 상태이상 저항 +20%로 생존 도모", False)
        ]
    },
    7: {
        "title": "🌌 7. Ancient 엔드게임, 오메가 & 고대신 ★5",
        "description": "풀강도 안심할 수 없는 최고난도 사투 & TRUE CLEAR",
        "fields": [
            ("🔴 Ancient 5대 보스 실제 체급", "• 🌳 **고대 엔트:** HP 6.6만 ~ 14만 (지속 각성 회복)\n• 💎 **고대 수정용:** HP 17만 / DEF 1,800 (절대 반사)\n• 🔥 **고대 이프리트:** HP 11만 / ATK 5,200 (초극딜 살인마)\n• ☄️ **고대 가디언:** HP 19만 / SPD 1,900 (스탯 25% 강탈)\n• 🪐 **오메가:** **HP 300,000 ~ 360,000** (방어력 50% 분쇄 관통)", False),
            ("🪐 오메가 4페이즈 & TRUE CLEAR", "• P1(10만) ➔ P2(9만) ➔ P3(9만) ➔ P4(8만)\n• ⚠️ P4 격파 후 **5턴 처형전 「죽지 않는 영광」** 돌입!\n• 5턴 내 격파 실패 시 **[Ω · 절대종언]** 강제 패배!", False),
            ("🌟 고대신의 갑옷 ★1 ~ ★5 확정 승급", "• 고대 보스 10회 토벌 시 전용 핵 확정 드랍 ➔ 100% 확정 승급!\n• ★당 전 스탯 +5% (★5 시 전 스탯 +30% & 최종 피해 -30%)", False)
        ]
    },
    8: {
        "title": "🗺️ 8. 초보자 추천 성장 루트 & FAQ",
        "description": "Lv.1부터 Lv.99 엔드게임까지의 로드맵 및 30초 요약",
        "fields": [
            ("🗺️ 추천 성장 로드맵", "1. **Lv.1~29:** 요정숲/수정동굴 ➔ 가죽+5 ➔ 노말 4종 정복 ➔ 일반혼 잠재 15% ➔ 보물+3\n2. **Lv.30~49:** 수정+8 ➔ 하드 4종 정복 ➔ 고급혼 잠재 30% ➔ 보물+5\n3. **Lv.50~69:** 천계+11 ➔ 악몽 4종 정복 ➔ 전설혼 잠재 45% ➔ 보물+8\n4. **Lv.70~99:** 고대신+15 ➔ 신화 4종 정복 ➔ 신화혼 잠재 60% ➔ 보물+10 ➔ Lv.99\n5. **Ancient:** 고대 4보스 각 10회 ➔ 고대신 ★4 ➔ 오메가 TRUE CLEAR ➔ 고대신 ★5 완성!", False),
            ("❓ 자주 묻는 질문 (FAQ)", "• Q. 사망하면 신수가 죽나요? ➔ A. **아닙니다!** 사망 폐지, 치명상(HP 10%) 시 병원 치료로 완치됩니다.\n• Q. 방어구 승급하면 강화 날아가나요? ➔ A. **100% 계승됩니다.**\n• Q. 오메가는 노말에 없나요? ➔ A. **오직 고대(Ancient)에만 존재합니다.**\n• Q. IV는 돈으로 올리나요? ➔ A. **환생 혈통 계승으로만 올릴 수 있습니다.**", False)
        ]
    }
}

def create_guide_embed(page_idx: int = 1) -> discord.Embed:
    """📖 v17.2 공식 플레이어 가이드북 Embed (총 8개 챕터 인터랙티브 페이징)"""
    page_idx = max(1, min(len(GUIDE_CHAPTERS), page_idx))
    chap = GUIDE_CHAPTERS[page_idx]
    
    embed = discord.Embed(
        title=f"📖 [공식 가이드북 v17.2] {chap['title']}",
        description=f"_{chap['description']}_\n━━━━━━━━━━━━━━━━━━━━",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    for f_name, f_val, inline in chap["fields"]:
        embed.add_field(name=f_name, value=f_val, inline=inline)
        
    embed.set_footer(text=f"신수키우기 v17.2 공식 가이드북 · 페이지 ({page_idx}/{len(GUIDE_CHAPTERS)}) | 하단 메뉴로 챕터 이동")
    return embed

class GuideView(discord.ui.View):
    """📖 독립형 가이드북 전용 인터랙티브 뷰 (슬래시 커맨드 /가이드 전용)"""
    def __init__(self, user: discord.User, page_idx: int = 1):
        super().__init__(timeout=300)
        self.user = user
        self.page_idx = page_idx
        self.rebuild_components()

    def rebuild_components(self):
        self.clear_items()
        
        # 1. 챕터 선택 드롭다운
        options = []
        for p_num, c_data in GUIDE_CHAPTERS.items():
            options.append(discord.SelectOption(
                label=f"{p_num}장. {c_data['title'].split('. ')[-1]}",
                value=str(p_num),
                description=c_data['description'][:50],
                default=(p_num == self.page_idx)
            ))
            
        select = discord.ui.Select(placeholder="📖 읽고 싶은 챕터를 선택하세요...", options=options, custom_id="guide_select_chap", row=0)
        select.callback = self.on_select_chapter
        self.add_item(select)
        
        # 2. 이전/다음 버튼
        btn_prev = discord.ui.Button(label="◀ 이전 챕터", style=discord.ButtonStyle.secondary, disabled=(self.page_idx <= 1), row=1)
        btn_prev.callback = self.on_prev_click
        self.add_item(btn_prev)
        
        btn_next = discord.ui.Button(label="다음 챕터 ▶", style=discord.ButtonStyle.primary, disabled=(self.page_idx >= len(GUIDE_CHAPTERS)), row=1)
        btn_next.callback = self.on_next_click
        self.add_item(btn_next)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("💡 본인이 호출한 가이드북 화면만 조작할 수 있습니다!", ephemeral=True)
            return False
        return True

    async def on_select_chapter(self, interaction: discord.Interaction):
        select = [item for item in self.children if isinstance(item, discord.ui.Select)][0]
        self.page_idx = int(select.values[0])
        self.rebuild_components()
        embed = create_guide_embed(self.page_idx)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_prev_click(self, interaction: discord.Interaction):
        self.page_idx = max(1, self.page_idx - 1)
        self.rebuild_components()
        embed = create_guide_embed(self.page_idx)
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_next_click(self, interaction: discord.Interaction):
        self.page_idx = min(len(GUIDE_CHAPTERS), self.page_idx + 1)
        self.rebuild_components()
        embed = create_guide_embed(self.page_idx)
        await interaction.response.edit_message(embed=embed, view=self)

# ⚔️ 하이브리드 실시간 턴제 배틀 뷰 & 스레드 룸 엔진 (v15.0 보스 스킬/패턴/Ancient 페이즈 연동)
class HybridBattleSession:
    def __init__(self, user: discord.User, pet: Pet, inv: Inventory, boss_id: int, diff_id: int):
        self.user = user
        self.pet = pet
        self.inv = inv
        self.boss_id = boss_id
        self.diff_id = diff_id
        
        self.boss_base = BOSS_DATABASE.get(boss_id, BOSS_DATABASE[1])
        self.diff_info = RAID_DIFFICULTIES.get(diff_id, RAID_DIFFICULTIES[1])
        self.b_skills = BOSS_SKILLS_DATABASE.get(boss_id, BOSS_SKILLS_DATABASE[1])
        
        # 👑 v17.2 정밀 보스 스탯 테이블 (Ground Truth)
        stat_data = BOSS_STAT_TABLE.get(diff_id, {}).get(boss_id, {})
        if stat_data:
            self.b_max_hp = stat_data["hp"]
            self.b_hp = self.b_max_hp
            self.b_atk = stat_data["atk"]
            self.b_def = stat_data["def"]
            self.b_spd = stat_data["spd"]
            self.b_crit = stat_data.get("crit", 100)
        else:
            self.b_max_hp = int(self.boss_base["base_hp"] * self.diff_info["hp_mult"])
            self.b_hp = self.b_max_hp
            self.b_atk = int(self.boss_base["base_atk"] * self.diff_info["atk_mult"])
            self.b_def = int(self.boss_base["base_def"] * self.diff_info["def_mult"])
            self.b_spd = int(self.boss_base["base_spd"] * self.diff_info["spd_mult"])
            self.b_crit = 100
        
        b_stats = pet.get_battle_stats(inv)
        self.p_max_hp = b_stats["max_hp"]
        self.p_hp = max(10, int(self.p_max_hp * (self.pet.health / 100.0))) # 시작 시 건강% 반영
        self.base_p_atk = b_stats["atk"]
        self.base_p_def = b_stats["def"]
        self.p_spd = b_stats["spd"]
        self.p_crit = b_stats["crit"]
        self.p_cp = b_stats.get("combat_power", 1000)
        self.rec_cp = get_recommended_cp(self.boss_id, self.diff_id)
        self.cp_penalty = calc_cp_deficit_penalty(self.p_cp, self.rec_cp, self.diff_id)
        self.p_trait = b_stats.get("personality_trait", "none")
        self.effect = b_stats.get("effect", "atk_boost")
        self.relic_is_10 = b_stats.get("relic_is_10", False)
        self.armor_dmg_red = b_stats.get("armor_dmg_red", 0.0)
        self.armor_burn_red = b_stats.get("burn_dmg_red", 0.0)
        self.armor_regen_hp = b_stats.get("regen_hp_pct", 0.0)
        self.armor_heal_bonus = b_stats.get("heal_bonus", 0.0)
        self.armor_first_hit = b_stats.get("first_hit_bonus", 0.0)
        self.armor_low_hp_red = b_stats.get("low_hp_dmg_red", 0.0)
        
        self.sp_key = getattr(pet, "species_key", "호랑이")
        self.skills = SPECIES_SKILLS.get(self.sp_key, SPECIES_SKILLS["호랑이"])
        
        if self.sp_key == "기린":
            self.p_max_hp = int(self.p_max_hp * 1.03)
            self.p_hp = max(10, int(self.p_max_hp * (self.pet.health / 100.0)))
            self.base_p_atk = int(self.base_p_atk * 1.03)
            self.base_p_def = int(self.base_p_def * 1.03)
            self.p_spd = int(self.p_spd * 1.03)

        self.turn = 0
        self.is_finished = False
        self.cd_unique = 0
        self.cd_ultimate = 0
        self.buff_atk_turns = 0; self.buff_atk_val = 0.0
        self.buff_def_turns = 0; self.buff_def_val = 0.0
        self.is_defending = False
        
        # 👑 보스 스킬 및 상태 제어 변수 (v15.0)
        self.b_cd_a = 0
        self.b_cd_b = 0
        self.b_ult_used = False
        self.b_warning = "" 
        self.b_buff_atk = 0.0
        self.b_buff_def = 0.0
        self.b_buff_spd = 0.0
        self.b_buff_turns = 0
        self.b_regen_turns = 0
        self.b_regen_val = 0.0
        self.b_barrier_turns = 0
        self.b_mirror_next_hit = False
        self.b_mirror_ratio = 0.0
        self.player_stunned = False 
        self.player_burn_turns = 0 
        self.player_debuff_atk = 0.0
        self.player_debuff_def = 0.0
        self.player_debuff_spd = 0.0
        self.player_debuff_turns = 0
        self.hellfire_stacks = 0
        self.last_turn_hp_lost = 0
        
        self.omega_phase = 1
        self.omega_p2_done = False
        self.omega_p3_done = False
        
        self.revived = False
        self.phoenix_survived = False
        self.phoenix_healed = False
        self.pet_revived = False
        self.first_hit_done = False
        self.hp70_done = False
        self.hp30_done = False
        self.hp10_done = False
        self.dialogue_quote = get_boss_dialogue(self.boss_id, "start")
        self.pet_dialogue_quote = get_pet_battle_quote(self.pet, self.p_hp, self.p_max_hp)

    def get_battle_embed(self, log_msg: str = "") -> tuple[discord.Embed, list[discord.File]]:
        b_bar = create_bar(self.b_hp, self.b_max_hp, length=12)
        p_bar = create_bar(self.p_hp, self.p_max_hp, length=12)
        
        rec_cp = get_recommended_cp(self.boss_id, self.diff_id)
        is_anc = (self.diff_id == 5)
        judge_tag, _ = get_power_judgement(self.p_cp, rec_cp, is_ancient=is_anc)
        
        boss_title = f"{self.diff_info['name']} · {self.boss_base['title_ancient'] if is_anc else self.boss_base['name']}"
        
        desc_lines = []
        if self.b_warning:
            desc_lines.append(f"⚠️ **[전조 예고]** {self.b_warning}\n")
        desc_lines.extend([
            f"⚔️ **내 전투력:** `{self.p_cp:,}` vs 🎯 **권장:** `{rec_cp:,}` ({judge_tag})",
            f"🔮 **고유 특성:** `「{self.boss_base['trait_name']}」` | 턴: **{self.turn}턴**"
        ])
        if self.cp_penalty.get("has_penalty", False):
            desc_lines.append(f"⚠️ **[{self.cp_penalty['name']}]** `{self.cp_penalty['desc']}` ({self.cp_penalty['ratio_pct']}% 수준)")
        
        embed = discord.Embed(
            title=f"⚔️ [실시간 보스전] {boss_title}",
            description="\n".join(desc_lines),
            color=discord.Color.dark_red() if self.b_warning else (discord.Color.red() if self.b_hp > 0 else discord.Color.green()),
            timestamp=datetime.now()
        )

        boss_status_tags = []
        if self.hellfire_stacks > 0: boss_status_tags.append(f"🔥 업화 x{self.hellfire_stacks}")
        if self.b_barrier_turns > 0: boss_status_tags.append("🛡️ 결정 장벽")
        if getattr(self, "b_mirror_hits_left", 0) > 0 or self.b_mirror_next_hit: boss_status_tags.append("🪞 천경반사(대기)")
        if self.b_regen_turns > 0: boss_status_tags.append("🌱 태고의 재생")
        if self.b_buff_atk > 0: boss_status_tags.append(f"⚔️ ATK +{int(self.b_buff_atk*100)}%")
        b_status_str = f" | 상태: `{' '.join(boss_status_tags)}`" if boss_status_tags else ""

        cur_b_atk = int(self.b_atk * (1.0 + self.b_buff_atk))
        cur_b_def = int(self.b_def * (1.0 + self.b_buff_def))
        cur_b_spd = int(self.b_spd * (1.0 + self.b_buff_spd))

        embed.add_field(
            name=f"👑 {self.boss_base['name']}{b_status_str}",
            value=(
                f"💬 _{self.dialogue_quote}_\n"
                f"❤️ HP `{b_bar}` {self.b_hp:,} / {self.b_max_hp:,}\n"
                f"⚔️ ATK `{cur_b_atk:,}` | 🛡️ DEF `{cur_b_def:,}` | ⚡ SPD `{cur_b_spd}`"
            ),
            inline=False
        )

        cd_u_str = " (사용 가능)" if self.cd_unique == 0 else f" (쿨타임 {self.cd_unique}턴)"
        cd_ult_str = " (사용 가능)" if self.cd_ultimate == 0 else f" (쿨타임 {self.cd_ultimate}턴)"

        player_status_tags = []
        if self.cp_penalty.get("has_penalty", False): player_status_tags.append(self.cp_penalty["name"])
        if self.player_stunned: player_status_tags.append("⏳ 시간 정지(봉인)")
        if self.player_burn_turns > 0: player_status_tags.append("🔥 화상")
        if self.player_debuff_atk > 0: player_status_tags.append(f"📉 ATK -{int(self.player_debuff_atk*100)}%")
        if self.player_debuff_def > 0: player_status_tags.append(f"📉 DEF -{int(self.player_debuff_def*100)}%")
        if self.is_defending: player_status_tags.append("🛡️ 방어 태세(-40%)")
        p_status_str = f" | 상태: `{' '.join(player_status_tags)}`" if player_status_tags else ""

        cur_p_atk = int(self.base_p_atk * (1.0 + self.buff_atk_val - self.player_debuff_atk))
        cur_p_def = int(self.base_p_def * (1.0 + self.buff_def_val - self.player_debuff_def))
        cur_p_spd = int(self.p_spd * (1.0 - self.player_debuff_spd))

        embed.add_field(
            name=f"🐾 {self.pet.name} ({self.user.display_name}){p_status_str}",
            value=(
                f"💬 _{self.pet_dialogue_quote}_\n"
                f"❤️ HP `{p_bar}` {self.p_hp:,} / {self.p_max_hp:,}\n"
                f"⚔️ ATK `{cur_p_atk:,}` | 🛡️ DEF `{cur_p_def:,}` | ⚡ SPD `{cur_p_spd}`\n"
                f"✨ **고유기:** `{self.skills['unique']['name']}`{cd_u_str}\n"
                f"👑 **궁극기:** `{self.skills['ultimate']['name']}`{cd_ult_str}"
            ),
            inline=False
        )

        files_att = []
        
        # 1. 🖼️ 보스 대형 와이드 메인 이미지 (set_image)
        b_img_path, b_img_file = resolve_boss_image(self.boss_id)
        if b_img_path and os.path.exists(b_img_path):
            files_att.append(discord.File(b_img_path, filename=b_img_file))
            embed.set_image(url=f"attachment://{b_img_file}")
            
        # 2. 🐾 플레이어 신수 우측 상단 썸네일 이미지 (set_thumbnail)
        p_img_path, p_img_file = resolve_pet_image(self.sp_key, self.pet.level)
        if p_img_path and os.path.exists(p_img_path):
            files_att.append(discord.File(p_img_path, filename=p_img_file))
            embed.set_thumbnail(url=f"attachment://{p_img_file}")

        if log_msg:
            embed.add_field(name="📜 실시간 전투 로그", value=log_msg, inline=False)

        embed.set_footer(text="버튼을 눌러 실시간 스킬을 지시하세요! ⚠️ 예고 패턴 시 [🛡️ 방어] 적극 추천!")
        return embed, files_att

    def process_turn(self, action: str) -> tuple[bool, str]:
        self.turn += 1
        logs = []
        old_b_hp = self.b_hp
        
        if self.turn == 1 and self.cp_penalty.get("has_penalty", False):
            logs.append(f"⚠️ **[{self.cp_penalty['name']}]** 현재 전투력이 권장치의 {self.cp_penalty['ratio_pct']}% 수준입니다. ({self.cp_penalty['desc']})")
        
        if self.buff_atk_turns > 0: self.buff_atk_turns -= 1
        else: self.buff_atk_val = 0.0
        if self.buff_def_turns > 0: self.buff_def_turns -= 1
        else: self.buff_def_val = 0.0
        if self.cd_unique > 0: self.cd_unique -= 1
        if self.cd_ultimate > 0: self.cd_ultimate -= 1
        
        if self.b_cd_a > 0: self.b_cd_a -= 1
        if self.b_cd_b > 0: self.b_cd_b -= 1
        if self.b_barrier_turns > 0: self.b_barrier_turns -= 1
        if self.b_buff_turns > 0: self.b_buff_turns -= 1
        else: self.b_buff_atk = 0.0; self.b_buff_def = 0.0; self.b_buff_spd = 0.0
        
        if self.player_debuff_turns > 0: self.player_debuff_turns -= 1
        else: self.player_debuff_atk = 0.0; self.player_debuff_def = 0.0; self.player_debuff_spd = 0.0

        if self.b_regen_turns > 0 and self.b_hp > 0:
            self.b_regen_turns -= 1
            regen_amt = int(self.b_max_hp * self.b_regen_val)
            self.b_hp = min(self.b_max_hp, self.b_hp + regen_amt)
            logs.append(f"🌱 **[태고의 재생]** {self.boss_base['name']}의 체력이 **+{regen_amt:,}** 회복되었습니다!")

        if self.boss_id == 1 and self.diff_id == 5 and (self.b_hp / max(1, self.b_max_hp)) <= 0.20 and self.b_hp > 0:
            anc_regen = int(self.b_max_hp * 0.03)
            self.b_hp = min(self.b_max_hp, self.b_hp + anc_regen)
            logs.append(f"🌳✨ **[대지의 심장]** 고대 엔트가 매 턴 체력을 **+{anc_regen:,} (3%)** 지속 회복합니다!")

        if self.boss_id == 3 and self.b_hp > 0:
            max_s = self.b_skills.get("trait", {}).get("max_stack_map", {}).get(self.diff_id, 8)
            add_s = 2 if (self.diff_id == 5 and (self.b_hp / max(1, self.b_max_hp)) <= 0.20) else 1
            self.hellfire_stacks = min(max_s, self.hellfire_stacks + add_s)

        if self.armor_regen_hp > 0 and self.p_hp > 0:
            regen_val = max(1, int(self.p_max_hp * self.armor_regen_hp))
            self.p_hp = min(self.p_max_hp, self.p_hp + regen_val)
            logs.append(f"❤️🌱 **[생명의 성의]** 매 턴 지속 재생으로 HP **+{regen_val:,}**를 회복했습니다!")

        if self.player_burn_turns > 0 and self.p_hp > 0:
            self.player_burn_turns -= 1
            burn_mult = 1.0 - self.armor_burn_red if self.armor_burn_red > 0 else 1.0
            b_dot = max(10, int(self.p_max_hp * 0.04 * burn_mult))
            self.p_hp = max(0, self.p_hp - b_dot)
            burn_tag = " (용신의 갑주 화상 방어)" if self.armor_burn_red > 0 else ""
            logs.append(f"🔥 [화상 지속 피해] 신수가 **{b_dot:,} 화염 피해**를 입었습니다!{burn_tag} (남은 HP: {self.p_hp:,})")

        cur_atk = int(self.base_p_atk * (1.0 + self.buff_atk_val - self.player_debuff_atk))
        lion_def_bonus = 0.10 if (self.sp_key == "사자" and (self.p_hp / max(1, self.p_max_hp)) <= 0.50) else 0.0
        cur_def = int(self.base_p_def * (1.0 + self.buff_def_val - self.player_debuff_def + lion_def_bonus))

        skill_info = None
        if self.player_stunned:
            self.player_stunned = False
            logs.append(f"⏳ **[시간 정지!]** 시간이 정지되어 이번 턴 행동할 수 없었습니다!")
        elif action == "basic1":
            skill_info = self.skills["basic1"]
        elif action == "basic2":
            skill_info = self.skills["basic2"]
        elif action == "unique":
            if self.cd_unique > 0:
                skill_info = self.skills["basic1"]
                logs.append(f"⚠️ 고유기 쿨타임 중! 기본기로 대체합니다.")
            else:
                skill_info = self.skills["unique"]
                self.cd_unique = skill_info["cooldown"]
        elif action == "ultimate":
            if self.cd_ultimate > 0:
                skill_info = self.skills["basic1"]
                logs.append(f"⚠️ 궁극기 쿨타임 중! 기본기로 대체합니다.")
            else:
                skill_info = self.skills["ultimate"]
                self.cd_ultimate = skill_info["cooldown"]
        elif action == "defend":
            self.is_defending = True
            logs.append(f"🛡️ **{self.pet.name}**이(가) 방어 태세를 취했습니다! (이번 턴 받는 피해 -40% & 궁극 패턴 완충)")

        if skill_info and self.p_hp > 0:
            ratio = skill_info.get("atk_ratio", 1.0)
            if self.armor_first_hit > 0 and self.turn == 1 and self.p_spd > self.b_spd:
                ratio *= (1.0 + self.armor_first_hit)
                logs.append("🌪️⚡ **[천풍의 경갑]** 선공 첫 타 피해가 +7% 증폭되었습니다!")
            hits = skill_info.get("hits", 1)
            crit_bonus = skill_info.get("crit_bonus", 0.0)
            base_crit_rate = self.p_crit / (self.p_crit + 900.0)
            crit_rate = min(0.70, base_crit_rate + crit_bonus + (0.15 if self.effect == 'crit' else 0.0))
            
            if self.sp_key == "호랑이" and (self.p_hp / max(1, self.p_max_hp)) >= 0.70:
                ratio *= 1.06
            elif self.sp_key == "사자" and (self.p_hp / max(1, self.p_max_hp)) <= 0.50:
                ratio *= 1.10  # 왕의 위엄: 방어 관통 +10%
            elif self.sp_key == "늑대" and self.p_spd > self.b_spd:
                ratio *= 1.06
            elif self.sp_key == "드래곤" and (self.p_hp / max(1, self.p_max_hp)) <= 0.40:
                ratio *= 1.08
            elif self.sp_key == "바하무트":
                ratio *= 1.08
            
            total_dmg = 0
            had_crit = False
            for _ in range(hits):
                is_crit = random.random() < crit_rate
                if is_crit: had_crit = True
                c_mult = 2.2 if (is_crit and self.p_trait == "calm_crit") else (2.0 if is_crit else 1.0)
                hit_dmg = max(10, int((cur_atk * ratio / hits) * random.uniform(0.95, 1.15) * c_mult))
                
                # ⚠️ v15.10 피해 감소 & CP 미달 페널티 (상한선 최대 -60% 캡)
                cp_pen = self.cp_penalty.get("dmg_penalty", 0.0)
                add_red = 0.0
                if self.boss_id == 1 and hit_dmg < (self.b_max_hp * 0.02):
                    add_red += 0.30
                elif self.boss_id == 5 and self.diff_id >= 4:
                    if cur_atk < (self.b_def * 0.60): hit_dmg = 0
                    elif cur_atk < (self.b_def * 0.80): add_red += 0.50

                if hit_dmg > 0:
                    tot_red = min(0.60, cp_pen + add_red)
                    hit_dmg = int(hit_dmg * (1.0 - tot_red))

                if self.b_barrier_turns > 0 and hit_dmg > 0:
                    hit_dmg = int(hit_dmg * 0.75)

                total_dmg += hit_dmg

            if getattr(self, "b_mirror_hits_left", 0) > 0 and total_dmg > 0:
                cur_ref_ratio = self.b_mirror_ratio if self.b_mirror_hits_left == 2 else (self.b_mirror_ratio * 0.70)
                self.b_mirror_hits_left -= 1
                mirror_dmg = int(total_dmg * cur_ref_ratio * (1.0 - self.armor_dmg_red))
                self.p_hp = max(0, self.p_hp - mirror_dmg)
                logs.append(f"🪞💥 **[천경반사 발동!!]** 거대한 거울이 {self.pet.name}의 공격을 반사하여 **{mirror_dmg:,} 반사 피해({int(cur_ref_ratio*100)}%)**를 입혔습니다!")
                total_dmg = 0 
            elif self.b_mirror_next_hit and total_dmg > 0:
                self.b_mirror_next_hit = False
                mirror_dmg = int(total_dmg * self.b_mirror_ratio * (1.0 - self.armor_dmg_red))
                self.p_hp = max(0, self.p_hp - mirror_dmg)
                logs.append(f"🪞💥 **[천경반사 발동!!]** 거대한 거울이 {self.pet.name}의 공격을 통째로 반사하여 **{mirror_dmg:,} 반사 피해**를 입혔습니다!")
                total_dmg = 0 

            if total_dmg > 0:
                self.b_hp = max(0, self.b_hp - total_dmg)
                crit_tag = " 💥 **CRITICAL!!**" if had_crit else ""
                logs.append(f"⚔️ **{self.pet.name}**의 「{skill_info['name']}」! **{total_dmg:,} 피해** 작렬!{crit_tag}")

                if self.sp_key == "구미호":
                    ls_rate = 0.08 if self.relic_is_10 else 0.05
                    heal_amt = max(1, int(total_dmg * ls_rate))
                    if self.cp_penalty.get("heal_penalty", 0.0) > 0:
                        heal_amt = max(1, int(heal_amt * (1.0 - self.cp_penalty["heal_penalty"])))
                    self.p_hp = min(self.p_max_hp, self.p_hp + heal_amt)
                    logs.append(f"🦊✨ **[정기흡수]** 입힌 피해의 {int(ls_rate*100)}%인 **+{heal_amt:,} HP**를 흡혈 회복했습니다! (현재 HP: {self.p_hp:,})")

                if not self.first_hit_done:
                    self.first_hit_done = True
                    q = get_boss_dialogue(self.boss_id, "first_hit")
                    if q: self.dialogue_quote = q; logs.append(f"💬 **[{self.boss_base['name']}]** _{q}_")
                elif had_crit:
                    q = get_boss_dialogue(self.boss_id, "player_crit")
                    if q: self.dialogue_quote = q; logs.append(f"💬 **[{self.boss_base['name']}]** _{q}_")

                if self.boss_id == 2:
                    ref_map = self.b_skills.get("trait", {}).get("reflect_map", {1: 0.05, 5: 0.15})
                    base_ref = ref_map.get(self.diff_id, 0.08)
                    if self.diff_id == 5 and (self.b_hp / max(1, self.b_max_hp)) <= 0.30:
                        base_ref += 0.05 
                    if self.b_barrier_turns > 0:
                        base_ref += 0.20
                    
                    ref_dmg = int(total_dmg * base_ref * (1.0 - self.armor_dmg_red))
                    self.p_hp = max(0, self.p_hp - ref_dmg)
                    logs.append(f"💎 [절대 반사] 보스로부터 **{ref_dmg:,} 반사 피해**를 입었습니다!")

        self.last_turn_hp_lost = max(0, old_b_hp - self.b_hp)

        if self.b_hp <= 0:
            if self.diff_id >= 4 and not self.revived and self.boss_id in [1, 3, 5]:
                self.revived = True
                self.b_hp = int(self.b_max_hp * (1.0 if self.boss_id == 5 else 0.5))
                logs.append(f"🌟🌟🌟 **[{self.boss_base['name']} 신화/고대 부활 각성!]** 🌟🌟🌟")
            else:
                self.is_finished = True
                q_def = get_boss_dialogue(self.boss_id, "defeat")
                if q_def: self.dialogue_quote = q_def; logs.append(f"💬 **[{self.boss_base['name']}]** _{q_def}_")
                logs.append(f"\n🏆 **[{self.boss_base['name']}] 완벽 토벌 성공!!**")
                return True, "\n".join(logs)

        # 👑 v15.7 Ancient 전용 보스별 특수 기믹 & 오메가 4개 페이즈 전환
        if self.diff_id == 5 and self.b_hp > 0:
            hp_r = self.b_hp / max(1, self.b_max_hp)
            # 🌳 1. 고대 엔트: HP 20% 이하 「태고의 재생」 매 턴 최대 HP 4% 지속 회복
            if self.boss_id == 1 and hp_r <= 0.20:
                ent_rec = int(self.b_max_hp * 0.04)
                self.b_hp = min(self.b_max_hp, self.b_hp + ent_rec)
                logs.append(f"🌿✨ **[고대 엔트 · 태고의 재생]** 대지의 뿌리로부터 HP **+{ent_rec:,} 회복** (매 턴 4% 재생)")

            # 💎 2. 크리스탈 드래곤: HP 30% 이하 「절대결정」
            elif self.boss_id == 2 and hp_r <= 0.30 and not getattr(self, "crystal_ancient_buff", False):
                self.crystal_ancient_buff = True
                self.b_buff_def += 0.25
                logs.append("💎👑 **[크리스탈 드래곤 · 절대결정 각성!]** 결정 비늘이 강화되어 DEF +25% 및 반사 피해가 증폭됩니다!")

            # 🔥 3. 이프리트: HP 25% 이하 「멸세의 업화」 매 턴 업화 +2 누적
            elif self.boss_id == 3 and hp_r <= 0.25:
                self.hellfire_stacks = min(10, self.hellfire_stacks + 2)
                logs.append(f"🔥💥 **[이프리트 · 멸세의 업화 폭주!]** 대기가 불타오르며 업화 +2 중첩! (현재 업화 x{self.hellfire_stacks})")

            # ☄️ 4. 성운 가디언: HP 30% 이하 「시간 붕괴」 20% 확률로 플레이어 스킬 쿨타임 +1 연장
            elif self.boss_id == 4 and hp_r <= 0.30 and random.random() < 0.20:
                self.cd_unique = min(5, self.cd_unique + 1)
                self.cd_ult = min(8, self.cd_ult + 1)
                logs.append("⏳🌀 **[성운 가디언 · 시간 붕괴!]** 시간축이 뒤틀려 플레이어의 모든 스킬 쿨타임이 +1턴 지연되었습니다!")

            # 🪐 5. 오메가: 4개 페이즈 단계별 진화
            elif self.boss_id == 5:
                if hp_r <= 0.10 and not getattr(self, "omega_final_done", False):
                    self.omega_final_done = True
                    self.omega_phase = 4
                    self.b_buff_spd += 0.20
                    self.b_warning = "다음 턴 멸세의 종언 「Ω · 최후의 종언」 발동 예정! 방어 태세를 취하세요!"
                    self.dialogue_quote = "「종말을 보여주마.」"
                    logs.append(f"\n🪐🌌💥 **[FINAL PHASE · 최후의 종언 전조!]** 오메가가 손을 들어 올립니다! 다음 턴 **「Ω · 최후의 종언」** 발동 예정!! [🛡️ 방어 태세] 필수!\n💬 _{self.dialogue_quote}_")
                elif hp_r <= 0.30 and not self.omega_p3_done:
                    self.omega_p3_done = True
                    self.omega_phase = 3
                    self.b_buff_atk += 0.20
                    self.dialogue_quote = "「이제부터는 시험이 아니다.」"
                    logs.append(f"\n🪐🔴 **[Phase 3 · 종말 진입!]** 오메가가 종말의 형상으로 변이하여 ATK +20% (누적 +40%), 방어관통 +15% 및 쿨타임이 -1턴 감소합니다!\n💬 _{self.dialogue_quote}_")
                elif hp_r <= 0.70 and not self.omega_p2_done:
                    self.omega_p2_done = True
                    self.omega_phase = 2
                    self.b_buff_atk += 0.20
                    self.b_buff_spd += 0.15
                    self.dialogue_quote = "「여기까지 밀어붙인 자는 오랜만이다.」"
                    logs.append(f"\n🪐🟣 **[Phase 2 · 파괴신의 각성 진입!]** 오메가가 각성하여 ATK +20%, SPD +15% 강화되었습니다!\n💬 _{self.dialogue_quote}_")

        if self.b_hp > 0 and self.p_hp > 0:
            hp_r = self.b_hp / max(1, self.b_max_hp)
            ctx = {"hellfire_stacks": self.hellfire_stacks, "omega_phase": self.omega_phase}
            warning_active = bool(self.b_warning)
            
            b_act = choose_boss_action(self.boss_id, self.diff_id, hp_r, self.turn, self.b_cd_a, self.b_cd_b, self.b_ult_used, warning_active, ctx)
            
            cur_b_atk = int(self.b_atk * (1.0 + self.b_buff_atk))
            cur_b_def = int(self.b_def * (1.0 + self.b_buff_def))
            shield_mult = (0.6 if self.is_defending else 1.0) * (1.0 - self.armor_dmg_red)
            if self.armor_low_hp_red > 0 and (self.p_hp / max(1, self.p_max_hp)) <= 0.30:
                shield_mult *= (1.0 - self.armor_low_hp_red)
            if self.sp_key == "현무": shield_mult *= 0.95
            if self.sp_key == "사자" and self.relic_is_10 and (self.p_hp / max(1, self.p_max_hp)) <= 0.50:
                shield_mult *= 0.90 # 태양왕의 위엄: HP 50% 이하 시 받는 피해 -10%
            if self.cp_penalty.get("incoming_dmg_increase", 0.0) > 0:
                shield_mult *= (1.0 + self.cp_penalty["incoming_dmg_increase"])

            if b_act == "warning_ult":
                ult_n = self.b_skills.get("ultimate", {}).get("name", "궁극 패턴")
                self.b_warning = f"다음 턴 보스의 궁극기 「{ult_n}」 발동 예정! 방어 태세를 취하세요!"
                logs.append(f"\n⚠️⚡ **[{self.boss_base['name']}의 전조 발생!]** 거대한 기운이 모여듭니다! 다음 턴 「{ult_n}」 발동! [🛡️ 방어 태세] 필수!")

            elif b_act == "ultimate":
                self.b_ult_used = True
                self.b_warning = ""
                ult_data = self.b_skills.get("ultimate", {})
                ult_n = ult_data.get("name", "궁극 패턴")
                
                if self.boss_id == 1: 
                    self.b_buff_def += 0.25
                    self.b_buff_turns = 3
                    self.b_regen_turns = 3
                    self.b_regen_val = 0.04
                    logs.append(f"\n🌳👑 **[{self.boss_base['name']}]** 궁극 패턴 「{ult_n}」 전개! DEF +25% 및 3턴간 매 턴 4% 지속 회복 시작!")
                
                elif self.boss_id == 2: 
                    self.b_mirror_hits_left = 2 if self.diff_id >= 3 else 1
                    self.b_mirror_ratio = ult_data.get("reflect_ratio_map", {}).get(self.diff_id, 0.60)
                    t_desc = "2회 연속 피격 피해를 (1타 100%, 2타 70%)" if self.diff_id >= 3 else "다음 공격 피해를"
                    logs.append(f"\n💎👑 **[{self.boss_base['name']}]** 궁극 패턴 「{ult_n}」 발동! 거대한 수정 거울이 {t_desc} **최대 {int(self.b_mirror_ratio*100)}% 반사**합니다!")
                
                elif self.boss_id == 3: 
                    self.b_buff_atk += 0.25
                    self.b_buff_turns = 3
                    self.hellfire_stacks = min(10, self.hellfire_stacks + 2)
                    b_dmg = max(10, int((cur_b_atk * 1.5 - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    logs.append(f"\n🔥👑 **[{self.boss_base['name']}]** 궁극 패턴 「{ult_n}」 강림! ATK +25% 및 업화 +2 중첩! **{b_dmg:,} 폭멸 피해!**")
                
                elif self.boss_id == 4: 
                    rewind_amt = int(self.last_turn_hp_lost * 0.50)
                    self.b_hp = min(self.b_max_hp, self.b_hp + rewind_amt)
                    b_dmg = max(10, int((cur_b_atk * 1.2 - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    logs.append(f"\n☄️👑 **[{self.boss_base['name']}]** 궁극 패턴 「{ult_n}」 발동! 시간을 되돌려 HP **+{rewind_amt:,} 회복** 및 즉시 연속 공격 **{b_dmg:,} 피해!**")
                
                elif self.boss_id == 5: 
                    if getattr(self, "omega_phase", 1) == 4:
                        # 🪐 Final Phase: Ω · 최후의 종언 (350% 피해, DEF 50% 관통)
                        def_ignored = int(cur_def * 0.50)
                        b_dmg = max(30, int((cur_b_atk * 3.5 - (def_ignored * 0.35)) * shield_mult))
                        self.p_hp = max(0, self.p_hp - b_dmg)
                        logs.append(f"\n🪐👑💥 **[{self.boss_base['name']}]** 멸세의 종언 **「Ω · 최후의 종언」** 작렬!! 방어력 50%를 붕괴시키며 **{b_dmg:,} 초극대 파멸 피해!!** (남은 HP: {self.p_hp:,})")
                    else:
                        def_ignored = int(cur_def * 0.60)
                        b_dmg = max(20, int((cur_b_atk * 3.0 - (def_ignored * 0.35)) * shield_mult))
                        self.p_hp = max(0, self.p_hp - b_dmg)
                        logs.append(f"\n🪐👑💥 **[{self.boss_base['name']}]** 멸세의 궁극 패턴 「{ult_n}」 작렬!! DEF 40%를 분쇄하며 **{b_dmg:,} 대재앙 피해!!** (남은 HP: {self.p_hp:,})")

            elif b_act == "skill_a":
                sk_a = self.b_skills.get("skill_a", {})
                self.b_cd_a = sk_a.get("cooldown", 3)
                if self.boss_id == 5 and self.omega_phase == 3: self.b_cd_a = max(1, self.b_cd_a - 1)
                
                if self.boss_id == 1: 
                    b_dmg = max(5, int((cur_b_atk * 1.2 - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    msg = f"🌿 **[{self.boss_base['name']}]**의 「{sk_a['name']}」! **{b_dmg:,} 피해!**"
                    if random.random() < 0.20:
                        self.player_debuff_spd = 0.15; self.player_debuff_turns = 2
                        msg += " (플레이어 SPD -15% 감속!)"
                    logs.append(msg)
                
                elif self.boss_id == 2: 
                    self.b_barrier_turns = 2
                    logs.append(f"💎 **[{self.boss_base['name']}]**이 「{sk_a['name']}」을 전개했습니다! (2턴간 받는 피해 -25%, 반사율 +20%)")
                
                elif self.boss_id == 3: 
                    bonus_map = sk_a.get("bonus_per_stack_map", {1: 0.05, 5: 0.15})
                    stack_bonus = self.hellfire_stacks * bonus_map.get(self.diff_id, 0.08)
                    b_dmg = max(10, int((cur_b_atk * (1.3 + stack_bonus) - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    logs.append(f"🔥💥 **[{self.boss_base['name']}]**의 「{sk_a['name']}」! (업화 x{self.hellfire_stacks} 폭발) **{b_dmg:,} 파멸 피해!**")
                
                elif self.boss_id == 4: 
                    stun_map = sk_a.get("stun_chance_map", {1: 0.10, 5: 0.30})
                    if random.random() < stun_map.get(self.diff_id, 0.15):
                        self.player_stunned = True
                        logs.append(f"⏳❌ **[{self.boss_base['name']}]**의 「{sk_a['name']}」 적중! 플레이어의 다음 행동이 봉인되었습니다!")
                    else:
                        b_dmg = max(5, int((cur_b_atk * 1.0 - (cur_def * 0.35)) * shield_mult))
                        self.p_hp = max(0, self.p_hp - b_dmg)
                        logs.append(f"☄️ **[{self.boss_base['name']}]**의 「{sk_a['name']}」 견제! **{b_dmg:,} 피해!**")
                
                elif self.boss_id == 5: 
                    self.player_debuff_atk = 0.15; self.player_debuff_def = 0.15; self.player_debuff_turns = 2
                    b_dmg = max(10, int((cur_b_atk * 1.2 - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    logs.append(f"🪐⚖️ **[{self.boss_base['name']}]**의 「{sk_a['name']}」! **{b_dmg:,} 피해** 및 2턴간 플레이어 ATK/DEF -15% 약화!")

            elif b_act == "skill_b":
                sk_b = self.b_skills.get("skill_b", {})
                self.b_cd_b = sk_b.get("cooldown", 3)
                if self.boss_id == 5 and self.omega_phase == 3: self.b_cd_b = max(1, self.b_cd_b - 1)
                
                if self.boss_id == 1: 
                    heal_amt = int(self.b_max_hp * sk_b.get("heal_ratio", 0.08))
                    self.b_hp = min(self.b_max_hp, self.b_hp + heal_amt)
                    logs.append(f"🌳💚 **[{self.boss_base['name']}]**의 「{sk_b['name']}」! 체력을 **+{heal_amt:,} (8%)** 회복했습니다!")
                
                elif self.boss_id == 2: 
                    b_dmg = max(5, int((cur_b_atk * 1.2 - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    msg = f"💎🌈 **[{self.boss_base['name']}]**의 「{sk_b['name']}」! **{b_dmg:,} 피해!**"
                    if random.random() < 0.20:
                        self.player_debuff_def = 0.15; self.player_debuff_turns = 2
                        msg += " (플레이어 DEF -15% 파쇄!)"
                    logs.append(msg)
                
                elif self.boss_id == 3: 
                    self.player_burn_turns = 3
                    self.hellfire_stacks = min(10, self.hellfire_stacks + 1)
                    b_dmg = max(5, int((cur_b_atk * 1.0 - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    logs.append(f"🔥🌋 **[{self.boss_base['name']}]**의 「{sk_b['name']}」! **{b_dmg:,} 피해** 및 3턴간 화상 부여! (업화 +1)")
                
                elif self.boss_id == 4: 
                    self.b_buff_spd += 0.20; self.b_buff_turns = 2
                    logs.append(f"☄️⚡ **[{self.boss_base['name']}]**이 「{sk_b['name']}」을 시전하여 2턴간 SPD +20% 가속했습니다!")
                
                elif self.boss_id == 5: 
                    self.player_debuff_atk = 0.10; self.player_debuff_def = 0.10; self.player_debuff_spd = 0.10; self.player_debuff_turns = 2
                    b_dmg = max(10, int((cur_b_atk * 1.2 - (cur_def * 0.35)) * shield_mult))
                    self.p_hp = max(0, self.p_hp - b_dmg)
                    logs.append(f"🪐🌊 **[{self.boss_base['name']}]**의 「{sk_b['name']}」! **{b_dmg:,} 피해** 및 2턴간 플레이어 전 스탯 -10% 약화!")

            else:
                sk_base = self.b_skills.get("basic", {})
                b_ratio = sk_base.get("ratio", 1.0)
                if self.boss_id == 4 and cur_b_spd > cur_p_spd: b_ratio += 0.15
                
                def_pen = 0.85 if self.boss_id == 5 else 1.0
                b_dmg = max(5, int((cur_b_atk * b_ratio * random.uniform(0.95, 1.05) - (cur_def * 0.35 * def_pen)) * shield_mult))
                self.p_hp = max(0, self.p_hp - b_dmg)
                logs.append(f"💥 **[{self.boss_base['name']}]**의 「{sk_base['name']}」! **{b_dmg:,} 피해**를 입었습니다! (남은 HP: {self.p_hp:,})")

            self.is_defending = False

            if self.p_hp > 0 and self.sp_key == "불사조" and (self.p_hp / max(1, self.p_max_hp)) <= 0.30 and not self.phoenix_healed:
                self.phoenix_healed = True
                heal_amt = int(self.p_max_hp * 0.08)
                if self.cp_penalty.get("heal_penalty", 0.0) > 0:
                    heal_amt = max(1, int(heal_amt * (1.0 - self.cp_penalty["heal_penalty"])))
                self.p_hp = min(self.p_max_hp, self.p_hp + heal_amt)
                logs.append(f"🦅🔥 [재생의 불꽃] 불사조의 패시브로 HP +{heal_amt:,} (8%)가 회복되었습니다!")

            if self.p_hp <= 0 and self.sp_key == "불사조" and self.relic_is_10 and not self.phoenix_survived:
                self.phoenix_survived = True
                self.p_hp = 1
                logs.append("🔥 [불멸의 깃털 발동] HP 1로 기적처럼 생존했습니다!")

            if self.p_hp <= 0 and self.sp_key == "불사조" and not self.pet_revived:
                self.pet_revived = True
                self.p_hp = int(self.p_max_hp * 0.25)
                logs.append(f"🦅👑 [주작환생] HP {self.p_hp:,} (25%)로 화려하게 부활했습니다! 🔥")

        # 💀 플레이어 HP 0 이하 시 패배 및 사망 판정 파이프라인 (v15.6)
        if self.p_hp <= 0:
            self.is_finished = True
            q_vic = get_boss_dialogue(self.boss_id, "victory")
            if q_vic: self.dialogue_quote = q_vic; logs.append(f"💬 **[{self.boss_base['name']}]** _{q_vic}_")
            
            h_loss = 20 if self.sp_key == "사자" else 25
            if self.diff_id == 1:
                self.pet.stamina = max(0, getattr(self.pet, "stamina", 100) - 20)
                self.pet.happiness = max(10, self.pet.happiness - 5)
                self.pet.health = max(10, self.pet.health - 10)
                logs.append("\n😭 **공략에 실패했습니다.** (모험기력 -20, 행복도 -5)")
            elif self.diff_id == 2:
                self.pet.stamina = max(0, getattr(self.pet, "stamina", 100) - 30)
                self.pet.happiness = max(10, self.pet.happiness - 10)
                self.pet.health = max(10, self.pet.health - 20)
                logs.append("\n😭 **공략에 실패했습니다.** (모험기력 -30, 행복도 -10, 건강 -20)")
            else:
                # 💀 고난도 레이드(악몽/신화/고대) 치명상(Critical Injury) 판정 시스템 (영구 사망 0% 완전 폐지)
                final_inj_rate, base_rate, aff_red, has_bond_retry = self.pet.calculate_injury_rate(self.diff_id)
                
                # 1. 💎 생명의 보석 보호 확인
                if self.inv.items.get("life_gem", 0) > 0:
                    self.inv.remove_item("life_gem", 1)
                    self.pet.health = 30
                    self.pet.stamina = 0
                    self.pet.happiness = max(0, self.pet.happiness - 15)
                    logs.append("\n💎✨ **[생명의 보석 발동!]** 품속의 생명의 보석이 부서지며 치명상을 1회 완전 무효화했습니다! (🏥 건강 30%)")
                else:
                    is_injured = (random.random() < final_inj_rate)
                    
                    # 2. 💖 애정도 100 [절대적 유대] 1회 기적 회피 재판정
                    if is_injured and has_bond_retry:
                        if random.random() >= final_inj_rate:
                            is_injured = False
                            logs.append("\n💖👑✨ **[절대적 유대 기적 발동!]** 깊은 신뢰로 신수가 마지막 힘으로 치명상을 모면했습니다!")

                    # 3. 치명상 판정 결과
                    if is_injured:
                        self.pet.is_critically_injured = True
                        self.pet.health = 1
                        self.pet.stamina = 0
                        self.pet.energy = min(20, getattr(self.pet, "energy", 100))
                        self.pet.happiness = max(0, self.pet.happiness - 35)
                        
                        logs.append(
                            f"\n💀🚨 **[{self.pet.name}] 치명상 발생!**\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"📊 **치명상 위험도 판정:** 기본 {int(base_rate*100)}% ➔ 애정 보호 -{int(aff_red*100)}% (최종 {int(final_inj_rate*100)}%)\n"
                            f"🏥 신수가 치명상을 입어 전투 불능 상태가 되었습니다. (❤️ HP 1, 🏥 건강 1%, 모험기력 0%)\n"
                            f"💉 _(병원 치료, [불사의 성수], [태초의 심장] 또는 수면으로 회복시킬 수 있습니다)_"
                        )
                    else:
                        norm_hp = 50 if self.diff_id == 3 else (30 if self.diff_id == 4 else 20)
                        self.pet.health = norm_hp
                        self.pet.stamina = 0
                        self.pet.happiness = max(10, self.pet.happiness - h_loss)
                        logs.append(
                            f"\n✨🛡️ **[치명상 회피!]** {self.pet.name}이(가) 패배했으나 기적적으로 치명상을 모면했습니다!\n"
                            f"📊 (기본 위험도 {int(base_rate*100)}% ➔ 애정 보호 -{int(aff_red*100)}% ➔ 최종 {int(final_inj_rate*100)}% 위험 극복! | 🏥 건강 {norm_hp}%)"
                        )

            self.pet_dialogue_quote = get_pet_battle_quote(self.pet, self.p_hp, self.p_max_hp, is_boss_dead=(self.b_hp <= 0))
            return False, "\n".join(logs)

        self.pet_dialogue_quote = get_pet_battle_quote(self.pet, self.p_hp, self.p_max_hp, is_boss_dead=(self.b_hp <= 0))
        return False, "\n".join(logs)

class HybridBattleView(discord.ui.View):
    def __init__(self, session: HybridBattleSession, meta: dict):
        super().__init__(timeout=None) # 🚀 전투 룸 무제한 영구 유지
        self.session = session
        self.meta = meta
        self.rebuild_buttons()

    def rebuild_buttons(self):
        self.clear_items()
        if self.session.is_finished:
            return

        sk = self.session.skills
        b1_name = sk["basic1"]["name"]
        b2_name = sk["basic2"]["name"]
        u_name = sk["unique"]["name"]
        ult_name = sk["ultimate"]["name"]

        # 1. 1기본기 & 2기본기
        btn_b1 = discord.ui.Button(label=f"{b1_name}", style=discord.ButtonStyle.primary, row=0)
        async def cb_b1(interaction: discord.Interaction):
            await self.handle_action(interaction, "basic1")
        btn_b1.callback = cb_b1
        self.add_item(btn_b1)

        btn_b2 = discord.ui.Button(label=f"{b2_name}", style=discord.ButtonStyle.primary, row=0)
        async def cb_b2(interaction: discord.Interaction):
            await self.handle_action(interaction, "basic2")
        btn_b2.callback = cb_b2
        self.add_item(btn_b2)

        # 2. 고유기 (쿨타임 반영)
        u_cd = self.session.cd_unique
        if u_cd > 0:
            btn_u = discord.ui.Button(label=f"{u_name} (⏳ {u_cd}턴)", style=discord.ButtonStyle.secondary, disabled=True, row=0)
        else:
            btn_u = discord.ui.Button(label=f"{u_name}", style=discord.ButtonStyle.success, row=0)
            async def cb_u(interaction: discord.Interaction):
                await self.handle_action(interaction, "unique")
            btn_u.callback = cb_u
        self.add_item(btn_u)

        # 3. 궁극기 (쿨타임 반영)
        ult_cd = self.session.cd_ultimate
        if ult_cd > 0:
            btn_ult = discord.ui.Button(label=f"{ult_name} (⏳ {ult_cd}턴)", style=discord.ButtonStyle.secondary, disabled=True, row=1)
        else:
            btn_ult = discord.ui.Button(label=f"{ult_name}", style=discord.ButtonStyle.danger, row=1)
            async def cb_ult(interaction: discord.Interaction):
                await self.handle_action(interaction, "ultimate")
            btn_ult.callback = cb_ult
        self.add_item(btn_ult)

        # 4. 방어
        btn_def = discord.ui.Button(label="🛡️ 방어 태세", style=discord.ButtonStyle.secondary, row=1)
        async def cb_def(interaction: discord.Interaction):
            await self.handle_action(interaction, "defend")
        btn_def.callback = cb_def
        self.add_item(btn_def)

    async def handle_action(self, interaction: discord.Interaction, action: str):
        if interaction.user.id != self.session.user.id:
            return await interaction.response.send_message("본인의 전투만 조작할 수 있습니다!", ephemeral=True)

        suc, log_text = self.session.process_turn(action)
        save_user_pet(self.session.user.id, self.session.pet, self.session.inv, self.meta)
        
        self.rebuild_buttons()
        embed, files_att = self.session.get_battle_embed(log_text)
        if self.session.is_finished:
            for item in self.children:
                item.disabled = True
            
            diff_id = getattr(self.session, "diff_id", 1)
            if suc:
                # 🏥 전투 후 잔여 HP 비율을 신수의 건강(Health)에 보존 반영 (즉시 100% 리셋 방지)
                rem_hp_ratio = self.session.p_hp / max(1, self.session.p_max_hp)
                post_health = max(10, min(100, int(rem_hp_ratio * 100)))
                self.session.pet.health = post_health
                
                b_gold = int(self.session.boss_base["base_gold"] * self.session.diff_info["gold_mult"])
                b_exp = int(self.session.boss_base["base_exp"] * self.session.diff_info["exp_mult"])
                self.session.pet.coins += b_gold
                # 🚪 v16.2 레이드 성장 관문 기록 및 보스별 누적 킬 카운트 갱신
                is_first, kills, clear_logs = self.session.pet.record_raid_clear(diff_id, self.session.boss_id)
                self.session.pet.total_dungeon_clears = getattr(self.session.pet, "total_dungeon_clears", 0) + 1
                exp_logs = self.session.pet.gain_exp(b_exp)
                
                # 🎁 고난도 레이드 전용 특수 재료 드랍 & 첫 클리어 확정 방어구 (v16.2)
                drop_logs = []
                if is_first:
                    first_armor_id = FIRST_CLEAR_ARMORS.get(diff_id)
                    if first_armor_id and first_armor_id in ARMORS_DATABASE:
                        self.session.inv.add_armor(first_armor_id, 0)
                        drop_logs.append(f"👑✨ **[최초 토벌 확정 보상!]** 🛡️ **{ARMORS_DATABASE[first_armor_id]['name']}** 획득!")

                if diff_id == 3: # 🟣 Nightmare 레이드
                    n_drop = random.randint(1, 2)
                    self.session.inv.add_item("nightmare_crystal", n_drop)
                    drop_logs.append(f"🟣 **악몽의 결정** `+{n_drop}개`")
                    s_drop = random.randint(1, 2)
                    self.session.inv.add_item("soul_nightmare", s_drop)
                    drop_logs.append(f"🟣 **전설 혼** `+{s_drop}개`")
                elif diff_id == 4: # 🟡 Mythic 레이드
                    m_drop = random.randint(1, 2)
                    self.session.inv.add_item("mythic_core", m_drop)
                    drop_logs.append(f"🟡 **신화의 핵** `+{m_drop}개`")
                    s_drop = random.randint(1, 2)
                    self.session.inv.add_item("soul_mythic", s_drop)
                    drop_logs.append(f"🟡 **신화 혼** `+{s_drop}개`")
                elif diff_id == 5: # 🔴 Ancient 레이드
                    a_drop = random.randint(1, 2)
                    self.session.inv.add_item("ancient_core", a_drop)
                    drop_logs.append(f"🌑 **태고의 핵** `+{a_drop}개`")
                    s_drop = random.randint(2, 4)
                    self.session.inv.add_item("soul_mythic", s_drop)
                    drop_logs.append(f"🟡 **신화 혼** `+{s_drop}개`")
                    
                    # 🌟 고대 보스 10회 토벌 전용 확정 핵 드랍
                    core_reward_map = {
                        1: ("ancient_core_ent", "🌳 태고목의 핵"),
                        2: ("ancient_core_dragon", "💎 불멸결정의 핵"),
                        3: ("ancient_core_ifrit", "🔥 영겁화염의 핵"),
                        4: ("ancient_core_guardian", "☄️ 성운의 핵"),
                        5: ("ancient_core_omega", "🪐 종말의 핵")
                    }
                    if self.session.boss_id in core_reward_map and kills >= 10:
                        c_id, c_name = core_reward_map[self.session.boss_id]
                        self.session.inv.add_item(c_id, 1)
                        drop_logs.append(f"🌟👑 **[{kills}회 토벌 달성 확정 보상!]** {c_name} `+1개` 획득!")
                elif diff_id == 1: # ⚪ Normal 레이드
                    s_drop = random.randint(1, 3)
                    self.session.inv.add_item("soul_normal", s_drop)
                    drop_logs.append(f"⚪ **일반 혼** `+{s_drop}개`")
                elif diff_id == 2: # 🔵 Hard 레이드
                    s_drop = random.randint(1, 3)
                    self.session.inv.add_item("soul_hard", s_drop)
                    drop_logs.append(f"🔵 **고급 혼** `+{s_drop}개`")

                # 🏆 레이드 클리어 메타데이터 기록 (v15.8)
                if diff_id == 3: self.meta["cleared_nightmare"] = True
                elif diff_id == 4: self.meta["cleared_mythic"] = True
                elif diff_id == 5:
                    self.meta["cleared_ancient"] = True
                    b_keys = {1: "ent_ancient", 2: "crystal_ancient", 3: "ifrit_ancient", 4: "guardian_ancient", 5: "omega_ancient"}
                    b_key = b_keys.get(self.session.boss_id)
                    if b_key:
                        c_bosses = self.meta.get("cleared_bosses", [])
                        if b_key not in c_bosses: c_bosses.append(b_key)
                        self.meta["cleared_bosses"] = c_bosses

                ach_logs = AchievementManager.check_and_claim(self.session.pet, self.session.inv, self.meta)
                save_user_pet(self.session.user.id, self.session.pet, self.session.inv, self.meta)
                
                drop_str = f"\n📦 **핵심 드랍:**\n• " + "\n• ".join(drop_logs) if drop_logs else ""
                clear_gate_str = ("\n\n" + "\n".join(clear_logs)) if clear_logs else ""
                ach_str = ("\n\n" + "\n".join(ach_logs)) if ach_logs else ""
                health_str = f"\n🏥 **전투 후 건강:** `{post_health}%` _(수면/치료약/사료로 회복 가능)_"
                embed.add_field(name="🎁 토벌 보상", value=f"💰 +{b_gold:,}G | ✨ +{b_exp:,} EXP{health_str}{drop_str}\n" + " ".join(exp_logs) + clear_gate_str + ach_str, inline=False)
            else:
                # 💀 패배 결과 처리 및 상태 저장 (치명상/건강/기력)
                save_user_pet(self.session.user.id, self.session.pet, self.session.inv, self.meta)
                fail_status = "💀 [치명상/전투 불능]" if getattr(self.session.pet, "is_critically_injured", False) else "🤕 [체력 소진/패배]"
                embed.add_field(
                    name="💀 레이드 토벌 실패...",
                    value=f"**{self.session.pet.name}**의 체력이 모두 소진되었습니다. {fail_status}\n🏥 _(건강이 낮아지면 치료나 휴식이 필요합니다)_",
                    inline=False
                )

            try:
                if interaction.response.is_done():
                    if files_att:
                        await interaction.edit_original_response(embed=embed, attachments=files_att, view=self)
                    else:
                        await interaction.edit_original_response(embed=embed, view=self)
                else:
                    if files_att:
                        await interaction.response.edit_message(embed=embed, attachments=files_att, view=self)
                    else:
                        await interaction.response.edit_message(embed=embed, view=self)
                await interaction.followup.send("🏁 전투가 종료되었습니다. 이 스레드는 잠시 후 보관됩니다.")
            except Exception:
                pass
        else:
            try:
                if interaction.response.is_done():
                    if files_att:
                        await interaction.edit_original_response(embed=embed, attachments=files_att, view=self)
                    else:
                        await interaction.edit_original_response(embed=embed, view=self)
                else:
                    if files_att:
                        await interaction.response.edit_message(embed=embed, attachments=files_att, view=self)
                    else:
                        await interaction.response.edit_message(embed=embed, view=self)
            except Exception:
                pass

class DamagochiView(discord.ui.View):
    """
    🐾 5대 카테고리 계층형 스마트 UI 네비게이터
    - 메인: [🍖 돌보기] [👑 모험] [🎒 가방] [🧬 성장] [⚙️ 기타] (5개 핵심 버튼)
    - 서브메뉴: 각 기능별 전문 패널 전환 및 [↩️ 메인으로] 원클릭 복귀
    """
    def __init__(self, user: discord.User, pet: Pet, inv: Inventory, meta: dict, view_mode: str = "main", selected_boss_id: int = 1, selected_dungeon_id: int = 1):
        super().__init__(timeout=None) # 🚀 24시간 무제한 영구 인터랙션 보장 (오래 방치해도 타임아웃 에러 방지)
        self.user = user
        self.pet = pet
        self.inv = inv
        self.meta = meta
        self.view_mode = view_mode
        self.selected_boss_id = selected_boss_id
        self.selected_dungeon_id = selected_dungeon_id
        self.rebuild_ui()

    def rebuild_ui(self):
        self.clear_items()
        
        # 1. 🏠 메인 대시보드
        if self.view_mode == "main":
            if getattr(self.pet, "is_dead", False):
                # ☠️ 신수 전사 상태 스마트 UI (부활 & 명예의 전당 & 새알)
                hw_cnt = self.inv.items.get("holy_water", 0)
                ph_cnt = self.inv.items.get("primordial_heart", 0)
                self.add_item(discord.ui.Button(label=f"🌟 불사의 성수 부활 ({hw_cnt}개)", style=discord.ButtonStyle.success, custom_id="btn_dead_revive_holy", row=0))
                self.add_item(discord.ui.Button(label=f"🌌 태초의 심장 부활 ({ph_cnt}개)", style=discord.ButtonStyle.primary, custom_id="btn_dead_revive_heart", row=0))
                self.add_item(discord.ui.Button(label="🥚 새로운 알 부화", style=discord.ButtonStyle.danger, custom_id="btn_growth_hatch", row=1))
                self.add_item(discord.ui.Button(label="🏛️ 명예의 전당", style=discord.ButtonStyle.secondary, custom_id="btn_view_hall", row=1))
                self.add_item(discord.ui.Button(label="🛒 상점", style=discord.ButtonStyle.secondary, custom_id="btn_etc_shop", row=1))
            else:
                self.add_item(discord.ui.Button(label="🍖 돌보기", style=discord.ButtonStyle.primary, custom_id="btn_nav_care", row=0))
                self.add_item(discord.ui.Button(label="👑 모험", style=discord.ButtonStyle.danger, custom_id="btn_nav_adv", row=0))
                self.add_item(discord.ui.Button(label="🎒 가방", style=discord.ButtonStyle.success, custom_id="btn_nav_bag", row=1))
                self.add_item(discord.ui.Button(label="🧬 성장", style=discord.ButtonStyle.primary, custom_id="btn_nav_growth", row=1))
                self.add_item(discord.ui.Button(label="⚙️ 기타", style=discord.ButtonStyle.secondary, custom_id="btn_nav_etc", row=1))

        # 1-1. 🏛️ [명예의 전당] 서브메뉴
        elif self.view_mode == "hall_of_fame":
            self.add_item(discord.ui.Button(label="↩️ 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=0))

        # 2. 🍖 [돌보기] 서브메뉴
        elif self.view_mode == "care":
            cure_cost = max(100, self.pet.level * 100)
            self.add_item(discord.ui.Button(label="🍖 먹이주기 (50G)", style=discord.ButtonStyle.primary, custom_id="btn_action_feed", row=0))
            self.add_item(discord.ui.Button(label="🧼 목욕하기", style=discord.ButtonStyle.primary, custom_id="btn_action_clean", row=0))
            self.add_item(discord.ui.Button(label=f"💉 병원 치료 ({cure_cost:,}G)", style=discord.ButtonStyle.danger, custom_id="btn_action_cure", row=0))
            self.add_item(discord.ui.Button(label="🌙 수면/기상", style=discord.ButtonStyle.secondary, custom_id="btn_action_sleep", row=1))
            self.add_item(discord.ui.Button(label="❤️ 쓰다듬기", style=discord.ButtonStyle.secondary, custom_id="btn_action_pet", row=1))
            self.add_item(discord.ui.Button(label="🏋️ 훈련(성장)", style=discord.ButtonStyle.success, custom_id="btn_action_train", row=1))
            self.add_item(discord.ui.Button(label="↩️ 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=2))

        # 3. 👑 [모험] 서브메뉴
        elif self.view_mode == "adventure":
            self.add_item(discord.ui.Button(label="🗺️ 던전 탐험 (선택)", style=discord.ButtonStyle.success, custom_id="btn_nav_dungeon_select", row=0))
            self.add_item(discord.ui.Button(label="👑 보스 레이드 (선택)", style=discord.ButtonStyle.danger, custom_id="btn_nav_raid_select", row=0))
            self.add_item(discord.ui.Button(label="⚡ 기력 확인", style=discord.ButtonStyle.primary, custom_id="btn_action_stamina", row=1))
            self.add_item(discord.ui.Button(label="↩️ 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=1))

        # 3-1. 🗺️ 던전 선택 메뉴
        elif self.view_mode == "dungeon_select":
            self.add_item(discord.ui.Button(label="🌲 초심자의 숲", style=discord.ButtonStyle.success, custom_id="btn_pick_dungeon_1", row=0))
            self.add_item(discord.ui.Button(label="💎 수정 동굴", style=discord.ButtonStyle.primary, custom_id="btn_pick_dungeon_2", row=0))
            self.add_item(discord.ui.Button(label="🌋 마그마 화산", style=discord.ButtonStyle.danger, custom_id="btn_pick_dungeon_3", row=1))
            self.add_item(discord.ui.Button(label="🌌 심연의 균열", style=discord.ButtonStyle.secondary, custom_id="btn_pick_dungeon_4", row=1))
            self.add_item(discord.ui.Button(label="↩️ 모험 메뉴로", style=discord.ButtonStyle.secondary, custom_id="btn_back_adv", row=2))

        # 3-1-1. 🏰 던전 난이도 선택 메뉴 (v15.3)
        elif self.view_mode == "dungeon_diff_select":
            d_id = self.selected_dungeon_id
            d_data = DUNGEON_DATABASE.get(d_id, DUNGEON_DATABASE[1])
            self.add_item(discord.ui.Button(label=f"🟢 일반 (Lv.{d_data['req_lvl'][1]}+)", style=discord.ButtonStyle.success, custom_id="btn_run_dungeon_1", row=0))
            self.add_item(discord.ui.Button(label=f"🟣 정예 (Lv.{d_data['req_lvl'][2]}+)", style=discord.ButtonStyle.primary, custom_id="btn_run_dungeon_2", row=0))
            self.add_item(discord.ui.Button(label=f"🔴 심연 (Lv.{d_data['req_lvl'][3]}+)", style=discord.ButtonStyle.danger, custom_id="btn_run_dungeon_3", row=1))
            self.add_item(discord.ui.Button(label="↩️ 던전 목록으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_dungeon", row=1))

        # 3-2. 👑 레이드 난이도 선택 메뉴 (1단계)
        elif self.view_mode == "raid_diff_select":
            self.add_item(discord.ui.Button(label="🟢 노말 (Lv.1+)", style=discord.ButtonStyle.success, custom_id="btn_pick_diff_1", row=0))
            self.add_item(discord.ui.Button(label="🔵 하드 (Lv.30+)", style=discord.ButtonStyle.primary, custom_id="btn_pick_diff_2", row=0))
            self.add_item(discord.ui.Button(label="🟣 악몽 (Lv.50+)", style=discord.ButtonStyle.danger, custom_id="btn_pick_diff_3", row=1))
            self.add_item(discord.ui.Button(label="🟡 신화 (Lv.70+)", style=discord.ButtonStyle.secondary, custom_id="btn_pick_diff_4", row=1))
            self.add_item(discord.ui.Button(label="🔴 고대 (Lv.99+)", style=discord.ButtonStyle.danger, custom_id="btn_pick_diff_5", row=2))
            self.add_item(discord.ui.Button(label="↩️ 모험 메뉴로", style=discord.ButtonStyle.secondary, custom_id="btn_back_adv", row=2))

        # 3-3. 👑 난이도별 레이드 보스 토벌 선택 메뉴 (2단계)
        elif self.view_mode == "raid_boss_select":
            d_id = getattr(self, "selected_diff_id", 1)
            rec1 = get_recommended_cp(1, d_id)
            rec2 = get_recommended_cp(2, d_id)
            rec3 = get_recommended_cp(3, d_id)
            rec4 = get_recommended_cp(4, d_id)

            self.add_item(discord.ui.Button(label=f"🌳 엔트 ({rec1:,})", style=discord.ButtonStyle.success, custom_id="btn_start_raid_boss_1", row=0))
            self.add_item(discord.ui.Button(label=f"💎 수정용 ({rec2:,})", style=discord.ButtonStyle.primary, custom_id="btn_start_raid_boss_2", row=0))
            self.add_item(discord.ui.Button(label=f"🔥 이프리트 ({rec3:,})", style=discord.ButtonStyle.danger, custom_id="btn_start_raid_boss_3", row=1))
            self.add_item(discord.ui.Button(label=f"☄️ 가디언 ({rec4:,})", style=discord.ButtonStyle.primary, custom_id="btn_start_raid_boss_4", row=1))
            if d_id == 5:
                rec5 = get_recommended_cp(5, 5)
                self.add_item(discord.ui.Button(label=f"🪐 오메가 ({rec5:,})", style=discord.ButtonStyle.danger, custom_id="btn_start_raid_boss_5", row=2))
            self.add_item(discord.ui.Button(label="↩️ 난이도 재선택", style=discord.ButtonStyle.secondary, custom_id="btn_back_raid_diff", row=2))

        # 4. 🎒 [가방] 서브메뉴
        elif self.view_mode == "bag":
            self.add_item(discord.ui.Button(label="🍬 사탕 먹이기", style=discord.ButtonStyle.primary, custom_id="btn_bag_use_candy", row=0))
            self.add_item(discord.ui.Button(label="💊 치료약 사용", style=discord.ButtonStyle.success, custom_id="btn_bag_cure", row=0))
            self.add_item(discord.ui.Button(label="⚒️ 장비 대장간 (강화/승급)", style=discord.ButtonStyle.danger, custom_id="btn_bag_upgrade", row=0))
            self.add_item(discord.ui.Button(label="↩️ 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=1))

        # 4-1. ⚒️ [장비 대장간 / 강화소] 서브메뉴 (v17.2)
        elif self.view_mode == "forge":
            self.add_item(discord.ui.Button(label="🎴 보물 강화", style=discord.ButtonStyle.primary, custom_id="btn_forge_relic", row=0))
            self.add_item(discord.ui.Button(label="🛡️ 방어구 강화", style=discord.ButtonStyle.success, custom_id="btn_forge_armor", row=0))
            
            if self.inv.equipped_armor:
                a_id = self.inv.equipped_armor.get("armor_id")
                a_lvl = self.inv.equipped_armor.get("level", 0)
                a_info = ARMORS_DATABASE.get(a_id, {})
                if a_info.get("is_mythic", False) and a_lvl >= 15:
                    self.add_item(discord.ui.Button(label="🌟 고대 성급 승급 (★)", style=discord.ButtonStyle.danger, custom_id="btn_forge_ascend", row=1))
            
            if len(self.inv.armors_inventory) > 0:
                self.add_item(discord.ui.Button(label="🔄 방어구 교체", style=discord.ButtonStyle.primary, custom_id="btn_forge_switch_armor", row=1))
            
            self.add_item(discord.ui.Button(label="↩️ 가방으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_bag", row=2))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=2))

        # 5. 🧬 [성장 및 혈통] 서브메뉴
        elif self.view_mode == "growth":
            self.add_item(discord.ui.Button(label="📊 상세 스탯", style=discord.ButtonStyle.primary, custom_id="btn_view_detail", row=0))
            self.add_item(discord.ui.Button(label="🧬 가문 혈통(IV)", style=discord.ButtonStyle.primary, custom_id="btn_view_lineage", row=0))
            self.add_item(discord.ui.Button(label="🌱 잠재 성장 각성소", style=discord.ButtonStyle.success, custom_id="btn_view_potential", row=1))
            self.add_item(discord.ui.Button(label="🥚 환생의 의식", style=discord.ButtonStyle.danger, custom_id="btn_view_reincarnate", row=1))
            self.add_item(discord.ui.Button(label="↩️ 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=2))

        # 5-1. 🌱 [잠재 성장 각성소] 서브메뉴 (v17.1)
        elif self.view_mode == "potential":
            self.add_item(discord.ui.Button(label="❤️ HP 각성 (+3%)", style=discord.ButtonStyle.primary, custom_id="btn_pot_up_hp", row=0))
            self.add_item(discord.ui.Button(label="⚔️ ATK 각성 (+3%)", style=discord.ButtonStyle.danger, custom_id="btn_pot_up_atk", row=0))
            self.add_item(discord.ui.Button(label="🛡️ DEF 각성 (+3%)", style=discord.ButtonStyle.success, custom_id="btn_pot_up_def", row=1))
            self.add_item(discord.ui.Button(label="⚡ SPD 각성 (+3%)", style=discord.ButtonStyle.primary, custom_id="btn_pot_up_spd", row=1))
            self.add_item(discord.ui.Button(label="🎯 CRIT 각성 (+3%)", style=discord.ButtonStyle.secondary, custom_id="btn_pot_up_crit", row=2))
            self.add_item(discord.ui.Button(label="↩️ 성장 메뉴로", style=discord.ButtonStyle.secondary, custom_id="btn_back_growth", row=2))

        # 5-2. 🥚 [환생의 의식] 서브메뉴
        elif self.view_mode == "reincarnate_select":
            self.add_item(discord.ui.Button(label="🌟 혈통 계승 환생 (종족 유지)", style=discord.ButtonStyle.danger, custom_id="btn_action_reincarnate_same", row=0))
            self.add_item(discord.ui.Button(label="🎲 새로운 운명의 알 (랜덤 가챠)", style=discord.ButtonStyle.primary, custom_id="btn_action_reincarnate_new", row=0))
            self.add_item(discord.ui.Button(label="↩️ 성장 메뉴로", style=discord.ButtonStyle.secondary, custom_id="btn_back_growth", row=1))

        # 6. ⚙️ [기타] 서브메뉴
        elif self.view_mode == "etc":
            self.add_item(discord.ui.Button(label="📖 플레이어 가이드", style=discord.ButtonStyle.success, custom_id="btn_etc_guide", row=0))
            self.add_item(discord.ui.Button(label="🏪 잡화 상점", style=discord.ButtonStyle.primary, custom_id="btn_nav_shop", row=0))
            self.add_item(discord.ui.Button(label="🎰 가챠 확률표", style=discord.ButtonStyle.primary, custom_id="btn_view_rates", row=0))
            self.add_item(discord.ui.Button(label="🏆 명예의 전당", style=discord.ButtonStyle.primary, custom_id="btn_nav_hall_of_fame", row=1))
            self.add_item(discord.ui.Button(label="🎖️ 업적 및 칭호", style=discord.ButtonStyle.secondary, custom_id="btn_nav_achievements", row=1))
            if self.pet.level == 1:
                self.add_item(discord.ui.Button(label="🎲 신수 다시 뽑기 (Lv.1)", style=discord.ButtonStyle.danger, custom_id="btn_etc_reroll_lv1", row=1))
            self.add_item(discord.ui.Button(label="🛠️ 개발자 모드", style=discord.ButtonStyle.danger, custom_id="btn_etc_dev", row=2))
            self.add_item(discord.ui.Button(label="↩️ 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=2))

        # 6-0-1. 🛒 [24시 잡화 상점] 서브메뉴 (v17.2)
        elif self.view_mode == "shop":
            self.add_item(discord.ui.Button(label="🍖 사료 (50G)", style=discord.ButtonStyle.secondary, custom_id="btn_buy_feed", row=0))
            self.add_item(discord.ui.Button(label="🥩 고기 (200G)", style=discord.ButtonStyle.secondary, custom_id="btn_buy_meat", row=0))
            self.add_item(discord.ui.Button(label="🍰 케이크 (500G)", style=discord.ButtonStyle.secondary, custom_id="btn_buy_cake", row=0))
            self.add_item(discord.ui.Button(label="🧼 샴푸 (150G)", style=discord.ButtonStyle.secondary, custom_id="btn_buy_shampoo", row=0))
            
            self.add_item(discord.ui.Button(label="🍬 사탕 (500G)", style=discord.ButtonStyle.primary, custom_id="btn_buy_candy", row=1))
            self.add_item(discord.ui.Button(label="🍭 슈퍼사탕 (1.5천G)", style=discord.ButtonStyle.primary, custom_id="btn_buy_super_candy", row=1))
            self.add_item(discord.ui.Button(label="💎 생명보석 (5천G)", style=discord.ButtonStyle.danger, custom_id="btn_buy_life_gem", row=1))
            
            self.add_item(discord.ui.Button(label="🌟 불사성수 (3천G)", style=discord.ButtonStyle.danger, custom_id="btn_buy_holy_water", row=2))
            self.add_item(discord.ui.Button(label="🌌 태초심장 (1만G)", style=discord.ButtonStyle.danger, custom_id="btn_buy_primordial_heart", row=2))
            
            self.add_item(discord.ui.Button(label="↩️ 기타 메뉴로", style=discord.ButtonStyle.secondary, custom_id="btn_nav_etc", row=3))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=3))

        # 6-0. 📖 [플레이어 가이드북] 서브메뉴 (v17.2)
        elif self.view_mode == "guide":
            g_page = getattr(self, "guide_page_idx", 1)
            self.add_item(discord.ui.Button(label="◀ 이전 챕터", style=discord.ButtonStyle.secondary, disabled=(g_page <= 1), custom_id="btn_guide_prev", row=0))
            self.add_item(discord.ui.Button(label=f"📄 {g_page}/8장", style=discord.ButtonStyle.primary, disabled=True, custom_id="btn_guide_cur", row=0))
            self.add_item(discord.ui.Button(label="다음 챕터 ▶", style=discord.ButtonStyle.secondary, disabled=(g_page >= 8), custom_id="btn_guide_next", row=0))
            self.add_item(discord.ui.Button(label="↩️ 기타 메뉴로", style=discord.ButtonStyle.secondary, custom_id="btn_nav_etc", row=1))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=1))

        # 6-1. 🛠️ [개발자 모드 대시보드] 서브메뉴
        elif self.view_mode == "dev_mode":
            self.add_item(discord.ui.Button(label="💰 골드 +100만", style=discord.ButtonStyle.success, custom_id="btn_dev_gold", row=0))
            self.add_item(discord.ui.Button(label="🍬 사탕+강화석", style=discord.ButtonStyle.primary, custom_id="btn_dev_items", row=0))
            self.add_item(discord.ui.Button(label="🌱 혼 4종 세트", style=discord.ButtonStyle.success, custom_id="btn_dev_souls", row=0))
            self.add_item(discord.ui.Button(label="📈 만렙(Lv.99)", style=discord.ButtonStyle.danger, custom_id="btn_dev_lvl99", row=1))
            self.add_item(discord.ui.Button(label="🌌 초월 Lv.20", style=discord.ButtonStyle.danger, custom_id="btn_dev_trans20", row=1))
            self.add_item(discord.ui.Button(label="💖 애정 Max", style=discord.ButtonStyle.primary, custom_id="btn_dev_aff_max", row=1))
            self.add_item(discord.ui.Button(label="🌱 잠재 60% Max", style=discord.ButtonStyle.success, custom_id="btn_dev_pot_max", row=2))
            self.add_item(discord.ui.Button(label="🧬 PERFECT 500", style=discord.ButtonStyle.primary, custom_id="btn_dev_iv500", row=2))
            self.add_item(discord.ui.Button(label="🐾 종족 변경", style=discord.ButtonStyle.secondary, custom_id="btn_dev_species_menu", row=2))
            self.add_item(discord.ui.Button(label="🎭 성격 변경", style=discord.ButtonStyle.secondary, custom_id="btn_dev_personality_menu", row=2))
            self.add_item(discord.ui.Button(label="🛡️ 방어구 에디터", style=discord.ButtonStyle.primary, custom_id="btn_dev_armor_menu", row=3))
            self.add_item(discord.ui.Button(label="🎴 보물 +10", style=discord.ButtonStyle.primary, custom_id="btn_dev_relic10", row=3))
            self.add_item(discord.ui.Button(label="⚪ 노말MAX", style=discord.ButtonStyle.secondary, custom_id="btn_dev_preset_normal", row=3))
            self.add_item(discord.ui.Button(label="🔵 하드MAX", style=discord.ButtonStyle.primary, custom_id="btn_dev_preset_hard", row=3))
            self.add_item(discord.ui.Button(label="🟣 악몽MAX", style=discord.ButtonStyle.danger, custom_id="btn_dev_preset_nightmare", row=3))
            self.add_item(discord.ui.Button(label="🟡 신화MAX", style=discord.ButtonStyle.success, custom_id="btn_dev_preset_mythic", row=4))
            self.add_item(discord.ui.Button(label="🌌 고대MAX (종결)", style=discord.ButtonStyle.danger, custom_id="btn_dev_preset_ancient", row=4))
            self.add_item(discord.ui.Button(label="🚪 레이드 올해금", style=discord.ButtonStyle.danger, custom_id="btn_dev_unlock_all", row=4))
            self.add_item(discord.ui.Button(label="🔒 개발자 잠금", style=discord.ButtonStyle.secondary, custom_id="btn_dev_lock_toggle", row=4))
            self.add_item(discord.ui.Button(label="↩️ 기타 메뉴로", style=discord.ButtonStyle.secondary, custom_id="btn_nav_etc", row=4))

        # 6-1-1. 🐾 개발자 종족 변경 메뉴
        elif self.view_mode == "dev_species":
            species_items = list(SPECIES_DATABASE.keys())
            for idx, sp_k in enumerate(species_items):
                r = idx // 5
                self.add_item(discord.ui.Button(label=f"{SPECIES_DATABASE[sp_k]['emoji']} {sp_k}", style=discord.ButtonStyle.primary, custom_id=f"btn_dev_set_species_{sp_k}", row=r))
            self.add_item(discord.ui.Button(label="↩️ 개발자 콘솔로", style=discord.ButtonStyle.secondary, custom_id="btn_etc_dev", row=2))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=2))

        # 6-1-2. 🎭 개발자 성격 변경 메뉴
        elif self.view_mode == "dev_personality":
            p_keys = list(PERSONALITIES.keys())
            for idx, p_k in enumerate(p_keys):
                r = idx // 5
                p_emo = PERSONALITIES[p_k].get("emoji", "🎭")
                self.add_item(discord.ui.Button(label=f"{p_emo} {p_k}", style=discord.ButtonStyle.primary, custom_id=f"btn_dev_set_p_{p_k}", row=r))
            self.add_item(discord.ui.Button(label="↩️ 개발자 콘솔로", style=discord.ButtonStyle.secondary, custom_id="btn_etc_dev", row=2))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=2))

        # 6-1-3. 🛡️ 개발자 방어구 에디터 메뉴
        elif self.view_mode == "dev_armor":
            armor_items = list(ARMORS_DATABASE.keys())
            for idx, a_k in enumerate(armor_items):
                r = idx // 4
                self.add_item(discord.ui.Button(label=f"🛡️ {ARMORS_DATABASE[a_k]['name']}", style=discord.ButtonStyle.primary, custom_id=f"btn_dev_set_armor_{a_k}", row=r))
            self.add_item(discord.ui.Button(label="⚔️ +15 강화", style=discord.ButtonStyle.danger, custom_id="btn_dev_armor_plus15", row=2))
            self.add_item(discord.ui.Button(label="★5 고대 성급", style=discord.ButtonStyle.danger, custom_id="btn_dev_armor_star5", row=2))
            self.add_item(discord.ui.Button(label="↩️ 개발자 콘솔로", style=discord.ButtonStyle.secondary, custom_id="btn_etc_dev", row=3))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=3))

        # 7-1. 📊 [상세 스탯 분석] 서브메뉴
        elif self.view_mode == "detail":
            self.add_item(discord.ui.Button(label="⚔️ 4대 고유 스킬 설명", style=discord.ButtonStyle.primary, custom_id="btn_detail_skills", row=0))
            self.add_item(discord.ui.Button(label="↩️ 뒤로 가기", style=discord.ButtonStyle.secondary, custom_id="btn_back_growth", row=0))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=0))

        # 7-2. ⚔️ [4대 고유 스킬 설명] 서브메뉴
        elif self.view_mode == "skills":
            self.add_item(discord.ui.Button(label="📊 상세 스탯으로", style=discord.ButtonStyle.primary, custom_id="btn_skills_to_detail", row=0))
            self.add_item(discord.ui.Button(label="↩️ 뒤로 가기", style=discord.ButtonStyle.secondary, custom_id="btn_back_growth", row=0))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.secondary, custom_id="btn_back_main", row=0))

        # 8. 📄 기타 하위 상세 뷰 (혈통/확률표 등)
        else:
            self.add_item(discord.ui.Button(label="↩️ 뒤로 가기", style=discord.ButtonStyle.secondary, custom_id="btn_back_prev", row=0))
            self.add_item(discord.ui.Button(label="🏠 메인으로", style=discord.ButtonStyle.primary, custom_id="btn_back_main", row=0))

    async def update_view(self, interaction: discord.Interaction, action_msg: str = ""):
        async with USER_ACTION_QUEUE.get_lock(self.user.id):
            old_stage = get_growth_stage(self.pet.level)
            self.pet.live_tick()
            new_stage = get_growth_stage(self.pet.level)
            
            if new_stage > old_stage:
                action_msg += f"\n🎊✨ **[진화 각성!]** 신수가 **Stage {new_stage}**로 진화했습니다! 🌟"

            ach_logs = AchievementManager.check_and_claim(self.pet, self.inv, self.meta)
            if ach_logs:
                action_msg += "\n" + "\n".join(ach_logs)
                
            save_user_pet(self.user.id, self.pet, self.inv, self.meta)
            self.rebuild_ui()
            
            file_att = None
            if self.view_mode == "detail":
                embed = create_detail_embed(self.user, self.pet, self.inv, self.meta)
            elif self.view_mode == "gacha_rates":
                embed = create_gacha_rates_embed()
            elif self.view_mode == "lineage":
                embed = create_lineage_embed(self.user, self.pet, self.meta)
            elif self.view_mode == "bag":
                embed = create_bag_embed(self.user, self.pet, self.inv)
            elif self.view_mode == "forge":
                embed = create_forge_embed(self.user, self.pet, self.inv)
            elif self.view_mode == "shop":
                embed = create_shop_embed(self.user, self.pet, self.inv)
            elif self.view_mode == "dungeon_select":
                embed = create_dungeon_select_embed(self.user, self.pet)
            elif self.view_mode == "dungeon_diff_select":
                embed = create_dungeon_diff_select_embed(self.user, self.pet, self.inv, self.selected_dungeon_id)
            elif self.view_mode == "raid_diff_select":
                embed, file_att = create_raid_diff_select_embed(self.user, self.pet, self.inv)
            elif self.view_mode == "raid_boss_select":
                embed, file_att = create_raid_boss_select_embed(self.user, self.pet, self.inv, getattr(self, "selected_diff_id", 1))
            elif self.view_mode == "reincarnate_select":
                embed = create_reincarnate_select_embed(self.user, self.pet, self.meta)
            elif self.view_mode == "potential":
                embed = create_potential_embed(self.user, self.pet, self.inv)
            elif self.view_mode == "dev_mode":
                embed = create_dev_embed(self.user, self.pet, self.inv)
            elif self.view_mode == "dev_species":
                embed = create_dev_species_embed(self.user, self.pet)
            elif self.view_mode == "dev_personality":
                embed = create_dev_personality_embed(self.user, self.pet)
            elif self.view_mode == "dev_armor":
                embed = create_dev_armor_embed(self.user, self.inv)
            elif self.view_mode == "hall_of_fame":
                embed = create_hall_of_fame_embed(self.user, self.meta)
            elif self.view_mode == "achievements":
                embed = create_achievements_embed(self.user, self.pet, self.meta)
            elif self.view_mode == "titles":
                embed = create_titles_embed(self.user, self.meta)
            elif self.view_mode == "guide":
                embed = create_guide_embed(getattr(self, "guide_page_idx", 1))
            elif self.view_mode == "detail":
                embed = create_detail_embed(self.user, self.pet, self.inv, self.meta)
            elif self.view_mode == "skills":
                embed = create_skills_embed(self.user, self.pet, self.inv)
            else:
                embed, file_att = create_main_embed(self.user, self.pet, self.inv, action_msg, meta=self.meta)

            try:
                if not interaction.response.is_done():
                    if file_att:
                        try:
                            await interaction.response.edit_message(embed=embed, attachments=[file_att], view=self)
                        except Exception:
                            await interaction.response.edit_message(embed=embed, view=self)
                    else:
                        await interaction.response.edit_message(embed=embed, view=self)
                else:
                    if file_att:
                        try:
                            await interaction.edit_original_response(embed=embed, attachments=[file_att], view=self)
                        except Exception:
                            await interaction.edit_original_response(embed=embed, view=self)
                    else:
                        await interaction.edit_original_response(embed=embed, view=self)
            except (discord.NotFound, discord.HTTPException):
                pass # 만료되거나 네트워크 일시 지연 인터랙션 안전 무시
            except Exception as e:
                import traceback
                traceback.print_exc()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message(
                f"💡 이 화면은 **{self.user.display_name}**님의 신수 대시보드입니다!\n"
                f"본인의 신수를 확인하고 돌보시려면 채팅창에 **`/다마고치`** 슬래시 명령어를 입력해 주세요! 💕",
                ephemeral=True
            )
            return False

        c_id = interaction.data.get("custom_id", "")
        
        # 📌 1. 메인 ➔ 5대 카테고리 네비게이션
        if c_id == "btn_nav_care":
            self.view_mode = "care"
            await self.update_view(interaction, "🍖 돌보기 메뉴로 이동했습니다.")
        elif c_id == "btn_nav_adv":
            self.view_mode = "adventure"
            await self.update_view(interaction, "👑 모험 메뉴로 이동했습니다.")
        elif c_id == "btn_nav_bag":
            self.view_mode = "bag"
            await self.update_view(interaction, "🎒 가방(인벤토리) 메뉴로 이동했습니다.")
        elif c_id == "btn_nav_growth":
            self.view_mode = "growth"
            await self.update_view(interaction, "🧬 성장 및 혈통 메뉴로 이동했습니다.")
        elif c_id == "btn_nav_etc":
            self.view_mode = "etc"
            await self.update_view(interaction, "⚙️ 기타 메뉴로 이동했습니다.")
        elif c_id == "btn_nav_achievements":
            self.view_mode = "achievements"
            await self.update_view(interaction)
        elif c_id == "btn_view_titles":
            self.view_mode = "titles"
            await self.update_view(interaction)
        elif c_id.startswith("btn_equip_title_"):
            idx = int(c_id.split("_")[-1])
            titles = self.meta.get("unlocked_titles", [])
            if idx < len(titles):
                t_name = titles[idx]
                _, msg = AchievementManager.equip_title(self.meta, t_name)
                await self.update_view(interaction, msg)
            else:
                await interaction.response.send_message("⚠️ 유효하지 않은 칭호입니다.", ephemeral=True)
        elif c_id == "btn_unequip_title":
            _, msg = AchievementManager.unequip_title(self.meta)
            await self.update_view(interaction, msg)

        # 📌 2. 공통 메인/뒤로가기
        elif c_id == "btn_back_main":
            self.view_mode = "main"
            await self.update_view(interaction, "메인 화면으로 복귀했습니다.")
        elif c_id == "btn_back_adv":
            self.view_mode = "adventure"
            await self.update_view(interaction, "👑 모험 메뉴로 이동했습니다.")
        elif c_id == "btn_back_dungeon":
            self.view_mode = "dungeon_select"
            await self.update_view(interaction, "🗺️ 던전 선택 화면으로 이동했습니다.")
        elif c_id == "btn_back_boss":
            self.view_mode = "raid_boss_select"
            await self.update_view(interaction, "👑 보스 선택 화면으로 이동했습니다.")
        elif c_id == "btn_back_etc":
            self.view_mode = "etc"
            await self.update_view(interaction, "⚙️ 기타 메뉴로 이동했습니다.")
        elif c_id == "btn_back_growth":
            self.view_mode = "growth"
            await self.update_view(interaction, "🧬 성장 메뉴로 이동했습니다.")
        elif c_id == "btn_back_bag":
            self.view_mode = "bag"
            await self.update_view(interaction, "🎒 가방 메뉴로 이동했습니다.")
        elif c_id == "btn_back_prev":
            if self.view_mode in ["detail", "lineage"]: self.view_mode = "growth"
            elif self.view_mode in ["shop", "gacha_rates"]: self.view_mode = "etc"
            elif self.view_mode == "forge": self.view_mode = "bag"
            elif self.view_mode in ["dungeon_select", "dungeon_diff_select", "raid_boss_select", "raid_diff_select"]: self.view_mode = "adventure"
            else: self.view_mode = "main"
            await self.update_view(interaction)

        # 📌 3. [돌보기] 액션
        elif c_id == "btn_action_feed":
            _, msg = self.pet.feed("normal")
            await self.update_view(interaction, msg)
        elif c_id == "btn_action_clean":
            _, msg = self.pet.clean()
            await self.update_view(interaction, msg)
        elif c_id == "btn_action_sleep":
            _, msg = self.pet.sleep_toggle()
            await self.update_view(interaction, msg)
        elif c_id == "btn_action_pet":
            _, msg = self.pet.pet_animal()
            await self.update_view(interaction, msg)
        elif c_id == "btn_action_train":
            _, msg = self.pet.train()
            await self.update_view(interaction, msg)
        elif c_id == "btn_action_cure":
            _, msg = self.pet.cure()
            await self.update_view(interaction, msg)

        # 📌 4. [모험] 메뉴 진입
        elif c_id == "btn_nav_dungeon_select":
            if getattr(self.pet, "is_critically_injured", False):
                return await interaction.response.send_message("💀 신수가 치명상을 입은 상태입니다! 치료약으로 치료하거나 건강을 60% 이상으로 회복시켜주세요.", ephemeral=True)
            self.view_mode = "dungeon_select"
            await self.update_view(interaction)
        elif c_id == "btn_nav_raid_select":
            if getattr(self.pet, "is_critically_injured", False):
                return await interaction.response.send_message("💀 신수가 치명상을 입은 상태입니다! 치료약으로 치료하거나 건강을 60% 이상으로 회복시켜주세요.", ephemeral=True)
            self.view_mode = "raid_diff_select"
            await self.update_view(interaction)
        elif c_id == "btn_action_stamina":
            max_e = getattr(self.pet, "max_energy", 100)
            cur_s = getattr(self.pet, "stamina", 100)
            cur_e = getattr(self.pet, "energy", 100)
            await self.update_view(interaction, f"⚡ 생활 에너지: `{cur_e}/{max_e}%` | 🔥 모험 기력: `{cur_s}/{max_e}%`")

        # 📌 4-1. 던전 선택 (1~4) ➔ 난이도 선택 화면으로 (v15.3)
        elif c_id.startswith("btn_pick_dungeon_"):
            d_id = int(c_id.split("_")[-1])
            self.selected_dungeon_id = d_id
            self.view_mode = "dungeon_diff_select"
            await self.update_view(interaction)

        # 📌 4-1-1. 던전 난이도 실행 (1~3: 일반/정예/심연)
        elif c_id.startswith("btn_run_dungeon_"):
            diff_id = int(c_id.split("_")[-1])
            d_id = getattr(self, "selected_dungeon_id", 1)
            d_info = DUNGEON_DATABASE.get(d_id, DUNGEON_DATABASE[1])
            req_l = d_info["req_lvl"].get(diff_id, 1)
            if self.pet.level < req_l:
                return await interaction.response.send_message(f"⚠️ 입장 레벨이 부족합니다! [{d_info['emoji']} {d_info['name']}] 필요: Lv.{req_l}", ephemeral=True)
            if getattr(self.pet, "stamina", 100) < 10:
                return await interaction.response.send_message("😫 모험 기력이 부족합니다! 수면으로 기력을 충전해 주세요.", ephemeral=True)
            
            suc, msg = AdventureSystem.run_multi_dungeon(self.pet, self.inv, dungeon_id=d_id, diff_id=diff_id, times=5)
            self.view_mode = "adventure"
            await self.update_view(interaction, msg)

        # 📌 4-2. 👑 레이드 난이도 선택 (1단계 ➔ 해당 난이도 보스 선택창으로)
        elif c_id.startswith("btn_pick_diff_"):
            diff_id = int(c_id.split("_")[-1])
            diff_req_lvls = {1: 1, 2: 30, 3: 50, 4: 70, 5: 99}
            req_l = diff_req_lvls.get(diff_id, 1)
            diff_name = RAID_DIFFICULTIES.get(diff_id, {}).get("name", "난이도")
            if self.pet.level < req_l:
                return await interaction.response.send_message(f"⚠️ 입장 레벨이 부족합니다! [{diff_name}] 필요: Lv.{req_l}", ephemeral=True)

            self.selected_diff_id = diff_id
            self.view_mode = "raid_boss_select"
            await self.update_view(interaction)

        # 📌 4-3. 👑 난이도 재선택 (뒤로가기)
        elif c_id == "btn_back_raid_diff":
            self.view_mode = "raid_diff_select"
            await self.update_view(interaction)

        # 📌 4-4. 👑 레이드 보스 선택 (2단계 ➔ 실시간 턴제 레이드 시작)
        elif c_id.startswith("btn_start_raid_boss_") or c_id.startswith("btn_pick_boss_"):
            b_id = int(c_id.split("_")[-1])
            diff_id = getattr(self, "selected_diff_id", 1)
            boss_base = BOSS_DATABASE.get(b_id, BOSS_DATABASE[1])
            diff_info = RAID_DIFFICULTIES.get(diff_id, RAID_DIFFICULTIES[1])

            # 오메가는 고대 전용 제한
            if b_id == 5 and diff_id != 5:
                return await interaction.response.send_message("⚠️ 🪐 **오메가**는 고대(Ancient) 난이도 전용 최종 졸업 보스입니다!", ephemeral=True)

            req_e = 23 if self.pet.species_key in ["그리핀", "늑대"] else 25
            if getattr(self.pet, "stamina", 100) < req_e:
                return await interaction.response.send_message("😫 모험 기력이 부족합니다! 수면으로 기력을 충전해 주세요.", ephemeral=True)

            # 🚀 3초 타임아웃 방지: 즉시 defer() 호출하여 안전한 비동기 작업 시간 확보
            if not interaction.response.is_done():
                await interaction.response.defer()

            self.pet.consume_energy(25, "raid")
            save_user_pet(self.user.id, self.pet, self.inv, self.meta)

            thread_name = f"⚔️ {self.user.display_name}-vs-{boss_base['name']}-{diff_info['name'].split()[0]}"

            try:
                thread = await interaction.channel.create_thread(name=thread_name, auto_archive_duration=60, type=discord.ChannelType.public_thread)
                session = HybridBattleSession(self.user, self.pet, self.inv, b_id, diff_id)
                start_embed, start_files = session.get_battle_embed("전투가 시작되었습니다! 첫 행동을 선택하세요.")
                battle_view = HybridBattleView(session, self.meta)
                if start_files:
                    battle_msg = await thread.send(embed=start_embed, files=start_files, view=battle_view)
                else:
                    battle_msg = await thread.send(embed=start_embed, view=battle_view)
                battle_view.message = battle_msg
                
                self.view_mode = "adventure"
                await self.update_view(interaction, f"⚔️ **[{diff_info['name'].split()[0]} {boss_base['name']}]** 레이드 스레드가 개설되었습니다! 👉 {thread.mention}")
            except Exception as e:
                suc, msg = AdventureSystem.run_boss_raid(self.pet, self.inv, boss_id=boss_id, diff_id=diff_id, interactive=False)
                self.view_mode = "adventure"
                await self.update_view(interaction, msg)

        # 📌 4-4. ☠️ [전사 신수 부활 액션] (v15.6)
        elif c_id == "btn_dead_revive_holy":
            if self.inv.items.get("holy_water", 0) <= 0:
                return await interaction.response.send_message("🚫 보유 중인 **[불사의 성수]**가 없습니다! 상점에서 구매해 주세요.", ephemeral=True)
            suc, msg = Shop.use_item(self.pet, self.inv, "holy_water")
            await self.update_view(interaction, msg)
        elif c_id == "btn_dead_revive_heart":
            if self.inv.items.get("primordial_heart", 0) <= 0:
                return await interaction.response.send_message("🚫 보유 중인 **[태초의 심장]**이 없습니다! 상점에서 구매해 주세요.", ephemeral=True)
            suc, msg = Shop.use_item(self.pet, self.inv, "primordial_heart")
            await self.update_view(interaction, msg)
        elif c_id == "btn_view_hall":
            self.view_mode = "hall_of_fame"
            await self.update_view(interaction)

        # 📌 5. [가방] 액션
        elif c_id == "btn_bag_use_candy":
            if self.inv.items.get("small_candy", 0) > 0:
                self.inv.items["small_candy"] -= 1
                logs = self.pet.gain_exp(150)
                await self.update_view(interaction, "🍬 작은 EXP 사탕을 먹여 +150 EXP를 획득했습니다! " + " ".join(logs))
            elif self.inv.items.get("super_candy", 0) > 0:
                self.inv.items["super_candy"] -= 1
                logs = self.pet.gain_exp(500)
                await self.update_view(interaction, "🍭 슈퍼 EXP 사탕을 먹여 +500 EXP를 획득했습니다! " + " ".join(logs))
            else:
                await interaction.response.send_message("🎒 보유 중인 EXP 사탕이 없습니다! 던전이나 상점에서 획득해 주세요.", ephemeral=True)
        elif c_id == "btn_bag_cure":
            if self.inv.items.get("holy_water", 0) > 0:
                suc, msg = Shop.use_item(self.pet, self.inv, "holy_water")
                await self.update_view(interaction, msg)
            elif self.inv.items.get("primordial_heart", 0) > 0:
                suc, msg = Shop.use_item(self.pet, self.inv, "primordial_heart")
                await self.update_view(interaction, msg)
            else:
                _, msg = self.pet.cure()
                await self.update_view(interaction, msg)
        # 📌 5-1. [가방 ➔ 대장간] 진입
        elif c_id == "btn_bag_upgrade":
            self.view_mode = "forge"
            await self.update_view(interaction)

        # 📌 5-2. ⚒️ [대장간] 전용 보물 강화
        elif c_id == "btn_forge_relic":
            if not self.inv.equipped_relic:
                return await interaction.response.send_message("🎒 장착 중인 전용 보물이 없습니다! 던전에서 파밍하거나 상점에서 제작해 주세요.", ephemeral=True)
            max_relic = self.pet.get_relic_max_level()
            suc, msg, new_c = self.inv.enhance_relic(self.pet.coins, max_allowed_lvl=max_relic)
            self.pet.coins = new_c
            await self.update_view(interaction, msg)

        # 📌 5-3. ⚒️ [대장간] 방어구 강화
        elif c_id == "btn_forge_armor":
            if not self.inv.equipped_armor:
                return await interaction.response.send_message("🎒 장착 중인 방어구가 없습니다! 던전/레이드에서 획득해 주세요.", ephemeral=True)
            suc, msg, new_c = self.inv.enhance_armor(self.pet.coins)
            self.pet.coins = new_c
            await self.update_view(interaction, msg)

        # 📌 5-4. ⚒️ [대장간] 방어구 고대 성급(★) 승급
        elif c_id == "btn_forge_ascend":
            if not self.inv.equipped_armor:
                return await interaction.response.send_message("🎒 장착 중인 방어구가 없습니다!", ephemeral=True)
            suc, msg, new_c = self.inv.ascend_armor_star(self.pet.coins)
            self.pet.coins = new_c
            await self.update_view(interaction, msg)

        # 📌 5-5. ⚒️ [대장간] 보유 방어구 순환 교체
        elif c_id == "btn_forge_switch_armor":
            if not self.inv.armors_inventory:
                return await interaction.response.send_message("🎒 인벤토리에 보유 중인 다른 방어구가 없습니다!", ephemeral=True)
            suc, msg = self.inv.equip_armor(0)
            await self.update_view(interaction, msg)

        # 📌 6. [성장] 액션
        elif c_id in ["btn_growth_potential", "btn_view_potential"]:
            self.view_mode = "potential"
            await self.update_view(interaction)
        elif c_id.startswith("btn_pot_"):
            stat_key = c_id.replace("btn_pot_", "")
            suc, msg = self.pet.upgrade_potential(stat_key, self.inv)
            await self.update_view(interaction, msg)
        elif c_id == "btn_back_growth":
            self.view_mode = "growth"
            await self.update_view(interaction)
        elif c_id in ["btn_growth_detail", "btn_view_detail", "btn_skills_to_detail"]:
            self.view_mode = "detail"
            await self.update_view(interaction)
        elif c_id == "btn_detail_skills":
            self.view_mode = "skills"
            await self.update_view(interaction)
        elif c_id in ["btn_growth_lineage", "btn_view_lineage"]:
            self.view_mode = "lineage"
            await self.update_view(interaction)
        elif c_id == "btn_view_reincarnate":
            self.view_mode = "reincarnate_select"
            await self.update_view(interaction)
        elif c_id == "btn_growth_transcend":
            if self.pet.level < 99:
                return await interaction.response.send_message(f"🌌 초월 승급은 **Lv.99 만렙** 달성 후 가능합니다! (현재 Lv.{self.pet.level})", ephemeral=True)
            if self.pet.transcend_exp < 50000:
                return await interaction.response.send_message(f"🌌 초월 경험치가 부족합니다! (현재 {self.pet.transcend_exp:,} / 50,000)", ephemeral=True)
            self.pet.transcend_exp -= 50000
            self.pet.transcend_level = getattr(self.pet, "transcend_level", 0) + 1
            await self.update_view(interaction, f"🌌 축하합니다! 신수가 **초월 Lv.{self.pet.transcend_level}**로 승급하여 기본 스탯이 영구적으로 +5% 강화되었습니다! 🌟")
        elif c_id in ["btn_growth_hatch", "btn_action_reincarnate_same", "btn_action_reincarnate_new"]:
            if self.pet.level != 1 and self.pet.level < 99:
                return await interaction.response.send_message(
                    f"🚫 **[새 알 부화 불가]**\n새 알 부화는 갓 태어난 **Lv.1 상태(초기 소환)** 또는 **Lv.99 만렙(환생)**에서만 가능합니다!\n현재는 **Lv.{self.pet.level}**이므로, **Lv.99 만렙** 달성 후 환생으로 이용해 주세요! 🔥",
                    ephemeral=True
                )
            pre_used = self.meta.get("pre_99_hatch_used", False)
            if self.pet.level < 99 and pre_used:
                return await interaction.response.send_message(
                    f"🚫 **[새 알 부화 1회 소모 완료]**\nLv.1 초기 소환 기회(1회)를 이미 사용하셨습니다! 이제 이 신수를 **Lv.99 만렙**까지 육성해 주세요!",
                    ephemeral=True
                )
            cost = 1000
            if self.pet.coins < cost:
                return await interaction.response.send_message(f"💸 골드가 부족합니다! (소환 비용: {cost:,}G, 보유: {self.pet.coins:,}G)", ephemeral=True)

            old_name = self.pet.name
            old_coins = self.pet.coins - cost
            old_pet = self.pet
            is_reincarnate = (self.pet.level >= 99)

            self.meta["total_hatches"] = self.meta.get("total_hatches", 0) + 1
            
            if is_reincarnate:
                lineage = self.meta.get("lineage", {"generation": 1, "history": []})
                history = lineage.get("history", [])
                history.append({
                    "generation": getattr(old_pet, "generation", 1),
                    "name": old_name,
                    "species": old_pet.species_name,
                    "total_iv": old_pet.total_iv,
                    "rank": old_pet.rank,
                    "is_shiny": old_pet.is_shiny,
                    "reincarnated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                lineage["history"] = history
                lineage["generation"] = getattr(old_pet, "generation", 1) + 1
                if old_pet.total_iv > lineage.get("best_total_iv", 0):
                    lineage["best_total_iv"] = old_pet.total_iv
                    lineage["best_generation"] = getattr(old_pet, "generation", 1)
                self.meta["lineage"] = lineage

            if self.pet.level < 99:
                self.meta["pre_99_hatch_used"] = True
                self.pet = Pet()
            else:
                self.meta["pre_99_hatch_used"] = False
                if c_id == "btn_action_reincarnate_same":
                    # 종족 유지 환생
                    self.pet = Pet(parent_pet=old_pet)
                    self.pet.change_species(old_pet.species_key, self.inv)
                else:
                    # 새로운 랜덤 종족 환생
                    self.pet = Pet(parent_pet=old_pet)

            # 🎴 신수 종족 전용 보물 기본 획득 및 자동 장착 (+0강)
            self.inv.equipped_relic = {"species": self.pet.species_key, "level": 0}
            self.pet.coins = old_coins
            self.view_mode = "main"

            shiny_tag = " 🌟 [대박! 극희귀 변이!]" if self.pet.is_shiny else ""
            mythic_tag = " 🔴 [초대박! 1% 신화 바하무트 강림!]" if self.pet.species_key == "바하무트" else ""
            reinc_tag = f" 🧬 **[제{self.pet.generation}대 혈통 환생!]**" if is_reincarnate else ""
            hatch_count = self.meta['total_hatches']
            
            msg = f"🎉 새로운 알이 부화했습니다! [{self.pet.emoji} {self.pet.name}] ({self.pet.species_name} {self.pet.rank}){reinc_tag}{shiny_tag}{mythic_tag} (누적 소환: {hatch_count}회)"
            await self.update_view(interaction, msg)

        # 📌 7. [기타] 액션
        elif c_id == "btn_etc_guide":
            self.guide_page_idx = 1
            self.view_mode = "guide"
            await self.update_view(interaction)
        elif c_id == "btn_guide_prev":
            self.guide_page_idx = max(1, getattr(self, "guide_page_idx", 1) - 1)
            await self.update_view(interaction)
        elif c_id == "btn_guide_next":
            self.guide_page_idx = min(len(GUIDE_CHAPTERS), getattr(self, "guide_page_idx", 1) + 1)
            await self.update_view(interaction)
        elif c_id in ["btn_etc_shop", "btn_nav_shop"]:
            self.view_mode = "shop"
            await self.update_view(interaction)
        elif c_id in ["btn_view_rates", "btn_etc_rates"]:
            self.view_mode = "gacha_rates"
            await self.update_view(interaction)
        elif c_id in ["btn_nav_hall_of_fame", "btn_view_hall"]:
            self.view_mode = "hall_of_fame"
            await self.update_view(interaction)
        elif c_id == "btn_etc_dev":
            if DEV_MODE_LOCKED:
                await interaction.response.send_message(
                    "🔒 **[개발자 모드 보안 잠금]**\n"
                    "현재 개발자 모드가 안전하게 잠겨 있습니다!\n"
                    "관리자 권한으로 해제하시려면 채팅창에 **`/개발자인증 [비밀번호]`**를 입력해 주세요! 💕",
                    ephemeral=True
                )
            else:
                self.view_mode = "dev_mode"
                await self.update_view(interaction)
        elif c_id == "btn_back_etc":
            self.view_mode = "etc"
            await self.update_view(interaction)
        elif c_id == "btn_etc_reroll_lv1":
            if self.pet.level > 1:
                return await interaction.response.send_message("⚠️ 신수 다시 뽑기는 **Lv.1 초기 상태**에서만 가능합니다!", ephemeral=True)
            # 새로운 신수 생성 (알 부화)
            new_pet = Pet()
            new_inv = Inventory()
            new_inv.equipped_relic = {"species": new_pet.species_key, "level": 0}
            self.pet = new_pet
            self.inv = new_inv
            save_user_pet(self.user.id, self.pet, self.inv, self.meta)
            self.view_mode = "main"
            
            shiny_str = "🌟 **[극희귀 황금 샤이니 변이 출현!]**\n" if new_pet.is_shiny else ""
            reroll_msg = (
                f"🎲✨ **[신수 다시 뽑기 완료!]** 새로운 운명의 알이 깨어났습니다!\n"
                f"{shiny_str}"
                f"🐾 **새로운 파트너:** `[{new_pet.name}]` ({new_pet.species_name} {new_pet.rank} · {new_pet.element} 속성 / {new_pet.personality})\n"
                f"📊 **초기 개체값(IV):** `{new_pet.total_iv}/500` (HP {new_pet.hp_iv} / ATK {new_pet.atk_iv} / DEF {new_pet.def_iv} / SPD {new_pet.spd_iv} / CRIT {new_pet.crit_iv})"
            )
            await self.update_view(interaction, reroll_msg)
        elif c_id == "btn_etc_rename":
            await interaction.response.send_message("✏️ 신수의 이름은 채팅창에 **`/이름변경 [새이름]`** 슬래시 명령어를 입력하여 변경하실 수 있습니다!", ephemeral=True)

        # 📌 7-1. 🛠️ [개발자 모드] 치트/디버그 네비게이션 & 액션
        elif c_id == "btn_dev_nav_species":
            self.view_mode = "dev_species"
            await self.update_view(interaction)
        elif c_id == "btn_dev_nav_personality":
            self.view_mode = "dev_personality"
            await self.update_view(interaction)
        elif c_id == "btn_dev_nav_armor":
            self.view_mode = "dev_armor"
            await self.update_view(interaction)
        elif c_id.startswith("btn_dev_set_species_"):
            sp_key = c_id.replace("btn_dev_set_species_", "")
            suc, sp_msg = self.pet.change_species(sp_key, self.inv)
            self.view_mode = "dev_mode"
            await self.update_view(interaction, sp_msg)
        elif c_id.startswith("btn_dev_set_pers_"):
            pers_key = c_id.replace("btn_dev_set_pers_", "")
            self.pet.personality = pers_key
            self.view_mode = "dev_mode"
            p_data = PERSONALITIES.get(pers_key, {})
            await self.update_view(interaction, f"🎭 [성격 변경] 신수의 성격이 **[{p_data.get('emoji', '')} {pers_key}]**(으)로 변경되었습니다! ({p_data.get('desc', '')})")
        elif c_id.startswith("btn_dev_set_armor_"):
            arm_id = c_id.replace("btn_dev_set_armor_", "")
            cur_lvl = self.inv.equipped_armor.get("level", 0) if self.inv.equipped_armor else 0
            cur_stars = self.inv.equipped_armor.get("stars", 0) if self.inv.equipped_armor else 0
            self.inv.equipped_armor = {
                "armor_id": arm_id,
                "level": cur_lvl,
                "stars": cur_stars,
                "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}
            }
            a_info = ARMORS_DATABASE.get(arm_id, {})
            await self.update_view(interaction, f"🛡️ [방어구 장착] **[{a_info.get('tier', '')} {a_info.get('name', arm_id)}]**을(를) 장착했습니다!")
        elif c_id == "btn_dev_armor_plus15":
            if not self.inv.equipped_armor:
                self.inv.equipped_armor = {"armor_id": "leather_armor", "level": 0, "stars": 0, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
            self.inv.equipped_armor["level"] = 15
            await self.update_view(interaction, "⚔️ [치트] 현재 장착 방어구의 강화 수치가 **+15 MAX**로 변경되었습니다!")
        elif c_id == "btn_dev_armor_star5":
            if not self.inv.equipped_armor:
                self.inv.equipped_armor = {"armor_id": "ancient_god_armor", "level": 15, "stars": 0, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
            self.inv.equipped_armor["stars"] = 5
            await self.update_view(interaction, "🌟 [치트] 현재 장착 방어구의 고대 성급이 **★★★★★ (5성 MAX)**로 변경되었습니다!")
        elif c_id == "btn_dev_preset_normal":
            suc, p_msg = self.pet.apply_preset("normal", self.inv, self.meta)
            await self.update_view(interaction, p_msg)
        elif c_id == "btn_dev_preset_hard":
            suc, p_msg = self.pet.apply_preset("hard", self.inv, self.meta)
            await self.update_view(interaction, p_msg)
        elif c_id == "btn_dev_preset_nightmare":
            suc, p_msg = self.pet.apply_preset("nightmare", self.inv, self.meta)
            await self.update_view(interaction, p_msg)
        elif c_id == "btn_dev_preset_mythic":
            suc, p_msg = self.pet.apply_preset("mythic", self.inv, self.meta)
            await self.update_view(interaction, p_msg)
        elif c_id == "btn_dev_preset_ancient":
            suc, p_msg = self.pet.apply_preset("ancient", self.inv, self.meta)
            await self.update_view(interaction, p_msg)
        elif c_id == "btn_dev_gold":
            self.pet.coins += 1000000
            await self.update_view(interaction, "💰 [치트] **1,000,000G**가 즉시 지급되었습니다!")
        elif c_id == "btn_dev_items":
            for c_id_name in ["small_candy", "super_candy", "mega_candy", "ancient_candy"]:
                self.inv.add_item(c_id_name, 20)
            self.inv.add_item("stone", 50)
            self.inv.add_item("armor_stone", 50)
            self.inv.add_item("relic_essence", 50)
            self.inv.add_item("nightmare_crystal", 20)
            self.inv.add_item("mythic_core", 20)
            self.inv.add_item("ancient_core", 20)
            await self.update_view(interaction, "🍬 [치트] 모든 사탕 20개 & 강화석/정수/핵 세트가 가방에 지급되었습니다!")
        elif c_id == "btn_dev_souls":
            self.inv.add_item("soul_normal", 55)
            self.inv.add_item("soul_hard", 55)
            self.inv.add_item("soul_nightmare", 55)
            self.inv.add_item("soul_mythic", 55)
            await self.update_view(interaction, "🌱 [치트] 노말/하드/악몽/신화 혼(Soul) 각 55개(풀파밍 세트)가 지급되었습니다!")
        elif c_id == "btn_dev_lvl99":
            self.pet.level = 99
            self.pet.exp = 0
            self.pet.max_exp = self.pet.calc_req_exp(99)
            await self.update_view(interaction, "📈 [치트] 신수가 즉시 **Lv.99 만렙**에 도달했습니다!")
        elif c_id == "btn_dev_transcend":
            self.pet.transcend_level = 20
            self.pet.transcend_exp = 0
            await self.update_view(interaction, "🌌 [치트] 신수가 즉시 **초월 Lv.20 (최고 단계)**에 도달했습니다!")
        elif c_id == "btn_dev_affection":
            self.pet.total_affection = 1000
            self.pet.affection = 1000
            await self.update_view(interaction, "💖 [치트] 신수의 애정도가 즉시 **Lv.10 (1,000/1,000 MAX)**에 도달했습니다!")
        elif c_id == "btn_dev_potential":
            self.pet.potential_growth = {"hp": 0.60, "atk": 0.60, "def": 0.60, "spd": 0.60, "crit": 0.60}
            await self.update_view(interaction, "🌱 [치트] 5대 스탯 잠재 성장이 즉시 **+60.0% (MAX 풀각성)**되었습니다!")
        elif c_id == "btn_dev_perfect_iv":
            self.pet.hp_iv = 100; self.pet.atk_iv = 100; self.pet.def_iv = 100; self.pet.spd_iv = 100; self.pet.crit_iv = 100
            self.pet.total_iv = 500
            self.pet.rank = "👑 PERFECT (완벽)"
            self.pet.is_shiny = True
            await self.update_view(interaction, "🧬 [치트] **PERFECT 500 IV (올 100)** 및 **🌟 황금 샤이니 변이**가 적용되었습니다!")
        elif c_id == "btn_dev_god_armor":
            self.inv.equipped_armor = {
                "armor_id": "ancient_god_armor",
                "level": 15,
                "stars": 5,
                "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}
            }
            await self.update_view(interaction, "🛡️ [치트] 최고위 종결 방어구 **[고대신의 갑옷 +15 ★★★★★]**이 장착되었습니다!")
        elif c_id == "btn_dev_max_relic":
            self.inv.equipped_relic = {
                "species": self.pet.species_key,
                "level": 10
            }
            await self.update_view(interaction, f"🎴 [치트] 종족 전용 보물 **[{self.pet.species_name}의 보물 +10 MAX]**이 장착되었습니다!")
        elif c_id == "btn_dev_heal_all":
            self.pet.health = 100; self.pet.stamina = getattr(self.pet, "max_energy", 100); self.pet.energy = getattr(self.pet, "max_energy", 100)
            self.pet.hunger = 100; self.pet.cleanliness = 100; self.pet.happiness = 100
            self.pet.is_critically_injured = False; self.pet.is_sick = False; self.pet.is_sleeping = False
            await self.update_view(interaction, "🏥 [치트] 신수의 건강/모험기력/생활에너지/행복도가 100% 풀충전되고 모든 질병/치명상이 완치되었습니다!")
        elif c_id == "btn_dev_unlock_raids":
            self.pet.raid_clears = {
                "1": [1, 2, 3, 4], "2": [1, 2, 3, 4],
                "3": [1, 2, 3, 4], "4": [1, 2, 3, 4],
                "5": [1, 2, 3, 4, 5]
            }
            self.pet.boss_kills = {"5_1": 15, "5_2": 15, "5_3": 15, "5_4": 15, "5_5": 15}
            self.meta["cleared_nightmare"] = True
            self.meta["cleared_mythic"] = True
            self.meta["cleared_ancient"] = True
            self.meta["cleared_bosses"] = ["ent_ancient", "crystal_ancient", "ifrit_ancient", "guardian_ancient", "omega_ancient"]
            await self.update_view(interaction, "🚪 [치트] 모든 난이도 레이드 관문 및 고대 15킬 칭호 조건이 100% 올클리어 처리되었습니다!")
        elif c_id == "btn_dev_zenith":
            # 신수왕 완전체 프리셋 원클릭 적용
            self.pet.level = 99
            self.pet.exp = 0
            self.pet.max_exp = self.pet.calc_req_exp(99)
            self.pet.is_shiny = True
            self.pet.hp_iv = 100; self.pet.atk_iv = 100; self.pet.def_iv = 100; self.pet.spd_iv = 100; self.pet.crit_iv = 100
            self.pet.total_iv = 500
            self.pet.rank = "👑 PERFECT (완벽)"
            self.pet.transcend_level = 20
            self.pet.total_affection = 1000; self.pet.affection = 1000
            self.pet.potential_growth = {"hp": 0.60, "atk": 0.60, "def": 0.60, "spd": 0.60, "crit": 0.60}
            self.pet.health = 100; self.pet.stamina = getattr(self.pet, "max_energy", 100); self.pet.energy = getattr(self.pet, "max_energy", 100)
            self.pet.hunger = 100; self.pet.cleanliness = 100; self.pet.happiness = 100
            self.pet.is_critically_injured = False; self.pet.is_sick = False
            self.pet.coins += 5000000
            
            self.inv.equipped_armor = {
                "armor_id": "ancient_god_armor", "level": 15, "stars": 5,
                "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}
            }
            self.inv.equipped_relic = {"species": self.pet.species_key, "level": 10}
            self.pet.raid_clears = {"1": [1, 2, 3, 4], "2": [1, 2, 3, 4], "3": [1, 2, 3, 4], "4": [1, 2, 3, 4], "5": [1, 2, 3, 4, 5]}
            self.pet.boss_kills = {"5_1": 15, "5_2": 15, "5_3": 15, "5_4": 15, "5_5": 15}
            self.meta["cleared_nightmare"] = True; self.meta["cleared_mythic"] = True; self.meta["cleared_ancient"] = True
            self.meta["cleared_bosses"] = ["ent_ancient", "crystal_ancient", "ifrit_ancient", "guardian_ancient", "omega_ancient"]
            await self.update_view(interaction, "👑✨ **[신수왕 완전체 (Zenith) 원클릭 세팅 완료!]**\n• Lv.99 / 초월 20 / 애정 10 / 잠재 60% / 500 IV / 샤이니 / 고대신+15★5 / 보물+10 / 골드 500만G")

        # 📌 8. [상점] 아이템 구매 액션
        elif c_id.startswith("btn_buy_"):
            buy_key = c_id.replace("btn_buy_", "")
            shop_prices = {
                "feed": (50, "일반 사료", "feed", 1),
                "meat": (200, "고급 고기", "meat", 1),
                "cake": (500, "신수 케이크", "cake", 1),
                "shampoo": (150, "신수 샴푸", "shampoo", 1),
                "candy": (500, "작은 EXP 사탕", "small_candy", 1),
                "super_candy": (1500, "슈퍼 EXP 사탕", "super_candy", 1),
                "life_gem": (5000, "생명의 보석", "life_gem", 1),
                "holy_water": (3000, "불사의 성수", "holy_water", 1),
                "primordial_heart": (10000, "태초의 심장", "primordial_heart", 1)
            }
            if buy_key in shop_prices:
                cost, item_name, inv_key, qty = shop_prices[buy_key]
                if self.pet.coins < cost:
                    return await interaction.response.send_message(f"💸 골드가 부족합니다! (필요: {cost:,}G, 보유: {self.pet.coins:,}G)", ephemeral=True)
                
                self.pet.coins -= cost
                
                # 즉시 소비류 처리 (사료/고기/케이크/목욕) or 인벤토리 보관
                if inv_key == "feed":
                    self.pet.hunger = min(100, self.pet.hunger + 30)
                    msg = f"🍖 **[{item_name}]**을 구매하여 바로 먹였습니다! (포만도 +30, 잔여 골드: {self.pet.coins:,}G)"
                elif inv_key == "meat":
                    self.pet.hunger = min(100, self.pet.hunger + 50)
                    self.pet.energy = min(getattr(self.pet, "max_energy", 100), self.pet.energy + 20)
                    msg = f"🥩 **[{item_name}]**을 구매하여 바로 먹였습니다! (포만도 +50, 기력 +20, 잔여 골드: {self.pet.coins:,}G)"
                elif inv_key == "cake":
                    self.pet.hunger = min(100, self.pet.hunger + 40)
                    self.pet.happiness = min(100, self.pet.happiness + 30)
                    msg = f"🍰 **[{item_name}]**을 구매하여 바로 먹였습니다! (포만도 +40, 행복도 +30, 잔여 골드: {self.pet.coins:,}G)"
                elif inv_key == "shampoo":
                    self.pet.cleanliness = min(100, self.pet.cleanliness + 60)
                    msg = f"🧼 **[{item_name}]**으로 신수를 깨끗하게 씻겼습니다! (청결도 +60, 잔여 골드: {self.pet.coins:,}G)"
                else:
                    self.inv.add_item(inv_key, qty)
                    msg = f"🛒 **[{item_name}]** x{qty}개를 구매하여 가방에 보관했습니다! (잔여 골드: {self.pet.coins:,}G)"
                
                await self.update_view(interaction, msg)

        # 📌 5. [가방] 액션
        elif c_id == "btn_bag_cure":
            if self.inv.items.get("holy_water", 0) > 0:
                self.inv.remove_item("holy_water", 1)
                self.pet.health = max(60, self.pet.health)
                self.pet.is_sick = False
                self.pet.is_critically_injured = False
                await self.update_view(interaction, "🌟 **[불사의 성수 사용]** 성수로 질병과 치명상을 깨끗이 정화했습니다! (건강 회복)")
            elif self.inv.items.get("primordial_heart", 0) > 0:
                self.inv.remove_item("primordial_heart", 1)
                self.pet.health = 100
                self.pet.energy = getattr(self.pet, "max_energy", 100)
                self.pet.stamina = getattr(self.pet, "max_energy", 100)
                self.pet.is_sick = False
                self.pet.is_critically_injured = False
                await self.update_view(interaction, "🌌 **[태초의 심장 사용]** 신수가 태초의 힘으로 완벽하게 부활했습니다! (건강/기력 100% 풀충전)")
            else:
                suc, msg = self.pet.cure()
                await self.update_view(interaction, msg)
                await self.update_view(interaction, msg)

        elif c_id == "btn_bag_use_candy":
            if self.inv.items.get("super_candy", 0) > 0:
                self.inv.remove_item("super_candy", 1)
                logs = self.pet.gain_exp(500)
                await self.update_view(interaction, "🍭 **[슈퍼 EXP 사탕 사용]** +500 EXP 획득!\n" + " ".join(logs))
            elif self.inv.items.get("small_candy", 0) > 0 or self.inv.items.get("candy", 0) > 0:
                k = "small_candy" if self.inv.items.get("small_candy", 0) > 0 else "candy"
                self.inv.remove_item(k, 1)
                logs = self.pet.gain_exp(150)
                await self.update_view(interaction, "🍬 **[작은 EXP 사탕 사용]** +150 EXP 획득!\n" + " ".join(logs))
            else:
                await interaction.response.send_message("🍬 가방에 사탕이 없습니다! [⚙️ 기타] ➔ [🛒 24시 상점]에서 사탕을 구매해 주세요.", ephemeral=True)

        elif c_id == "btn_bag_upgrade":
            if not self.inv.equipped_armor:
                await interaction.response.send_message("🛡️ 현재 장착된 방어구가 없습니다! 던전이나 레이드에서 방어구를 먼저 획득해 주세요.", ephemeral=True)
            else:
                cur_lvl = self.inv.equipped_armor["level"]
                req_stone = cur_lvl + 1
                if self.inv.items.get("armor_stone", 0) < req_stone and self.inv.items.get("stone", 0) < req_stone:
                    await interaction.response.send_message(f"💎 강화석이 부족합니다! (필요: {req_stone}개)", ephemeral=True)
                else:
                    k = "armor_stone" if self.inv.items.get("armor_stone", 0) >= req_stone else "stone"
                    self.inv.remove_item(k, req_stone)
                    self.inv.equipped_armor["level"] += 1
                    await self.update_view(interaction, f"✨ **[방어구 강화 성공!]** 방어구가 **+{self.inv.equipped_armor['level']}**강으로 강화되었습니다! 🎉")

        return True

intents = discord.Intents.default()
# intents.message_content는 디스코드 개발자 포털의 Privileged Intent 활성화 필요
# 슬래시 명령어(/다마고치, /채팅정리 등)와 버튼 UI는 기본 Intents만으로 100% 정상 작동합니다.
bot = commands.Bot(command_prefix="!", intents=intents)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 Render 헬스체크 HTTP 서버 (aiohttp)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_health_server_started = False

async def start_health_server():
    """🌐 Render 무료 플랜 스핀다운 방지용 aiohttp 헬스체크 서버"""
    global _health_server_started
    if _health_server_started:
        return  # on_ready 재호출 시 중복 방지
    _health_server_started = True

    try:
        from aiohttp import web
    except ImportError:
        print("⚠️ aiohttp 미설치 → 헬스체크 서버 비활성화 (로컬 환경)")
        return

    async def health_check(request):
        return web.json_response({
            "status": "ok",
            "service": "damagochi",
            "discord": "ready" if bot.is_ready() else "connecting",
            "backend": get_backend_info()
        })

    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 [Health Server] 포트 {port}에서 헬스체크 서버 가동 완료!")

@bot.event
async def on_ready():
    print(f"✨ [신수키우기 v18 온라인] {bot.user} 접속 완료! ({get_backend_info()})")
    # 헬스체크 서버 시작 (첫 연결 시 1회만)
    await start_health_server()
    try:
        synced = await bot.tree.sync()
        print(f"🌐 슬래시 명령어 {len(synced)}개 글로벌 동기화 성공!")
    except Exception as e:
        print(f"동기화 에러: {e}")

async def delete_after_delay(msg: discord.Message, delay: int = 3):
    """메인 이벤트 루프를 블로킹하지 않는 안전한 지연 삭제 헬퍼"""
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.strip()

    # 1. ⚔️ 전투 전용 Thread 내 채팅 스킬 입력 처리
    if isinstance(message.channel, discord.Thread):
        return await bot.process_commands(message)

    # 2. 🧹 채팅정리 명령어 (!채팅정리, 채팅정리, !청소, 청소, !clear, clear)
    if content.startswith(("!채팅정리", "채팅정리", "!청소", "청소", "!clear", "clear")):
        parts = content.split()
        limit = 100
        if len(parts) > 1 and parts[1].isdigit():
            limit = min(100, max(1, int(parts[1])))
        try:
            deleted = await message.channel.purge(limit=limit)
            temp = await message.channel.send(f"🧹✨ {message.author.mention}님의 요청으로 **{len(deleted)}개**의 메시지를 깨끗하게 청소했습니다!")
            asyncio.create_task(delete_after_delay(temp, 3))
        except Exception as e:
            temp = await message.channel.send(f"⚠️ 메시지 삭제 권한(Manage Messages)이 봇에게 필요합니다: {e}")
            asyncio.create_task(delete_after_delay(temp, 3))
        return

    # 3. 신수 메인 대시보드 (!다마고치, 다마고치, !신수, 신수, !상태, 상태)
    if content.startswith(("!다마고치", "다마고치", "!신수", "신수", "!상태", "상태")):
        pet, inv, meta, msg = get_or_create_user_pet(message.author.id)
        embed, file_att = create_main_embed(message.author, pet, inv, msg)
        view = DamagochiView(message.author, pet, inv, meta, view_mode="main")
        if file_att:
            await message.channel.send(embed=embed, file=file_att, view=view)
        else:
            await message.channel.send(embed=embed, view=view)
        return
    elif content.startswith(("!확률표", "확률표")):
        embed = create_gacha_rates_embed()
        await message.channel.send(embed=embed)
        return
    elif content.startswith(("!가방", "가방", "!인벤", "인벤")):
        pet, inv, meta, _ = get_or_create_user_pet(message.author.id)
        embed = create_bag_embed(message.author, pet, inv)
        view = DamagochiView(message.author, pet, inv, meta, view_mode="bag")
        await message.channel.send(embed=embed, view=view)
        return
    elif content.startswith(("!상점", "상점")):
        pet, inv, meta, _ = get_or_create_user_pet(message.author.id)
        embed = create_shop_embed(message.author, pet, inv)
        view = DamagochiView(message.author, pet, inv, meta, view_mode="shop")
        await message.channel.send(embed=embed, view=view)
        return
    elif content.startswith(("!혈통", "혈통")):
        pet, inv, meta, _ = get_or_create_user_pet(message.author.id)
        embed = create_lineage_embed(message.author, pet, meta)
        view = DamagochiView(message.author, pet, inv, meta, view_mode="lineage")
        await message.channel.send(embed=embed, view=view)
        return

    await bot.process_commands(message)

@bot.tree.command(name="채팅정리", description="🧹 현재 채널의 최근 메시지를 깨끗하게 일괄 청소합니다.")
@app_commands.describe(개수="삭제할 메시지 수 (1~100개, 기본 100개)")
async def cmd_clear(interaction: discord.Interaction, 개수: int = 100):
    cnt = min(100, max(1, 개수))
    await interaction.response.defer(ephemeral=True)
    try:
        deleted = await interaction.channel.purge(limit=cnt)
        await interaction.followup.send(f"🧹✨ 현재 채널에서 **{len(deleted)}개**의 메시지를 깨끗하게 청소 완료했습니다!", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ 메시지 삭제 권한이 부족합니다: {e}", ephemeral=True)

@bot.tree.command(name="다마고치", description="✨ 신수키우기 메인 대시보드를 엽니다.")
async def cmd_damagochi(interaction: discord.Interaction):
    pet, inv, meta, msg = get_or_create_user_pet(interaction.user.id)
    embed, file_att = create_main_embed(interaction.user, pet, inv, msg)
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="main")
    
    if file_att:
        await interaction.response.send_message(embed=embed, file=file_att, view=view)
    else:
        await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="확률표", description="🎲 10대 신수 및 극희귀 변이 소환 공식 확률표를 확인합니다.")
async def cmd_rates(interaction: discord.Interaction):
    embed = create_gacha_rates_embed()
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="이름변경", description="✏️ 내 신수의 이름을 새로운 멋진 닉네임으로 변경합니다.")
@app_commands.describe(새이름="새로 지어줄 신수의 닉네임 (최대 15자)")
async def cmd_rename(interaction: discord.Interaction, 새이름: str):
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    suc, msg = pet.rename(새이름)
    save_user_pet(interaction.user.id, pet, inv, meta)
    
    embed, file_att = create_main_embed(interaction.user, pet, inv, msg)
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="main")
    if file_att:
        await interaction.response.send_message(content=f"🎉 **{msg}**", embed=embed, file=file_att, view=view)
    else:
        await interaction.response.send_message(content=f"🎉 **{msg}**", embed=embed, view=view)

@bot.tree.command(name="혈통", description="🧬 내 가문의 세대별 혈통 계보도 및 역대 최고 IV 기록을 확인합니다.")
async def cmd_lineage(interaction: discord.Interaction):
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    embed = create_lineage_embed(interaction.user, pet, meta)
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="lineage")
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="가방", description="🎒 내 인벤토리의 모든 아이템, 강화석, 장비 현황을 확인합니다.")
async def cmd_bag(interaction: discord.Interaction):
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    embed = create_bag_embed(interaction.user, pet, inv)
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="bag")
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="가이드", description="📖 [공식 가이드북] DAMAGOCHI v17.2 플레이어 가이드북을 확인합니다.")
@app_commands.describe(챕터="열람할 가이드북 챕터 번호 (1~8장)")
@app_commands.choices(챕터=[
    app_commands.Choice(name="1장. 입문 & 핵심 게임 루프", value=1),
    app_commands.Choice(name="2장. 10대 신수 종족값 (BST) & 4대 스킬", value=2),
    app_commands.Choice(name="3장. 개체값(IV), 10대 성격 & 5대 속성", value=3),
    app_commands.Choice(name="4장. 레벨 제한, 혼 4종 & 잠재 성장", value=4),
    app_commands.Choice(name="5장. 4대 던전, 방어구 승급 & 종족 보물", value=5),
    app_commands.Choice(name="6장. 5대 레이드 보스 공략 & 방어 태세", value=6),
    app_commands.Choice(name="7장. Ancient 엔드게임, 오메가 & 고대신 ★5", value=7),
    app_commands.Choice(name="8장. 추천 성장 루트 & FAQ", value=8)
])
async def cmd_guide(interaction: discord.Interaction, 챕터: app_commands.Choice[int] = None):
    page_idx = 챕터.value if 챕터 is not None else 1
    embed = create_guide_embed(page_idx)
    view = GuideView(interaction.user, page_idx=page_idx)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="스킬", description="⚔️ 현재 내 신수의 4대 고유 전투 스킬과 전용 보물 정보를 확인합니다.")
async def cmd_skills(interaction: discord.Interaction):
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    embed = create_skills_embed(interaction.user, pet, inv)
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="skills")
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="다시뽑기", description="🎲 [Lv.1 전용] 현재 1레벨인 신수를 새로운 운명의 알로 다시 부화합니다.")
async def cmd_reroll(interaction: discord.Interaction):
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    if pet.level > 1:
        return await interaction.response.send_message("⚠️ 신수 다시 뽑기는 **Lv.1 초기 상태**에서만 가능합니다!", ephemeral=True)
    new_pet = Pet()
    new_inv = Inventory()
    new_inv.equipped_relic = {"species": new_pet.species_key, "level": 0}
    save_user_pet(interaction.user.id, new_pet, new_inv, meta)
    
    shiny_str = "🌟 **[극희귀 황금 샤이니 변이 출현!]**\n" if new_pet.is_shiny else ""
    reroll_msg = (
        f"🎲✨ **[신수 다시 뽑기 완료!]** 새로운 운명의 알이 깨어났습니다!\n"
        f"{shiny_str}"
        f"🐾 **새로운 파트너:** `[{new_pet.name}]` ({new_pet.species_name} {new_pet.rank} · {new_pet.element} 속성 / {new_pet.personality})\n"
        f"📊 **초기 개체값(IV):** `{new_pet.total_iv}/500` (HP {new_pet.hp_iv} / ATK {new_pet.atk_iv} / DEF {new_pet.def_iv} / SPD {new_pet.spd_iv} / CRIT {new_pet.crit_iv})"
    )
    embed, file_att = create_main_embed(interaction.user, new_pet, new_inv, reroll_msg, meta=meta)
    view = DamagochiView(interaction.user, new_pet, new_inv, meta, view_mode="main")
    attachments = [file_att] if file_att else []
    await interaction.response.send_message(embed=embed, attachments=attachments, view=view)

@bot.tree.command(name="상점", description="🛒 24시 신수 편의 상점을 열어 돌봄/성장/치료 물품을 확인합니다.")
async def cmd_shop(interaction: discord.Interaction):
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    embed = create_shop_embed(interaction.user, pet, inv)
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="shop")
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="개발자인증", description="🔑 [관리자] 개발자 모드 보안 잠금/해제를 전환합니다.")
@app_commands.describe(비밀번호="관리자 보안 비밀번호 (기본: 7777)")
async def cmd_dev_auth(interaction: discord.Interaction, 비밀번호: str):
    global DEV_MODE_LOCKED
    if 비밀번호 == DEV_ADMIN_PIN:
        DEV_MODE_LOCKED = not DEV_MODE_LOCKED
        if DEV_MODE_LOCKED:
            msg = "🔒 **[개발자 모드 보안 잠금 완료]**\n개발자 모드 및 치트 콘솔 접근이 안전하게 차단되었습니다."
        else:
            msg = "🔓✨ **[개발자 모드 잠금 해제 완료!]**\n이제 `/개발자모드`, `/신수설정` 및 관리자 치트 콘솔을 자유롭게 이용하실 수 있습니다!"
        await interaction.response.send_message(msg, ephemeral=True)
    else:
        await interaction.response.send_message("🚫 **[인증 실패]** 관리자 비밀번호가 일치하지 않습니다.", ephemeral=True)

@bot.tree.command(name="개발자모드", description="🛠️ 신수 스탯/장비/재화 디버그 및 관리자 치트 콘솔을 엽니다.")
async def cmd_dev_mode(interaction: discord.Interaction):
    if DEV_MODE_LOCKED:
        return await interaction.response.send_message(
            "🔒 **[접근 거부]** 개발자 모드가 보안 잠금 상태입니다.\n"
            "채팅창에 **`/개발자인증 7777`**을 입력하여 잠금을 해제한 후 이용해 주세요! 💕",
            ephemeral=True
        )
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    embed = create_dev_embed(interaction.user, pet, inv)
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="dev_mode")
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="신수설정", description="🛠️ [개발자] 신수의 종족/난이도MAX프리셋/레벨/장비/잠재 등을 자유 설정합니다.")
@app_commands.describe(
    프리셋="원클릭 난이도별 MAX 종결 세팅 (노말MAX, 하드MAX, 악몽MAX, 신화MAX, 고대MAX)",
    종족="변경할 10대 신수 종족",
    레벨="신수 레벨 (1~99)",
    초월="초월 단계 (0~20)",
    애정도="애정도 수치 (0~1000)",
    방어구="장착할 방어구 ID",
    방어구강화="방어구 강화 수치 (0~15)",
    고대성급="고대 방어구 성급 (0~5)",
    보물강화="전용 보물 강화 수치 (0~10)",
    잠재성장="5대 스탯 잠재 성장 % (0~60)",
    샤이니변이="황금 샤이니 변이 On/Off",
    개체값500="PERFECT 500 IV (올 100) 적용 여부",
    골드="보유 골드 수치"
)
@app_commands.choices(프리셋=[
    app_commands.Choice(name="⚪ 노말 MAX (Lv.25 / 가죽+5 / 보물+2 / 잠재 15%)", value="normal"),
    app_commands.Choice(name="🔵 하드 MAX (Lv.50 / 수정+8 / 보물+5 / 잠재 30%)", value="hard"),
    app_commands.Choice(name="🟣 악몽 MAX (Lv.75 / 천계+11 / 보물+8 / 잠재 45%)", value="nightmare"),
    app_commands.Choice(name="🟡 신화 MAX (Lv.99 / 고대신+15 / 보물+10 / 잠재 60%)", value="mythic"),
    app_commands.Choice(name="🌌 고대 MAX (Lv.99 / 고대신+15★5 / 보물+10 / 잠재 60% / 초월 20 / 500 IV / 샤이니)", value="ancient")
])
@app_commands.choices(종족=[
    app_commands.Choice(name="🐯 호랑이 (백호)", value="호랑이"),
    app_commands.Choice(name="🦁 사자 (황금 사자)", value="사자"),
    app_commands.Choice(name="🐺 늑대 (달빛 늑대)", value="늑대"),
    app_commands.Choice(name="🐉 드래곤", value="드래곤"),
    app_commands.Choice(name="🦅 불사조 (주작)", value="불사조"),
    app_commands.Choice(name="🐢 현무 (현무 거북)", value="현무"),
    app_commands.Choice(name="🦊 구미호", value="구미호"),
    app_commands.Choice(name="🪽 그리핀", value="그리핀"),
    app_commands.Choice(name="🦄 기린 (신성 기린)", value="기린"),
    app_commands.Choice(name="🐲 바하무트 (신화)", value="바하무트")
])
@app_commands.choices(방어구=[
    app_commands.Choice(name="가죽 갑옷 (일반)", value="leather_armor"),
    app_commands.Choice(name="수정 갑옷 (고급)", value="crystal_armor"),
    app_commands.Choice(name="용린 갑옷 (희귀)", value="dragon_armor"),
    app_commands.Choice(name="생명의 로브 (희귀)", value="life_robe"),
    app_commands.Choice(name="질풍 경갑 (영웅)", value="wind_armor"),
    app_commands.Choice(name="심연의 갑주 (영웅)", value="abyss_armor"),
    app_commands.Choice(name="천계 갑주 (전설)", value="celestial_armor"),
    app_commands.Choice(name="고대신의 갑옷 (신화)", value="ancient_god_armor")
])
async def cmd_custom_set(
    interaction: discord.Interaction,
    프리셋: app_commands.Choice[str] = None,
    종족: app_commands.Choice[str] = None,
    레벨: int = None,
    초월: int = None,
    애정도: int = None,
    방어구: app_commands.Choice[str] = None,
    방어구강화: int = None,
    고대성급: int = None,
    보물강화: int = None,
    잠재성장: int = None,
    샤이니변이: bool = None,
    개체값500: bool = None,
    골드: int = None
):
    if DEV_MODE_LOCKED:
        return await interaction.response.send_message(
            "🔒 **[접근 거부]** 개발자 모드가 보안 잠금 상태입니다.\n"
            "채팅창에 **`/개발자인증 7777`**을 입력하여 잠금을 해제한 후 이용해 주세요! 💕",
            ephemeral=True
        )
    pet, inv, meta, _ = get_or_create_user_pet(interaction.user.id)
    logs = []

    if 프리셋 is not None:
        suc, p_msg = pet.apply_preset(프리셋.value, inv, meta)
        logs.append(p_msg)

    if 종족 is not None:
        pet.change_species(종족.value, inv)
        logs.append(f"• 종족: `{종족.name}`")
    if 레벨 is not None:
        pet.level = max(1, min(99, 레벨))
        pet.exp = 0
        pet.max_exp = pet.calc_req_exp(pet.level)
        logs.append(f"• 레벨: `Lv.{pet.level}`")
    if 초월 is not None:
        pet.transcend_level = max(0, min(20, 초월))
        logs.append(f"• 초월: `Lv.{pet.transcend_level}`")
    if 애정도 is not None:
        pet.total_affection = max(0, min(1000, 애정도))
        pet.affection = pet.total_affection
        logs.append(f"• 애정도: `{pet.total_affection}/1000`")
    if 방어구 is not None or 방어구강화 is not None or 고대성급 is not None:
        if not inv.equipped_armor:
            inv.equipped_armor = {"armor_id": "leather_armor", "level": 0, "stars": 0, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
        if 방어구 is not None:
            inv.equipped_armor["armor_id"] = 방어구.value
        if 방어구강화 is not None:
            inv.equipped_armor["level"] = max(0, min(15, 방어구강화))
        if 고대성급 is not None:
            inv.equipped_armor["stars"] = max(0, min(5, 고대성급))
        a_name = ARMORS_DATABASE.get(inv.equipped_armor["armor_id"], {}).get("name", "방어구")
        logs.append(f"• 방어구: `[{a_name} +{inv.equipped_armor['level']} ★{inv.equipped_armor.get('stars', 0)}]`")
    if 보물강화 is not None:
        if not inv.equipped_relic:
            inv.equipped_relic = {"species": pet.species_key, "level": 0}
        inv.equipped_relic["level"] = max(0, min(10, 보물강화))
        logs.append(f"• 전용 보물: `+{inv.equipped_relic['level']}강`")
    if 잠재성장 is not None:
        pot_p = max(0.0, min(0.60, 잠재성장 / 100.0))
        pet.potential_growth = {"hp": pot_p, "atk": pot_p, "def": pot_p, "spd": pot_p, "crit": pot_p}
        logs.append(f"• 5대 스탯 잠재 성장: `+{int(pot_p*100)}%`")
    if 샤이니변이 is not None:
        pet.is_shiny = 샤이니변이
        logs.append(f"• 샤이니 변이: `{'🌟 On' if pet.is_shiny else 'Off'}`")
    if 개체값500 is not None and 개체값500:
        pet.hp_iv = 100; pet.atk_iv = 100; pet.def_iv = 100; pet.spd_iv = 100; pet.crit_iv = 100
        pet.total_iv = 500
        pet.rank = "👑 PERFECT (완벽)"
        logs.append(f"• 개체값: `PERFECT 500 IV (올 100)`")
    if 골드 is not None:
        pet.coins = max(0, 골드)
        logs.append(f"• 골드: `{pet.coins:,}G`")

    save_user_pet(interaction.user.id, pet, inv, meta)
    b_stats = pet.get_battle_stats(inv)
    
    desc = "🛠️ **[신수 커스텀 설정 완료!]**\n" + "\n".join(logs) if logs else "변경할 항목을 입력하지 않았습니다."
    desc += f"\n\n⚔️ **현재 신수 전투력:** `👑 {b_stats['combat_power']:,} CP`"
    desc += "\n\n💡 _하단 버튼을 누르면 설정된 최신 스탯의 신수 콘솔을 바로 조작하실 수 있습니다!_"
    
    embed = discord.Embed(title=f"🛠️ {pet.name} ({pet.species_name}) 스탯 커스텀 완료", description=desc, color=discord.Color.gold())
    view = DamagochiView(interaction.user, pet, inv, meta, view_mode="dev_mode")
    await interaction.response.send_message(embed=embed, view=view)

def main():
    token = load_token()
    if not token or token == "YOUR_DISCORD_BOT_TOKEN_HERE":
        print(f"🚫 '{CONFIG_FILE}'에 유효한 디스코드 봇 토큰을 입력해 주세요.")
        return
    bot.run(token)

if __name__ == "__main__":
    main()
