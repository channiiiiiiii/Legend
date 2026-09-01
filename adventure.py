# -*- coding: utf-8 -*-
"""
🗺️ DAMAGOCHI 10 Species 4-Skills & Full Equipment Battle Engine (v17.2)
10대 신수 4대 스킬, 종족 전용 보물(+10 고유 효과), 8종 방어구(피해감소/저항), 5대 보스 DPT/TTK 기반 밸런스 & 21전 완성형 엔진
"""

import random
from farming import roll_gem_drop, roll_stone_drop
import time
from shop import EXCLUSIVE_RELICS, ARMORS_DATABASE
from species import PERSONALITIES, SPECIES_SKILLS

BOSS_DATABASE = {
    1: {
        "id": 1,
        "name": "고대 엔트",
        "emoji": "🌳",
        "title_ancient": "「태고의 숲의 왕」 고대 엔트",
        "type": "방어 / 회복형",
        "trait_name": "불멸의 뿌리",
        "check_stat": "순간 화력 검사 (강한 한 방)",
        "req_level": 1,
        "energy_cost": 25,
        "base_hp": 1200, "base_atk": 45, "base_def": 80, "base_spd": 70,
        "base_gold": 1200, "base_exp": 600,
        "desc": "약한 공격을 무시하고 체력을 회복하는 「불멸의 뿌리」 보유"
    },
    2: {
        "id": 2,
        "name": "크리스탈 드래곤",
        "emoji": "💎",
        "title_ancient": "「영원의 수정용제」 크리스탈 드래곤",
        "type": "반사 / 방어형",
        "trait_name": "절대 반사",
        "check_stat": "생존력 검사 (HP / DEF / 흡혈)",
        "req_level": 25,
        "energy_cost": 35,
        "base_hp": 2200, "base_atk": 95, "base_def": 150, "base_spd": 120,
        "base_gold": 3500, "base_exp": 1800,
        "desc": "가한 피해를 반사하여 생존력을 시험하는 「절대 반사」 보유"
    },
    3: {
        "id": 3,
        "name": "이프리트",
        "emoji": "🔥",
        "title_ancient": "「태초의 염제 대악마」 이프리트",
        "type": "공격 / 화상형",
        "trait_name": "업화 누적",
        "check_stat": "DPS 검사 (신속한 격파)",
        "req_level": 50,
        "energy_cost": 45,
        "base_hp": 3200, "base_atk": 140, "base_def": 110, "base_spd": 115,
        "base_gold": 9000, "base_exp": 4500,
        "desc": "시간이 지날수록 공격력과 화상이 누적되는 「업화 누적」 보유"
    },
    4: {
        "id": 4,
        "name": "성운 가디언",
        "emoji": "☄️",
        "title_ancient": "「시간의 지배자」 성운 가디언",
        "type": "속도 / 연타형",
        "trait_name": "시간 지배",
        "check_stat": "SPD 검사 (선공 및 시간 왜곡 방어)",
        "req_level": 70,
        "energy_cost": 50,
        "base_hp": 2500, "base_atk": 110, "base_def": 95, "base_spd": 160,
        "base_gold": 15000, "base_exp": 7500,
        "desc": "플레이어와의 SPD 차이에 따라 추가 턴과 시간 정지를 발동하는 「시간 지배」 보유"
    },
    5: {
        "id": 5,
        "name": "오메가",
        "emoji": "🪐",
        "title_ancient": "「태초의 암흑 파괴신」 오메가",
        "type": "종합형 최종보스",
        "trait_name": "약자멸시",
        "check_stat": "종합 스펙 검사 (풀세팅 육성)",
        "req_level": 85,
        "energy_cost": 50,
        "base_hp": 6000, "base_atk": 220, "base_def": 300, "base_spd": 140,
        "base_gold": 30000, "base_exp": 15000,
        "desc": "기준 공격력 미달 시 피해를 면역하는 절대 지고의 「약자멸시」 보유"
    }
}

BOSS_DIALOGUES = {
    1: { # 🌳 고대 엔트
        "start": ["「작은 생명이여... 숲 앞에서 고개를 숙여라.」", "「수백 번의 겨울이 지나도 나는 이곳에 서 있었다.」", "「네가 베려는 것은 나무가 아니다. 태고의 시간이다.」"],
        "first_hit": ["「그 정도 칼날로 나의 뿌리를 자를 수 있겠느냐.」", "「바람이 스친 줄 알았구나.」"],
        "trait": ["「숲은 죽지 않는다. 다시 자라날 뿐이다.」", "「대지가 나의 피이고, 뿌리가 나의 심장이다.」", "「베어라. 다시 돋아날 것이다.」"],
        "hp_70": ["「오랜만에 숲이 흔들리는군.」", "「조금은 진지해져야겠구나.」"],
        "hp_30": ["「태고의 뿌리여... 더 깊이 내려가라.」", "「숲 전체가 나와 함께 숨 쉰다.」"],
        "hp_10": ["「이 몸이 쓰러진다 해도 숲은 남는다.」", "「마지막 가지 하나까지 너를 막겠다.」"],
        "player_crit": ["「...제법 깊이 들어오는구나.」", "「작은 발톱이라 얕보았더니, 상처를 남기는군.」"],
        "player_low_hp": ["「작은 생명은 흙으로 돌아가는 법이다.」", "「그만 쉬어라. 숲이 너를 품어주마.」"],
        "victory": ["「숲은 오늘도 변함없이 서 있다.」"],
        "defeat": ["「숲은... 다시 자랄 것이다...」", "「잘했다... 작은 생명이여...」"]
    },
    2: { # 💎 크리스탈 드래곤
        "start": ["「눈부신 것은 나뿐이면 충분하다.」", "「다가오거라. 네 힘이 얼마나 아름답게 깨지는지 보자.」", "「내 비늘 하나조차 네 칼날보다 단단하다.」"],
        "first_hit": ["「흥미롭군. 그 힘, 그대로 돌려주마.」", "「깨뜨릴 생각이라면 네 손부터 조심하는 게 좋을 것이다.」"],
        "trait": ["「네가 준 상처를 그대로 돌려주마.」", "「수정은 빛만 반사하는 것이 아니다.」", "「더 강하게 때려보아라. 그만큼 네가 아플 테니.」"],
        "hp_70": ["「내 몸에 금이 갔다고 생각했나? 그건 빛의 굴절일 뿐이다.」", "「조금은 흥미로운 상대군.」"],
        "hp_30": ["「감히... 나의 결정을 깨뜨리다니.」", "「좋다. 이제 네 피로 이 균열을 메우겠다.」"],
        "hp_10": ["「완벽함에도 끝이 있다는 것인가...」", "「아니. 아직 나는 부서지지 않았다.」"],
        "player_crit": ["「좋은 일격이다. 그래서 더 아름답게 반사되겠지.」", "「네 힘이 강할수록 네 고통도 커진다.」"],
        "player_low_hp": ["「빛나는 것은 아름답지만... 깨지기 쉽지.」", "「네 조각도 꽤 아름다울 것 같군.」"],
        "victory": ["「역시 완벽한 것은 나 하나면 충분하다.」"],
        "defeat": ["「결국... 나조차 깨지는가...」", "「이 균열을... 기억하겠다...」"]
    },
    3: { # 🔥 이프리트
        "start": ["「타올라라! 재조차 남기지 않겠다!」", "「내 앞에 섰다는 건 불타고 싶다는 뜻이겠지!」", "「좋아! 어디까지 버티나 보자!」"],
        "first_hit": ["「하하! 더 세게 와라!」", "「이 정도 열기로 나를 꺼뜨릴 셈이냐!」"],
        "trait": ["「시간이 길어질수록 네 죽음만 가까워진다.」", "「한 번 붙은 불은 멈추지 않는다.」", "「숨 쉬는 것조차 뜨거워질 것이다!」"],
        "hp_70": ["「좋아! 불꽃이 더 거세지는군!」", "「이제 좀 뜨거워졌나!」"],
        "hp_30": ["「크하하하! 이 정도 상처로 불이 꺼질 것 같으냐!」", "「내 피도 불이다!」"],
        "hp_10": ["「끝까지 타오른 자가 승자다!」", "「꺼질 바엔 세상까지 태워버리겠다!」"],
        "player_crit": ["「좋다! 그 정도는 되어야 불맛이 나지!」", "「크하하! 더 뜨겁게 해봐라!」"],
        "player_low_hp": ["「타는 냄새가 제법 좋군!」", "「조금만 더 버텨봐라. 완전히 재가 될 때까지!」"],
        "victory": ["「하하하! 결국 다 타버리는군!」"],
        "defeat": ["「내 불꽃이... 꺼질 리가...」", "「아직... 더 태울 것이...」"]
    },
    4: { # ☄️ 성운 가디언
        "start": ["「너의 한 걸음은 나에겐 영겁이다.」", "「시작과 끝은 이미 보았다. 너만 아직 모를 뿐이다.」", "「시간은 강자의 편이 아니라, 나의 것이다.」"],
        "first_hit": ["「느리군.」", "「그 공격은 이미 지나간 미래에서 보았다.」"],
        "trait": ["「멈춰라. 아직 네 차례가 아니다.」", "「시간은 나에게 한 번 더 흐른다.」", "「네 순간을 빼앗겠다.」"],
        "hp_70": ["「예상보다 조금 빠르군.」", "「시간축을 다시 계산해야겠군.」"],
        "hp_30": ["「이 미래는... 기록에 없었다.」", "「그렇다면 시간을 직접 고치겠다.」"],
        "hp_10": ["「끝이 가까워지는 감각... 이것이군.」", "「처음으로 나 역시 시간을 두려워하는가.」"],
        "player_crit": ["「예측에서 벗어났군. 미세하지만 의미 있는 오차다.」"],
        "player_low_hp": ["「네 시간은 거의 끝났다.」", "「마지막 몇 초를 소중히 써라.」"],
        "victory": ["「예정된 결과다.」"],
        "defeat": ["「시간이... 나를 떠나는군...」", "「이 결말은... 보지 못했다...」"]
    },
    5: { # 🪐 오메가
        "start": ["「약자는 나를 바라볼 자격조차 없다.」", "「여기까지 왔다는 사실만은 인정하지.」", "「너의 힘이 진짜인지, 아니면 운이었는지 확인해주마.」"],
        "first_hit": ["「...이게 공격인가?」", "「조금은 존재감이 있군.」"],
        "trait": ["「약자는 나를 상처 입힐 자격조차 없다.」", "「기준조차 넘지 못한 힘으로 무엇을 증명하려는 것이냐.」", "「강해져서 돌아오든가, 여기서 사라져라.」"],
        "hp_70": ["「여기까지 밀어붙인 자는 오랜만이다.」", "「좋다. 이제 조금 힘을 써주지.」"],
        "hp_30": ["「필멸자가 여기까지 밀어붙이다니...」", "「그렇다면 너도 종말을 보아라.」", "「이제부터는 시험이 아니다.」"],
        "hp_10": ["「신화의 끝을... 네가 쓰겠다는 것이냐.」", "「오너라. 마지막까지 발버둥 쳐봐라.」"],
        "player_crit": ["「훌륭하다. 한 번 더 해봐라.」", "「그 일격은 기억해둘 가치가 있군.」"],
        "player_low_hp": ["「결국 여기까지인가. 실망이군.」", "「더 강해져서 오너라.」"],
        "victory": ["「결국 약자는 사라질 뿐이다.」"],
        "defeat": ["「...훌륭하다.」", "「새로운 신화가... 시작되었구나.」"]
    }
}

