# -*- coding: utf-8 -*-
"""
🐾 DAMAGOCHI 10 Legendary Species & 4-Skill System Database (v8.2)
10종 공식 명칭, 10대 고유 성격, 4대 고유 전투 스킬(기본기1·기본기2·고유기·궁극기), 5V 개체값
"""

import random

SPECIES_DATABASE = {
    "호랑이": {
        "name": "백호 (호랑이)",
        "emoji": "🐯",
        "tier": "일반 (Common)",
        "gacha_prob": 0.16,
        "base_hp": 115, "base_atk": 165, "base_def": 110, "base_spd": 130, "base_crit": 150, # BST 670 (바하무트 초과 순수 화력 1위)
        "max_life_energy": 100, "max_adventure_stamina": 100,
        "battle_passive_name": "⚔️ 「맹수의 본능」", "battle_passive_desc": "HP 70% 이상일 때 최종 피해 +6%",
        "mood_title": "🔥 「투쟁심」", "mood_desc": "훈련 EXP +10%, 먹이 행복 +5, 레이드 승리 애정 +2",
        "role": "단일 폭딜 / 치명타 암살형",
        "desc": "강력한 단일 물리 화력과 방어 관통을 지닌 백수의 왕"
    },
    "사자": {
        "name": "황금 사자",
        "emoji": "🦁",
        "tier": "일반 (Common)",
        "gacha_prob": 0.16,
        "base_hp": 155, "base_atk": 130, "base_def": 150, "base_spd": 115, "base_crit": 120, # BST 670 (단단한 공방 밸런서)
        "max_life_energy": 105, "max_adventure_stamina": 105,
        "battle_passive_name": "⚔️ 「왕의 위엄」", "battle_passive_desc": "HP 50% 이하일 때 DEF +10% 및 방어 관통 +10%",
        "mood_title": "👑 「왕의 여유」", "mood_desc": "행복도 자연 감소 -10%, 패배 시 행복도 손실 -20%",
        "role": "안정적인 공방 밸런서 (저체력 역전형)",
        "desc": "체력이 낮아질수록 방어와 관통이 동시에 상승하는 역전형 공방 밸런서"
    },
    "늑대": {
        "name": "달빛 늑대",
        "emoji": "🐺",
        "tier": "일반 (Common)",
        "gacha_prob": 0.16,
        "base_hp": 125, "base_atk": 135, "base_def": 115, "base_spd": 150, "base_crit": 140, # BST 665 (바하무트의 83.1% 기준선)
        "max_life_energy": 95, "max_adventure_stamina": 95,
        "battle_passive_name": "⚔️ 「사냥 본능」", "battle_passive_desc": "적보다 SPD가 높으면 최종 피해 +6%",
        "mood_title": "🌙 「자유로운 사냥꾼」", "mood_desc": "던전 기력 소모 -10% (애정 Lv.8+ 시 추가 -5% 감쇄)",
        "role": "초고속 속도 / 다단히트 암살자",
        "desc": "최고의 스피드와 그림자 연타로 적을 유린하는 신속의 늑대"
    },
    "드래곤": {
        "name": "드래곤",
        "emoji": "🐉",
        "tier": "희귀 (Rare)",
        "gacha_prob": 0.12,
        "base_hp": 135, "base_atk": 160, "base_def": 130, "base_spd": 125, "base_crit": 140, # BST 690
        "max_life_energy": 100, "max_adventure_stamina": 100,
        "battle_passive_name": "⚔️ 「용혈 폭주」", "battle_passive_desc": "HP 40% 이하일 때 스킬 최종 피해 +8%",
        "mood_title": "🔥 「성장에 굶주린 자존심」", "mood_desc": "훈련 EXP +15%, 하드 이상 보스 승리 시 행복 +10",
        "role": "초고화력 원소 폭격 누커",
        "desc": "천룡파와 뇌전을 뿜어내는 압도적인 원소 파괴자"
    },
    "불사조": {
        "name": "주작 불사조",
        "emoji": "🦅",
        "tier": "희귀 (Rare)",
        "gacha_prob": 0.12,
        "base_hp": 145, "base_atk": 135, "base_def": 125, "base_spd": 140, "base_crit": 145, # BST 690
        "max_life_energy": 100, "max_adventure_stamina": 100,
        "battle_passive_name": "⚔️ 「재생의 불꽃」", "battle_passive_desc": "HP 30% 이하 시 최초 1회 최대 HP의 8% 회복",
        "mood_title": "🔥 「따뜻한 생명의 불꽃」", "mood_desc": "건강 회복 효과 +20%, 질병 치료 효과 +20%",
        "role": "무한 재생 / 부활 서스테이너",
        "desc": "불사의 심장, 주작환생을 지닌 불멸조"
    },
    "현무": {
        "name": "현무 거북",
        "emoji": "🐢",
        "tier": "희귀 (Rare)",
        "gacha_prob": 0.10,
        "base_hp": 175, "base_atk": 110, "base_def": 175, "base_spd": 90, "base_crit": 120, # BST 670 (최고 HP & 최고 방어력 1위)
        "max_life_energy": 110, "max_adventure_stamina": 110,
        "battle_passive_name": "⚔️ 「금강불괴」", "battle_passive_desc": "받는 최종 피해 -5%",
        "mood_title": "🌊 「느긋한 철벽」", "mood_desc": "포만/청결/생활에너지 감소 -15% (초장기 지속)",
        "role": "철벽 절대 방어 / 반사 탱커",
        "desc": "북방의 철벽, 천지현무진의 절대 철벽"
    },
    "구미호": {
        "name": "구미호",
        "emoji": "🦊",
        "tier": "영웅 (Heroic)",
        "gacha_prob": 0.07,
        "base_hp": 120, "base_atk": 150, "base_def": 115, "base_spd": 150, "base_crit": 155, # BST 690 (최고 치명타율)
        "max_life_energy": 100, "max_adventure_stamina": 100,
        "battle_passive_name": "⚔️ 「정기흡수」", "battle_passive_desc": "적에게 가한 최종 피해의 5%만큼 HP 회복",
        "mood_title": "🦊 「변덕스러운 애정쟁이」", "mood_desc": "행복도 80+ 시 기력소모 -10%, 애정 Lv.8+ 시 전투 EXP +10%",
        "role": "흡혈 / 매혹 / 디버프",
        "desc": "낮은 방어력을 공격 기반 정기 흡혈과 구천환몽으로 극복하는 지속전형 요수"
    },
    "그리핀": {
        "name": "그리핀",
        "emoji": "🪽",
        "tier": "영웅 (Heroic)",
        "gacha_prob": 0.05,
        "base_hp": 130, "base_atk": 145, "base_def": 120, "base_spd": 160, "base_crit": 135, # BST 690 (최고 스피드 1위)
        "max_life_energy": 95, "max_adventure_stamina": 95,
        "battle_passive_name": "⚔️ 「창공 지배」", "battle_passive_desc": "전투 첫 턴 SPD +12%",
        "mood_title": "🌪️ 「멈추지 않는 질주」", "mood_desc": "던전 기력 소모 -10%, 레이드 기력 소모 -5%",
        "role": "초고속 선공 / 공중 연타 맹금",
        "desc": "천공 폭풍참으로 하늘에서 급강하하는 공중 지배자"
    },
    "기린": {
        "name": "신성 기린",
        "emoji": "🦄",
        "tier": "전설 (Legendary)",
        "gacha_prob": 0.05,
        "base_hp": 150, "base_atk": 150, "base_def": 145, "base_spd": 150, "base_crit": 145, # BST 740 (전설 완전체 2위)
        "max_life_energy": 105, "max_adventure_stamina": 105,
        "battle_passive_name": "⚔️ 「천계의 조화」", "battle_passive_desc": "전투 시작 시 HP/ATK/DEF/SPD +3%",
        "mood_title": "✨ 「천계의 평온」", "mood_desc": "포만/청결/행복 감소 -5%, 질병 발생 확률 -20%",
        "role": "올라운더 만능 완전체 버퍼",
        "desc": "신성한 천계의 지배자"
    },
    "바하무트": {
        "name": "바하무트",
        "emoji": "🐲",
        "tier": "신화 (Mythic)",
        "gacha_prob": 0.01,
        "base_hp": 160, "base_atk": 160, "base_def": 160, "base_spd": 160, "base_crit": 160, # BST 800 (태초의 신화 종합 1위)
        "max_life_energy": 110, "max_adventure_stamina": 110,
        "battle_passive_name": "⚔️ 「파괴신의 혈통」", "battle_passive_desc": "보스에게 주는 최종 피해 +8%",
        "mood_title": "🌌 「종말의 포식자」", "mood_desc": "보스전 EXP +10%, 레이드 보상 +5%, 포만감 감소 +15%",
        "role": "종결 폭딜 / 보스 킬러",
        "desc": "창세종언으로 전 우주를 멸하는 지고의 파괴신"
    }
}

