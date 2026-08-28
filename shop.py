# -*- coding: utf-8 -*-
"""
🛒 DAMAGOCHI Equipment & Shop System (v17.2)
10대 종족 전용 보물(+10 강화 및 고유 효과), 8종 방어구 승급(강화 보존 & ★1~★5 성급), 혼 소모 및 재료 상점
"""

import random

# 10대 종족 전용 보물 데이터베이스 (공식 명칭 및 +0 ~ +10 스탯 & +10 고유 효과)
EXCLUSIVE_RELICS = {
    "호랑이": {
        "id": "relic_tiger", "species": "호랑이", "name": "🐯 백호의 송곳니", "emoji": "🐯",
        "base_atk": 8, "base_crit_dmg": 0.05,
        "max_atk": 80, "max_crit_dmg": 0.20,
        "special_10": "🐯 백호살: 치명타 발생 시 15% 확률로 추가 공격!",
        "desc": "백호의 날카로운 송곳니 (치명타 피해 및 추가타 특화)"
    },
    "사자": {
        "id": "relic_lion", "species": "사자", "name": "🦁 태양의 갈기", "emoji": "🦁",
        "base_hp": 80, "base_def": 5,
        "max_hp": 350, "max_def": 60,
        "special_10": "☀️ 태양왕의 위엄: HP 50% 이하일 때 받는 피해 -10% 감소!",
        "desc": "황금빛 태양의 기운이 깃든 갈기 (체력 및 위기 방어 특화)"
    },
    "늑대": {
        "id": "relic_wolf", "species": "늑대", "name": "🐺 월광의 발톱", "emoji": "🐺",
        "base_spd": 6, "base_crit_rate": 0.03,
        "max_spd": 55, "max_crit_rate": 0.12,
        "special_10": "🌙 월식 사냥: 적보다 SPD가 높으면 최종 피해 +10% 상승!",
        "desc": "달빛을 머금은 늑대의 발톱 (초고속 스피드 및 치명타 특화)"
    },
    "드래곤": {
        "id": "relic_dragon", "species": "드래곤", "name": "🐉 드래곤의 역린", "emoji": "🐉",
        "base_atk": 10, "base_pen_def": 0.03,
        "max_atk": 90, "max_pen_def": 0.15,
        "special_10": "🐉 용제의 분노: HP 30% 이하일 때 ATK +20% 폭증!",
        "desc": "건드려선 안 될 용의 역린 (공격력 및 방어 관통 특화)"
    },
    "불사조": {
        "id": "relic_phoenix", "species": "불사조", "name": "🦅 불멸의 깃털", "emoji": "🦅",
        "base_hp": 60, "base_heal_bonus": 0.03,
        "max_hp": 400, "max_heal_bonus": 0.15,
        "special_10": "🔥 불사: 치명적인 피해를 받을 때 전투당 1회 HP 1로 생존!",
        "desc": "영원히 타오르는 불사조의 깃털 (체력 및 불사 생존 특화)"
    },
    "현무": {
        "id": "relic_turtle", "species": "현무", "name": "🐢 현무의 갑각", "emoji": "🐢",
        "base_def": 10, "base_dmg_red": 0.02,
        "max_def": 100, "max_dmg_red": 0.08,
        "special_10": "🛡️ 절대수호: HP 30% 이하일 때 DEF +20% 추가 상승!",
        "desc": "금강석보다 단단한 현무의 등껍질 (절대 방어 및 피해 감소 특화)"
    },
    "구미호": {
        "id": "relic_fox", "species": "구미호", "name": "🦊 구미호의 여우구슬", "emoji": "🦊",
        "base_atk": 6, "base_lifesteal": 0.02,
        "max_atk": 60, "max_lifesteal": 0.12,
        "special_10": "🦊 혼령 흡수: 「정기흡수」의 흡혈량이 5% → 8%로 대폭 증가!",
        "desc": "천년 요기가 응축된 신비한 구슬 (마법 공격 및 정기 흡혈 특화)"
    },
    "그리핀": {
        "id": "relic_griffin", "species": "그리핀", "name": "🪽 폭풍의 깃털", "emoji": "🪽",
        "base_spd": 7, "base_double_rate": 0.02,
        "max_spd": 65, "max_double_rate": 0.10,
        "special_10": "🌪️ 폭풍 강습: 선공 시 첫 공격 피해 +20% 상승!",
        "desc": "창공을 가르는 폭풍의 날개깃 (선공 및 2연타 특화)"
    },
    "기린": {
        "id": "relic_kirin", "species": "기린", "name": "🦄 천계의 뿔", "emoji": "🦄",
        "base_all_stats": 3,
        "max_hp": 60, "max_atk": 30, "max_def": 30, "max_spd": 30, "max_crit": 30,
        "special_10": "✨ 천계의 축복: 전투 시작 시 모든 5대 스탯 +5% 상승!",
        "desc": "천상의 조화가 깃든 신성한 뿔 (전 5대 스탯 올라운드 특화)"
    },
    "바하무트": {
        "id": "relic_bahamut", "species": "바하무트", "name": "🐲 종말의 용핵", "emoji": "🐲",
        "base_atk": 12, "base_final_dmg": 0.03,
        "max_atk": 120, "max_final_dmg": 0.12,
        "special_10": "🌌 종말의 권능: 보스에게 주는 피해 +10% 추가 상승!",
        "desc": "전 우주를 멸하는 암흑의 핵 (초월적 공격력 및 보스 킬러 특화)"
    }
}

