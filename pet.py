# -*- coding: utf-8 -*-
"""
🐾 DAMAGOCHI Pet Entity & Total Equipment Matrix Engine (v17.2)
10대 신수 BST 리마스터, 잠재 혼 성장, 종족 전용 보물(+10 강화), 방어구 승급 강화 보존, 초월 및 개발자 모드
"""

import random
import time
from species import Genetics, SPECIES_DATABASE, PERSONALITIES
from shop import EXCLUSIVE_RELICS, ARMORS_DATABASE

ASCII_ARTS = {
    "드래곤": {
        1: r"""
           / \__
          (    @\___   ~[아기 드래곤 삐약]
          /         O
         /   (_____/
        /_____/   U
        """,
        2: r"""
             / \__     🔥
            (    @\___/  [불꽃의 드래곤]
           /         O
          /   (_____/
         /_____/   U
        """,
        3: r"""
           \  /\  /    🔥🔥🔥
           (O)(O)/     [업화의 극의 드래곤]
          /  __  \
         /  (  )  \   === 크와아앙! ===
        /__/ || \__\
        """,
        4: r"""
         .---.  ✨👑✨  .---.
        /  ★  \ ( ✦∇✦ )/  ★  \   [태초의 전설 드래곤 오메가]
       |  🔥🔥 |  \💥/  |  🔥🔥 |
        \_____/         \_____/
        """
    },
    "default": {
        1: r"""
            /\_/\
           ( o.o )  ~응애!
            > ^ <
           (______)
        """,
        2: r"""
           |\---/|  ✨
           |^ o ^| / [각성 형태]
            \_♡_/
           /|   |\
          (_|_|_|_)
        """,
        3: r"""
           / \__    🔥🔥
          (    ^ \___/ [극의 형태]
          /         ♥
         /   (_____/
        /_____/   U
        """,
        4: r"""
          .---.  ✨👑✨  .---.
         /  ★  \ ( ✦∇✦ )/  ★  \  [전설의 초월 오메가]
        |   ♡   |  \♥/  |   ♡   |
         \_____/         \_____/
        """
        }
}

import math

# 💖 DAMAGOCHI 애정도 10단계 누적 시스템 테이블 (DAMAGOCHI_AFFECTION_10_LEVEL_SYSTEM.md & v14.1)
AFFECTION_LEVELS = {
    1: {"name": "낯섦", "icon": "🤍", "quote": "아직 당신을 낯설어합니다.", "bonus": "기본 상태"},
    2: {"name": "관심", "icon": "🤍", "quote": "당신을 조금씩 바라보기 시작합니다.", "bonus": "기본 상태"},
    3: {"name": "익숙함", "icon": "💛", "quote": "이제 당신의 손길이 익숙합니다.", "bonus": "돌봄 효과 +3%"},
    4: {"name": "친근함", "icon": "💛", "quote": "당신이 다가오면 먼저 반응합니다.", "bonus": "훈련 EXP +2%"},
    5: {"name": "친밀함", "icon": "💚", "quote": "당신과 함께 있는 것을 좋아합니다.", "bonus": "애정 획득량 +5%"},
    6: {"name": "호감", "icon": "💚", "quote": "당신을 잘 따릅니다.", "bonus": "전투 EXP +2%"},
    7: {"name": "신뢰", "icon": "💙", "quote": "당신을 믿고 전장에 나섭니다.", "bonus": "전투 EXP +4%"},
    8: {"name": "깊은 신뢰", "icon": "💙", "quote": "어떤 상황에서도 당신을 신뢰합니다.", "bonus": "모험 기력 소모 -2%"},
    9: {"name": "깊은 유대", "icon": "💖", "quote": "당신과 깊은 유대를 맺었습니다.", "bonus": "치명상 확률 -10%"},
    10: {"name": "절대적 유대", "icon": "👑", "quote": "어떤 위험 속에서도 당신을 믿습니다.", "bonus": "치명상 확률 -20% & 최초 1회 재굴림"}
}

def calc_combat_power(hp: int, atk: int, defence: int, spd: int, crit: int) -> int:
    """
    ⚔️ v14.2 플레이어 전투력(CP) 공식:
    EffectiveHP = HP × (1 + DEF / 500)
    EffectiveOffense = ATK × (1 + CritRate) × (1 + SPD / 1000)
    CombatPower = 10 × √(EffectiveHP × EffectiveOffense) (10단위 반올림)
    """
    crit_rate = min(0.70, crit / (crit + 900.0))
    effective_hp = hp * (1.0 + defence / 500.0)
    effective_offense = atk * (1.0 + crit_rate) * (1.0 + spd / 1000.0)
    cp = 10.0 * math.sqrt(max(1.0, effective_hp * effective_offense))
    return int(round(cp / 10.0) * 10)