# 10대 신수 종족별 4대 고유 전투 스킬 (기본기1, 기본기2, 고유기, 궁극기)
SPECIES_SKILLS = {
    "호랑이": {
        "basic1": {"name": "🐾 백호격", "atk_ratio": 1.10, "crit_bonus": 0.10, "desc": "ATK 110% 피해 (치명타율 +10%)"},
        "basic2": {"name": "⚡ 맹호 연참", "atk_ratio": 0.65, "hits": 2, "desc": "ATK 65% 피해 × 2회 개별 치명타"},
        "unique": {"name": "🌪️ 서방의 포효", "cooldown": 3, "buff_atk": 0.20, "pen_def": 0.15, "duration": 2, "desc": "2턴간 ATK +20%, 방어 관통 +15%"},
        "ultimate": {"name": "👑 백호멸천격", "cooldown": 5, "atk_ratio": 2.30, "pen_def": 0.30, "execute_bonus": 0.25, "desc": "ATK 230% 피해, DEF 30% 무시, 적 HP 30% 이하 시 피해 +25%"}
    },
    "사자": {
        "basic1": {"name": "☀️ 태양의 발톱", "atk_ratio": 1.05, "desc": "ATK 105% 피해"},
        "basic2": {"name": "🦁 왕의 포효", "atk_ratio": 0.80, "debuff_atk": 0.10, "duration": 2, "desc": "ATK 80% 피해, 2턴간 적 ATK -10%"},
        "unique": {"name": "🛡️ 황금 수호", "cooldown": 3, "dmg_reduction": 0.25, "low_hp_def": 0.15, "duration": 2, "desc": "2턴간 피해 -25%, HP 50% 이하 시 추가 DEF +15%"},
        "ultimate": {"name": "👑 태양왕의 심판", "cooldown": 5, "atk_ratio": 1.80, "heal_hp_pct": 0.15, "buff_all": 0.15, "duration": 2, "desc": "ATK 180% 피해, 최대 HP 15% 회복, 2턴간 ATK/DEF +15%"}
    },
    "늑대": {
        "basic1": {"name": "🌙 월광참", "atk_ratio": 0.90, "spd_bonus": 0.20, "desc": "ATK 90% 피해 (적보다 빠르면 피해 +20%)"},
        "basic2": {"name": "🐺 그림자 사냥", "atk_ratio": 0.55, "hits": 2, "extra_hit_chance": 0.20, "desc": "ATK 55% 피해 × 2회 (20% 확률 추가 1회)"},
        "unique": {"name": "🌫️ 그림자 질주", "cooldown": 3, "buff_spd": 0.25, "buff_dodge": 0.10, "duration": 2, "desc": "2턴간 SPD +25%, 회피율 +10%"},
        "ultimate": {"name": "👑 월식의 사냥", "cooldown": 5, "atk_ratio": 0.70, "hits": 4, "spd_finisher": 0.50, "desc": "ATK 70% 피해 × 4회 개별 치명타 (빠르면 막타 +50%)"}
    },
    "드래곤": {
        "basic1": {"name": "⚡ 뇌룡격", "atk_ratio": 1.20, "debuff_atk_chance": 0.15, "desc": "ATK 120% 피해 (15% 확률 적 ATK -10%)"},
        "basic2": {"name": "🌊 용의 파동", "atk_ratio": 1.35, "pen_def": 0.10, "desc": "ATK 135% 피해 (DEF 10% 무시)"},
        "unique": {"name": "🌩️ 용맥 폭주", "cooldown": 3, "buff_atk": 0.25, "penalty_dmg_taken": 0.10, "duration": 2, "desc": "2턴간 ATK +25% (받는 피해 +10%)"},
        "ultimate": {"name": "👑 용제멸세", "cooldown": 6, "atk_ratio": 2.60, "pen_def": 0.25, "crit_extra_atk": 0.60, "desc": "ATK 260% 피해, DEF 25% 무시 (치명타 시 추가 60% 피해)"}
    },
    "불사조": {
        "basic1": {"name": "🔥 화염 날개", "atk_ratio": 1.00, "burn_chance": 0.30, "desc": "ATK 100% 피해 (30% 확률 화상)"},
        "basic2": {"name": "🌋 불사의 불꽃", "atk_ratio": 0.85, "heal_hp_pct": 0.05, "desc": "ATK 85% 피해 (최대 HP 5% 즉시 회복)"},
        "unique": {"name": "❤️ 불사의 심장", "cooldown": 4, "regen_turn_pct": 0.04, "duration": 3, "desc": "3턴간 턴 종료 시 HP 4% 지속 회복"},
        "ultimate": {"name": "👑 주작환생", "cooldown": 6, "atk_ratio": 1.70, "clutch_heal": 0.30, "revive_hp_pct": 0.25, "desc": "ATK 170% 피해, HP 30% 이하 시 30% 즉시 회복 & 1회 부활"}
    },
    "현무": {
        "basic1": {"name": "🪨 현무철갑", "atk_ratio": 0.75, "buff_def": 0.20, "duration": 1, "desc": "ATK 75% 피해 (1턴간 DEF +20%)"},
        "basic2": {"name": "🌊 대지 충격", "atk_ratio": 1.00, "slow_chance": 0.20, "desc": "ATK 100% 피해 (20% 확률 적 SPD -15%)"},
        "unique": {"name": "🛡️ 북방의 철벽", "cooldown": 3, "dmg_reduction": 0.35, "penalty_spd": 0.10, "duration": 2, "desc": "2턴간 받는 피해 -35% (SPD -10%)"},
        "ultimate": {"name": "👑 천지현무진", "cooldown": 6, "buff_def": 0.40, "dmg_reduction": 0.20, "reflect_pct": 0.20, "duration": 3, "desc": "3턴간 DEF +40%, 피해 -20%, 피격 시 20% 반사"}
    },
    "구미호": {
        "basic1": {"name": "🔥 여우불", "atk_ratio": 0.95, "burn_chance": 0.30, "duration": 2, "desc": "ATK 95% 피해 (30% 확률 2턴 화상)"},
        "basic2": {"name": "💋 매혹", "atk_ratio": 0.70, "stun_chance": 0.20, "desc": "ATK 70% 피해 (20% 확률 적 다음 행동 실패)"},
        "unique": {"name": "🌙 구미 흡령", "cooldown": 3, "atk_ratio": 1.20, "lifesteal_pct": 0.25, "desc": "ATK 120% 피해 (입힌 피해의 25% HP 회복)"},
        "ultimate": {"name": "👑 구천환몽", "cooldown": 5, "atk_ratio": 1.90, "debuff_all": 0.15, "lifesteal_pct": 0.20, "duration": 2, "desc": "ATK 190% 피해, 2턴간 적 공/속 -15%, 피해 20% 흡혈"}
    },
    "그리핀": {
        "basic1": {"name": "🌪️ 폭풍 발톱", "atk_ratio": 0.95, "first_strike_bonus": 0.20, "desc": "ATK 95% 피해 (선공 시 피해 +20%)"},
        "basic2": {"name": "🪽 공중 강습", "atk_ratio": 0.75, "double_hit_chance": 0.35, "desc": "ATK 75% 피해 (35% 확률 추가 1회 공격)"},
        "unique": {"name": "⚡ 폭풍의 날개", "cooldown": 3, "buff_spd": 0.30, "buff_double": 0.10, "duration": 2, "desc": "2턴간 SPD +30%, 2연타 확률 +10%"},
        "ultimate": {"name": "👑 천공 폭풍참", "cooldown": 5, "atk_ratio": 0.80, "hits": 3, "speed_diff_hit": 0.20, "desc": "ATK 80% × 3회 (SPD 차이 20% 이상 시 4번째 추가 공격)"}
    },
    "기린": {
        "basic1": {"name": "✨ 성광", "atk_ratio": 1.10, "desc": "ATK 110% 피해"},
        "basic2": {"name": "🌈 천계의 축복", "heal_hp_pct": 0.10, "buff_all": 0.10, "duration": 2, "desc": "HP 10% 회복, 2턴간 전 스탯 +10%"},
        "unique": {"name": "🌌 신성 정화", "cooldown": 3, "cleanse": True, "resist_buff": 0.30, "duration": 2, "desc": "상태이상 제거, 2턴간 저항 +30%"},
        "ultimate": {"name": "👑 천계강림", "cooldown": 6, "atk_ratio": 2.00, "heal_hp_pct": 0.15, "buff_all": 0.15, "duration": 3, "desc": "ATK 200% 피해, HP 15% 회복, 3턴간 전 스탯 +15%"}
    },
    "바하무트": {
        "basic1": {"name": "☄️ 종말의 발톱", "atk_ratio": 1.25, "desc": "ATK 125% 피해"},
        "basic2": {"name": "🌌 심연 브레스", "atk_ratio": 1.50, "pen_def": 0.15, "desc": "ATK 150% 피해 (적 DEF 15% 무시)"},
        "unique": {"name": "👁️ 파괴신의 위압", "cooldown": 4, "buff_atk": 0.30, "buff_crit": 0.15, "debuff_enemy_def": 0.10, "duration": 2, "desc": "2턴간 ATK +30%, CRIT +15%, 적 DEF -10%"},
        "ultimate": {"name": "👑 창세종언", "cooldown": 6, "atk_ratio": 3.00, "pen_def": 0.35, "execute_bonus": 0.40, "desc": "ATK 300% 피해, DEF 35% 무시, 적 HP 30% 이하 시 피해 +40%"}
    }
}