# 🛡️ 8종 방어구 데이터베이스 (v17.2 던전 강화 & 레이드 독립 획득 & 신화 5종 체계)
ARMORS_DATABASE = {
    "leather_armor": {
        "id": "leather_armor", "name": "가죽 갑옷", "tier": "🟢 초급", "type": "중갑형",
        "max_enhance": 5, "is_mythic": False,
        "base_hp": 70, "base_def": 30, "resist": 0.0, "dmg_red": 0.0,
        "desc": "Normal 레이드에서 획득하는 질긴 가죽 갑옷 (최대 +5 강화)"
    },
    "crystal_armor": {
        "id": "crystal_armor", "name": "수정 갑옷", "tier": "🔵 고급", "type": "중갑형",
        "max_enhance": 8, "is_mythic": False,
        "base_hp": 120, "base_def": 55, "resist": 0.05, "dmg_red": 0.0,
        "desc": "Hard 레이드에서 획득하는 수정 갑옷 (상태이상 저항 +5%, 최대 +8 강화)"
    },
    "celestial_armor": {
        "id": "celestial_armor", "name": "천계 갑주", "tier": "🟣 전설", "type": "중갑형",
        "max_enhance": 11, "is_mythic": False,
        "base_hp": 220, "base_def": 90, "resist": 0.10, "dmg_red": 0.05,
        "desc": "Nightmare 레이드에서 획득하는 천계 갑주 (상태이상 저항 +10%, 피해감소 -5%, 최대 +11 강화)"
    },
    "mythic_dragon_armor": {
        "id": "mythic_dragon_armor", "name": "용신의 갑주", "tier": "🔴 신화", "type": "방어형",
        "max_enhance": 15, "is_mythic": True,
        "base_hp": 260, "base_def": 150, "dmg_red": 0.08, "burn_dmg_red": 0.30,
        "ancient_passive": "용신의 가호", "ancient_desc": "화상 피해 -30% 감소 및 받는 피해 -8% 감소 (★5 각성 시 특효 극대화)",
        "desc": "Mythic 이프리트 토벌로 획득하는 신화 갑주 (DEF +150, 피해감소 -8%, 화상피해 -30%, 최대 +15 & ★1~★5)"
    },
    "mythic_life_armor": {
        "id": "mythic_life_armor", "name": "생명의 성의", "tier": "🔴 신화", "type": "생명형",
        "max_enhance": 15, "is_mythic": True,
        "base_hp": 400, "base_def": 80, "heal_bonus": 0.20, "regen_hp_pct": 0.01,
        "ancient_passive": "태고의 생명", "ancient_desc": "회복량 +20% 및 매 턴 최대 HP의 1% 지속 회복 (★5 각성 시 특효 극대화)",
        "desc": "Mythic 엔트 토벌로 획득하는 신화 성의 (HP +400, 회복량 +20%, 턴당 1% 재생, 최대 +15 & ★1~★5)"
    },
    "mythic_gale_armor": {
        "id": "mythic_gale_armor", "name": "천풍의 경갑", "tier": "🔴 신화", "type": "속도형",
        "max_enhance": 15, "is_mythic": True,
        "base_hp": 220, "base_def": 100, "base_spd": 60, "first_hit_bonus": 0.07,
        "ancient_passive": "천공의 질풍", "ancient_desc": "SPD +60 및 선공 시 첫 공격 피해 +7% 증폭 (★5 각성 시 특효 극대화)",
        "desc": "Mythic 성운 가디언 토벌로 획득하는 신화 경갑 (SPD +60, 선공 첫타 +7%, 최대 +15 & ★1~★5)"
    },
    "mythic_abyss_armor": {
        "id": "mythic_abyss_armor", "name": "심연의 갑주", "tier": "🔴 신화", "type": "저항형",
        "max_enhance": 15, "is_mythic": True,
        "base_hp": 280, "base_def": 140, "resist": 0.25, "low_hp_dmg_red": 0.10,
        "ancient_passive": "심연의 결계", "ancient_desc": "상태이상 저항 +25% 및 HP 30% 이하 시 최종 피해 -10% 감소 (★5 각성 시 특효 극대화)",
        "desc": "Mythic 성운 가디언 토벌로 획득하는 신화 갑주 (저항 +25%, HP 30% 이하 피해감소 -10%, 최대 +15 & ★1~★5)"
    },
    "mythic_celestial_armor": {
        "id": "mythic_celestial_armor", "name": "천계신의 갑주", "tier": "🔴 신화", "type": "올라운드",
        "max_enhance": 15, "is_mythic": True,
        "base_hp": 320, "base_def": 130, "resist": 0.15, "dmg_red": 0.08,
        "ancient_passive": "천계의 권능", "ancient_desc": "상태이상 저항 +15% 및 받는 피해 -8% 감소 (★5 각성 시 특효 극대화)",
        "desc": "Mythic 크리스탈 드래곤 토벌로 획득하는 신화 갑주 (HP +320, DEF +130, 피해감소 -8%, 최대 +15 & ★1~★5)"
    }
}