def get_boss_dialogue(boss_id: int, trigger: str) -> str:
    """👑 5대 레이드 보스 상황별 대사 추출기"""
    b_d = BOSS_DIALOGUES.get(boss_id, BOSS_DIALOGUES.get(1, {}))
    lines = b_d.get(trigger, [])
    if lines:
        return random.choice(lines)
    return ""

RAID_DIFFICULTIES = {
    1: {"name": "🟢 노말 (Normal)", "req_lvl_add": 0, "hp_mult": 3.5, "atk_mult": 2.2, "def_mult": 1.2, "spd_mult": 1.00, "exp_mult": 1.0, "gold_mult": 1.0, "injury_rate": 0.0},
    2: {"name": "🔵 하드 (Hard)", "req_lvl_add": 10, "hp_mult": 8.0, "atk_mult": 3.5, "def_mult": 1.6, "spd_mult": 1.10, "exp_mult": 1.5, "gold_mult": 2.0, "injury_rate": 0.0},
    3: {"name": "🟣 악몽 (Nightmare)", "req_lvl_add": 20, "hp_mult": 18.0, "atk_mult": 5.5, "def_mult": 2.2, "spd_mult": 1.35, "exp_mult": 2.2, "gold_mult": 3.0, "injury_rate": 0.10},
    4: {"name": "🟡 신화 (Mythic)", "req_lvl_add": 30, "hp_mult": 35.0, "atk_mult": 7.5, "def_mult": 2.8, "spd_mult": 1.50, "exp_mult": 3.2, "gold_mult": 4.5, "injury_rate": 0.25},
    5: {"name": "🔴 고대 (Ancient)", "req_lvl_add": 40, "hp_mult": 55.0, "atk_mult": 9.5, "def_mult": 3.5, "spd_mult": 1.50, "exp_mult": 4.0, "gold_mult": 4.0, "injury_rate": 0.50}
}

# 👑 5대 레이드 보스 난이도별 정밀 스탯 데이터베이스 (v17.2 Master Ground Truth)
BOSS_STAT_TABLE = {
    1: { # ⚪ Normal
        1: {"hp": 8000, "atk": 320, "def": 200, "spd": 180, "crit": 100},   # 🌳 엔트
        2: {"hp": 11000, "atk": 430, "def": 300, "spd": 220, "crit": 140},  # 💎 크리스탈 드래곤
        3: {"hp": 9000, "atk": 580, "def": 120, "spd": 220, "crit": 220},   # 🔥 이프리트
        4: {"hp": 14000, "atk": 500, "def": 180, "spd": 340, "crit": 180},  # ☄️ 성운 가디언
    },
    2: { # 🔵 Hard
        1: {"hp": 22000, "atk": 700, "def": 360, "spd": 340, "crit": 180},  # 🌳 엔트
        2: {"hp": 28000, "atk": 900, "def": 520, "spd": 450, "crit": 240},  # 💎 크리스탈 드래곤
        3: {"hp": 24000, "atk": 1200, "def": 250, "spd": 430, "crit": 330}, # 🔥 이프리트
        4: {"hp": 36000, "atk": 1050, "def": 340, "spd": 650, "crit": 280}, # ☄️ 성운 가디언
    },
    3: { # 🟣 Nightmare
        1: {"hp": 45000, "atk": 1200, "def": 600, "spd": 520, "crit": 280}, # 🌳 엔트
        2: {"hp": 58000, "atk": 1600, "def": 820, "spd": 680, "crit": 370}, # 💎 크리스탈 드래곤
        3: {"hp": 48000, "atk": 2100, "def": 400, "spd": 650, "crit": 520}, # 🔥 이프리트
        4: {"hp": 75000, "atk": 1800, "def": 550, "spd": 980, "crit": 440}, # ☄️ 성운 가디언
    },
    4: { # 🟡 Mythic
        1: {"hp": 75000, "atk": 2000, "def": 900, "spd": 760, "crit": 420},  # 🌳 엔트
        2: {"hp": 95000, "atk": 2650, "def": 1250, "spd": 960, "crit": 550}, # 💎 크리스탈 드래곤
        3: {"hp": 65000, "atk": 3500, "def": 600, "spd": 920, "crit": 750},  # 🔥 이프리트
        4: {"hp": 125000, "atk": 3000, "def": 800, "spd": 1400, "crit": 650},# ☄️ 성운 가디언
    },
    5: { # 🔴 Ancient
        1: {"hp": 160000, "atk": 3300, "def": 1350, "spd": 1150, "crit": 600}, # 🌳 고대 엔트
        2: {"hp": 210000, "atk": 4400, "def": 2000, "spd": 1500, "crit": 760}, # 💎 고대 크리스탈 드래곤
        3: {"hp": 130000, "atk": 5800, "def": 800, "spd": 1400, "crit": 1000}, # 🔥 고대 이프리트
        4: {"hp": 240000, "atk": 5000, "def": 1100, "spd": 2050, "crit": 900}, # ☄️ 고대 성운 가디언
        5: {"hp": 420000, "atk": 7000, "def": 2400, "spd": 1950, "crit": 1200} # 🪐 오메가 (종합 최종보스)
    }
}

# ⚔️ 5대 보스 난이도별 공식 추천 전투력 (v17.2 표준 늑대 CP 기반 정밀 밸런스)
RECOMMENDED_COMBAT_POWERS = {
    1: {1: 12000, 2: 35000, 3: 75000,  4: 150000, 5: 250000}, # 🌳 고대 엔트
    2: {1: 18000, 2: 45000, 3: 90000,  4: 175000, 5: 270000}, # 💎 크리스탈 드래곤
    3: {1: 25000, 2: 55000, 3: 110000, 4: 200000, 5: 285000}, # 🔥 이프리트
    4: {1: 30000, 2: 65000, 3: 130000, 4: 230000, 5: 300000}, # ☄️ 성운 가디언
    5: {1: 35000, 2: 75000, 3: 150000, 4: 250000, 5: 320000}  # 🪐 오메가 (Ancient 전용 종결)
}

# 🎁 v17.2 첫 클리어 확정 방어구 보상 매핑
FIRST_CLEAR_ARMORS = {
    1: "leather_armor",         # ⚪ Normal: 🟢 가죽 갑옷
    2: "crystal_armor",         # 🔵 Hard: 🔵 수정 갑옷
    3: "celestial_armor",       # 🟣 Nightmare: 🟣 천계 갑주
    4: "mythic_celestial_armor" # 🟡 Mythic: 🔴 천계신의 갑주
}

# 🌑 v16.2 Ancient 보스별 10회 토벌 확정 별 승급 핵 매핑
ANCIENT_BOSS_CORES = {
    1: "ancient_core_ent",      # 🌳 태고목의 핵
    2: "ancient_core_dragon",   # 💎 불멸결정의 핵
    3: "ancient_core_ifrit",    # 🔥 영겁화염의 핵
    4: "ancient_core_guardian", # ☄️ 성운의 핵
    5: "ancient_core_omega"     # 🪐 종말의 핵
}

def get_recommended_cp(boss_id: int, diff_id: int) -> int:
    """보스 및 난이도별 추천 전투력 반환"""
    return RECOMMENDED_COMBAT_POWERS.get(boss_id, {}).get(diff_id, 10000)

def get_power_judgement(player_cp: int, recommended_cp: int, is_ancient: bool = False) -> tuple[str, str]:
    """플레이어 전투력 vs 추천 전투력 비교 판정 태그 및 설명 반환 (v15.1 표준)"""
    # 잡지식: '판정(Judgement)'은 수치뿐 아니라 보스 상성과 기믹 숙련도에 따라 실제 체감 난이도가 달라져용!
    ratio = player_cp / max(1, recommended_cp)
    if is_ancient:
        if ratio >= 1.15:
            return "🟢 매우 높은 완성도", "종결 육성 스펙을 갖추어 고대 졸업 시험에 도전할 준비가 되었습니다."
        elif ratio >= 1.00:
            return "🔵 적정", "권장 전투력을 충족했습니다. 무결점 패턴 대응으로 졸업을 노려보세요."
        elif ratio >= 0.90:
            return "🟡 도전", "전투력이 다소 부족합니다. 상성과 철저한 기믹 파훼가 요구됩니다."
        elif ratio >= 0.80:
            return "🟠 위험", "전투력 격차가 있습니다. 종결 장비 및 초월 보강 후 도전을 권장합니다."
        else:
            return "🔴 극위험", "엔드게임 최고 난이도입니다. 만렙 및 풀강 세팅이 필수적입니다."
    else:
        if ratio >= 1.20:
            return "🟢 압도적", "현재 전투력이 권장치를 상회하여 매우 안정적입니다."
        elif ratio >= 1.00:
            return "🔵 적정", "권장 전투력을 충족하여 안정적인 도전 구간입니다."
        elif ratio >= 0.90:
            return "🟡 도전", "전투력이 다소 부족하지만 전략과 스킬로 승부 가능합니다."
        elif ratio >= 0.75:
            return "🟠 위험", "전투력이 부족하여 장비/상성/컨디션의 철저한 관리가 필요합니다."
        else:
            return "🔴 매우 위험", "전투력 격차가 큽니다. 육성 및 장비 강화 후 도전을 권장합니다."