PERSONALITIES = {
    "사나움": {"emoji": "🔥", "name": "사나움", "desc": "ATK +12%, DEF -6% (초공격형)", "stat_mod": {"atk_mult": 1.12, "def_mult": 0.94}, "battle_trait": "fierce"},
    "용맹함": {"emoji": "🛡️", "name": "용맹함", "desc": "HP 50% 이하 시 ATK/DEF +10% (위기 돌파)", "stat_mod": {}, "battle_trait": "brave_crisis"},
    "소심함": {"emoji": "🌙", "name": "소심함", "desc": "회피율 +10%, ATK -5% (생존 회피형)", "stat_mod": {"atk_mult": 0.95}, "battle_trait": "dodge_boost"},
    "민첩함": {"emoji": "⚡", "name": "민첩함", "desc": "SPD +12%, HP -5% (선공·연타형)", "stat_mod": {"spd_mult": 1.12, "hp_mult": 0.95}, "battle_trait": "swift"},
    "신중함": {"emoji": "🧱", "name": "신중함", "desc": "DEF +12%, SPD -8% (철벽 탱커형)", "stat_mod": {"def_mult": 1.12, "spd_mult": 0.92}, "battle_trait": "cautious"},
    "성급함": {"emoji": "💢", "name": "성급함", "desc": "첫 3턴 ATK +15%, 이후 -5% (초반 폭딜)", "stat_mod": {}, "battle_trait": "early_burst"},
    "온순함": {"emoji": "❤️", "name": "온순함", "desc": "턴 종료 시 HP 2% 회복, CRIT -5% (장기전형)", "stat_mod": {"crit_mod": -5}, "battle_trait": "gentle_regen"},
    "냉정함": {"emoji": "🎯", "name": "냉정함", "desc": "CRIT +8%, 치명 피해 +10%, HP -5% (크리 특화)", "stat_mod": {"crit_mod": 8, "hp_mult": 0.95}, "battle_trait": "calm_crit"},
    "오만함": {"emoji": "👑", "name": "오만함", "desc": "일반 몬스터 상대 피해 +15% (약자 상대 강함)", "stat_mod": {}, "battle_trait": "arrogant_crush"},
    "불굴": {"emoji": "🌌", "name": "불굴", "desc": "피격 시 20% 확률 피해 절반 (불사신 버티기)", "stat_mod": {}, "battle_trait": "indomitable"}
}