# 🌟 구버전 호환용 빈 승급 트리 (v17.2 승급 소모 폐지 ➔ 독립 영구 획득 전환)
ARMOR_PROMOTION_TREE = {}

ITEMS_DATABASE = {
    "small_candy": {"name": "🍬 작은 경험치 사탕", "price": 50, "exp": 500, "desc": "신수에게 500 EXP를 즉시 부여합니다."},
    "super_candy": {"name": "🍭 슈퍼 경험치 사탕", "price": 200, "exp": 2000, "desc": "신수에게 2,000 EXP를 즉시 부여합니다."},
    "mega_candy": {"name": "🌟 특급 경험치 사탕", "price": 800, "exp": 8000, "desc": "신수에게 8,000 EXP를 즉시 부여합니다."},
    "ancient_candy": {"name": "🌌 태초의 사탕", "price": 3000, "exp": 25000, "desc": "신수에게 25,000 EXP를 즉시 부여합니다."},
    "soul_normal": {"name": "⚪ 일반 혼", "price": 0, "desc": "Normal 레이드 클리어 보상. 스탯별 잠재 성장을 0% -> 15%로 각성시킵니다. (1, 4, 9, 16, 25개 소모)"},
    "soul_hard": {"name": "🔵 고급 혼", "price": 0, "desc": "Hard 레이드 클리어 보상. 스탯별 잠재 성장을 15% -> 30%로 각성시킵니다. (1, 4, 9, 16, 25개 소모)"},
    "soul_nightmare": {"name": "🟣 전설 혼", "price": 0, "desc": "Nightmare 레이드 클리어 보상. 스탯별 잠재 성장을 30% -> 45%로 각성시킵니다. (1, 4, 9, 16, 25개 소모)"},
    "soul_mythic": {"name": "🟡 신화 혼", "price": 0, "desc": "Mythic 레이드 클리어 보상. 스탯별 잠재 성장을 45% -> 60%로 각성시킵니다. (1, 4, 9, 16, 25개 소모)"},
    "stone": {"name": "💎 강화석", "price": 100, "desc": "장비와 방어구를 강화하는 기초 강화석"},
    "relic_essence": {"name": "🔮 보물의 정수", "price": 200, "desc": "전용 보물 및 고단계 방어구 강화에 필요한 신비한 정수"},
    "armor_stone": {"name": "💎 방어구 강화석", "price": 500, "desc": "방어구를 +1 ~ +10까지 강화하는 신비한 광석"},
    "nightmare_crystal": {"name": "🟣 악몽의 결정", "price": 0, "desc": "Nightmare 레이드 클리어 보상. 방어구 +11~+13 강화에 필요합니다."},
    "mythic_core": {"name": "🟡 신화의 핵", "price": 0, "desc": "Mythic 레이드 클리어 보상. 방어구 +14~+15 강화에 필요합니다."},
    "ancient_core": {"name": "🌑 태고의 핵", "price": 0, "desc": "Ancient 레이드 범용 클리어 보상. 고대 방어구 ★ 승급에 사용됩니다."},
    "ancient_core_ent": {"name": "🌳 태고목의 핵", "price": 0, "desc": "고대 엔트 10회 토벌 보상. 고대 방어구 ★1~★5 확정 승급에 사용됩니다."},
    "ancient_core_dragon": {"name": "💎 불멸결정의 핵", "price": 0, "desc": "크리스탈 드래곤 10회 토벌 보상. 고대 방어구 ★1~★5 확정 승급에 사용됩니다."},
    "ancient_core_ifrit": {"name": "🔥 영겁화염의 핵", "price": 0, "desc": "이프리트 10회 토벌 보상. 고대 방어구 ★1~★5 확정 승급에 사용됩니다."},
    "ancient_core_guardian": {"name": "☄️ 성운의 핵", "price": 0, "desc": "성운 가디언 10회 토벌 보상. 고대 방어구 ★1~★5 확정 승급에 사용됩니다."},
    "ancient_core_omega": {"name": "🪐 종말의 핵", "price": 0, "desc": "오메가 10회 토벌 보상. 고대 방어구 ★1~★5 확정 승급에 사용됩니다."},
    "life_gem": {"name": "💎 생명의 보석", "price": 1000, "desc": "고대 레이드 패배 시 치명상 판정을 1회 자동 무효화합니다. (가방 보유 시 자동 작동)"},
    "holy_water": {"name": "🌟 불사의 성수", "price": 1500, "desc": "치명상을 즉시 치료하고 건강 50%, 모험 기력 50%를 회복합니다."},
    "primordial_heart": {"name": "🌌 태초의 심장", "price": 4000, "desc": "치명상을 즉시 치료하고 건강/생활/모험 기력을 100% 완전 회복합니다."}
}