class Pet:
    def __init__(self, custom_data=None, parent_pet=None, keep_species: bool = True):
        if custom_data:
            self.load_from_dict(custom_data)
        else:
            if parent_pet:
                gene = Genetics.hatch_reincarnated_egg(parent_pet, keep_species=keep_species)
                self.generation = getattr(parent_pet, "generation", 1) + 1
            else:
                gene = Genetics.hatch_random_egg()
                self.generation = 1

            self.species_key = gene["species_key"]
            self.species_name = gene["species_name"]
            self.emoji = gene["emoji"]
            self.tier = gene["tier"]
            self.element = gene["element"]
            self.role = gene["role"]
            self.role_desc = gene["role_desc"]
            self.effect = gene["effect"]
            self.is_shiny = gene["is_shiny"]
            
            # 5대 개체값 (5V)
            self.hp_iv = gene["hp_iv"]
            self.atk_iv = gene["atk_iv"]
            self.def_iv = gene["def_iv"]
            self.spd_iv = gene["spd_iv"]
            self.crit_iv = gene["crit_iv"]
            self.total_iv = gene["total_iv"]
            self.rank = gene["rank"]
            
            self.charm = gene["charm"]
            self.affection = 0
            self.total_affection = 0 # 💖 0~1000 누적 애정도 (Lv.1 0/100 시작)
            self.personality = gene.get("personality", "용맹함")
            _, self.name = Genetics.get_form_title(self.species_key, self.element, 1, self.is_shiny)
            self.is_custom_name = False
            self.level = 1
            self.stage = 1
            self.exp = 0
            self.max_exp = self.calc_req_exp(1)
            
            self.transcend_level = 0
            self.transcend_exp = 0
            self.has_relic = False # 호환성 플래그
            
            self.hunger = 100
            self.cleanliness = 100
            self.happiness = 100
            self.energy = 100    # ⚡ 생활 에너지 (훈련/돌봄)
            self.stamina = 100   # 🔥 모험 기력 (던전/레이드)
            self.health = 100
            self.coins = 1000
            self.poops = 0
            self.is_sleeping = False
            self.is_sick = False
            self.last_pet_time = 0.0 # ❤️ 쓰다듬기 쿨타임 (60초)
            self.potential_growth = {"hp": 0.0, "atk": 0.0, "def": 0.0, "spd": 0.0, "crit": 0.0} # 🌱 5대 스탯 잠재 성장 (스탯당 0% ~ 60%)
            self.total_adventures = 0
            self.total_dungeon_clears = 0
            self.raid_clears = {"1": [], "2": [], "3": [], "4": [], "5": []} # 🚪 난이도별 클리어한 보스 ID 목록 (v16.2 관문)
            self.boss_kills = {} # 👑 "diff_boss": 누적 킬 수 (예: "5_1": 10)

    @staticmethod
    def calc_req_exp(lvl: int) -> int:
        """
        🐾 레벨업 요구 경험치 공식 (v17.2 2차 다항 곡선 스케일링)
        RequiredEXP = 100 + (Level - 1) * 60 + 5 * (Level ** 1.8)
        """
        return int(100 + (lvl - 1) * 60 + 5 * (lvl ** 1.8))

    @property
    def max_energy(self) -> int:
        sp_data = SPECIES_DATABASE.get(self.species_key, {})
        return sp_data.get("max_life_energy", 100)

    def rename(self, new_name: str) -> tuple[bool, str]:
        cleaned = new_name.strip()
        if not cleaned:
            return False, "⚠️ 신수의 이름은 공백일 수 없습니다!"
        if len(cleaned) > 15:
            return False, "⚠️ 신수의 이름은 최대 15자까지 가능합니다!"
        
        old_name = self.name
        self.name = cleaned
        self.is_custom_name = True
        return True, f"✨ [{old_name}]의 이름이 💖 [{self.name}](으)로 성공적으로 변경되었습니다!"

    def change_species(self, new_sp_key: str, inventory=None) -> tuple[bool, str]:
        """🛠️ 개발자 모드: 신수의 종족을 원하는 10대 신수로 즉시 변경"""
        if new_sp_key not in SPECIES_DATABASE:
            return False, f"존재하지 않는 종족 키입니다: {new_sp_key}"

        sp_data = SPECIES_DATABASE[new_sp_key]
        old_sp = getattr(self, "species_name", "신수")
        
        self.species_key = new_sp_key
        self.species_name = sp_data.get("name", new_sp_key)
        self.emoji = sp_data.get("emoji", "🐾")
        self.tier = sp_data.get("tier", "일반")
        self.element = sp_data.get("element", "무속성")
        self.role = sp_data.get("role", "공격형")
        self.role_desc = sp_data.get("role_desc", "")
        self.effect = sp_data.get("effect", "atk_boost")

        if not getattr(self, "is_custom_name", False):
            self.name = f"아기 {self.species_name}" if self.level <= 10 else self.species_name

        if inventory:
            if inventory.equipped_relic:
                r_lvl = inventory.equipped_relic.get("level", 0)
                inventory.equipped_relic = {"species": new_sp_key, "level": r_lvl}
            else:
                inventory.equipped_relic = {"species": new_sp_key, "level": 0}

        return True, f"✨🐾 **[{old_sp}]**에서 🌟 **[{self.emoji} {self.species_name}]**(으)로 종족이 즉시 변경되었습니다!"

    def apply_preset(self, preset_name: str, inventory, meta: dict = None) -> tuple[bool, str]:
        """🛠️ 개발자 모드: 난이도별 MAX 프리셋 원클릭 세팅"""
        p_name = preset_name.lower().strip()
        
        # 1. ⚪ 노말 MAX
        if p_name in ["normal", "normal_max", "노말", "노말max"]:
            self.level = 25
            self.exp = 0
            self.max_exp = self.calc_req_exp(25)
            self.transcend_level = 0
            self.potential_growth = {"hp": 0.15, "atk": 0.15, "def": 0.15, "spd": 0.15, "crit": 0.15}
            self.health = 100; self.stamina = 100; self.energy = 100; self.hunger = 100; self.cleanliness = 100; self.happiness = 100
            self.is_critically_injured = False; self.is_sick = False
            self.coins = max(self.coins, 100000)
            if inventory:
                inventory.equipped_armor = {"armor_id": "leather_armor", "level": 5, "stars": 0, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
                inventory.equipped_relic = {"species": self.species_key, "level": 2}
            self.raid_clears = {"1": [1, 2, 3, 4], "2": [], "3": [], "4": [], "5": []}
            return True, "⚪ **[노말 MAX 프리셋 적용 완료!]**\n• Lv.25 / 가죽 갑옷 +5 / 보물 +2 / 잠재 +15% / 노말 4종 올클리어"

        # 2. 🔵 하드 MAX
        elif p_name in ["hard", "hard_max", "하드", "하드max"]:
            self.level = 50
            self.exp = 0
            self.max_exp = self.calc_req_exp(50)
            self.transcend_level = 0
            self.potential_growth = {"hp": 0.30, "atk": 0.30, "def": 0.30, "spd": 0.30, "crit": 0.30}
            self.health = 100; self.stamina = 100; self.energy = 100; self.hunger = 100; self.cleanliness = 100; self.happiness = 100
            self.is_critically_injured = False; self.is_sick = False
            self.coins = max(self.coins, 500000)
            if inventory:
                inventory.equipped_armor = {"armor_id": "crystal_armor", "level": 8, "stars": 0, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
                inventory.equipped_relic = {"species": self.species_key, "level": 5}
            self.raid_clears = {"1": [1, 2, 3, 4], "2": [1, 2, 3, 4], "3": [], "4": [], "5": []}
            return True, "🔵 **[하드 MAX 프리셋 적용 완료!]**\n• Lv.50 / 수정 갑옷 +8 / 보물 +5 / 잠재 +30% / 하드 4종 올클리어"

        # 3. 🟣 악몽 MAX
        elif p_name in ["nightmare", "nightmare_max", "악몽", "악몽max"]:
            self.level = 75
            self.exp = 0
            self.max_exp = self.calc_req_exp(75)
            self.transcend_level = 5
            self.potential_growth = {"hp": 0.45, "atk": 0.45, "def": 0.45, "spd": 0.45, "crit": 0.45}
            self.health = 100; self.stamina = 100; self.energy = 100; self.hunger = 100; self.cleanliness = 100; self.happiness = 100
            self.is_critically_injured = False; self.is_sick = False
            self.coins = max(self.coins, 1000000)
            if inventory:
                inventory.equipped_armor = {"armor_id": "celestial_armor", "level": 11, "stars": 0, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
                inventory.equipped_relic = {"species": self.species_key, "level": 8}
            self.raid_clears = {"1": [1, 2, 3, 4], "2": [1, 2, 3, 4], "3": [1, 2, 3, 4], "4": [], "5": []}
            if meta is not None: meta["cleared_nightmare"] = True
            return True, "🟣 **[악몽 MAX 프리셋 적용 완료!]**\n• Lv.75 / 천계 갑주 +11 / 보물 +8 / 잠재 +45% / 악몽 4종 올클리어"

        # 4. 🟡 신화 MAX
        elif p_name in ["mythic", "mythic_max", "신화", "신화max"]:
            self.level = 99
            self.exp = 0
            self.max_exp = self.calc_req_exp(99)
            self.transcend_level = 10
            self.potential_growth = {"hp": 0.60, "atk": 0.60, "def": 0.60, "spd": 0.60, "crit": 0.60}
            self.health = 100; self.stamina = 100; self.energy = 100; self.hunger = 100; self.cleanliness = 100; self.happiness = 100
            self.is_critically_injured = False; self.is_sick = False
            self.coins = max(self.coins, 3000000)
            if inventory:
                inventory.equipped_armor = {"armor_id": "mythic_celestial_armor", "level": 15, "stars": 0, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
                inventory.equipped_relic = {"species": self.species_key, "level": 10}
            self.raid_clears = {"1": [1, 2, 3, 4], "2": [1, 2, 3, 4], "3": [1, 2, 3, 4], "4": [1, 2, 3, 4], "5": []}
            if meta is not None:
                meta["cleared_nightmare"] = True
                meta["cleared_mythic"] = True
            return True, "🟡 **[신화 MAX 프리셋 적용 완료!]**\n• Lv.99 / 천계신의 갑주 +15 / 보물 +10 / 잠재 +60% / 신화 4종 올클리어"

        # 5. 🌌 고대 MAX (신수왕 종결 Zenith)
        elif p_name in ["ancient", "ancient_max", "고대", "고대max", "zenith", "종결"]:
            self.level = 99
            self.exp = 0
            self.max_exp = self.calc_req_exp(99)
            self.is_shiny = True
            self.hp_iv = 100; self.atk_iv = 100; self.def_iv = 100; self.spd_iv = 100; self.crit_iv = 100
            self.total_iv = 500
            self.rank = "👑 PERFECT (완벽)"
            self.transcend_level = 20
            self.total_affection = 1000; self.affection = 1000
            self.potential_growth = {"hp": 0.60, "atk": 0.60, "def": 0.60, "spd": 0.60, "crit": 0.60}
            self.health = 100; self.stamina = 100; self.energy = 100; self.hunger = 100; self.cleanliness = 100; self.happiness = 100
            self.is_critically_injured = False; self.is_sick = False
            self.coins = max(self.coins, 10000000)
            if inventory:
                inventory.equipped_armor = {"armor_id": "mythic_celestial_armor", "level": 15, "stars": 5, "opt": {"key": "def_pct", "name": "방어력", "val": 0.07}}
                inventory.equipped_relic = {"species": self.species_key, "level": 10}
            self.raid_clears = {"1": [1, 2, 3, 4], "2": [1, 2, 3, 4], "3": [1, 2, 3, 4], "4": [1, 2, 3, 4], "5": [1, 2, 3, 4, 5]}
            self.boss_kills = {"5_1": 15, "5_2": 15, "5_3": 15, "5_4": 15, "5_5": 15}
            if meta is not None:
                meta["cleared_nightmare"] = True
                meta["cleared_mythic"] = True
                meta["cleared_ancient"] = True
                meta["cleared_bosses"] = ["ent_ancient", "crystal_ancient", "ifrit_ancient", "guardian_ancient", "omega_ancient"]
            return True, "🌌👑 **[고대 MAX 종결 (Zenith) 프리셋 적용 완료!]**\n• Lv.99 / 초월 20 / 애정 10 / 잠재 60% / 500 IV / 샤이니 / 천계신의 갑주+15★5 / 보물+10 / 골드 1,000만G"

        return False, f"알 수 없는 프리셋 이름입니다: {preset_name}"

    def upgrade_potential(self, stat_key: str, inventory) -> tuple[bool, str]:
        """
        🌱 v17.2 혼(Soul) 소모형 잠재 성장 업그레이드 시스템
        - 5대 스탯 각 0% -> 60% (3%씩 총 20단계)
        - Normal (1~5단계: 0%->15%): 일반 혼 1, 4, 9, 16, 25개
        - Hard (6~10단계: 15%->30%): 고급 혼 1, 4, 9, 16, 25개
        - Nightmare (11~15단계: 30%->45%): 전설 혼 1, 4, 9, 16, 25개
        - Mythic (16~20단계: 45%->60%): 신화 혼 1, 4, 9, 16, 25개
        """
        stat_names = {"hp": "❤️ 체력", "atk": "⚔️ 공격력", "def": "🛡️ 방어력", "spd": "⚡ 스피드", "crit": "💥 치명타"}
        if stat_key not in stat_names:
            return False, "올바르지 않은 스탯 키입니다."

        if not hasattr(self, "potential_growth") or not isinstance(self.potential_growth, dict):
            self.potential_growth = {"hp": 0.0, "atk": 0.0, "def": 0.0, "spd": 0.0, "crit": 0.0}

        cur_val = self.potential_growth.get(stat_key, 0.0)
        cur_step = int(round(cur_val / 0.03))
        if cur_step >= 20:
            return False, f"이미 [{stat_names[stat_key]}] 잠재 성장이 최고 단계(+60.0% MAX)에 도달했습니다!"

        next_step = cur_step + 1
        sub_step = (next_step - 1) % 5 + 1
        soul_req_table = [1, 4, 9, 16, 25]
        req_count = soul_req_table[sub_step - 1]

        tier_idx = (next_step - 1) // 5
        soul_ids = ["soul_normal", "soul_hard", "soul_nightmare", "soul_mythic"]
        soul_names = ["⚪ 일반 혼", "🔵 고급 혼", "🟣 전설 혼", "🟡 신화 혼"]
        target_soul_id = soul_ids[tier_idx]
        target_soul_name = soul_names[tier_idx]

        if not inventory or inventory.items.get(target_soul_id, 0) < req_count:
            cur_have = inventory.items.get(target_soul_id, 0) if inventory else 0
            return False, f"🚫 [{target_soul_name}]이(가) 부족합니다! (필요: {req_count}개, 보유: {cur_have}개 | 레이드 토벌로 획득)"

        inventory.remove_item(target_soul_id, req_count)
        self.potential_growth[stat_key] = round(next_step * 0.03, 4)
        new_pct = int(round(self.potential_growth[stat_key] * 100))

        return True, f"🌱✨ **[{stat_names[stat_key]}] 잠재 성장 대성공!**\n• 현재 잠재 스탯: **+{new_pct}%** (소모: {target_soul_name} {req_count}개)"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "is_custom_name": getattr(self, "is_custom_name", False),
            "species_key": getattr(self, "species_key", "드래곤"),
            "species_name": getattr(self, "species_name", "드래곤"),
            "emoji": getattr(self, "emoji", "🐉"),
            "tier": getattr(self, "tier", "희귀 (Rare)"),
            "element": getattr(self, "element", "화염"),
            "role": getattr(self, "role", "공격형"),
            "role_desc": getattr(self, "role_desc", ""),
            "effect": getattr(self, "effect", "atk_boost"),
            "is_shiny": getattr(self, "is_shiny", False),
            "hp_iv": getattr(self, "hp_iv", 70),
            "atk_iv": getattr(self, "atk_iv", 70),
            "def_iv": getattr(self, "def_iv", 70),
            "spd_iv": getattr(self, "spd_iv", 70),
            "crit_iv": getattr(self, "crit_iv", 70),
            "total_iv": getattr(self, "total_iv", 350),
            "charm": getattr(self, "charm", 70),
            "affection": getattr(self, "affection", 0),
            "total_affection": getattr(self, "total_affection", 0), # 💖 0~1000
            "potential_growth": getattr(self, "potential_growth", {"hp": 0.0, "atk": 0.0, "def": 0.0, "spd": 0.0, "crit": 0.0}),
            "personality": getattr(self, "personality", "용맹함"),
            "rank": getattr(self, "rank", "✨ S (우수)"),
            "generation": getattr(self, "generation", 1),
            "level": self.level,
            "stage": self.stage,
            "exp": self.exp,
            "max_exp": self.max_exp,
            "transcend_level": getattr(self, "transcend_level", 0),
            "transcend_exp": getattr(self, "transcend_exp", 0),
            "has_relic": getattr(self, "has_relic", False),
            "hunger": self.hunger,
            "cleanliness": self.cleanliness,
            "happiness": self.happiness,
            "energy": getattr(self, "energy", 100),
            "stamina": getattr(self, "stamina", 100),
            "health": self.health,
            "coins": self.coins,
            "poops": self.poops,
            "is_sleeping": self.is_sleeping,
            "is_sick": self.is_sick,
            "is_critically_injured": getattr(self, "is_critically_injured", False),
            "is_dead": getattr(self, "is_dead", False),
            "death_date": getattr(self, "death_date", None),
            "death_boss": getattr(self, "death_boss", None),
            "death_difficulty": getattr(self, "death_difficulty", None),
            "death_count": getattr(self, "death_count", 0),
            "potential_growth": getattr(self, "potential_growth", {"hp": 0.0, "atk": 0.0, "def": 0.0, "spd": 0.0, "crit": 0.0}),
            "total_adventures": getattr(self, "total_adventures", 0),
            "total_dungeon_clears": getattr(self, "total_dungeon_clears", 0),
            "last_pet_time": getattr(self, "last_pet_time", 0.0),
            "raid_clears": getattr(self, "raid_clears", {"1": [], "2": [], "3": [], "4": [], "5": []}),
            "boss_kills": getattr(self, "boss_kills", {})
        }

    def load_from_dict(self, data: dict):
        self.name = data.get("name", "아기 신수")
        self.is_custom_name = data.get("is_custom_name", False)
        self.species_key = data.get("species_key", "드래곤")
        self.species_name = data.get("species_name", "드래곤")
        self.emoji = data.get("emoji", "🐉")
        self.tier = data.get("tier", "희귀 (Rare)")
        self.element = data.get("element", "화염")
        self.role = data.get("role", "공격형")
        self.role_desc = data.get("role_desc", "")
        self.effect = data.get("effect", "atk_boost")
        self.is_shiny = data.get("is_shiny", False)
        self.hp_iv = data.get("hp_iv", 70)
        self.atk_iv = data.get("atk_iv", 70)
        self.def_iv = data.get("def_iv", 70)
        self.spd_iv = data.get("spd_iv", 70)
        self.crit_iv = data.get("crit_iv", 70)
        self.total_iv = data.get("total_iv", 350)
        self.charm = data.get("charm", 70)
        self.total_affection = data.get("total_affection", data.get("affection", 0))
        self.affection = self.total_affection
        self.personality = data.get("personality", "용맹함")
        self.rank = data.get("rank", "✨ S (우수)")
        self.generation = data.get("generation", 1)
        self.level = data.get("level", 1)
        self.stage = data.get("stage", 1)
        self.exp = data.get("exp", 0)
        self.max_exp = data.get("max_exp", self.calc_req_exp(self.level))
        self.transcend_level = data.get("transcend_level", 0)
        self.transcend_exp = data.get("transcend_exp", 0)
        self.has_relic = data.get("has_relic", False)
        self.hunger = data.get("hunger", 100)
        self.cleanliness = data.get("cleanliness", 100)
        self.happiness = data.get("happiness", 100)
        self.energy = data.get("energy", 100)
        self.stamina = data.get("stamina", getattr(self, "energy", 100))
        self.health = data.get("health", 100)
        self.coins = data.get("coins", 1000)
        self.poops = data.get("poops", 0)
        self.is_sleeping = data.get("is_sleeping", False)
        self.is_sick = data.get("is_sick", False)
        self.is_critically_injured = data.get("is_critically_injured", False)
        self.is_dead = data.get("is_dead", False)
        self.death_date = data.get("death_date", None)
        self.death_boss = data.get("death_boss", None)
        self.death_difficulty = data.get("death_difficulty", None)
        self.death_count = data.get("death_count", 0)
        self.potential_growth = data.get("potential_growth", {"hp": 0.0, "atk": 0.0, "def": 0.0, "spd": 0.0, "crit": 0.0})
        self.total_adventures = data.get("total_adventures", 0)
        self.total_dungeon_clears = data.get("total_dungeon_clears", 0)
        self.last_pet_time = data.get("last_pet_time", 0.0)
        self.raid_clears = data.get("raid_clears", {"1": [], "2": [], "3": [], "4": [], "5": []})
        self.boss_kills = data.get("boss_kills", {})

    def reincarnate(self, inventory=None, keep_species: bool = True) -> tuple[bool, str]:
        """
        🔄 v17.1 만렙(Lv.99) 환생의 의식
        - Lv, 방어구(+0), 방어구 강화(+0), 보물 강화(+0), 잠재 성장(0%), 애정도(Lv.1 0/100) 초기화
        - 칭호(유지), 종족(유지), 성격(유지), 속성(유지)
        - IV 혈통 50% 직계 유전 + 50% 롤 (max(parent-10, 0) ~ 100)
        """
        if self.level < 99:
            return False, f"⚠️ 환생은 **Lv.99 만렙**에 도달한 신수만 진행할 수 있습니다! (현재: Lv.{self.level})"

        gene = Genetics.hatch_reincarnated_egg(self, keep_species=keep_species)
        
        self.hp_iv = gene["hp_iv"]
        self.atk_iv = gene["atk_iv"]
        self.def_iv = gene["def_iv"]
        self.spd_iv = gene["spd_iv"]
        self.crit_iv = gene["crit_iv"]
        self.total_iv = gene["total_iv"]
        self.rank = gene["rank"]
        self.is_shiny = gene["is_shiny"]
        
        self.generation = getattr(self, "generation", 1) + 1
        self.level = 1
        self.stage = 1
        self.exp = 0
        self.max_exp = self.calc_req_exp(1)
        self.transcend_level = 0
        self.transcend_exp = 0
        self.potential_growth = {"hp": 0.0, "atk": 0.0, "def": 0.0, "spd": 0.0, "crit": 0.0}
        self.affection = 0
        self.total_affection = 0
        self.raid_clears = {"1": [], "2": [], "3": [], "4": [], "5": []}
        self.is_critically_injured = False
        self.is_dead = False
        self.health = 100
        self.hunger = 100
        self.cleanliness = 100
        self.happiness = 100
        self.energy = 100
        self.stamina = 100

        if inventory:
            inventory.equipped_armor = {
                "armor_id": "leather_armor",
                "level": 0,
                "stars": 0,
                "opt": None
            }
            inventory.equipped_relic = {
                "species": self.species_key,
                "level": 0
            }

        return True, (
            f"🌌✨ **[환생의 의식 완료!]**\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🐣 **제{self.generation}세대 [{self.name}]**(으)로 새롭게 태어났습니다!\n"
            f"🧬 **계승된 혈통 IV:** `{self.rank}` (총합: {self.total_iv}/500)\n"
            f"• 체력: {self.hp_iv} | 공격: {self.atk_iv} | 방어: {self.def_iv} | 스피드: {self.spd_iv} | 치명: {self.crit_iv}\n"
            f"🛡️ 방어구와 보물이 기본 상태(+0)로 재정비되었으며, 칭호와 종족/성격/속성은 온전히 보존되었습니다!"
        )

    def calculate_injury_rate(self, diff_id: int, gear_resist: float = 0.0) -> tuple[float, float, float, bool]:
        """
        💀 레이드 HP 0 패배 시 치명상(Critical Injury) 위험도 계산 (영구 사망 0% 완전 폐지)
        - 잡지식: 애정도는 단순한 수치가 아니라 위기의 순간 신수를 지켜내는 영혼의 방패입니다!
        - 노말(1)/하드(2): 0.0 (치명상 위험 0%)
        - 악몽(3): 기본 10% (0.10)
        - 신화(4): 기본 25% (0.25)
        - 고대(5): 기본 50% (0.50)
        - 애정도 보호: 80+ (-10%), 60~79 (-5%), 40~59 (-2%)
        - 애정도 100 달성 시 💖 「절대적 유대」 1회 기적 회피 기회 부여
        """
        if diff_id in [1, 2]:
            return 0.0, 0.0, 0.0, False
        
        base_rates = {3: 0.10, 4: 0.25, 5: 0.50}
        base_rate = base_rates.get(diff_id, 0.10)
        
        lvl, _, _ = self.get_affection_state()
        aff_val = self.affection
        
        aff_reduce = 0.0
        if aff_val >= 80:
            aff_reduce = 0.10
        elif aff_val >= 60:
            aff_reduce = 0.05
        elif aff_val >= 40:
            aff_reduce = 0.02
            
        final_rate = max(0.01, min(0.90, base_rate - aff_reduce - gear_resist))
        has_bond_retry = (aff_val >= 100 or lvl >= 10)
        return final_rate, base_rate, aff_reduce, has_bond_retry

    def calculate_death_rate(self, diff_id: int, gear_resist: float = 0.0) -> tuple[float, float, float, bool]:
        """하위 호환용 치명상 위험도 별칭"""
        return self.calculate_injury_rate(diff_id, gear_resist)

    def get_affection_state(self) -> tuple[int, int, dict]:
        """💖 애정도 10단계 상태 반환: (level, progress, info_dict)"""
        tot = max(0, min(1000, getattr(self, "total_affection", 0)))
        if tot >= 1000:
            lvl, prog = 10, 100
        else:
            lvl = (tot // 100) + 1
            prog = tot % 100
        info = AFFECTION_LEVELS.get(lvl, AFFECTION_LEVELS[1])
        return lvl, prog, info

    def gain_affection(self, amount: int) -> list[str]:
        """💖 애정도 획득 및 10단계 레벨업 연출 로그 (절대 감소하지 않음)"""
        old_lvl, _, _ = self.get_affection_state()
        
        # Lv.5+ 친밀함 보너스: 애정 획득량 +5%
        if old_lvl >= 5:
            amount = max(1, int(amount * 1.05))
            
        cur_tot = getattr(self, "total_affection", 0)
        new_tot = min(1000, cur_tot + amount)
        self.total_affection = new_tot
        self.affection = new_tot
        
        new_lvl, new_prog, new_info = self.get_affection_state()
        logs = []
        
        if new_lvl > old_lvl:
            if new_lvl == 10:
                logs.append(f"👑✨ **[절대적 유대 달성!]** 애정도가 최고 단계인 **Lv.10 · 절대적 유대**에 도달했습니다! 「{new_info['quote']}」 💖")
            else:
                logs.append(f"💖✨ **[애정 레벨 상승!]** 애정도가 **Lv.{new_lvl} · {new_info['name']}**으로 올랐습니다! 「{new_info['quote']}」")
        return logs

    def get_battle_stats(self, inventory=None) -> dict:
        """
        7단계 종합 스탯 매트릭스 + 10대 성격 + 종족 보물(+10 강화) + 방어구(+10 강화 & 랜덤 옵션)
        + [신규] 포만감(Hunger) & 행복도(Happiness) 실시간 다이내믹 컨디션 연산
        """
        sp_data = SPECIES_DATABASE.get(self.species_key, {})
        base_hp = sp_data.get("base_hp", 100)
        base_atk = sp_data.get("base_atk", 100)
        base_def = sp_data.get("base_def", 100)
        base_spd = sp_data.get("base_spd", 100)
        base_crit = sp_data.get("base_crit", 100)
        
        # 🎭 10대 성격 보정값
        p_info = PERSONALITIES.get(getattr(self, "personality", "용맹함"), PERSONALITIES["용맹함"])
        p_stat = p_info.get("stat_mod", {})
        p_atk_mult = p_stat.get("atk_mult", 1.0)
        p_def_mult = p_stat.get("def_mult", 1.0)
        p_hp_mult = p_stat.get("hp_mult", 1.0)
        p_spd_mult = p_stat.get("spd_mult", 1.0)
        p_crit_mod = p_stat.get("crit_mod", 0)

        # 🍚 1. 포만감(Hunger) 실시간 스탯 보정
        # 80%+ : 배부름(ATK/DEF +10%), 40~79%: 보통(100%), 20~39%: 허기(ATK-15%, DEF-10%), <20%: 극심한 굶주림(ATK-30%, DEF-25%, HP-20%)
        hunger_atk_mult = 1.0; hunger_def_mult = 1.0; hunger_hp_mult = 1.0
        hunger_status_tag = "보통"
        if self.hunger >= 80:
            hunger_atk_mult = 1.10; hunger_def_mult = 1.10
            hunger_status_tag = "🍗 배부름 (공/방 +10%)"
        elif self.hunger >= 40:
            hunger_status_tag = "🍚 든든함 (기본 100%)"
        elif self.hunger >= 20:
            hunger_atk_mult = 0.85; hunger_def_mult = 0.90
            hunger_status_tag = "⚠️ 허기짐 (공-15%, 방-10%)"
        else:
            hunger_atk_mult = 0.70; hunger_def_mult = 0.75; hunger_hp_mult = 0.80
            hunger_status_tag = "🚨 극심한 굶주림 (공-30%, 방-25%, 체-20%)"

        # 💖 2. 행복도(Happiness) 실시간 스탯 보정
        # 80%+ : 최상의 기분(CRIT/SPD +10%, ATK +5%), 40~79%: 보통(100%), 20~39%: 우울(CRIT/SPD -10%), <20%: 절망(전스탯 -20%)
        happy_atk_mult = 1.0; happy_spd_mult = 1.0; happy_crit_mult = 1.0; happy_all_mult = 1.0
        happy_status_tag = "보통"
        if self.happiness >= 80:
            happy_atk_mult = 1.05; happy_spd_mult = 1.10; happy_crit_mult = 1.10
            happy_status_tag = "🥰 최상의 기분 (치명/속도+10%, 공+5%)"
        elif self.happiness >= 40:
            happy_status_tag = "😊 평온함 (기본 100%)"
        elif self.happiness >= 20:
            happy_spd_mult = 0.90; happy_crit_mult = 0.90
            happy_status_tag = "🥺 우울함 (치명/속도 -10%)"
        else:
            happy_all_mult = 0.80
            happy_status_tag = "😭 절망/슬픔 (전 스탯 -20%)"

        # 🎴 종족 전용 보물 스탯 계산 (장비 HP ×2.5 스케일링)
        relic_hp = 0; relic_atk = 0; relic_def = 0; relic_spd = 0; relic_crit = 0
        relic_level = 0
        relic_is_10 = False
        
        if inventory and inventory.equipped_relic and inventory.equipped_relic["species"] == self.species_key:
            relic_level = inventory.equipped_relic["level"]
            r_info = EXCLUSIVE_RELICS.get(self.species_key, {})
            scale = relic_level / 10.0
            relic_hp = int((r_info.get("base_hp", 0) + (r_info.get("max_hp", 0) - r_info.get("base_hp", 0)) * scale) * 2.5)
            relic_atk = int(r_info.get("base_atk", 0) + (r_info.get("max_atk", 0) - r_info.get("base_atk", 0)) * scale)
            relic_def = int(r_info.get("base_def", 0) + (r_info.get("max_def", 0) - r_info.get("base_def", 0)) * scale)
            relic_spd = int(r_info.get("base_spd", 0) + (r_info.get("max_spd", 0) - r_info.get("base_spd", 0)) * scale)
            if "base_all_stats" in r_info:
                all_s = int(r_info["base_all_stats"] + (30 - r_info["base_all_stats"]) * scale)
                relic_hp += int(all_s * 2.5); relic_atk += all_s; relic_def += all_s; relic_spd += all_s; relic_crit += all_s
            if relic_level >= 10:
                relic_is_10 = True
        elif getattr(self, "has_relic", False):
            r_info = EXCLUSIVE_RELICS.get(self.species_key, {})
            relic_atk = r_info.get("max_atk", 40)

        # 🛡️ 방어구 스탯 & 랜덤 옵션 계산 (v15.4: +15 강화 & ★1~★5 고대 성급 승급 연동)
        armor_hp = 0; armor_def = 0; armor_spd = 0
        armor_dmg_red = 0.0; armor_resist = 0.0
        burn_dmg_red = 0.0; regen_hp_pct = 0.0; heal_bonus = 0.0; first_hit_bonus = 0.0; low_hp_dmg_red = 0.0
        armor_level = 0
        armor_stars = 0
        armor_ancient_passive = None
        opt_def_pct = 0.0; opt_hp_pct = 0.0; opt_spd_pct = 0.0
        
        if inventory and inventory.equipped_armor:
            a_data = ARMORS_DATABASE.get(inventory.equipped_armor["armor_id"], {})
            armor_level = inventory.equipped_armor.get("level", 0)
            armor_stars = inventory.equipped_armor.get("stars", 0)
            
            # +0(1.0x) ~ +15(2.0x) 기본 강화 배율
            enhance_mult = 1.0 + (armor_level * (1.0 / 15.0))
            # ★1(+6%) ~ ★5(+30%) 고대 성급 배율
            star_bonus = {1: 0.06, 2: 0.12, 3: 0.18, 4: 0.24, 5: 0.30}.get(armor_stars, 0.0)
            a_mult = enhance_mult + star_bonus

            armor_hp = int(a_data.get("base_hp", 0) * a_mult)
            armor_def = int(a_data.get("base_def", 0) * a_mult)
            armor_spd = int(a_data.get("base_spd", 0) * a_mult)
            armor_dmg_red = a_data.get("dmg_red", 0.0)
            armor_resist = a_data.get("resist", 0.0)
            burn_dmg_red = a_data.get("burn_dmg_red", 0.0)
            regen_hp_pct = a_data.get("regen_hp_pct", 0.0)
            heal_bonus = a_data.get("heal_bonus", 0.0)
            first_hit_bonus = a_data.get("first_hit_bonus", 0.0)
            low_hp_dmg_red = a_data.get("low_hp_dmg_red", 0.0)
            
            # ★5 달성 시 고대 특효 해금
            if armor_stars >= 5:
                armor_ancient_passive = a_data.get("ancient_passive", None)
            
            if inventory.equipped_armor.get("opt"):
                opt = inventory.equipped_armor["opt"]
                if opt["key"] == "def_pct": opt_def_pct = opt["val"]
                elif opt["key"] == "hp_pct": opt_hp_pct = opt["val"]
                elif opt["key"] == "spd_pct": opt_spd_pct = opt["val"]

        shiny_mult = 1.20 if getattr(self, "is_shiny", False) else 1.0
        aff_lvl, _, _ = self.get_affection_state()
        aff_bonus = 1.15 if aff_lvl >= 8 else 1.0
        trans_mult = 1.0 + (getattr(self, "transcend_level", 0) * 0.01)
        
        hp_mult = 1.25 if "체력" in getattr(self, "role", "") else 1.0
        atk_mult = 1.20 if "공격" in getattr(self, "role", "") or "파괴" in getattr(self, "role", "") else 1.0
        def_mult = 1.25 if "방어" in getattr(self, "role", "") or "수호" in getattr(self, "role", "") else 1.0
        spd_mult = 1.20 if "스피드" in getattr(self, "role", "") else 1.0
        crit_mult = 1.20 if "치명" in getattr(self, "role", "") else 1.0
        
        lvl_factor = 1 + (self.level * 0.08)
        
        # 🧬 Palworld-style IV 잠재력 배율 (IV 0 = 1.0배, IV 100 = 1.30배)
        hp_iv_mult = 1.0 + (getattr(self, "hp_iv", 70) * 0.003)
        atk_iv_mult = 1.0 + (getattr(self, "atk_iv", 70) * 0.003)
        def_iv_mult = 1.0 + (getattr(self, "def_iv", 70) * 0.003)
        spd_iv_mult = 1.0 + (getattr(self, "spd_iv", 70) * 0.003)
        crit_iv_mult = 1.0 + (getattr(self, "crit_iv", 70) * 0.003)

        # 🌱 v17.2 잠재 성장(Potential Growth) 배율 (+0% ~ +60% | 1.0x ~ 1.60x)
        pot_g = getattr(self, "potential_growth", {}) or {}
        pot_hp_mult = 1.0 + pot_g.get("hp", 0.0)
        pot_atk_mult = 1.0 + pot_g.get("atk", 0.0)
        pot_def_mult = 1.0 + pot_g.get("def", 0.0)
        pot_spd_mult = 1.0 + pot_g.get("spd", 0.0)
        pot_crit_mult = 1.0 + pot_g.get("crit", 0.0)

        # 🌿 속성 패시브 스탯 보정 (대지 속성: 최대 HP +25%)
        elem_hp_mult = 1.25 if getattr(self, "element", "") == "대지" else 1.0

        # 🚀 [최종 스탯 공식] HP ×4.0 전용 스케일링 + IV 잠재력 × 잠재 성장 × 레벨 성장 × 성격/컨디션/초월 + 장비 (온전한 최대 체력 스탯)
        max_hp = int(base_hp * hp_iv_mult * lvl_factor * 4.0 * hp_mult * shiny_mult * trans_mult * p_hp_mult * hunger_hp_mult * happy_all_mult * pot_hp_mult * elem_hp_mult * (1.0 + opt_hp_pct)) + relic_hp + armor_hp
        atk = int(base_atk * atk_iv_mult * lvl_factor * atk_mult * shiny_mult * aff_bonus * trans_mult * p_atk_mult * hunger_atk_mult * happy_atk_mult * happy_all_mult * pot_atk_mult) + relic_atk
        defence = int(base_def * def_iv_mult * (1 + self.level * 0.05) * def_mult * shiny_mult * trans_mult * p_def_mult * hunger_def_mult * happy_all_mult * pot_def_mult * (1.0 + opt_def_pct)) + relic_def + armor_def
        spd = int(base_spd * spd_iv_mult * (1 + self.level * 0.03) * spd_mult * shiny_mult * trans_mult * p_spd_mult * happy_spd_mult * happy_all_mult * pot_spd_mult * (1.0 + opt_spd_pct)) + relic_spd + armor_spd
        crit = int((base_crit * crit_iv_mult * (1 + self.level * 0.03) * crit_mult * shiny_mult * aff_bonus + p_crit_mod) * trans_mult * happy_crit_mult * happy_all_mult * pot_crit_mult) + relic_crit
        
        f_max_hp = max(100, max_hp)
        f_cur_hp = max(10, int(f_max_hp * (self.health / 100.0)))
        f_atk = max(10, atk)
        f_def = max(5, defence)
        f_spd = max(10, spd)
        f_crit = max(10, crit)
        
        # ⚔️ v14.2 종합 전투력(Combat Power) 산출 (온전한 최대 스탯 기준)
        cp = calc_combat_power(f_max_hp, f_atk, f_def, f_spd, f_crit)

        return {
            "max_hp": f_max_hp,
            "current_hp": f_cur_hp,
            "atk": f_atk,
            "def": f_def,
            "spd": f_spd,
            "crit": f_crit,
            "combat_power": cp,
            "effect": getattr(self, "effect", "atk_boost"),
            "role": getattr(self, "role", "밸런스형"),
            "personality": getattr(self, "personality", "용맹함"),
            "personality_trait": p_info.get("battle_trait", "none"),
            "affection": getattr(self, "affection", 50),
            "charm": getattr(self, "charm", 70),
            "transcend_level": getattr(self, "transcend_level", 0),
            "relic_level": relic_level,
            "relic_is_10": relic_is_10,
            "armor_level": armor_level,
            "armor_stars": armor_stars,
            "armor_ancient_passive": armor_ancient_passive,
            "armor_dmg_red": armor_dmg_red,
            "armor_resist": armor_resist,
            "burn_dmg_red": burn_dmg_red,
            "regen_hp_pct": regen_hp_pct,
            "heal_bonus": heal_bonus,
            "first_hit_bonus": first_hit_bonus,
            "low_hp_dmg_red": low_hp_dmg_red,
            "hunger_status_tag": hunger_status_tag,
            "happy_status_tag": happy_status_tag,
            "is_critically_injured": getattr(self, "is_critically_injured", False)
        }

    def get_level_cap(self) -> tuple[int, str]:
        """
        🚪 v17.2 레이드 4단계 레벨 성장 관문 (Level Caps)
        - Normal(1) 4대 보스 미클리어 시: Lv.35 캡
        - Hard(2) 4대 보스 미클리어 시: Lv.55 캡
        - Nightmare(3) 4대 보스 미클리어 시: Lv.75 캡
        - Mythic(4) 4대 보스 미클리어 시: Lv.99 캡
        - Mythic 올클리어 시: Lv.99 및 Ancient 고대 개방
        """
        clears = getattr(self, "raid_clears", {})
        
        # 1. Normal 관문
        norm_clears = set(clears.get("1", []) + clears.get(1, []))
        if len(norm_clears) < 4:
            remain = 4 - len(norm_clears)
            return 35, f"⚪ 노말 레이드 4대 보스를 모두 토벌해야 Lv.36 이후로 성장할 수 있습니다! (잔여: {remain}마리)"
            
        # 2. Hard 관문
        hard_clears = set(clears.get("2", []) + clears.get(2, []))
        if len(hard_clears) < 4:
            remain = 4 - len(hard_clears)
            return 55, f"🔵 하드 레이드 4대 보스를 모두 토벌해야 Lv.56 이후로 성장할 수 있습니다! (잔여: {remain}마리)"
            
        # 3. Nightmare 관문
        night_clears = set(clears.get("3", []) + clears.get(3, []))
        if len(night_clears) < 4:
            remain = 4 - len(night_clears)
            return 75, f"🟣 악몽 레이드 4대 보스를 모두 토벌해야 Lv.76 이후로 성장할 수 있습니다! (잔여: {remain}마리)"
            
        # 4. Mythic 관문
        myth_clears = set(clears.get("4", []) + clears.get(4, []))
        if len(myth_clears) < 4:
            remain = 4 - len(myth_clears)
            return 99, f"🟡 신화 레이드 4대 보스를 모두 토벌해야 Ancient 고대 영역에 진입할 수 있습니다! (잔여: {remain}마리)"
            
        return 99, "🌌 최고 레벨 도달! Lv.99 이후에는 초월 성장이 가능합니다."

    def get_relic_max_level(self) -> int:
        """
        🎴 v17.2 종족 전용 보물 단계별 강화 상한 (레이드 관문 연동)
        - 시작: +3
        - Normal 4/4 올클리어: +5
        - Hard 4/4 올클리어: +8
        - Nightmare 4/4 올클리어: +10 (최종 완성 & 고유 특효)
        """
        clears = getattr(self, "raid_clears", {})
        if len(set(clears.get("3", []) + clears.get(3, []))) >= 4:
            return 10
        elif len(set(clears.get("2", []) + clears.get(2, []))) >= 4:
            return 8
        elif len(set(clears.get("1", []) + clears.get(1, []))) >= 4:
            return 5
        return 3

    def record_raid_clear(self, diff_id: int, boss_id: int) -> tuple[bool, int, list[str]]:
        """
        👑 레이드 클리어 기록 및 보스별 킬 카운트 갱신 (v16.2 관문 & 핵 보상)
        반환: (is_first_clear_for_diff_boss, boss_total_kills, logs)
        """
        logs = []
        if not hasattr(self, "raid_clears") or not isinstance(self.raid_clears, dict):
            self.raid_clears = {"1": [], "2": [], "3": [], "4": [], "5": []}
        if not hasattr(self, "boss_kills") or not isinstance(self.boss_kills, dict):
            self.boss_kills = {}
            
        diff_str = str(diff_id)
        if diff_str not in self.raid_clears:
            self.raid_clears[diff_str] = []
            
        is_first = False
        if boss_id not in self.raid_clears[diff_str]:
            self.raid_clears[diff_str].append(boss_id)
            is_first = True
            
        kill_key = f"{diff_id}_{boss_id}"
        self.boss_kills[kill_key] = self.boss_kills.get(kill_key, 0) + 1
        total_kills = self.boss_kills[kill_key]
        
        # 난이도 완파 체크
        if len(set(self.raid_clears[diff_str])) == 5 and is_first:
            diff_names = {1: "⚪ 노말", 2: "🔵 하드", 3: "🟣 악몽", 4: "🟡 신화", 5: "🌌 고대"}
            d_name = diff_names.get(diff_id, "레이드")
            logs.append(f"🎊👑🎉 **[{d_name} 레이드 완전 정복!]** 5대 보스를 모두 토벌하여 다음 단계의 레벨 상한 및 장비 강화 상한이 전격 해제되었습니다!")
            
        return is_first, total_kills, logs

    def gain_exp(self, amount: int) -> list:
        logs = []
        if self.level >= 99:
            # 잡지식: '초월(Transcend)'은 라틴어 transcendere(넘어가다)에서 유래! 게임에선 한계돌파를 뜻해용~
            MAX_TRANSCEND_LEVEL = 20
            if self.transcend_level >= MAX_TRANSCEND_LEVEL:
                logs.append(f"🌌 **초월이 최고 단계 Lv.{MAX_TRANSCEND_LEVEL}에 도달했습니다!** (초월 EXP 획득 중단)")
                return logs
            self.transcend_exp += amount
            logs.append(f"🌌 [초월 EXP +{amount:,}] (누적: {self.transcend_exp:,}/50,000)")
            while self.transcend_exp >= 50000 and self.transcend_level < MAX_TRANSCEND_LEVEL:
                self.transcend_exp -= 50000
                self.transcend_level += 1
                if self.transcend_level >= MAX_TRANSCEND_LEVEL:
                    self.transcend_exp = 0
                    logs.append(f"👑✨🌟 [초월 MAX 달성!] 초월 Lv.{self.transcend_level} 최고 단계! (전 스탯 +{self.transcend_level}% 영구 강화!)")
                else:
                    logs.append(f"👑✨ [초월 LEVEL UP!] 초월 Lv.{self.transcend_level} 달성! (전 스탯 +1% 영구 강화!)")
            return logs

        # 🚪 v16.2 성장 관문 (레벨 소프트캡 검사)
        cap_lvl, cap_msg = self.get_level_cap()
        
        if self.level >= cap_lvl:
            self.exp = min(self.max_exp, self.exp + amount)
            logs.append(f"✨ EXP +{amount:,} (현재 {self.exp:,}/{self.max_exp:,})")
            logs.append(f"⚠️ **[성장 관문 정지]** Lv.{cap_lvl} 상한에 도달했습니다! {cap_msg}")
            return logs

        self.exp += amount
        logs.append(f"✨ EXP +{amount:,} (현재 {self.exp:,}/{self.max_exp:,})")
        
        while self.exp >= self.max_exp and self.level < 99:
            # 다음 레벨이 캡을 넘는지 체크
            if self.level >= cap_lvl:
                logs.append(f"⚠️ **[성장 관문 정지]** Lv.{cap_lvl} 상한에 도달했습니다! {cap_msg}")
                break
                
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = self.calc_req_exp(self.level)
            bonus_coin = self.level * 150
            self.coins += bonus_coin
            self.affection = min(100, self.affection + 3)
            self.charm = min(100, self.charm + 1)
            logs.append(f"🎉 LEVEL UP! [Lv.{self.level}] 달성! (+{bonus_coin:,}G, 애정도+3, 외모력+1)")
            
            new_stage, new_title = Genetics.get_form_title(self.species_key, self.element, self.level, getattr(self, "is_shiny", False))
            if new_stage > self.stage:
                self.stage = new_stage
                if not getattr(self, "is_custom_name", False):
                    self.name = new_title
                    logs.append(f"\n🔥🔥🔥 [초대박 각성!] [{self.name}](으)로 진화 각성했습니다! 🎊🎊🎊")
                else:
                    logs.append(f"\n🔥🔥🔥 [초대박 각성!] {self.name}이(가) [{new_title}]의 경지로 진화 각성했습니다! 🎊🎊🎊")

            if self.level >= cap_lvl:
                logs.append(f"⚠️ **[성장 관문 정지]** 현재 Lv.{cap_lvl} 상한에 도달했습니다! {cap_msg}")
                break

        return logs

    @property
    def max_energy(self) -> int:
        return SPECIES_DATABASE.get(self.species_key, {}).get("max_life_energy", 100)

    @property
    def max_stamina(self) -> int:
        return SPECIES_DATABASE.get(self.species_key, {}).get("max_adventure_stamina", 100)

    def consume_energy(self, cost: int, action_type: str = "general") -> int:
        """종족 고유 무드 및 시그니처 특성 반영 소모 연산"""
        # 늑대: 던전/행동 -10% (애정도 80+ 시 -15%)
        if self.species_key == "늑대":
            discount = 0.85 if getattr(self, "affection", 50) >= 80 else 0.90
            cost = max(1, int(cost * discount))
        # 그리핀: 던전 -10%, 레이드 -5%
        elif self.species_key == "그리핀":
            if action_type == "dungeon": cost = max(1, int(cost * 0.90))
            elif action_type == "raid": cost = max(1, int(cost * 0.95))
        # 구미호: 행복도 80+ 시 -10%, 30 이하 시 +10%
        elif self.species_key == "구미호" and action_type in ["dungeon", "raid"]:
            if getattr(self, "happiness", 50) >= 80: cost = max(1, int(cost * 0.90))
            elif getattr(self, "happiness", 50) <= 30: cost = int(cost * 1.10)
        # 바하무트: 훈련 에너지 소모 +10% (파괴신의 대가)
        elif self.species_key == "바하무트" and action_type == "train":
            cost = int(cost * 1.10)

        if action_type in ["dungeon", "raid"]:
            # 🔥 모험 기력 차감
            self.stamina = max(0, getattr(self, "stamina", 100) - cost)
        else:
            # ⚡ 생활 에너지 차감
            self.energy = max(0, getattr(self, "energy", 100) - cost)
        return cost

    def live_tick(self) -> list:
        logs = []
        max_e = self.max_energy
        if self.is_sleeping:
            rec = 20
            self.energy = min(max_e, getattr(self, "energy", 100) + rec)
            self.stamina = min(max_e, getattr(self, "stamina", 100) + rec)
            self.health = min(100, getattr(self, "health", 100) + 15)
            if self.energy >= max_e and self.stamina >= max_e and self.health >= 100:
                self.is_sleeping = False
                logs.append(f"☀️ 꿀잠을 자고 일어났습니다! 건강/생활 에너지/모험 기력이 100% 완충되었습니다!")
            return logs

        # ⚡ 평상시 생활 에너지 & 🔥 모험 기력 & 🏥 건강 점진적 자연 치유
        if getattr(self, "energy", 100) < max_e and self.hunger >= 20 and random.random() < 0.50:
            self.energy = min(max_e, self.energy + 2)

        if getattr(self, "stamina", 100) < max_e and random.random() < 0.50:
            self.stamina = min(max_e, self.stamina + 2)

        if getattr(self, "health", 100) < 100 and self.hunger >= 50 and not self.is_sick and random.random() < 0.50:
            self.health = min(100, self.health + 2)

        # 💀 치명상 자연 해제 판정 (건강 60 이상 회복 시)
        if getattr(self, "is_critically_injured", False) and self.health >= 60:
            self.is_critically_injured = False
            logs.append("✨ **[치명상 자연 치유]** 건강이 안정선(60% 이상)에 도달하여 치명상이 완벽하게 치료되었습니다!")

        if random.random() < 0.10: self.hunger = max(0, self.hunger - 1)
        if random.random() < 0.10: self.cleanliness = max(0, self.cleanliness - 1)

        if self.hunger > 50 and random.random() < 0.04 and self.poops < 5:
            self.poops += 1
            self.cleanliness = max(0, self.cleanliness - 10)
            self.charm = max(0, self.charm - 2)
            logs.append(f"💩 뽀롱! {self.name}이(가) 똥을 쌌습니다! 치워주세요.")

        if (self.cleanliness <= 5 and self.hunger <= 5 or self.poops >= 5) and not self.is_sick:
            if random.random() < 0.05:
                self.is_sick = True
                self.affection = max(0, self.affection - 5)
                logs.append("🤒 청결과 영양이 극도로 악화되어 병에 걸렸습니다! 병원 치료가 시급합니다.")

        if self.is_sick and random.random() < 0.2:
            self.health = max(10, self.health - 2)

        return logs

    def apply_offline_time(self, elapsed_minutes: float) -> list:
        logs = []
        if elapsed_minutes < 0.1: return logs
        max_e = self.max_energy
        
        if self.is_sleeping:
            recovered_energy = int(elapsed_minutes * 35)
            recovered_health = int(elapsed_minutes * 25)
            self.energy = min(max_e, getattr(self, "energy", 100) + recovered_energy)
            self.stamina = min(max_e, getattr(self, "stamina", 100) + recovered_energy)
            self.health = min(100, getattr(self, "health", 100) + recovered_health)
            if self.energy >= max_e and self.stamina >= max_e and self.health >= 100:
                self.is_sleeping = False
                logs.append(f"☀️ 꿀잠을 자고 개운하게 일어났습니다! (건강 100%, 생활/모험 기력 {max_e}% 완충)")
            else:
                logs.append(f"💤 수면 중 건강 +{recovered_health}% / 기력 +{recovered_energy}% 회복 (건강: {self.health}%, 모험: {self.stamina}%)")
            return logs

        # ⚡ 오프라인 자연 기력 및 건강 회복 (깨어있을 때도 분당 생활+2%, 모험+3%, 건강+1.5% 지속 충전)
        nat_rec_stam = int(elapsed_minutes * 3)
        nat_rec_energy = int(elapsed_minutes * 2)
        nat_rec_health = int(elapsed_minutes * 1.5)
        self.stamina = min(max_e, getattr(self, "stamina", 100) + nat_rec_stam)
        if self.hunger >= 20:
            self.energy = min(max_e, getattr(self, "energy", 100) + nat_rec_energy)
        if self.hunger >= 40 and not self.is_sick and not getattr(self, "is_critically_injured", False):
            self.health = min(100, getattr(self, "health", 100) + nat_rec_health)

        hunger_loss = int(elapsed_minutes * 0.2)
        clean_loss = int(elapsed_minutes * 0.15)

        self.hunger = max(0, self.hunger - hunger_loss)
        self.cleanliness = max(0, self.cleanliness - clean_loss)
        
        new_poops = int(elapsed_minutes // 40)
        if new_poops > 0:
            self.poops = min(5, self.poops + new_poops)
            self.charm = max(10, self.charm - new_poops * 2)
            logs.append(f"💩 자리를 비운 사이 똥이 {new_poops}개 쌓였습니다!")

        if (self.cleanliness < 20 or self.hunger < 20 or self.poops >= 3) and not self.is_sick:
            self.is_sick = True
            logs.append("🤒 관리가 소홀하여 병에 걸렸습니다!")
        
        if self.is_sick:
            self.health = max(10, self.health - int(elapsed_minutes * 0.3))
        
        logs.append(f"⏳ 약 {elapsed_minutes:.1f}분 동안의 변화가 반영되었습니다. (생활 기력: {self.energy}%, 모험 기력: {self.stamina}%)")
        return logs

    def feed(self, food_type="normal") -> tuple[bool, str]:
        if self.is_sleeping: return False, "💤 수면 중에는 먹이를 먹을 수 없습니다."
        if self.hunger >= 100: return False, "😋 배가 가득 차서 더 이상 먹을 수 없습니다."
        
        aff_logs = []
        if food_type == "normal":
            cost = 50
            if self.coins < cost:
                return False, f"💸 사료를 구매할 골드가 부족합니다! (50G 필요, 보유: {self.coins:,}G)"
            self.coins -= cost
            self.hunger = min(100, self.hunger + 30)
            self.health = min(100, self.health + 5)
            aff_logs = self.gain_affection(3)
            if self.species_key == "호랑이":
                self.happiness = min(100, self.happiness + 5)
            self.gain_exp(50)
            if random.random() < 0.35: self.poops = min(5, self.poops + 1)
            msg = f"🍚 맛있는 사료를 배부르게 먹였습니다! (-{cost}G, 포만감 +30, 애정도 +3, EXP +50)"
        elif food_type == "snack":
            self.hunger = min(100, self.hunger + 15)
            self.happiness = min(100, self.happiness + 25)
            aff_logs = self.gain_affection(4)
            self.gain_exp(100)
            msg = "🍰 달콤한 간식을 먹고 기분이 좋아졌습니다! (포만감 +15, 애정도 +4, 행복도 +25)"
        elif food_type == "super":
            self.hunger = 100; self.happiness = 100; self.health = 100
            aff_logs = self.gain_affection(5)
            self.charm = min(100, self.charm + 10)
            self.gain_exp(300)
            msg = "🥩 특급 한우 스테이크로 포만감과 컨디션이 MAX로 회복되었습니다! (애정도 +5, 외모력 +10, EXP +300)"
        else:
            return False, "알 수 없는 음식입니다."
        if aff_logs: msg += "\n" + " ".join(aff_logs)
        return True, msg

    def clean(self) -> tuple[bool, str]:
        if self.is_sleeping: return False, "💤 수면 중에는 목욕을 할 수 없습니다."
        p = self.poops
        self.poops = 0
        self.cleanliness = 100
        self.charm = min(100, self.charm + 10)
        aff_logs = self.gain_affection(3)
        self.happiness = min(100, self.happiness + 15)
        bonus = p * 50
        self.coins += bonus
        self.gain_exp(40 + p * 20)
        msg = f"🧼 버블 목욕 완료! 청결도 100% & 외모력 +10 (애정도 +3, 똥 {p}개 청소 보너스: +{bonus}G)"
        if aff_logs: msg += "\n" + " ".join(aff_logs)
        return True, msg

    def groom(self) -> tuple[bool, str]:
        if self.is_sleeping: return False, "💤 수면 중에는 미용을 할 수 없습니다."
        self.charm = min(100, self.charm + 8)
        aff_logs = self.gain_affection(4)
        self.happiness = min(100, self.happiness + 10)
        self.gain_exp(30)
        msg = f"✨ 빗으로 정성껏 털을 빗겨주었습니다! (외모력 +8, 애정도 +4, 현재 외모력: {self.charm})"
        if aff_logs: msg += "\n" + " ".join(aff_logs)
        return True, msg

    def sleep_toggle(self) -> tuple[bool, str]:
        if not self.is_sleeping:
            self.is_sleeping = True
            return True, f"🌙 조명을 끄고 잠자리에 들었습니다. (약 3~4분 후 {self.max_energy}% 완충)"
        else:
            self.is_sleeping = False
            return True, "☀️ 개운하게 일어났습니다!"

    def cure(self) -> tuple[bool, str]:
        if not self.is_sick and not getattr(self, "is_critically_injured", False) and self.health >= 100:
            return False, "💖 상처나 질병 없이 100% 건강한 상태입니다!"
        
        cost = max(100, self.level * 100)
        if self.coins < cost:
            return False, f"💸 치료비가 부족합니다! ({cost:,}G 필요, 보유: {self.coins:,}G)"
        
        self.coins -= cost
        self.is_sick = False
        self.is_critically_injured = False
        self.health = 100
        self.cleanliness = max(60, self.cleanliness)
        aff_logs = self.gain_affection(5)
        msg = f"💉 병원에서 정성껏 치료받고 상처와 건강이 100% 완치되었습니다! (-{cost:,}G, 건강 100%, 청결도 회복, 애정도 +5)"
        if aff_logs: msg += "\n" + " ".join(aff_logs)
        return True, msg

    def train(self) -> tuple[bool, str]:
        if self.is_sleeping: return False, "💤 수면 중에는 훈련할 수 없습니다."
        if getattr(self, "is_critically_injured", False):
            return False, "💀 치명상을 입어 훈련할 수 없습니다! 휴식이나 치료약이 필요합니다."
        req_e = 18 if self.species_key == "늑대" else 20
        if self.energy < req_e: return False, "😫 생활 에너지가 부족합니다! 잠을 재워주세요."
        if self.is_sick: return False, "🤒 아픈 상태에서는 훈련할 수 없습니다!"

        used_e = self.consume_energy(20, "train")
        self.hunger = max(0, self.hunger - 15)
        self.cleanliness = max(0, self.cleanliness - 15)
        self.happiness = min(100, self.happiness + 10)
        aff_logs = self.gain_affection(2)
        
        g = random.randint(50, 150) + self.level * 20
        xp = random.randint(50, 120) + self.level * 15

        # 종족 무드 훈련 EXP 보너스
        if self.species_key == "호랑이": xp = int(xp * 1.10) # 호랑이: 훈련 EXP +10%
        elif self.species_key == "드래곤": xp = int(xp * 1.15) # 드래곤: 훈련 EXP +15%

        # 애정도 Lv.4+ 훈련 EXP +2%
        lvl, _, _ = self.get_affection_state()
        if lvl >= 4: xp = int(xp * 1.02)

        self.coins += g
        logs = self.gain_exp(xp)
        
        msg = f"🏋️ 불타는 훈련 완료! (생활에너지 -{used_e}%, +{g:,}G, +{xp:,} EXP, 애정도 +2)\n" + " ".join(logs)
        if aff_logs: msg += "\n" + " ".join(aff_logs)
        return True, msg

    def pet_animal(self) -> tuple[bool, str]:
        if self.is_sleeping: return False, "💤 새근새근 자고 있어 쓰다듬을 수 없습니다."

        # ⏳ 60초(1분) 쓰다듬기 쿨타임 검사 (무한 연타 어뷰징 방지)
        now = time.time()
        last_t = getattr(self, "last_pet_time", 0.0)
        cooldown_sec = 60
        if (now - last_t) < cooldown_sec:
            rem_sec = max(1, int(cooldown_sec - (now - last_t)))
            return False, f"⏳ **{self.name}**이(가) 아직 방금 쓰다듬어준 손길의 여운을 느끼며 흐뭇해하고 있습니다! (남은 쿨타임: **{rem_sec}초**)"

        self.last_pet_time = now
        self.happiness = min(100, self.happiness + 10)
        self.energy = min(self.max_energy, getattr(self, "energy", 100) + 10)
        aff_logs = self.gain_affection(8)
        self.gain_exp(20)
        lvl, prog, info = self.get_affection_state()
        msg = f"❤️ **{self.name}**을(를) 정성껏 쓰다듬어 주었습니다! (생활에너지 +10%, 애정도 +8 · 현재 {info['icon']} **Lv.{lvl} {info['name']}** {prog}/100)"
        if aff_logs: msg += "\n" + " ".join(aff_logs)
        return True, msg

    def get_current_art(self) -> str:
        sp_art = ASCII_ARTS.get(self.species_key, ASCII_ARTS["default"])
        return sp_art.get(self.stage, sp_art.get(1, ASCII_ARTS["default"][1]))

    def get_status_bar(self, val: int, max_val: int = 100, length: int = 10, fill_char="■", empty_char="□") -> str:
        filled = int((val / max_val) * length)
        filled = max(0, min(length, filled))
        return fill_char * filled + empty_char * (length - filled)