ELEMENT_PASSIVES = {
    "화염": {"name": "작열의 불꽃", "desc": "치명타 확률 +20% & 방어 관통", "effect": "crit"},
    "수호": {"name": "절대 철벽", "desc": "받는 모든 피해 25% 상시 흡수 감소", "effect": "shield"},
    "질풍": {"name": "신속의 돌풍", "desc": "스피드 비례 최대 40% 확률로 1턴 2연타", "effect": "double_strike"},
    "암흑": {"name": "심연의 갈증", "desc": "입힌 피해의 20% 체력 흡수 (흡혈)", "effect": "lifesteal"},
    "대지": {"name": "대지의 재생력", "desc": "최대 HP +25% & 턴당 3% 체력 재생", "effect": "hp_regen"}
}

ELEMENT_MAP = {
    "호랑이": ["화염", "질풍", "수호", "암흑", "대지"],
    "사자": ["수호", "화염", "대지", "질풍", "암흑"],
    "늑대": ["질풍", "암흑", "화염", "수호", "대지"],
    "드래곤": ["화염", "대지", "질풍", "암흑", "수호"],
    "불사조": ["화염", "대지", "수호", "질풍", "암흑"],
    "현무": ["수호", "대지", "화염", "질풍", "암흑"],
    "구미호": ["암흑", "화염", "질풍", "수호", "대지"],
    "그리핀": ["질풍", "수호", "화염", "암흑", "대지"],
    "기린": ["수호", "대지", "화염", "질풍", "암흑"],
    "바하무트": ["암흑", "화염", "대지", "질풍", "수호"]
}