class Inventory:
    def __init__(self, data=None):
        self.items = {}
        # 장착 슬롯 (종족 보물 1개, 방어구 1개)
        self.equipped_relic = None # {"species": "호랑이", "level": 0}
        self.equipped_armor = None # {"armor_id": "leather_armor", "level": 0, "opt": {"type": "def_pct", "val": 0.05}}
        
        # 보유 장비 보관함
        self.relics_inventory = [] # list of {"species": "호랑이", "level": 0}
        self.armors_inventory = [] # list of {"armor_id": "mythic_dragon_armor", "level": 0, "opt": ...}
        self.species_essences = {} # {"호랑이": 10, "드래곤": 5, ...}
        
        migration_map = {
            "ancient_god_armor": "mythic_celestial_armor",
            "dragon_scale_armor": "mythic_dragon_armor",
            "robe_of_life": "mythic_life_armor",
            "gale_light_armor": "mythic_gale_armor",
            "abyssal_armor": "mythic_abyss_armor"
        }

        if data:
            self.items = data.get("items", {})
            self.equipped_relic = data.get("equipped_relic", None)
            self.equipped_armor = data.get("equipped_armor", None)
            if self.equipped_armor and self.equipped_armor.get("armor_id") in migration_map:
                self.equipped_armor["armor_id"] = migration_map[self.equipped_armor["armor_id"]]
            
            raw_armors = data.get("armors_inventory", [])
            for a in raw_armors:
                if isinstance(a, dict):
                    if a.get("armor_id") in migration_map:
                        a["armor_id"] = migration_map[a["armor_id"]]
                    self.armors_inventory.append(a)

            self.relics_inventory = data.get("relics_inventory", [])
            self.species_essences = data.get("species_essences", {})
        else:
            self.items = {"small_candy": 3, "armor_stone": 5}
            self.species_essences = {}

    def to_dict(self) -> dict:
        return {
            "items": self.items,
            "equipped_relic": self.equipped_relic,
            "equipped_armor": self.equipped_armor,
            "relics_inventory": self.relics_inventory,
            "armors_inventory": self.armors_inventory,
            "species_essences": self.species_essences
        }

    def add_item(self, item_id: str, count: int = 1):
        self.items[item_id] = self.items.get(item_id, 0) + count

    def remove_item(self, item_id: str, count: int = 1) -> bool:
        if self.items.get(item_id, 0) >= count:
            self.items[item_id] -= count
            if self.items[item_id] <= 0:
                del self.items[item_id]
            return True
        return False

    def add_relic(self, species_key: str, level: int = 0):
        self.relics_inventory.append({"species": species_key, "level": level})

    def add_armor(self, armor_id: str, level: int = 0, stars: int = 0):
        # 🛡️ v17.2 방어구 영구 수집 및 독립 획득
        migration_map = {
            "ancient_god_armor": "mythic_celestial_armor",
            "dragon_scale_armor": "mythic_dragon_armor",
            "robe_of_life": "mythic_life_armor",
            "gale_light_armor": "mythic_gale_armor",
            "abyssal_armor": "mythic_abyss_armor"
        }
        if armor_id in migration_map:
            armor_id = migration_map[armor_id]

        opt = None
        a_info = ARMORS_DATABASE.get(armor_id, {})
        if a_info.get("is_mythic", False) or a_info.get("tier") in ["🟣 전설", "🔴 신화"]:
            opt_pool = [
                ("hp_pct", "최대 HP", 0.05),
                ("def_pct", "방어력", 0.07),
                ("spd_pct", "스피드", 0.06),
                ("crit_dmg_red", "치명타 피해 감소", 0.10),
                ("resist_burn", "화상 저항", 0.15)
            ]
            chosen = random.choice(opt_pool)
            opt = {"key": chosen[0], "name": chosen[1], "val": chosen[2]}
        
        armor_item = {"armor_id": armor_id, "level": level, "stars": stars, "opt": opt}
        if not self.equipped_armor:
            self.equipped_armor = armor_item
        else:
            self.armors_inventory.append(armor_item)

    def equip_relic(self, species_key: str) -> tuple[bool, str]:
        # 인벤토리에서 해당 보물 찾아서 장착
        for idx, r in enumerate(self.relics_inventory):
            if r["species"] == species_key:
                if self.equipped_relic:
                    self.relics_inventory.append(self.equipped_relic)
                self.equipped_relic = self.relics_inventory.pop(idx)
                r_name = EXCLUSIVE_RELICS[species_key]["name"]
                return True, f"🎴 [{r_name} +{self.equipped_relic['level']}] 장착 완료!"
        return False, "보유 중인 해당 종족의 전용 보물이 없습니다."

    def equip_armor(self, inv_idx: int) -> tuple[bool, str]:
        if 0 <= inv_idx < len(self.armors_inventory):
            if self.equipped_armor:
                self.armors_inventory.append(self.equipped_armor)
            self.equipped_armor = self.armors_inventory.pop(inv_idx)
            a_info = ARMORS_DATABASE.get(self.equipped_armor["armor_id"], ARMORS_DATABASE["leather_armor"])
            return True, f"🛡️ [{a_info['name']} +{self.equipped_armor['level']}] 장착 완료!"
        return False, "잘못된 방어구 번호입니다."

    def dismantle_relic(self, inv_idx: int) -> tuple[bool, str]:
        if 0 <= inv_idx < len(self.relics_inventory):
            r = self.relics_inventory.pop(inv_idx)
            sp = r["species"]
            essence_gain = 10 + r["level"] * 3
            self.species_essences[sp] = self.species_essences.get(sp, 0) + essence_gain
            r_name = EXCLUSIVE_RELICS[sp]["name"]
            return True, f"♻️ [{r_name}] 분해 완료! (🌟 {sp}의 정수 +{essence_gain}개 획득, 현재: {self.species_essences[sp]}개)"
        return False, "존재하지 않는 보물입니다."

    def craft_relic(self, species_key: str, pet_coins: int) -> tuple[bool, str, int]:
        req_essence = 50
        req_gold = 20000
        cur_ess = self.species_essences.get(species_key, 0)
        
        if cur_ess < req_essence:
            return False, f"🚫 {species_key}의 정수가 부족합니다! (필요: {req_essence}개, 현재: {cur_ess}개)", pet_coins
        if pet_coins < req_gold:
            return False, f"💸 골드가 부족합니다! (필요: {req_gold:,}G)", pet_coins

        self.species_essences[species_key] -= req_essence
        new_coins = pet_coins - req_gold
        self.add_relic(species_key, level=0)
        r_name = EXCLUSIVE_RELICS[species_key]["name"]
        return True, f"🎉 🌟 [{r_name}] 제작 성공! 인벤토리에 보관되었습니다!", new_coins

    def enhance_relic(self, pet_coins: int, max_allowed_lvl: int = 10) -> tuple[bool, str, int]:
        """🎴 종족 전용 보물 +0 ~ +10 강화 시스템 (v16.2 레이드 관문 연동)"""
        # 잡지식: 종족 전용 보물은 Mythic(+10)에서 최종 완성과 함께 종족 고유 시그니처 특효가 개방돼용!
        if not self.equipped_relic:
            return False, "장착 중인 종족 전용 보물이 없습니다.", pet_coins
        
        cur_lvl = self.equipped_relic.get("level", 0)
        sp = self.equipped_relic.get("species", "호랑이")
        r_name = EXCLUSIVE_RELICS.get(sp, {}).get("name", "전용 보물")
        
        if cur_lvl >= 10:
            return False, f"이미 최고 강화 단계(+10)입니다! 👑 「{EXCLUSIVE_RELICS[sp]['special_10']}」", pet_coins

        if cur_lvl >= max_allowed_lvl:
            return False, f"⚠️ 현재 레이드 성장 관문에서는 보물을 최대 **+{max_allowed_lvl}**까지만 강화할 수 있습니다! 다음 난이도 레이드를 올클리어하여 강화 상한을 해제하세요.", pet_coins
        
        # 단계별 재료 요구량 계산
        req_stone = (cur_lvl + 1) * 2
        req_ess = (cur_lvl + 1)
        req_nc = 0
        req_gold = (cur_lvl + 1) * 2500

        if cur_lvl == 8: # +9 시도 (Nightmare 재료)
            req_nc = 1
            req_gold = 25000
        elif cur_lvl == 9: # +10 시도 (Nightmare 재료)
            req_nc = 2
            req_gold = 35000

        cur_stone = self.items.get("stone", 0) + self.items.get("armor_stone", 0)
        # 종족 고유 정수 또는 범용 보물 정수 둘 다 사용 가능
        cur_sp_ess = self.species_essences.get(sp, 0)
        cur_gen_ess = self.items.get("relic_essence", 0)
        tot_ess = cur_sp_ess + cur_gen_ess
        cur_nc = self.items.get("nightmare_crystal", 0)

        if cur_stone < req_stone:
            return False, f"🚫 강화석이 부족합니다! (필요: {req_stone}개, 현재: {cur_stone}개)", pet_coins
        if tot_ess < req_ess:
            return False, f"🚫 보물의 정수가 부족합니다! (필요: {req_ess}개, 현재: {tot_ess}개)", pet_coins
        if req_nc > 0 and cur_nc < req_nc:
            return False, f"🚫 🟣 악몽의 결정이 부족합니다! (Nightmare 레이드 드랍 | 필요: {req_nc}개, 현재: {cur_nc}개)", pet_coins
        if pet_coins < req_gold:
            return False, f"💸 골드가 부족합니다! (필요: {req_gold:,}G, 보유: {pet_coins:,}G)", pet_coins

        # 재료 차감
        # 1. 강화석 차감
        rem_st = req_stone
        if self.items.get("stone", 0) >= rem_st:
            self.remove_item("stone", rem_st)
        else:
            u_st = self.items.get("stone", 0)
            if u_st > 0: self.remove_item("stone", u_st)
            self.remove_item("armor_stone", rem_st - u_st)

        # 2. 정수 차감 (종족 전용 정수 우선 소모)
        rem_es = req_ess
        if cur_sp_ess >= rem_es:
            self.species_essences[sp] -= rem_es
        else:
            self.species_essences[sp] = 0
            self.remove_item("relic_essence", rem_es - cur_sp_ess)

        # 3. 악몽의 결정 차감
        if req_nc > 0:
            self.remove_item("nightmare_crystal", req_nc)

        new_coins = pet_coins - req_gold

        # v15.5 공식 성공률 테이블
        rates = {
            0: 1.00, 1: 1.00, 2: 1.00,
            3: 0.90, 4: 0.80,
            5: 0.70, 6: 0.60, 7: 0.50,
            8: 0.35, 9: 0.20
        }
        success_rate = rates.get(cur_lvl, 0.20)
        
        if random.random() < success_rate:
            self.equipped_relic["level"] += 1
            new_lvl = self.equipped_relic["level"]
            spec_msg = f"\n👑✨ **[+10 종결 특효 해금!]** 「{EXCLUSIVE_RELICS[sp]['special_10']}」" if new_lvl == 10 else ""
            return True, f"🎊 **보물 강화 대성공!** [{r_name} +{new_lvl}] 달성!{spec_msg}", new_coins
        else:
            return True, f"😭 보물 강화 실패... 재료만 소모되고 장비는 안전하게 유지되었습니다. (성공률: {int(success_rate*100)}%)", new_coins

    def enhance_armor(self, pet_coins: int) -> tuple[bool, str, int]:
        """🛡️ 방어구 +0 ~ +15 강화 시스템 (v16.2 등급별 강화 상한 연동)"""
        # 잡지식: 방어구는 파괴와 하락이 전혀 없는 갓벽한 혜자 시스템으로 설계되었어용!
        if not self.equipped_armor:
            return False, "장착 중인 방어구가 없습니다.", pet_coins

        a_info = ARMORS_DATABASE.get(self.equipped_armor["armor_id"], ARMORS_DATABASE["leather_armor"])
        a_name = a_info["name"]
        max_enh = a_info.get("max_enhance", 15)
        cur_lvl = self.equipped_armor.get("level", 0)

        if cur_lvl >= max_enh:
            if max_enh == 15:
                return False, "이미 최대 강화 단계(+15)입니다! [고대 성급(★) 승급]을 진행해 주세요.", pet_coins
            else:
                return False, f"⚠️ [{a_name}]은(는) 최대 **+{max_enh}**까지만 강화할 수 있습니다! 상위 난이도 레이드에서 더 높은 등급의 방어구를 획득하세요.", pet_coins

        # 강화 단계별 소모 재료 및 비용
        req_stone = cur_lvl + 1
        req_essence = max(1, (cur_lvl + 1) // 2)
        req_gold = (cur_lvl + 1) * 1500
        req_nc = 0
        req_mc = 0

        if cur_lvl == 10:   # +11 시도
            req_stone, req_essence, req_nc, req_gold = 12, 6, 1, 20000
        elif cur_lvl == 11: # +12 시도
            req_stone, req_essence, req_nc, req_gold = 15, 8, 2, 25000
        elif cur_lvl == 12: # +13 시도
            req_stone, req_essence, req_nc, req_gold = 18, 10, 3, 30000
        elif cur_lvl == 13: # +14 시도
            req_stone, req_essence, req_mc, req_gold = 22, 12, 2, 40000
        elif cur_lvl == 14: # +15 시도
            req_stone, req_essence, req_mc, req_gold = 25, 15, 4, 50000

        # 재료 보유 체크 (stone 또는 armor_stone 사용 가능)
        stone_cnt = self.items.get("stone", 0) + self.items.get("armor_stone", 0)
        ess_cnt = self.items.get("relic_essence", 0)
        nc_cnt = self.items.get("nightmare_crystal", 0)
        mc_cnt = self.items.get("mythic_core", 0)

        if stone_cnt < req_stone:
            return False, f"🚫 강화석이 부족합니다! (필요: {req_stone}개, 현재: {stone_cnt}개)", pet_coins
        if cur_lvl >= 5 and ess_cnt < req_essence:
            return False, f"🚫 보물의 정수가 부족합니다! (필요: {req_essence}개, 현재: {ess_cnt}개)", pet_coins
        if req_nc > 0 and nc_cnt < req_nc:
            return False, f"🚫 🟣 악몽의 결정이 부족합니다! (Nightmare 레이드 드랍 | 필요: {req_nc}개, 현재: {nc_cnt}개)", pet_coins
        if req_mc > 0 and mc_cnt < req_mc:
            return False, f"🚫 🟡 신화의 핵이 부족합니다! (Mythic 레이드 드랍 | 필요: {req_mc}개, 현재: {mc_cnt}개)", pet_coins
        if pet_coins < req_gold:
            return False, f"💸 골드가 부족합니다! (필요: {req_gold:,}G, 보유: {pet_coins:,}G)", pet_coins

        # 재료 차감
        rem_st = req_stone
        if self.items.get("armor_stone", 0) >= rem_st:
            self.remove_item("armor_stone", rem_st)
        else:
            used_as = self.items.get("armor_stone", 0)
            if used_as > 0: self.remove_item("armor_stone", used_as)
            self.remove_item("stone", rem_st - used_as)

        if cur_lvl >= 5:
            self.remove_item("relic_essence", req_essence)
        if req_nc > 0:
            self.remove_item("nightmare_crystal", req_nc)
        if req_mc > 0:
            self.remove_item("mythic_core", req_mc)
        new_coins = pet_coins - req_gold

        rates = {
            0: 1.00, 1: 1.00, 2: 1.00, 3: 0.95, 4: 0.90, 5: 0.85,
            6: 0.75, 7: 0.65, 8: 0.55, 9: 0.45,
            10: 0.35, 11: 0.25, 12: 0.18, 13: 0.12, 14: 0.08
        }
        success_rate = rates.get(cur_lvl, 0.08)

        stars = self.equipped_armor.get("stars", 0)
        star_str = f" {'★' * stars}" if stars > 0 else ""

        if random.random() < success_rate:
            self.equipped_armor["level"] += 1
            new_lvl = self.equipped_armor["level"]
            unl_msg = "\n🌟 **[+15 종결 달성!]** 고대 성급(★) 승급 메뉴가 해금되었습니다!" if new_lvl == 15 else ""
            return True, f"🎊 **방어구 강화 대성공!** [{a_name} +{new_lvl}{star_str}] 달성!{unl_msg}", new_coins
        else:
            return True, f"😭 방어구 강화 실패... 재료만 소모되고 단계는 유지되었습니다. (성공률: {int(success_rate*100)}%)", new_coins

    def ascend_armor_star(self, pet_coins: int, specific_core: str = None) -> tuple[bool, str, int]:
        """🌟 +15 고대 방어구 100% 확정 별 승급 (★1 ~ ★5) 시스템 (v16.2 무확률/노파괴)"""
        # 잡지식: '성급(Star Ascension)'은 Ancient 보스 10회 정복마다 획득하는 전용 핵으로 100% 확정 승급해용!
        if not self.equipped_armor:
            return False, "장착 중인 방어구가 없습니다.", pet_coins

        a_info = ARMORS_DATABASE.get(self.equipped_armor["armor_id"], ARMORS_DATABASE["leather_armor"])
        a_name = a_info["name"]

        if not a_info.get("is_mythic", False) and a_info.get("max_enhance", 15) < 15:
            return False, "⚠️ 고대 성급(★) 승급은 Mythic 신화 방어구 5종([용신/생명/천풍/심연/천계신])만 가능합니다!", pet_coins

        cur_lvl = self.equipped_armor.get("level", 0)
        if cur_lvl < 15:
            return False, f"⚠️ 고대 성급 승급은 **+15 강화**를 달성한 신화 방어구만 가능합니다! (현재: +{cur_lvl})", pet_coins

        cur_stars = self.equipped_armor.get("stars", 0)
        if cur_stars >= 5:
            return False, "이미 방어구 고대 성급이 최고 단계(★5 MAX 완전 정복)입니다!", pet_coins

        # 성급별 골드 요구량
        star_gold = {0: 30000, 1: 50000, 2: 70000, 3: 90000, 4: 120000}
        req_gold = star_gold.get(cur_stars, 120000)

        # 소모 가능한 고대 핵 목록 (보스별 전용 핵 5종 또는 범용 태고의 핵)
        candidate_cores = [
            "ancient_core_ent", "ancient_core_dragon", "ancient_core_ifrit",
            "ancient_core_guardian", "ancient_core_omega", "ancient_core"
        ]
        if specific_core and specific_core in candidate_cores:
            candidate_cores = [specific_core] + [c for c in candidate_cores if c != specific_core]

        used_core = None
        for core_id in candidate_cores:
            if self.items.get(core_id, 0) >= 1:
                used_core = core_id
                break

        if not used_core:
            return False, "🚫 고대 보스 전용 핵(태고목/불멸결정/영겁화염/성운/종말의 핵) 또는 태고의 핵이 부족합니다! (Ancient 보스 10회 토벌 보상 | 필요: 1개)", pet_coins

        if pet_coins < req_gold:
            return False, f"💸 골드가 부족합니다! (필요: {req_gold:,}G, 보유: {pet_coins:,}G)", pet_coins

        core_name = ITEMS_DATABASE.get(used_core, {}).get("name", "고대 핵")
        self.remove_item(used_core, 1)
        new_coins = pet_coins - req_gold
        self.equipped_armor["stars"] = cur_stars + 1
        new_stars = self.equipped_armor["stars"]

        star_str = "★" * new_stars
        bonus_pct = {1: 6, 2: 12, 3: 18, 4: 24, 5: 30}.get(new_stars, 30)

        ancient_msg = ""
        if new_stars == 5:
            ancient_msg = (
                f"\n\n🌌👑 **[고대 특효 & 완전 정복 영구 해금!]**\n"
                f"🛡️ **「{a_info.get('ancient_passive', '고대의 가호')}」**: _{a_info.get('ancient_desc', '')}_\n"
                f"✨ _고대 보스를 50회 이상 정복한 자만이 도달할 수 있는 지고의 경지입니다!_"
            )

        res_text = (
            f"🌑 [{core_name}]의 태고의 힘이 방어구에 깃듭니다...\n"
            f"🌟✨ **[고대 성급 100% 확정 승급 성공!]**\n"
            f"🛡️ **[{a_name} +15 {star_str}]** 달성! (고대 스탯 보너스: +{bonus_pct}%){ancient_msg}"
        )
        return True, res_text, new_coins

    def promote_armor(self, pet_coins: int, pet=None) -> tuple[bool, str, int]:
        """🛡️ v17.2에서는 방어구 승급 트리가 폐지되었으며, 레이드에서 새로운 방어구를 독립적으로 획득하여 영구 소장합니다."""
        return False, "⚠️ v17.2에서는 방어구 승급 트리가 폐지되었습니다! 레이드에서 새로운 상위 방어구를 독립 완제품으로 획득하여 자유롭게 교체 장착하세요.", pet_coins

class Shop:
    @staticmethod
    def buy_item(pet, inventory: Inventory, item_id: str, count: int = 1) -> tuple[bool, str]:
        item_data = ITEMS_DATABASE.get(item_id)
        if not item_data:
            return False, "존재하지 않는 아이템입니다."
        
        total_price = item_data["price"] * count
        if pet.coins < total_price:
            return False, f"💸 골드가 부족합니다! (필요: {total_price:,}G, 보유: {pet.coins:,}G)"

        pet.coins -= total_price
        inventory.add_item(item_id, count)
        return True, f"🛒 [{item_data['name']}] {count}개를 구매했습니다! (-{total_price:,}G)"

    @staticmethod
    def use_item(pet, inventory: Inventory, item_id: str) -> tuple[bool, str]:
        if inventory.items.get(item_id, 0) <= 0:
            return False, "보유하고 있지 않은 아이템입니다."

        item_data = ITEMS_DATABASE.get(item_id)
        
        if "exp" in item_data:
            inventory.remove_item(item_id, 1)
            logs = pet.gain_exp(item_data["exp"])
            return True, f"🍬 [{item_data['name']}] 사용 완료!\n" + "\n".join(logs)

        elif item_id == "potion_atk":
            if pet.atk_iv >= 100: return False, "공격력 IV가 이미 100 MAX입니다!"
            inventory.remove_item(item_id, 1)
            pet.atk_iv = min(100, pet.atk_iv + 1)
            pet.total_iv += 1
            return True, f"⚔️ 공격력 IV 영구 상승! (현재: {pet.atk_iv}/100)"

        elif item_id == "potion_def":
            if pet.def_iv >= 100: return False, "방어력 IV가 이미 100 MAX입니다!"
            inventory.remove_item(item_id, 1)
            pet.def_iv = min(100, pet.def_iv + 1)
            pet.total_iv += 1
            return True, f"🛡️ 방어력 IV 영구 상승! (현재: {pet.def_iv}/100)"

        elif item_id == "potion_hp":
            if pet.hp_iv >= 100: return False, "체력 IV가 이미 100 MAX입니다!"
            inventory.remove_item(item_id, 1)
            pet.hp_iv = min(100, pet.hp_iv + 1)
            pet.total_iv += 1
            return True, f"💖 체력 IV 영구 상승! (현재: {pet.hp_iv}/100)"

        elif item_id == "potion_spd":
            if getattr(pet, "spd_iv", 70) >= 100: return False, "스피드 IV가 이미 100 MAX입니다!"
            inventory.remove_item(item_id, 1)
            pet.spd_iv = min(100, pet.spd_iv + 1)
            pet.total_iv += 1
            return True, f"⚡ 스피드 IV 영구 상승! (현재: {pet.spd_iv}/100)"

        elif item_id == "potion_crit":
            if getattr(pet, "crit_iv", 70) >= 100: return False, "치명타 IV가 이미 100 MAX입니다!"
            inventory.remove_item(item_id, 1)
            pet.crit_iv = min(100, pet.crit_iv + 1)
            pet.total_iv += 1
            return True, f"🎯 치명타 IV 영구 상승! (현재: {pet.crit_iv}/100)"

        elif item_id == "holy_water":
            inventory.remove_item(item_id, 1)
            was_dead = getattr(pet, "is_dead", False)
            pet.is_dead = False
            pet.is_critically_injured = False
            pet.is_sick = False
            if was_dead:
                pet.health = 30
                pet.energy = 0
                pet.stamina = 0
                pet.happiness = 0
                pet.affection = max(0, getattr(pet, "affection", 50) - 20)
                return True, "🌟✨ **[불사의 성수 부활!]** 전사했던 신수가 기적처럼 다시 눈을 떴습니다! (건강 30%, 애정도 -20)"
            else:
                pet.health = min(100, max(50, pet.health + 50))
                pet.stamina = min(pet.max_energy, getattr(pet, "stamina", 100) + 50)
                return True, "🌟 **[불사의 성수 사용]** 신수의 치명상과 부상이 즉시 치료되었습니다! (건강 +50%, 모험기력 +50)"

        elif item_id == "primordial_heart":
            inventory.remove_item(item_id, 1)
            was_dead = getattr(pet, "is_dead", False)
            pet.is_dead = False
            pet.is_critically_injured = False
            pet.is_sick = False
            pet.health = 100
            pet.energy = pet.max_energy
            pet.stamina = pet.max_energy
            pet.happiness = 100
            if was_dead:
                return True, "🌌👑✨ **[태초의 심장 완전 부활!]** 신화의 권능으로 신수가 애정도 손실 없이 100% 완벽하게 부활했습니다! (HP/건강/기력 100% 풀충전)"
            else:
                return True, "🌌✨ **[태초의 심장 사용]** 신수가 완전 회복 상태로 복귀했습니다! (치명상 치료, 건강/생활/모험 기력 100% 완충)"

        elif item_id == "life_gem":
            return False, "💎 생명의 보석은 가방에 보유하고 있으면 고대 레이드 치명상 판정 시 자동으로 발동되어 소모됩니다."

        return False, "사용할 수 없는 아이템입니다."