def calc_cp_deficit_penalty(player_cp: int, recommended_cp: int, diff_id: int) -> dict:
    """
    ⚠️ v15.10 추천 전투력 미달 디버프(후처리) 산출 시스템
    - Normal: 페널티 없음
    - Hard / Nightmare / Mythic / Ancient: 단계별 최종 피해 감소, 받는 피해 증가, 회복량 감소
    """
    ratio = player_cp / max(1, recommended_cp)
    ratio_pct = int(ratio * 100)
    
    dmg_p = 0.0
    inc_p = 0.0
    heal_p = 0.0
    name = "⚠️ 전투력 열세"
    
    if diff_id == 1: # Normal: 페널티 없음
        return {
            "has_penalty": False,
            "ratio": ratio,
            "ratio_pct": ratio_pct,
            "name": "✅ 적정 전투력",
            "dmg_penalty": 0.0,
            "incoming_dmg_increase": 0.0,
            "heal_penalty": 0.0,
            "desc": "정상 전투 상태입니다."
        }
    elif diff_id == 2: # Hard
        name = "⚠️ 전투력 열세"
        if ratio < 0.70:
            dmg_p = 0.15; inc_p = 0.10
        elif ratio < 0.80:
            dmg_p = 0.10; inc_p = 0.05
        elif ratio < 0.90:
            dmg_p = 0.05
    elif diff_id == 3: # Nightmare
        name = "🟣 악몽의 압박"
        if ratio < 0.60:
            dmg_p = 0.35; inc_p = 0.25; heal_p = 0.15
        elif ratio < 0.70:
            dmg_p = 0.25; inc_p = 0.15; heal_p = 0.10
        elif ratio < 0.80:
            dmg_p = 0.15; inc_p = 0.10; heal_p = 0.05
        elif ratio < 0.90:
            dmg_p = 0.10; inc_p = 0.05
        elif ratio < 1.00:
            dmg_p = 0.05
    elif diff_id == 4: # Mythic
        name = "🟡 신화의 위압"
        if ratio < 0.70:
            dmg_p = 0.35; inc_p = 0.30; heal_p = 0.20
        elif ratio < 0.80:
            dmg_p = 0.25; inc_p = 0.20; heal_p = 0.15
        elif ratio < 0.90:
            dmg_p = 0.15; inc_p = 0.10; heal_p = 0.10
        elif ratio < 0.95:
            dmg_p = 0.10; inc_p = 0.05
        elif ratio < 1.00:
            dmg_p = 0.05
    elif diff_id == 5: # Ancient
        name = "🌑 고대의 중압"
        if ratio < 0.70:
            dmg_p = 0.40; inc_p = 0.35; heal_p = 0.30
        elif ratio < 0.80:
            dmg_p = 0.30; inc_p = 0.25; heal_p = 0.20
        elif ratio < 0.90:
            dmg_p = 0.20; inc_p = 0.15; heal_p = 0.10
        elif ratio < 0.95:
            dmg_p = 0.10; inc_p = 0.05; heal_p = 0.05
        elif ratio < 1.00:
            dmg_p = 0.05

    has_pen = (dmg_p > 0 or inc_p > 0 or heal_p > 0)
    
    parts = []
    if dmg_p > 0: parts.append(f"⚔️ 피해 -{int(dmg_p*100)}%")
    if inc_p > 0: parts.append(f"💥 피격 +{int(inc_p*100)}%")
    if heal_p > 0: parts.append(f"💖 회복 -{int(heal_p*100)}%")
    
    desc_str = " · ".join(parts) if parts else "✅ 전투력 보정 없음"
    
    return {
        "has_penalty": has_pen,
        "ratio": ratio,
        "ratio_pct": ratio_pct,
        "name": name,
        "dmg_penalty": dmg_p,
        "incoming_dmg_increase": inc_p,
        "heal_penalty": heal_p,
        "desc": desc_str
    }

# 🏰 4대 테마 던전 및 3단계 난이도 데이터베이스 (v15.3)
DUNGEON_DATABASE = {
    1: {
        "id": 1, "name": "초심자의 숲", "emoji": "🌲",
        "base_gold": 350, "base_exp": 200, "energy_cost": 10,
        "req_lvl": {1: 1, 2: 15, 3: 30},
        "rec_cp": {1: 3000, 2: 7000, 3: 15000},
        "theme": "회복 / 독",
        "env_desc": {
            1: "피톤치드 기운으로 회복 효과가 +10% 증가합니다.",
            2: "짙은 안개로 회복 +15% 및 적이 독 공격을 시도합니다.",
            3: "태고의 원시림으로 회복 +20% 및 치명적인 독이 피어납니다."
        }
    },
    2: {
        "id": 2, "name": "수정 동굴", "emoji": "💎",
        "base_gold": 900, "base_exp": 550, "energy_cost": 12,
        "req_lvl": {1: 20, 2: 35, 3: 50},
        "rec_cp": {1: 11000, 2: 18000, 3: 28000},
        "theme": "고방어 / 관통",
        "env_desc": {
            1: "수정 결정 지형으로 적의 DEF가 +5% 증가합니다.",
            2: "단단한 광석 지형으로 적의 DEF가 +10% 증가합니다.",
            3: "완전 결정화 지형으로 적의 DEF가 +15% 증가하고 피해를 경감합니다."
        }
    },
    3: {
        "id": 3, "name": "마그마 화산", "emoji": "🌋",
        "base_gold": 2400, "base_exp": 1400, "energy_cost": 15,
        "req_lvl": {1: 45, 2: 60, 3: 75},
        "rec_cp": {1: 24000, 2: 36000, 3: 52000},
        "theme": "화상 / 시간압박",
        "relic_rate": {1: 0.04, 2: 0.05, 3: 0.06},
        "env_desc": {
            1: "열기로 인해 낮은 확률로 화상 상태가 됩니다.",
            2: "화염 지대로 인해 2층부터 화상이 누적됩니다.",
            3: "극열 지옥으로 2~3층에서 화상 2스택이 누적됩니다."
        }
    },
    4: {
        "id": 4, "name": "심연의 균열", "emoji": "🌌",
        "base_gold": 6000, "base_exp": 3800, "energy_cost": 18,
        "req_lvl": {1: 70, 2: 85, 3: 99},
        "rec_cp": {1: 38000, 2: 52000, 3: 75000},
        "theme": "회복 제한 / 종결 검사",
        "relic_rate": {1: 0.06, 2: 0.075, 3: 0.09},
        "env_desc": {
            1: "심연의 기운으로 회복 효과가 -10% 감소합니다.",
            2: "심연의 압박으로 회복 효과 -20% 및 엘리트 몬스터가 출현합니다.",
            3: "종결의 심연으로 회복 효과 -30% 및 최고위 엘리트가 대거 출현합니다."
        }
    }
}

DUNGEON_DIFFICULTIES = {
    1: {"name": "🟢 일반", "energy_mult": 1.0, "gold_mult": 1.0, "exp_mult": 1.0, "mat_mult": 1.0, "hidden_rate": 0.05},
    2: {"name": "🟣 정예", "energy_mult": 1.1, "gold_mult": 1.4, "exp_mult": 1.3, "mat_mult": 1.5, "hidden_rate": 0.08},
    3: {"name": "🔴 심연", "energy_mult": 1.2, "gold_mult": 1.8, "exp_mult": 1.5, "mat_mult": 2.0, "hidden_rate": 0.12}
}