class Genetics:
    @staticmethod
    def iv_multiplier(iv: int) -> float:
        """Palworld-style IV 잠재력 배율 공식: IV 0 = 1.00배 (+0%), IV 100 = 1.30배 (+30%)"""
        iv = max(0, min(100, iv))
        return 1.0 + (iv * 0.003)

    @staticmethod
    def calc_rank(total_iv: int) -> str:
        """공식 8단계 IV 랭크 판정 (0 ~ 500)"""
        if total_iv >= 500:
            return "🌌 PERFECT"
        elif total_iv >= 460:
            return "👑 SSS"
        elif total_iv >= 420:
            return "💎 SS"
        elif total_iv >= 360:
            return "✨ S"
        elif total_iv >= 300:
            return "🔹 A"
        elif total_iv >= 230:
            return "🟢 B"
        elif total_iv >= 150:
            return "⚪ C"
        else:
            return "⚫ F"

    @staticmethod
    def hatch_random_egg() -> dict:
        r = random.random()
        cumulative = 0.0
        selected_species_key = "호랑이"
        
        for sp_key, sp_data in SPECIES_DATABASE.items():
            cumulative += sp_data["gacha_prob"]
            if r <= cumulative:
                selected_species_key = sp_key
                break
                
        sp_data = SPECIES_DATABASE[selected_species_key]
        element = random.choice(ELEMENT_MAP.get(selected_species_key, ["화염", "수호", "질풍", "암흑", "대지"]))
        passive = ELEMENT_PASSIVES.get(element, ELEMENT_PASSIVES["화염"])
        
        # 5V 초기 개체값 (1세대 초기 신수: 총합 300 이하 제한, 개별 스탯 10 ~ 60)
        while True:
            hp_iv = random.randint(10, 60)
            atk_iv = random.randint(10, 60)
            def_iv = random.randint(10, 60)
            spd_iv = random.randint(10, 60)
            crit_iv = random.randint(10, 60)
            if hp_iv + atk_iv + def_iv + spd_iv + crit_iv <= 300:
                break
        
        # 2% 확률 히든 변이 (이로치)
        is_shiny = (random.random() < 0.02)
        if is_shiny:
            hp_iv = min(65, hp_iv + 10)
            atk_iv = min(65, atk_iv + 10)
            def_iv = min(65, def_iv + 10)
            spd_iv = min(65, spd_iv + 10)
            crit_iv = min(65, crit_iv + 10)
            
            # 샤이니 변이 적용 후에도 1세대 초기 IV 총합 300 이하 엄격 보장
            tot = hp_iv + atk_iv + def_iv + spd_iv + crit_iv
            if tot > 300:
                excess = tot - 300
                crit_iv = max(0, crit_iv - excess)

        total_iv = hp_iv + atk_iv + def_iv + spd_iv + crit_iv
        rank = Genetics.calc_rank(total_iv)

        charm = random.randint(50, 95)
        affection = random.randint(40, 60)
        personality_key = random.choice(list(PERSONALITIES.keys()))

        return {
            "species_key": selected_species_key,
            "species_name": sp_data["name"],
            "emoji": sp_data["emoji"],
            "tier": sp_data["tier"],
            "element": element,
            "role": sp_data["role"],
            "role_desc": passive["desc"],
            "effect": passive["effect"],
            "hp_iv": hp_iv,
            "atk_iv": atk_iv,
            "def_iv": def_iv,
            "spd_iv": spd_iv,
            "crit_iv": crit_iv,
            "total_iv": total_iv,
            "rank": rank,
            "charm": charm,
            "affection": affection,
            "personality": personality_key,
            "is_shiny": is_shiny
        }

    @staticmethod
    def hatch_reincarnated_egg(parent_pet, keep_species: bool = True) -> dict:
        """99렙 만렙 환생 개체값 혈통 유전 공식:
        - keep_species=True: 부모와 동일한 종족/속성 유지 및 IV 유전
        - keep_species=False: 10대 신수 중 새로운 종족 랜덤 가챠 및 IV 유전"""
        if keep_species and parent_pet:
            selected_species_key = getattr(parent_pet, "species_key", "호랑이")
            sp_data = SPECIES_DATABASE.get(selected_species_key, SPECIES_DATABASE["호랑이"])
            element = getattr(parent_pet, "element", "화염")
            passive = ELEMENT_PASSIVES.get(element, ELEMENT_PASSIVES["화염"])
            is_shiny = (random.random() < 0.03) or getattr(parent_pet, "is_shiny", False)
            charm = random.randint(60, 99)
            affection = random.randint(40, 60)
            personality_key = getattr(parent_pet, "personality", random.choice(list(PERSONALITIES.keys())))
            
            egg_data = {
                "species_key": selected_species_key,
                "species_name": sp_data["name"],
                "emoji": sp_data["emoji"],
                "tier": sp_data["tier"],
                "element": element,
                "role": sp_data["role"],
                "role_desc": passive["desc"],
                "effect": passive["effect"],
                "charm": charm,
                "affection": affection,
                "personality": personality_key,
                "is_shiny": is_shiny
            }
        else:
            egg_data = Genetics.hatch_random_egg()
        
        p_hp = getattr(parent_pet, "hp_iv", 70)
        p_atk = getattr(parent_pet, "atk_iv", 70)
        p_def = getattr(parent_pet, "def_iv", 70)
        p_spd = getattr(parent_pet, "spd_iv", 70)
        p_crit = getattr(parent_pet, "crit_iv", 70)

        def roll_inherited_stat(parent_val: int) -> int:
            if random.random() < 0.50:
                return parent_val # 50% 확률로 부모 값 100% 그대로 유전
            else:
                low = max(0, parent_val - 10)
                return random.randint(low, 100) # 50% 확률로 (부모값-10 ~ 100) 랜덤 롤

        hp_iv = roll_inherited_stat(p_hp)
        atk_iv = roll_inherited_stat(p_atk)
        def_iv = roll_inherited_stat(p_def)
        spd_iv = roll_inherited_stat(p_spd)
        crit_iv = roll_inherited_stat(p_crit)

        # 변이인 경우 +15 보정
        if egg_data["is_shiny"]:
            hp_iv = min(100, hp_iv + 15)
            atk_iv = min(100, atk_iv + 15)
            def_iv = min(100, def_iv + 15)
            spd_iv = min(100, spd_iv + 15)
            crit_iv = min(100, crit_iv + 15)

        total_iv = hp_iv + atk_iv + def_iv + spd_iv + crit_iv
        rank = Genetics.calc_rank(total_iv)

        egg_data.update({
            "hp_iv": hp_iv,
            "atk_iv": atk_iv,
            "def_iv": def_iv,
            "spd_iv": spd_iv,
            "crit_iv": crit_iv,
            "total_iv": total_iv,
            "rank": rank
        })
        return egg_data

    @staticmethod
    def get_form_title(species_key: str, element: str, level: int, is_shiny: bool = False) -> tuple[int, str]:
        sp_name = SPECIES_DATABASE.get(species_key, {}).get("name", species_key)
        shiny_tag = "✨ " if is_shiny else ""
        
        if level >= 99:
            return 4, f"{shiny_tag}👑 태초의 전설 {element} {sp_name} 오메가"
        elif level >= 70:
            return 3, f"{shiny_tag}업화의 극의 {element} {sp_name}"
        elif level >= 40:
            return 2, f"{shiny_tag}불꽃의 {element} {sp_name}"
        else:
            return 1, f"{shiny_tag}아기 {element} {sp_name}"