# 👑 5대 레이드 보스 전용 스킬 · 패턴 · Ancient 페이즈 데이터베이스 (v15.0)
BOSS_SKILLS_DATABASE = {
    1: { # 🌳 고대 엔트
        "basic": {"name": "고목의 일격", "ratio": 1.0, "desc": "단단한 고목 가지로 강하게 내려칩니다."},
        "skill_a": {"name": "뿌리 채찍", "ratio": 1.2, "cooldown": 3, "slow_rate": 0.15, "slow_turns": 2, "slow_chance": 0.25, "desc": "날카로운 뿌리를 휘둘러 플레이어의 SPD를 -15% 감소시킵니다. (2턴)"},
        "skill_b": {"name": "대지의 재생", "heal_ratio": 0.10, "cooldown": 4, "desc": "대지의 기운을 흡수하여 최대 HP의 10%를 회복합니다."},
        "ultimate": {"name": "태고의 숲", "req_hp_pct": 0.30, "def_buff": 0.25, "regen_ratio": 0.05, "regen_turns": 3, "desc": "태고의 원시림을 전개하여 DEF +25% 증가 및 3턴간 매 턴 최대 HP의 5%를 지속 회복합니다."},
        "trait": {"name": "불멸의 뿌리", "cutoff_pct": 0.02, "dmg_red": 0.30, "desc": "보스 최대 HP의 2% 미만의 미약한 피해를 30% 감소시킵니다."},
        "ancient_phase": {"name": "태고의 재생", "req_hp_pct": 0.20, "regen_ratio": 0.04, "desc": "Ancient 전용: HP 20% 이하 시 매 턴 최대 HP의 4%를 추가 회복합니다."}
    },
    2: { # 💎 크리스탈 드래곤
        "basic": {"name": "수정 발톱", "ratio": 1.1, "desc": "날카로운 다이아몬드 발톱으로 베어 가릅니다."},
        "skill_a": {"name": "결정 장벽", "cooldown": 4, "dmg_red": 0.25, "reflect_ratio": 0.20, "duration": 2, "desc": "2턴 동안 받는 피해를 -25% 감소시키고, 받은 피해의 20%를 반사합니다."},
        "skill_b": {"name": "프리즘 파동", "ratio": 1.2, "cooldown": 3, "def_shred": 0.15, "shred_turns": 2, "shred_chance": 0.25, "desc": "무지갯빛 파동을 방출하여 25% 확률로 플레이어의 DEF를 -15% 깎아냅니다. (2턴)"},
        "ultimate": {"name": "천경반사", "req_hp_pct": 0.35, "warning": True, "reflect_ratio_map": {1: 0.40, 2: 0.50, 3: 0.60, 4: 0.70, 5: 0.80}, "desc": "거대한 수정 거울을 펼쳐 다음 피격 피해를 최대 80% 반사합니다."},
        "trait": {"name": "절대 반사", "reflect_map": {1: 0.05, 2: 0.08, 3: 0.10, 4: 0.12, 5: 0.15}, "desc": "피격 시 피해의 일부를 상시 반사합니다."},
        "ancient_phase": {"name": "완전결정화", "req_hp_pct": 0.30, "def_buff": 0.25, "extra_reflect": 0.10, "desc": "Ancient 전용: HP 30% 이하 시 DEF +25% 및 기본 반사율 +10% 강화."}
    },
    3: { # 🔥 이프리트
        "basic": {"name": "화염격", "ratio": 1.2, "burn_chance": 0.25, "desc": "작열하는 불꽃 주먹으로 타격합니다. (25% 확률 화상)"},
        "skill_a": {"name": "업화 폭발", "ratio": 1.3, "cooldown": 3, "bonus_per_stack_map": {1: 0.05, 2: 0.08, 3: 0.10, 4: 0.12, 5: 0.15}, "desc": "누적된 업화 중첩에 비례하여 폭발적인 추가 피해를 입힙니다."},
        "skill_b": {"name": "불지옥", "ratio": 1.0, "cooldown": 3, "burn_turns": 3, "stack_add": 1, "desc": "대지를 용암으로 뒤덮어 3턴간 화상을 입히고 업화를 +1 중첩합니다."},
        "ultimate": {"name": "지옥화신", "req_hp_pct": 0.30, "warning": True, "atk_buff": 0.25, "stack_add": 2, "duration": 3, "desc": "진정한 대악마의 형상으로 각성하여 ATK +25% 및 즉시 업화 +2 중첩. (3턴)"},
        "trait": {"name": "업화 누적", "max_stack_map": {1: 5, 2: 6, 3: 7, 4: 8, 5: 10}, "desc": "매 턴 업화가 1중첩씩 누적되어 공격력이 지속 강화됩니다."},
        "ancient_phase": {"name": "멸세의 업화", "req_hp_pct": 0.25, "stack_per_turn": 2, "desc": "Ancient 전용: HP 25% 이하 시 매 턴 업화가 +2씩 급속 누적됩니다."}
    },
    4: { # ☄️ 성운 가디언
        "basic": {"name": "성운참", "ratio": 1.05, "spd_bonus": 0.15, "desc": "별의 궤적을 베어내며, 플레이어보다 빠를 시 피해가 +15% 증가합니다."},
        "skill_a": {"name": "시간 정지", "cooldown": 4, "stun_chance_map": {1: 0.10, 2: 0.15, 3: 0.20, 4: 0.25, 5: 0.30}, "desc": "시간을 멈추어 플레이어의 다음 행동을 봉인합니다."},
        "skill_b": {"name": "시간 가속", "cooldown": 4, "spd_buff": 0.20, "extra_turn_chance_map": {1: 0.10, 2: 0.12, 3: 0.15, 4: 0.20, 5: 0.25}, "duration": 2, "desc": "2턴 동안 자신의 SPD +20% 및 추가 행동 확률 증가."},
        "ultimate": {"name": "시간 역행", "req_hp_pct": 0.30, "warning": True, "rewind_ratio": 0.50, "extra_turn": True, "desc": "직전 턴에 잃은 HP의 50%를 되돌리고 즉시 추가 행동을 취합니다."},
        "trait": {"name": "시간 지배", "desc": "SPD 차이에 따라 추가 행동을 취할 확률이 발생합니다."},
        "ancient_phase": {"name": "시간 붕괴", "req_hp_pct": 0.30, "cd_increase_chance": 0.20, "desc": "Ancient 전용: HP 30% 이하 시 20% 확률로 플레이어 스킬 쿨타임 +1턴 증가."}
    },
    5: { # 🪐 오메가
        "basic": {"name": "암흑 붕괴", "ratio": 1.4, "def_ignore": 0.15, "desc": "암흑의 중력으로 플레이어 DEF의 15%를 무시하고 분쇄합니다."},
        "skill_a": {"name": "약자 판결", "cooldown": 3, "debuff_val": 0.15, "duration": 2, "desc": "플레이어의 미달된 힘을 단죄하여 2턴간 ATK/DEF -15% 디버프를 부여합니다."},
        "skill_b": {"name": "종말의 파동", "ratio": 1.2, "cooldown": 4, "all_stat_debuff": 0.12, "duration": 2, "desc": "종말의 기운을 퍼뜨려 2턴간 플레이어 전 스탯 -12% 약화."},
        "ultimate": {"name": "Ω · 창세종언", "req_hp_pct": 0.20, "warning": True, "ratio": 3.0, "def_ignore": 0.40, "desc": "우주를 멸망시키는 궁극의 일격 (ATK 300%, DEF 40% 무시)."},
        "trait": {"name": "약자멸시", "cutoff_0": 0.60, "cutoff_50": 0.80, "desc": "ATK가 기준치(DEF x 0.6) 미만 시 피해 완전 면역(0), 0.8 미만 시 피해 50% 감소."},
        "ancient_phases": {
            "phase_2": {"req_hp_pct": 0.70, "name": "파괴신의 각성", "atk_buff": 0.20, "spd_buff": 0.15, "quote": "「여기까지 밀어붙인 자는 오랜만이다.」"},
            "phase_3": {"req_hp_pct": 0.30, "name": "종말", "atk_buff": 0.20, "def_ignore": 0.15, "cd_reduce": 1, "quote": "「이제부터는 시험이 아니다.」"},
            "final_pattern": {"req_hp_pct": 0.10, "name": "Ω · 최후의 종언", "warning": True, "ratio": 3.5, "def_ignore": 0.50, "desc": "Ancient 전용 최후의 섬멸기 (ATK 350%, DEF 50% 무시, 회복 불가)."}
        }
    }
}

def choose_boss_action(boss_id: int, diff_id: int, hp_ratio: float, turn: int, cd_a: int, cd_b: int, ult_used: bool, warning_active: bool, ctx: dict = None) -> str:
    """
    🧠 지능형 보스 AI 액션 셀렉터 (v15.0)
    반환값: 'warning_ult', 'ultimate', 'skill_a', 'skill_b', 'basic'
    """
    b_skills = BOSS_SKILLS_DATABASE.get(boss_id, BOSS_SKILLS_DATABASE[1])
    ult_info = b_skills.get("ultimate", {})
    
    # 1. 예고가 활성화되어 있던 상태라면 이번 턴 즉시 궁극기 발동!
    if warning_active:
        return "ultimate"

    # 2. 궁극 패턴 조건 검사 (HP 조건 충족 & 미사용)
    req_hp = ult_info.get("req_hp_pct", 0.30)
    if hp_ratio <= req_hp and not ult_used:
        if ult_info.get("warning", False):
            return "warning_ult" # 1턴 전 예고 전조 발동!
        else:
            return "ultimate"

    # 3. 보스별 지능형 조건 스킬 판단
    if boss_id == 1: # 엔트: 체력 50% 미만이고 힐 스킬(B) 가능 시 회복 최우선
        if hp_ratio <= 0.50 and cd_b == 0:
            return "skill_b"
        if cd_a == 0:
            return "skill_a"
    elif boss_id == 2: # 크리스탈 드래곤: 결정 장벽(A) 우선 순환
        if cd_a == 0:
            return "skill_a"
        if cd_b == 0:
            return "skill_b"
    elif boss_id == 3: # 이프리트: 스택이 쌓였으면 업화 폭발(A) 우선
        cur_stacks = ctx.get("hellfire_stacks", 0) if ctx else 0
        if cur_stacks >= 3 and cd_a == 0:
            return "skill_a"
        if cd_b == 0:
            return "skill_b"
        if cd_a == 0:
            return "skill_a"
    elif boss_id == 4: # 성운 가디언: 시간 가속(B) ➔ 시간 정지(A) 연계
        if cd_b == 0:
            return "skill_b"
        if cd_a == 0:
            return "skill_a"
    elif boss_id == 5: # 오메가: 종말의 파동(B) ➔ 약자 판결(A)
        if cd_b == 0:
            return "skill_b"
        if cd_a == 0:
            return "skill_a"

    # 4. 일반 쿨타임 완료 스킬 사용 (우선순위: A > B)
    if cd_a == 0 and random.random() < 0.70:
        return "skill_a"
    if cd_b == 0 and random.random() < 0.70:
        return "skill_b"

    # 5. 기본 공격
    return "basic"

class AdventureSystem:
    @staticmethod
    def run_boss_raid(pet, inventory, boss_id: int, diff_id: int = 1, interactive=True) -> tuple[bool, str]:
        if getattr(pet, "is_critically_injured", False):
            return False, "💀 신수가 치명상을 입은 상태입니다! 치료하거나 건강을 회복시켜주세요."

        # 🪐 v17.2 오메가는 Ancient(고대) 난이도에서만 도전 가능
        if boss_id == 5 and diff_id != 5:
            return False, "⚠️ 🪐 **오메가**는 고대(Ancient) 4대 보스를 모두 정복한 후 도전할 수 있는 최종 졸업 보스입니다!"

        boss_base = BOSS_DATABASE.get(boss_id, BOSS_DATABASE[1])
        diff_info = RAID_DIFFICULTIES.get(diff_id, RAID_DIFFICULTIES[1])
        
        pet.consume_energy(boss_base["energy_cost"], "raid")
        pet.hunger = max(0, pet.hunger - 20)
        pet.cleanliness = max(0, pet.cleanliness - 20)
        pet.total_adventures = getattr(pet, "total_adventures", 0) + 1
        
        # 👑 v17.2 정밀 보스 스탯 테이블 (Ground Truth)
        stat_data = BOSS_STAT_TABLE.get(diff_id, {}).get(boss_id, {})
        if stat_data:
            b_max_hp = stat_data["hp"]
            b_hp = b_max_hp
            b_atk = stat_data["atk"]
            b_def = stat_data["def"]
            b_spd = stat_data["spd"]
        else:
            b_max_hp = int(boss_base["base_hp"] * diff_info["hp_mult"])
            b_hp = b_max_hp
            b_atk = int(boss_base["base_atk"] * diff_info["atk_mult"])
            b_def = int(boss_base["base_def"] * diff_info["def_mult"])
            b_spd = int(boss_base["base_spd"] * diff_info["spd_mult"])
            if boss_id == 4 and diff_id >= 2:
                b_spd = int(b_spd * 1.05)

        b_gold = int(boss_base["base_gold"] * diff_info["gold_mult"])
        b_exp = int(boss_base["base_exp"] * diff_info["exp_mult"])
        
        boss_title = f"{boss_base['emoji']} {boss_base['name']} [{diff_info['name'].split()[0]}]"
        if diff_id == 5:
            boss_title = f"{boss_base['emoji']} {boss_base['title_ancient']}"

        battle_stats = pet.get_battle_stats(inventory)
        pet_max_hp = battle_stats["max_hp"]
        pet_hp = pet_max_hp
        base_pet_atk = battle_stats["atk"]
        base_pet_def = battle_stats["def"]
        pet_spd = battle_stats.get("spd", 100)
        pet_crit = battle_stats.get("crit", 100)
        effect = battle_stats.get("effect", "atk_boost")
        p_trait = battle_stats.get("personality_trait", "none")
        p_name = battle_stats.get("personality", "용맹함")
        
        relic_is_10 = battle_stats.get("relic_is_10", False)
        armor_dmg_red = battle_stats.get("armor_dmg_red", 0.0)
        armor_resist = battle_stats.get("armor_resist", 0.0)

        sp_key = getattr(pet, "species_key", "호랑이")
        pet_skills = SPECIES_SKILLS.get(sp_key, SPECIES_SKILLS["호랑이"])

        # 🦄 기린 전투 패시브: 전투 시작 시 전 5대 스탯 +3%
        if sp_key == "기린":
            pet_hp = int(pet_hp * 1.03)
            pet_max_hp = int(pet_max_hp * 1.03)
            base_pet_atk = int(base_pet_atk * 1.03)
            base_pet_def = int(base_pet_def * 1.03)
            pet_spd = int(pet_spd * 1.03)

        # 🦄 기린 +10 전용 효과: 전투 시작 시 전 스탯 +5% 추가
        if sp_key == "기린" and relic_is_10:
            pet_hp = int(pet_hp * 1.05)
            pet_max_hp = int(pet_max_hp * 1.05)
            base_pet_atk = int(base_pet_atk * 1.05)
            base_pet_def = int(base_pet_def * 1.05)
            pet_spd = int(pet_spd * 1.05)

        if interactive:
            print("\n" + "="*70)
            print(f"⚔️ [레이드 전투 개시] {boss_title}")
            print(f"🔮 고유 절대 특성: 「{boss_base['trait_name']}」 | 🎯 {boss_base['check_stat']}")
            print(f"🐾 출전: {pet.name} (Lv.{pet.level} / 초월 Lv.{getattr(pet, 'transcend_level', 0)}) | 성격: [{p_name}]")
            
            relic_str = f"{EXCLUSIVE_RELICS[sp_key]['name']} +{battle_stats.get('relic_level', 0)}" if battle_stats.get('relic_level', 0) > 0 else "미장착"
            armor_str = f"{ARMORS_DATABASE[inventory.equipped_armor['armor_id']]['name']} +{battle_stats.get('armor_level', 0)}" if inventory and inventory.equipped_armor else "미장착"
            print(f"🎴 보물: [{relic_str}] | 🛡️ 방어구: [{armor_str}]")
            print(f"📊 스탯 | HP: {pet_hp:,} | ATK: {base_pet_atk:,} | DEF: {base_pet_def:,} | SPD: {pet_spd} | CRIT: {pet_crit}")
            print(f"👑 보스 스탯 | HP: {b_hp:,} | ATK: {b_atk:,} | DEF: {b_def:,} | SPD: {b_spd}")
            print("="*70)
            time.sleep(1.0)

        turn = 0
        revived = False
        pet_revived = False
        phoenix_passive_healed = False
        phoenix_relic_survived = False
        countdown_doom = -1
        player_def_debuff = 0.0
        hellfire_stacks = 0
        player_time_stopped = False

        cd_unique = 0
        cd_ultimate = 0
        buff_atk_turns = 0; buff_atk_val = 0.0
        buff_def_turns = 0; buff_def_val = 0.0
        buff_spd_turns = 0; buff_spd_val = 0.0
        shield_buff_turns = 0; shield_buff_val = 0.0
        reflect_buff_turns = 0; reflect_buff_val = 0.0

        while pet_hp > 0 and b_hp > 0:
            turn += 1
            
            if buff_atk_turns > 0: buff_atk_turns -= 1
            else: buff_atk_val = 0.0
            if buff_def_turns > 0: buff_def_turns -= 1
            else: buff_def_val = 0.0
            if buff_spd_turns > 0: buff_spd_turns -= 1
            else: buff_spd_val = 0.0
            if shield_buff_turns > 0: shield_buff_turns -= 1
            else: shield_buff_val = 0.0
            if reflect_buff_turns > 0: reflect_buff_turns -= 1
            else: reflect_buff_val = 0.0
            
            if cd_unique > 0: cd_unique -= 1
            if cd_ultimate > 0: cd_ultimate -= 1

            pet_atk = int(base_pet_atk * (1.0 + buff_atk_val))
            pet_def = int(base_pet_def * (1.0 + buff_def_val) * (1.0 - player_def_debuff))
            cur_pet_spd = int(pet_spd * (1.0 + buff_spd_val))

            # 🐉 드래곤 +10: HP 30% 이하 시 ATK +20%
            if sp_key == "드래곤" and relic_is_10 and pet_hp <= (pet_max_hp * 0.3):
                pet_atk = int(pet_atk * 1.20)

            # 🐢 현무 +10: HP 30% 이하 시 DEF +20%
            if sp_key == "현무" and relic_is_10 and pet_hp <= (pet_max_hp * 0.3):
                pet_def = int(pet_def * 1.20)

            # 성격 보정
            if p_trait == "brave_crisis" and pet_hp <= (pet_max_hp * 0.5):
                pet_atk = int(pet_atk * 1.10)
                pet_def = int(pet_def * 1.10)
            if p_trait == "early_burst":
                pet_atk = int(pet_atk * 1.15) if turn <= 3 else int(pet_atk * 0.95)

            if effect == "hp_regen" and turn <= 10 and pet_hp < pet_max_hp:
                pet_hp = min(pet_max_hp, pet_hp + max(5, int(pet_max_hp * 0.015)))
            if p_trait == "gentle_regen" and pet_hp < pet_max_hp:
                pet_hp = min(pet_max_hp, pet_hp + max(3, int(pet_max_hp * 0.02)))

            # 보스 특성
            if boss_id == 1:
                regen_rate = 0.02 if diff_id == 5 else (0.015 if diff_id == 4 else (0.01 if diff_id >= 2 else 0.0))
                if regen_rate > 0:
                    ent_heal = int(b_max_hp * regen_rate)
                    b_hp = min(b_max_hp, b_hp + ent_heal)
                    if interactive and turn % 2 == 1:
                        print(f"🌱 [불멸의 뿌리] 고대 엔트가 HP를 {ent_heal:,} 회복했습니다!")

            elif boss_id == 3:
                stack_interval = 5 if diff_id == 2 else (4 if diff_id == 3 else (3 if diff_id >= 4 else 999))
                if turn % stack_interval == 0:
                    hellfire_stacks = min(5, hellfire_stacks + 1)
                    bonus_p = {1: 0.05, 2: 0.10, 3: 0.20, 4: 0.30, 5: 0.40}.get(hellfire_stacks, 0.40)
                    b_atk = int(int(boss_base["base_atk"] * diff_info["atk_mult"]) * (1.0 + bonus_p))
                    if interactive:
                        print(f"\n🔥 [업화 {hellfire_stacks}중첩 누적!] 이프리트의 ATK +{int(bonus_p*100)}% 상승!")

                if hellfire_stacks >= 1:
                    burn_pct = (0.03 if (diff_id == 5 and hellfire_stacks >= 5) else 0.02) * (1.0 - armor_resist)
                    burn_dmg = max(5, int(pet_max_hp * burn_pct))
                    pet_hp -= burn_dmg
                    if interactive:
                        print(f"🔥 [화상 피해] {pet.name}이(가) {burn_dmg:,} 화상 피해를 입었습니다! (남은 HP: {max(0, pet_hp):,})")

            elif boss_id == 5 and diff_id >= 2 and turn == 2:
                player_def_debuff = 0.20 * (1.0 - armor_resist)
                if interactive:
                    print("👁️ [절대자의 시선] 플레이어의 방어력이 감소했습니다!")

            # 신수 공격 턴
            if player_time_stopped:
                player_time_stopped = False
                if interactive:
                    print(f"\n🌀 [시간 정지!] {pet.name}은(는) 이번 턴에 행동할 수 없습니다!")
                    time.sleep(0.5)
            else:
                skill_type = "basic1"
                if cd_ultimate == 0 and turn >= 3:
                    skill_type = "ultimate"
                    cd_ultimate = pet_skills["ultimate"]["cooldown"]
                elif cd_unique == 0:
                    skill_type = "unique"
                    cd_unique = pet_skills["unique"]["cooldown"]
                else:
                    skill_type = "basic2" if turn % 2 == 0 else "basic1"

                sk_info = pet_skills[skill_type]
                sk_name = sk_info["name"]
                
                if skill_type == "unique":
                    if "buff_atk" in sk_info:
                        buff_atk_turns = sk_info["duration"]; buff_atk_val = sk_info["buff_atk"]
                    if "buff_def" in sk_info or "dmg_reduction" in sk_info:
                        shield_buff_turns = sk_info.get("duration", 2); shield_buff_val = sk_info.get("dmg_reduction", 0.0)
                    if "buff_spd" in sk_info:
                        buff_spd_turns = sk_info["duration"]; buff_spd_val = sk_info["buff_spd"]
                    if sk_info.get("regen_turn_pct", 0) > 0:
                        pet_hp = min(pet_max_hp, pet_hp + int(pet_max_hp * sk_info["regen_turn_pct"]))
                    if sk_info.get("cleanse", False):
                        player_def_debuff = 0.0
                    if interactive:
                        print(f"\n✨ [{pet.name}의 고유기!] {sk_name}! ({sk_info['desc']})")
                        time.sleep(0.3)

                base_ratio = sk_info.get("atk_ratio", 1.0)
                num_hits = sk_info.get("hits", 1)
                
                # 🐾 종족 전투 패시브 연동 (v13.9)
                if sp_key == "호랑이" and (pet_hp / max(1, pet_max_hp)) >= 0.70:
                    base_ratio *= 1.06 # 🐯 맹수의 본능: HP 70%+ 피해 +6%
                elif sp_key == "사자" and (pet_hp / max(1, pet_max_hp)) <= 0.50:
                    base_ratio *= 1.10 # 🦁 왕의 위엄: HP 50%- 방어 관통 +10%
                elif sp_key == "늑대" and cur_pet_spd > b_spd:
                    base_ratio *= 1.06 # 🐺 사냥 본능: SPD 우위 피해 +6%
                elif sp_key == "드래곤" and (pet_hp / max(1, pet_max_hp)) <= 0.40:
                    base_ratio *= 1.08 # 🐉 용혈 폭주: HP 40%- 스킬피해 +8%
                elif sp_key == "구미호":
                    base_ratio *= 1.07 # 🦊 요기의 흔적: 피해 +7%
                elif sp_key == "바하무트":
                    base_ratio *= 1.08 # 🐲 파괴신의 혈통: 보스 피해 +8%

                # 🐺 늑대 +10: 적보다 빠르면 최종 피해 +10%
                if sp_key == "늑대" and relic_is_10 and cur_pet_spd > b_spd:
                    base_ratio *= 1.10
                # 🪽 그리핀 +10: 선공 시 첫 턴 피해 +20%
                if sp_key == "그리핀" and relic_is_10 and turn == 1:
                    base_ratio *= 1.20
                # 🐲 바하무트 +10: 보스전 피해 +10%
                if sp_key == "바하무트" and relic_is_10:
                    base_ratio *= 1.10

                if skill_type == "ultimate":
                    if sp_key == "호랑이" and (b_hp / b_max_hp) <= 0.3:
                        base_ratio += sk_info.get("execute_bonus", 0.25)
                    elif sp_key == "바하무트" and (b_hp / b_max_hp) <= 0.3:
                        base_ratio += sk_info.get("execute_bonus", 0.40)
                    elif sp_key == "사자":
                        pet_hp = min(pet_max_hp, pet_hp + int(pet_max_hp * sk_info.get("heal_hp_pct", 0.15)))
                    elif sp_key == "불사조" and (pet_hp / pet_max_hp) <= 0.3:
                        pet_hp = min(pet_max_hp, pet_hp + int(pet_max_hp * 0.30))
                    elif sp_key == "현무":
                        reflect_buff_turns = 3; reflect_buff_val = 0.20
                    elif sp_key == "기린":
                        pet_hp = min(pet_max_hp, pet_hp + int(pet_max_hp * 0.15))
                        buff_atk_turns = 3; buff_atk_val = 0.15; buff_def_turns = 3; buff_def_val = 0.15

                crit_bonus = sk_info.get("crit_bonus", 0.0)
                base_crit_rate = pet_crit / (pet_crit + 900.0)
                final_crit_rate = min(0.70, base_crit_rate + crit_bonus + (0.15 if effect == "crit" else 0.0))
                
                total_skill_dmg = 0
                for hit_idx in range(num_hits):
                    is_crit = (random.random() < final_crit_rate)
                    crit_mult = 2.2 if (is_crit and p_trait == "calm_crit") else (2.0 if is_crit else 1.0)
                    hit_dmg = max(10, int((pet_atk * base_ratio / num_hits) * random.uniform(0.9, 1.15) * crit_mult))
                    
                    # 🐯 호랑이 +10 백호살: 치명타 시 15% 확률 추가 공격
                    if sp_key == "호랑이" and relic_is_10 and is_crit and random.random() < 0.15:
                        hit_dmg = int(hit_dmg * 1.5)
                        if interactive:
                            print("🐯 [백호살 발동!] 날카로운 추가 타격이 연속으로 작렬합니다!")

                    if boss_id == 1: # 엔트 1% 컷
                        one_pct_hp = b_max_hp * 0.01
                        if hit_dmg < one_pct_hp and diff_id >= 4:
                            hit_dmg = 0
                    elif boss_id == 5: # 오메가 약자멸시
                        req_cut = b_def * (0.6 if diff_id == 5 else 0.5)
                        if pet_atk < req_cut: hit_dmg = 0
                        elif pet_atk < (b_def * 0.9): hit_dmg = int(hit_dmg * 0.5)

                    total_skill_dmg += hit_dmg

                b_hp = max(0, b_hp - total_skill_dmg)
                crit_tag = " 💥 CRITICAL!" if random.random() < final_crit_rate else ""
                if interactive:
                    print(f"⚔️ [{pet.name}]의 {sk_name}! {total_skill_dmg:,} 피해 작렬!{crit_tag} (보스 HP: {b_hp:,}/{b_max_hp:,})")
                    time.sleep(0.3)

                # 수정용 반사
                if boss_id == 2 and total_skill_dmg > 0:
                    ref_rate = 0.15 if diff_id == 5 else (0.10 if diff_id >= 3 else 0.05)
                    ref_dmg = int(total_skill_dmg * ref_rate * (1.0 - armor_dmg_red))
                    if ref_dmg > 0:
                        pet_hp -= ref_dmg
                        if interactive:
                            print(f"💎 [절대 반사!] {pet.name}이(가) 반사된 {ref_dmg:,} 피해를 입었습니다! (남은 HP: {max(0, pet_hp):,})")

                # 흡혈 (구미호 +10 혼령흡수 포함)
                ls_pct = sk_info.get("lifesteal_pct", 0.0)
                if effect == "lifesteal": ls_pct += 0.18
                if sp_key == "구미호" and relic_is_10: ls_pct *= 1.5
                if ls_pct > 0 and total_skill_dmg > 0:
                    h_amt = min(int(pet_max_hp * 0.20), int(total_skill_dmg * ls_pct))
                    pet_hp = min(pet_max_hp, pet_hp + h_amt)
                    if interactive and h_amt > 0:
                        print(f"🩸 [흡혈] HP +{h_amt:,} 회복!")

            if b_hp <= 0 and diff_id >= 4 and not revived:
                if boss_id in [1, 3, 5]:
                    revived = True
                    b_hp = int(b_max_hp * (1.0 if boss_id == 5 else 0.5))
                    b_atk = int(b_atk * 1.25); b_def = int(b_def * 1.25)
                    if interactive:
                        print(f"\n🌟🌟🌟 [{boss_base['name']} 신화/고대 부활 각성!] 🌟🌟🌟\n")
                        time.sleep(0.8)
                    continue

            if b_hp <= 0:
                break

            if countdown_doom > 0:
                countdown_doom -= 1
                if countdown_doom == 0:
                    pet_hp = 0
                    break

            if p_trait == "dodge_boost" and random.random() < 0.10:
                if interactive:
                    print(f"💨 [소심함 회피!] {pet.name}이(가) 공격을 완벽히 피했습니다! (피해 0)")
                continue

            # 보스 공격
            base_shield = (0.75 if effect == "shield" else 0.90) * (1.0 - shield_buff_val) * (1.0 - armor_dmg_red)
            if sp_key == "현무": base_shield *= 0.95 # 🐢 금강불괴: 받는 피해 -5%
            # 🦁 사자 +10 태양왕의 위엄: HP 50% 이하 시 받는 피해 -10%
            if sp_key == "사자" and relic_is_10 and pet_hp <= (pet_max_hp * 0.5):
                base_shield *= 0.90

            cur_p_def = pet_def
            if sp_key == "사자" and (pet_hp / max(1, pet_max_hp)) <= 0.50:
                cur_p_def = int(cur_p_def * 1.10) # 🦁 왕의 위엄: HP 50%- DEF +10%

            mob_dmg = max(5, int((b_atk * random.uniform(0.9, 1.1) - (cur_p_def * 0.35)) * base_shield))
            
            extra_actions = 0
            if boss_id == 4:
                if b_spd > cur_pet_spd:
                    spd_ratio = b_spd / max(1, cur_pet_spd)
                    if diff_id == 5 and spd_ratio >= 1.5:
                        if random.random() < 0.35: extra_actions = 1
                        if random.random() < (0.15 * (1.0 - armor_resist)): player_time_stopped = True
                    elif spd_ratio >= 1.2 and random.random() < 0.20:
                        extra_actions = 1

            if p_trait == "indomitable" and random.random() < 0.20:
                mob_dmg = max(2, int(mob_dmg * 0.5))
                if interactive:
                    print("🌌 [불굴의 버티기!] 받는 피해 50% 감소!")

            pet_hp -= mob_dmg
            if interactive:
                print(f"🛡️ [{boss_base['name']}]의 공격! {mob_dmg:,} 피해! (남은 HP: {max(0, pet_hp):,})")
                time.sleep(0.2)

            if reflect_buff_val > 0 and mob_dmg > 0:
                ref_mob_dmg = int(mob_dmg * reflect_buff_val)
                b_hp -= ref_mob_dmg
                if interactive:
                    print(f"🐢 [천지현무진 반사!] 보스에게 {ref_mob_dmg:,} 반사 피해!")

            if extra_actions > 0 and pet_hp > 0:
                extra_dmg = max(5, int(mob_dmg * 0.75))
                pet_hp -= extra_dmg
                if interactive:
                    print(f"☄️ [시간 지배 추가타!] {extra_dmg:,} 추가 피해! (남은 HP: {max(0, pet_hp):,})")
                    time.sleep(0.2)

            # 🦅 불사조 전투 패시브: HP 30% 이하 시 최초 1회 8% 회복
            if pet_hp > 0 and sp_key == "불사조" and (pet_hp / max(1, pet_max_hp)) <= 0.30 and not phoenix_passive_healed:
                phoenix_passive_healed = True
                heal_8 = int(pet_max_hp * 0.08)
                pet_hp = min(pet_max_hp, pet_hp + heal_8)
                if interactive:
                    print(f"🦅🔥 [재생의 불꽃!] 불사조의 패시브로 HP +{heal_8:,} (8%)가 회복되었습니다!")

            # 🦅 불사조 +10 불사: 치명적 피해 시 HP 1 생존
            if pet_hp <= 0 and sp_key == "불사조" and relic_is_10 and not phoenix_relic_survived:
                phoenix_relic_survived = True
                pet_hp = 1
                if interactive:
                    print("\n🔥 [불멸의 깃털 발동!] 불사조가 치명적인 일격을 버텨내고 HP 1로 생존했습니다!\n")

            if pet_hp <= 0 and sp_key == "불사조" and not pet_revived:
                pet_revived = True
                pet_hp = int(pet_max_hp * 0.25)
                if interactive:
                    print(f"\n🦅👑 [주작환생 발동!] 불사조가 HP {pet_hp:,} (25%)로 화려하게 부활했습니다! 🔥\n")
                    time.sleep(0.8)

        if pet_hp <= 0:
            if interactive:
                print(f"\n😭 {pet.name}이(가) 패배하여 레이드에서 탈출했습니다...")
            
            # 💀 난이도별 패배 페널티 & 치명상(Critical Injury) 시스템 (영구 사망 0% 완전 폐지)
            h_loss = 20 if sp_key == "사자" else 25
            
            if diff_id == 1: # 🟢 Normal
                pet.stamina = max(0, getattr(pet, "stamina", 100) - 20)
                pet.happiness = max(10, pet.happiness - 5)
                pet.health = max(10, pet.health - 10)
                return False, f"[{boss_title}] 공략에 실패했습니다. (모험기력 -20, 행복도 -5)"
                
            elif diff_id == 2: # 🔵 Hard
                pet.stamina = 0
                pet.health = max(10, pet.health - 20)
                pet.happiness = max(10, pet.happiness - h_loss)
                return False, f"[{boss_title}] 공략에 실패했습니다. (모험기력 0, 건강 -20, 행복도 -{h_loss})"
                
            else: # 🟣 Nightmare (10%), 🟡 Mythic (25%), 🔴 Ancient (50%)
                final_inj_rate, base_rate, aff_red, has_bond_retry = pet.calculate_injury_rate(diff_id)
                
                # 1. 💎 생명의 보석 체크
                if inventory and inventory.items.get("life_gem", 0) > 0:
                    inventory.remove_item("life_gem", 1)
                    pet.health = 30
                    pet.stamina = 0
                    pet.happiness = max(0, pet.happiness - 15)
                    if interactive:
                        print("💎✨ **[생명의 보석 발동!]** 품속의 생명의 보석이 부서지며 치명상을 1회 완전 무효화했습니다!")
                    return False, f"[{boss_title}] 공략에 실패했습니다. (생명의 보석으로 치명상 방어, 건강 30%)"

                # 2. 치명상 판정
                is_injured = (random.random() < final_inj_rate)
                
                # 3. 👑 Lv.10 절대적 유대 1회 기적 재판정
                if is_injured and has_bond_retry:
                    if random.random() >= final_inj_rate:
                        is_injured = False
                        if interactive:
                            print("💖👑✨ **[절대적 유대 기적 발동!]** 깊은 신뢰로 신수가 마지막 힘으로 치명상을 모면했습니다!")

                if is_injured:
                    pet.is_critically_injured = True
                    pet.health = 1
                    pet.stamina = 0
                    pet.energy = min(20, getattr(pet, "energy", 100))
                    pet.happiness = max(0, pet.happiness - 35)
                    if interactive:
                        print(f"\n💀🚨 [{pet.name}] 치명상 발생! 신수가 전투 불능 상태가 되었습니다.")
                        print(f"📊 (치명상 위험도: 기본 {int(base_rate*100)}% ➔ 애정 보호 -{int(aff_red*100)}% ➔ 최종 {int(final_inj_rate*100)}%)")
                    return False, f"💀🚨 **[{boss_title} 패배 - 치명상 발생!]** 신수가 치명상을 입었습니다! (건강 1%, 모험기력 0, 치료 필요)"
                else:
                    norm_hp = 50 if diff_id == 3 else (30 if diff_id == 4 else 20)
                    pet.health = norm_hp
                    pet.stamina = 0
                    pet.happiness = max(10, pet.happiness - h_loss)
                    if interactive:
                        print(f"\n✨🛡️ **[치명상 회피!]** {pet.name}이(가) 패배했으나 기적적으로 치명상을 모면했습니다! (건강 {norm_hp}%)")
                    return False, f"[{boss_title}] 공략에 실패했습니다. (건강 {norm_hp}%, 모험기력 0, 치명상 회피 성공)"

        # 종족 무드 보상/경험치 보너스
        if sp_key == "바하무트":
            b_exp = int(b_exp * 1.10); b_gold = int(b_gold * 1.05) # 바하무트: EXP +10%, 보상 +5%
        elif sp_key == "구미호" and getattr(pet, "affection", 50) >= 80:
            b_exp = int(b_exp * 1.10) # 구미호: 애정도 80+ 시 전투 EXP +10%

        # 호랑이 / 드래곤 무드 승리 보너스 & 10단계 애정도 획득
        aff_gain = 4
        if sp_key == "호랑이":
            aff_gain += 2 # 호랑이: 레이드 승리 시 애정도 +2 추가
        elif sp_key == "드래곤":
            pet.happiness = min(100, pet.happiness + 10) # 드래곤: 보스 승리 시 행복도 +10

        aff_logs = pet.gain_affection(aff_gain)

        pet.coins += b_gold
        pet.total_dungeon_clears = getattr(pet, "total_dungeon_clears", 0) + 1
        exp_logs = pet.gain_exp(b_exp)
        
        bonus_rewards = []

        # 🌱 v17.2 난이도별 잠재 혼 드랍 (엔트 25% 1개, 수정용 35% 1개, 이프리트 50% 1개, 가디언 50% 1~2개)
        if diff_id in [1, 2, 3, 4]:
            soul_rates = {1: (0.25, 1), 2: (0.35, 1), 3: (0.50, 1), 4: (0.50, "1-2")}
            s_rate, s_cnt_type = soul_rates.get(boss_id, (0.25, 1))
            if random.random() < s_rate:
                drop_soul_amt = random.choice([1, 2]) if s_cnt_type == "1-2" else 1
                soul_map = {1: ("soul_normal", "⚪ 일반 혼"), 2: ("soul_hard", "🔵 고급 혼"), 3: ("soul_nightmare", "🟣 전설 혼"), 4: ("soul_mythic", "🟡 신화 혼")}
                s_id, s_name = soul_map[diff_id]
                inventory.add_item(s_id, drop_soul_amt)
                bonus_rewards.append(f"🌱 **{s_name} x{drop_soul_amt}**")

        # 🎁 v17.2 난이도별 방어구 및 보상 드랍 풀
        if diff_id == 1:
            inventory.add_item("small_candy", 2)
            inventory.add_item("armor_stone", 2)
            if random.random() < 0.30:
                inventory.add_armor("leather_armor")
                bonus_rewards.append("🛡️ 가죽 갑옷 획득!")
            bonus_rewards.append("🍬 작은 사탕 2개, 💎 강화석 2개")
        elif diff_id == 2:
            inventory.add_item("super_candy", 2)
            inventory.add_item("armor_stone", 3)
            if random.random() < 0.25:
                inventory.add_armor("crystal_armor")
                bonus_rewards.append("🛡️ 수정 갑옷 획득!")
            bonus_rewards.append("🍭 슈퍼 사탕 2개, 💎 강화석 3개")
        elif diff_id == 3:
            inventory.add_item("mega_candy", 2)
            inventory.add_item("armor_stone", 5)
            inventory.add_item("nightmare_crystal", random.randint(1, 2))
            if random.random() < 0.25:
                inventory.add_armor("celestial_armor")
                bonus_rewards.append("🛡️ 천계 갑주 획득!")
            bonus_rewards.append("🌟 특급 사탕 2개, 💎 강화석 5개, 🟣 악몽의 결정")
        elif diff_id == 4:
            inventory.add_item("ancient_candy", 1)
            inventory.add_item("armor_stone", 8)
            inventory.add_item("mythic_core", random.randint(1, 2))
            
            # 👑 Mythic 보스별 신화 방어구 드롭 매핑 (25% 확률)
            mythic_boss_armors = {
                1: "mythic_life_armor",       # 🌳 엔트 ➔ 생명의 성의
                2: "mythic_celestial_armor",  # 💎 크리스탈 드래곤 ➔ 천계신의 갑주
                3: "mythic_dragon_armor",     # 🔥 이프리트 ➔ 용신의 갑주
                4: random.choice(["mythic_gale_armor", "mythic_abyss_armor"]) # ☄️ 성운 가디언 ➔ 천풍의 경갑 or 심연의 갑주
            }
            if random.random() < 0.25:
                drop_a_id = mythic_boss_armors.get(boss_id, "mythic_celestial_armor")
                inventory.add_armor(drop_a_id)
                a_name = ARMORS_DATABASE[drop_a_id]["name"]
                bonus_rewards.append(f"🛡️🔴 **[신화] {a_name} 획득!!**")
            bonus_rewards.append("🌌 태초의 사탕 1개, 💎 강화석 8개, 🟡 신화의 핵")
        elif diff_id == 5:
            inventory.add_item("ancient_candy", 3)
            inventory.add_item("armor_stone", 15)
            inventory.add_item("ancient_core", random.randint(1, 2))
            
            # Ancient에서도 15% 확률로 신화 방어구 완제품 드롭
            all_mythic_ids = ["mythic_dragon_armor", "mythic_life_armor", "mythic_gale_armor", "mythic_abyss_armor", "mythic_celestial_armor"]
            if random.random() < 0.15:
                drop_a_id = random.choice(all_mythic_ids)
                inventory.add_armor(drop_a_id)
                a_name = ARMORS_DATABASE[drop_a_id]["name"]
                bonus_rewards.append(f"🛡️🔴 **[신화] {a_name} 획득!!**")
            bonus_rewards.append("👑 태초의 사탕 3개, 💎 강화석 15개, 🌑 태고의 핵")

        clear_msg = (
            f"🏆 [{boss_title}] 완벽 토벌 성공!\n"
            f"💰 획득: +{b_gold:,}G | ✨ EXP: +{b_exp:,} EXP\n"
            f"🎁 획득 보상: {', '.join(bonus_rewards)}"
        )
        
        if interactive:
            print("\n" + "="*70)
            print(clear_msg)
            if exp_logs:
                for l in exp_logs:
                    print(l)
            print("="*70)
            input("\n[Enter] 키를 눌러 계속하기...")

        return True, clear_msg

    @staticmethod
    def run_multi_dungeon(pet, inventory, dungeon_id: int = 1, diff_id: int = 1, times: int = 5) -> tuple[bool, str]:
        """🏰 4대 테마 던전 3단계 난이도 5회 연속 고속 자동 탐험 & 숨겨진 방 시스템 (v15.3)"""
        # 잡지식: '던전(Dungeon)'은 중세 성채의 지하 감옥을 뜻하는 donjon에서 유래한 모험 파밍의 근본 공간이에용!
        if getattr(pet, "is_critically_injured", False):
            return False, "💀 신수가 치명상을 입은 상태입니다! 치료하거나 건강을 회복시켜주세요."

        d_info = DUNGEON_DATABASE.get(dungeon_id, DUNGEON_DATABASE[1])
        diff_info = DUNGEON_DIFFICULTIES.get(diff_id, DUNGEON_DIFFICULTIES[1])
        
        req_l = d_info["req_lvl"].get(diff_id, 1)
        if pet.level < req_l:
            return False, f"⚠️ 레벨이 부족합니다! [{d_info['emoji']} {d_info['name']} · {diff_info['name']}] 입장 필요 레벨: **Lv.{req_l}**"
        
        # 난이도별 기력 계산 + 종족 무드 패시브 연동
        base_cost = int(d_info["energy_cost"] * diff_info["energy_mult"])
        cost_per_run = base_cost
        sp_key = getattr(pet, "species_key", "")
        aff_lvl, _, _ = pet.get_affection_state()
        
        if sp_key == "늑대":
            w_disc = 0.15 if aff_lvl >= 8 else 0.10
            cost_per_run = max(1, int(cost_per_run * (1.0 - w_disc)))
        elif sp_key == "그리핀":
            cost_per_run = max(1, int(cost_per_run * 0.90))
        elif sp_key == "구미호" and pet.happiness >= 80:
            cost_per_run = max(1, int(cost_per_run * 0.90))
            
        cur_stam = getattr(pet, "stamina", 100)
        max_possible_runs = cur_stam // max(1, cost_per_run)
        actual_runs = min(times, max_possible_runs)

        if actual_runs <= 0:
            return False, f"😫 모험 기력이 부족하여 던전을 진행할 수 없습니다! (필요: {cost_per_run}%, 보유: {cur_stam}%) 수면으로 충전해 주세요."

        used_e = pet.consume_energy(actual_runs * base_cost, "dungeon")
        pet.hunger = max(0, pet.hunger - (actual_runs * 3))
        pet.cleanliness = max(0, pet.cleanliness - (actual_runs * 3))
        pet.total_adventures = getattr(pet, "total_adventures", 0) + actual_runs

        tot_gold = 0
        tot_exp = 0
        dropped_items = []
        hidden_rooms = 0
        hidden_rewards = []
        sp_key = getattr(pet, "species_key", "호랑이")

        for run_idx in range(1, actual_runs + 1):
            run_g = int(d_info["base_gold"] * diff_info["gold_mult"] * random.uniform(0.9, 1.2))
            run_e = int(d_info["base_exp"] * diff_info["exp_mult"] * random.uniform(0.95, 1.1))
            tot_gold += run_g
            tot_exp += run_e

            farming_tier = max(1, min(4, diff_id))
            stone_id = roll_stone_drop(inventory, pet, "armor", farming_tier)
            if stone_id:
                dropped_items.append(f"🛡️ 방어구 각인석 ({stone_id})")
            gem_type, gem_level = roll_gem_drop(inventory, max(1, min(5, diff_id)))
            dropped_items.append(f"💎 {gem_type.upper()} 보석 Lv.{gem_level}")

            # 재료 드랍 배율 반영 (정예 1.5x, 심연 2.0x)
            m_mult = diff_info["mat_mult"]

            # 보물 정수 드랍 (30% * m_mult)
            if random.random() < min(0.80, 0.30 * m_mult):
                amt = 2 if (diff_id == 3 and random.random() < 0.30) else 1
                inventory.add_item("relic_essence", amt)
                dropped_items.append(f"🔮 보물의 정수 x{amt}")

            # 강화석 드랍 (40% * m_mult)
            if random.random() < min(0.80, 0.40 * m_mult):
                amt = 2 if (diff_id == 3 and random.random() < 0.30) else 1
                inventory.add_item("stone", amt)
                dropped_items.append(f"💎 강화석 x{amt}")

            # 전용 보물 완제품 드랍 (마그마 4~6%, 심연 6~9%)
            relic_rate = d_info.get("relic_rate", {}).get(diff_id, 0.0)
            if relic_rate > 0 and not inventory.equipped_relic and random.random() < relic_rate:
                inventory.add_relic(sp_key, level=0)
                r_name = EXCLUSIVE_RELICS.get(sp_key, {}).get("name", "보물")
                dropped_items.append(f"🎴🔥 **[대박!] {r_name} 완제품**")

            # 방어구 드랍 (15%)
            if random.random() < 0.15:
                if dungeon_id == 1:
                    inventory.add_armor("leather_armor")
                    dropped_items.append("🛡️ 가죽 방어구")
                elif dungeon_id == 2:
                    inventory.add_armor("crystal_armor")
                    dropped_items.append("🛡️ 수정 방어구")
                elif dungeon_id >= 3:
                    a_pick = random.choice(["dragon_scale_armor", "robe_of_life", "gale_light_armor", "abyssal_armor"])
                    inventory.add_armor(a_pick)
                    a_name = ARMORS_DATABASE.get(a_pick, {}).get("name", "방어구")
                    dropped_items.append(f"🛡️ {a_name}")

            # ✨ 숨겨진 방 (Hidden Chamber) 이벤트 (일반 5%, 정예 8%, 심연 12%)
            if random.random() < diff_info["hidden_rate"]:
                hidden_rooms += 1
                h_type = random.choice(["stones", "essence", "gold_box", "armor"])
                if h_type == "stones":
                    s_cnt = random.randint(2, 4)
                    inventory.add_item("stone", s_cnt)
                    hidden_rewards.append(f"💎 강화석 x{s_cnt}")
                elif h_type == "essence":
                    e_cnt = random.randint(2, 3)
                    inventory.add_item("relic_essence", e_cnt)
                    hidden_rewards.append(f"🔮 보물의 정수 x{e_cnt}")
                elif h_type == "gold_box":
                    bonus_g = int(d_info["base_gold"] * 3 * random.uniform(1.0, 1.5))
                    tot_gold += bonus_g
                    hidden_rewards.append(f"💰 황금 상자 (+{bonus_g:,}G)")
                elif h_type == "armor" and dungeon_id >= 2:
                    a_pick = random.choice(["crystal_armor", "dragon_scale_armor", "robe_of_life", "abyssal_armor"])
                    inventory.add_armor(a_pick)
                    a_name = ARMORS_DATABASE.get(a_pick, {}).get("name", "방어구")
                    hidden_rewards.append(f"🛡️ 고옵션 {a_name}")

        # 🏥 던전 탐험 피격 건강 소모 (일반 2%, 정예 3%, 심연 5% / run)
        dmg_per_run = 2 if diff_id == 1 else (3 if diff_id == 2 else 5)
        tot_health_loss = actual_runs * dmg_per_run
        pet.health = max(10, getattr(pet, "health", 100) - tot_health_loss)

        pet.coins += tot_gold
        exp_logs = pet.gain_exp(tot_exp)
        aff_logs = pet.gain_affection(2) # 💖 던전 완료 시 애정도 +2

        item_summary = ", ".join(dropped_items) if dropped_items else "기본 재료 외 없음"
        env_msg = d_info["env_desc"].get(diff_id, "")
        
        result_msg = (
            f"🏰 **[{d_info['emoji']} {d_info['name']} · {diff_info['name']}] {actual_runs}회 연속 고속 탐험 완료!**\n"
            f"🌐 **환경 효과:** _{env_msg}_\n"
            f"💰 **총 획득 골드:** `+{tot_gold:,}G`\n"
            f"✨ **총 획득 경험치:** `+{tot_exp:,} EXP` (애정도 +2)\n"
            f"🎁 **드랍 전리품:** {item_summary}\n"
        )
        if hidden_rooms > 0:
            h_summary = ", ".join(hidden_rewards)
            result_msg += f"✨🌟 **[숨겨진 방 {hidden_rooms}회 발견!!]** {h_summary}\n"

        result_msg += f"🏥 **현재 건강:** `{pet.health}%` (-{tot_health_loss}%) · 🔥 **남은 모험 기력:** `{getattr(pet, 'stamina', 100)}%`"
        if exp_logs:
            result_msg += "\n" + " ".join(exp_logs)
        if aff_logs:
            result_msg += "\n" + " ".join(aff_logs)

        return True, result_msg

