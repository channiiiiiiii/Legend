# -*- coding: utf-8 -*-
"""
🏆 DAMAGOCHI Achievements & Titles System (v17.2)
- 14대 카테고리 업적 데이터베이스 & 칭호 수집 시스템
- 업적 점수, 칭호 장착/해제, 프로필 연동
- 잡지식: 칭호는 스탯이 아니라 계정의 품격과 역사를 증명하는 최고의 명예 뱃지입니다!
"""

ACHIEVEMENTS_DATABASE = [
    # 🐣 1. 육성 업적 (Grow)
    {
        "id": "grow_hatch_1",
        "category": "grow",
        "title": "새로운 인연",
        "name": "신수 첫 부화",
        "desc": "신수 알을 처음으로 부화시키기",
        "points": 10,
        "reward_coins": 1000,
        "check": lambda pet, inv, meta: getattr(pet, "generation", 1) >= 1
    },
    {
        "id": "grow_lvl_50",
        "category": "grow",
        "title": "성장의 증명",
        "name": "Lv.50 달성",
        "desc": "신수 레벨 50 도달하기",
        "points": 25,
        "reward_coins": 5000,
        "check": lambda pet, inv, meta: pet.level >= 50
    },
    {
        "id": "grow_lvl_99",
        "category": "grow",
        "title": "완성된 신수",
        "name": "Lv.99 만렙 달성",
        "desc": "신수 최고 레벨 99 만렙 도달하기",
        "points": 50,
        "reward_coins": 20000,
        "check": lambda pet, inv, meta: pet.level >= 99
    },

    # 💖 2. 애정 업적 (Affection)
    {
        "id": "aff_lvl_5",
        "category": "affection",
        "title": "친밀한 동료",
        "name": "애정도 Lv.5 달성",
        "desc": "신수와의 애정도 5단계 도달하기",
        "points": 15,
        "reward_coins": 2000,
        "check": lambda pet, inv, meta: pet.get_affection_state()[0] >= 5
    },
    {
        "id": "aff_lvl_8",
        "category": "affection",
        "title": "깊은 신뢰",
        "name": "애정도 Lv.8 달성",
        "desc": "신수와의 애정도 8단계 도달하기",
        "points": 30,
        "reward_coins": 5000,
        "check": lambda pet, inv, meta: pet.get_affection_state()[0] >= 8
    },
    {
        "id": "aff_lvl_10",
        "category": "affection",
        "title": "절대적 유대",
        "name": "애정도 Lv.10 최고봉",
        "desc": "신수와의 애정도 10단계(1,000점) 완전 달성",
        "points": 50,
        "reward_coins": 15000,
        "check": lambda pet, inv, meta: pet.get_affection_state()[0] >= 10
    },

    # 🧬 3. 혈통 및 잠재력 (Lineage)
    {
        "id": "lineage_reinc_1",
        "category": "lineage",
        "title": "혈통을 잇는 자",
        "name": "첫 환생 계승",
        "desc": "환생의 의식을 통해 2세대 계승하기",
        "points": 20,
        "reward_coins": 3000,
        "check": lambda pet, inv, meta: getattr(pet, "generation", 1) >= 2
    },
    {
        "id": "lineage_rank_s",
        "category": "lineage",
        "title": "우수한 혈통",
        "name": "IV S 랭크 달성",
        "desc": "총합 IV 350 이상 우수 신수 육성",
        "points": 20,
        "reward_coins": 3000,
        "check": lambda pet, inv, meta: pet.total_iv >= 350
    },
    {
        "id": "lineage_rank_sss",
        "category": "lineage",
        "title": "선택받은 혈통",
        "name": "IV SSS 랭크 달성",
        "desc": "총합 IV 450 이상 최상위 명문 신수 육성",
        "points": 50,
        "reward_coins": 10000,
        "check": lambda pet, inv, meta: pet.total_iv >= 450
    },
    {
        "id": "lineage_perfect_iv",
        "category": "lineage",
        "title": "완전한 존재",
        "name": "PERFECT 5V 500 IV",
        "desc": "전 5대 스탯 IV 100 MAX (총합 500 IV) 완전무결 달성",
        "points": 100,
        "reward_coins": 50000,
        "check": lambda pet, inv, meta: pet.total_iv >= 500
    },

    # 🌟 4. 초월 업적 (Transcend)
    {
        "id": "transcend_lvl_1",
        "category": "transcend",
        "title": "한계를 넘은 자",
        "name": "초월 1단계 승급",
        "desc": "만렙 이후 최초로 초월 Lv.1 승급하기",
        "points": 25,
        "reward_coins": 5000,
        "check": lambda pet, inv, meta: getattr(pet, "transcend_level", 0) >= 1
    },
    {
        "id": "transcend_lvl_10",
        "category": "transcend",
        "title": "경계를 부순 자",
        "name": "초월 10단계 승급",
        "desc": "초월 Lv.10 도달하기",
        "points": 50,
        "reward_coins": 20000,
        "check": lambda pet, inv, meta: getattr(pet, "transcend_level", 0) >= 10
    },
    {
        "id": "transcend_lvl_20",
        "category": "transcend",
        "title": "한계를 지운 자",
        "name": "초월 20단계 최고봉",
        "desc": "초월 최고 레벨 Lv.20(x20★) 완전 정복",
        "points": 100,
        "reward_coins": 50000,
        "check": lambda pet, inv, meta: getattr(pet, "transcend_level", 0) >= 20
    },

    # ⚔️ 5. 전투 & 토벌 누적 (Battle)
    {
        "id": "battle_win_10",
        "category": "battle",
        "title": "첫 발자국",
        "name": "전투 10승 달성",
        "desc": "던전/레이드 누적 10승 달성",
        "points": 10,
        "reward_coins": 1000,
        "check": lambda pet, inv, meta: getattr(pet, "total_adventures", 0) >= 10
    },
    {
        "id": "battle_win_100",
        "category": "battle",
        "title": "백전노장",
        "name": "전투 100승 달성",
        "desc": "던전/레이드 누적 100승 달성",
        "points": 30,
        "reward_coins": 10000,
        "check": lambda pet, inv, meta: getattr(pet, "total_adventures", 0) >= 100
    },
    {
        "id": "battle_boss_10",
        "category": "battle",
        "title": "🥉 사냥꾼",
        "name": "보스 10회 처치",
        "desc": "레이드 보스 누적 10회 토벌",
        "points": 15,
        "reward_coins": 3000,
        "check": lambda pet, inv, meta: getattr(pet, "total_dungeon_clears", 0) >= 10
    },
    {
        "id": "battle_boss_100",
        "category": "battle",
        "title": "🥇 보스 학살자",
        "name": "보스 100회 처치",
        "desc": "레이드 보스 누적 100회 토벌",
        "points": 50,
        "reward_coins": 25000,
        "check": lambda pet, inv, meta: getattr(pet, "total_dungeon_clears", 0) >= 100
    },

    # 🎴 6. 전용 보물 & 대장간 (Equipment)
    {
        "id": "relic_obtain",
        "category": "equip",
        "title": "유물 발견자",
        "name": "전용 보물 획득",
        "desc": "종족 전용 보물 장착하기",
        "points": 15,
        "reward_coins": 2000,
        "check": lambda pet, inv, meta: bool(inv.equipped_relic)
    },
    {
        "id": "relic_plus_5",
        "category": "equip",
        "title": "유물 강화자",
        "name": "전용 보물 +5 강화",
        "desc": "전용 보물 +5 강화 달성",
        "points": 25,
        "reward_coins": 5000,
        "check": lambda pet, inv, meta: bool(inv.equipped_relic and inv.equipped_relic.get("level", 0) >= 5)
    },
    {
        "id": "relic_plus_10",
        "category": "equip",
        "title": "유물 각성자",
        "name": "전용 보물 +10 종결",
        "desc": "전용 보물 +10 최고 강화 및 종족 전용 특효 완전 해금",
        "points": 75,
        "reward_coins": 30000,
        "check": lambda pet, inv, meta: bool(inv.equipped_relic and inv.equipped_relic.get("level", 0) >= 10)
    },
    {
        "id": "armor_plus_10",
        "category": "equip",
        "title": "숙련 대장장이",
        "name": "방어구 +10 강화",
        "desc": "방어구 +10 강화 달성",
        "points": 25,
        "reward_coins": 5000,
        "check": lambda pet, inv, meta: bool(inv.equipped_armor and inv.equipped_armor.get("level", 0) >= 10)
    },
    {
        "id": "armor_plus_15",
        "category": "equip",
        "title": "집념의 강화사",
        "name": "방어구 +15 최고 강화",
        "desc": "방어구 +15 강화 완전 정복",
        "points": 60,
        "reward_coins": 25000,
        "check": lambda pet, inv, meta: bool(inv.equipped_armor and inv.equipped_armor.get("level", 0) >= 15)
    },
    {
        "id": "armor_star_5",
        "category": "equip",
        "title": "고대 장비의 주인",
        "name": "방어구 ★5 고대 성급",
        "desc": "방어구 +15 ★★★★★ 최고 성급 및 고대 특효 영구 해금",
        "points": 100,
        "reward_coins": 50000,
        "check": lambda pet, inv, meta: bool(inv.equipped_armor and inv.equipped_armor.get("stars", 0) >= 5)
    },

    # 🟣🟡🔴 7. 고난도 레이드 정복 (Raid)
    {
        "id": "raid_nightmare_1",
        "category": "raid",
        "title": "악몽을 걷는 자",
        "name": "Nightmare 레이드 클리어",
        "desc": "악몽(Nightmare) 난이도 보스 최초 격파",
        "points": 30,
        "reward_coins": 10000,
        "check": lambda pet, inv, meta: meta.get("cleared_nightmare", False)
    },
    {
        "id": "raid_mythic_1",
        "category": "raid",
        "title": "신화를 넘은 자",
        "name": "Mythic 레이드 클리어",
        "desc": "신화(Mythic) 난이도 보스 최초 격파",
        "points": 50,
        "reward_coins": 20000,
        "check": lambda pet, inv, meta: meta.get("cleared_mythic", False)
    },
    {
        "id": "raid_ancient_1",
        "category": "raid",
        "title": "고대를 깨운 자",
        "name": "Ancient 레이드 클리어",
        "desc": "고대(Ancient) 난이도 보스 최초 격파",
        "points": 100,
        "reward_coins": 50000,
        "check": lambda pet, inv, meta: meta.get("cleared_ancient", False)
    },
    {
        "id": "boss_ent_ancient",
        "category": "raid",
        "title": "태고의 벌목꾼",
        "name": "Ancient 고대 엔트 토벌",
        "desc": "Ancient 고대 엔트 격파",
        "points": 50,
        "reward_coins": 20000,
        "check": lambda pet, inv, meta: "ent_ancient" in meta.get("cleared_bosses", [])
    },
    {
        "id": "boss_crystal_ancient",
        "category": "raid",
        "title": "거울을 부순 자",
        "name": "Ancient 크리스탈 드래곤 토벌",
        "desc": "Ancient 크리스탈 드래곤 격파",
        "points": 60,
        "reward_coins": 25000,
        "check": lambda pet, inv, meta: "crystal_ancient" in meta.get("cleared_bosses", [])
    },
    {
        "id": "boss_ifrit_ancient",
        "category": "raid",
        "title": "업화를 삼킨 자",
        "name": "Ancient 이프리트 토벌",
        "desc": "Ancient 이프리트 격파",
        "points": 70,
        "reward_coins": 30000,
        "check": lambda pet, inv, meta: "ifrit_ancient" in meta.get("cleared_bosses", [])
    },
    {
        "id": "boss_guardian_ancient",
        "category": "raid",
        "title": "시간을 거스른 자",
        "name": "Ancient 성운 가디언 토벌",
        "desc": "Ancient 성운 가디언 격파",
        "points": 80,
        "reward_coins": 35000,
        "check": lambda pet, inv, meta: "guardian_ancient" in meta.get("cleared_bosses", [])
    },
    {
        "id": "boss_omega_ancient",
        "category": "raid",
        "title": "🪐 종말의 정복자",
        "name": "Ancient 오메가 최종 토벌",
        "desc": "Ancient 오메가(240K CP) 격파 및 엔드게임 최종 졸업",
        "points": 150,
        "reward_coins": 100000,
        "check": lambda pet, inv, meta: "omega_ancient" in meta.get("cleared_bosses", [])
    },

    # 🎖️ v17.2 신규 레이드 4단계 정복 및 고대 15킬 칭호
    {
        "id": "raid_clear_normal_4",
        "category": "raid",
        "title": "레이드 입문가",
        "name": "노말 레이드 4종 정복",
        "desc": "Normal 레이드 4대 보스(엔트·수정용·이프리트·가디언) 올클리어",
        "points": 30,
        "reward_coins": 5000,
        "check": lambda pet, inv, meta: len(set(getattr(pet, "raid_clears", {}).get("1", []) + getattr(pet, "raid_clears", {}).get(1, []))) >= 4
    },
    {
        "id": "raid_clear_hard_4",
        "category": "raid",
        "title": "레이드 숙련가",
        "name": "하드 레이드 4종 정복",
        "desc": "Hard 레이드 4대 보스(엔트·수정용·이프리트·가디언) 올클리어",
        "points": 50,
        "reward_coins": 10000,
        "check": lambda pet, inv, meta: len(set(getattr(pet, "raid_clears", {}).get("2", []) + getattr(pet, "raid_clears", {}).get(2, []))) >= 4
    },
    {
        "id": "raid_clear_nightmare_4",
        "category": "raid",
        "title": "악몽을 쫓아낸 자",
        "name": "악몽 레이드 4종 정복",
        "desc": "Nightmare 레이드 4대 보스(엔트·수정용·이프리트·가디언) 올클리어",
        "points": 80,
        "reward_coins": 20000,
        "check": lambda pet, inv, meta: len(set(getattr(pet, "raid_clears", {}).get("3", []) + getattr(pet, "raid_clears", {}).get(3, []))) >= 4
    },
    {
        "id": "raid_clear_mythic_4",
        "category": "raid",
        "title": "신화가 된 자",
        "name": "신화 레이드 4종 정복",
        "desc": "Mythic 레이드 4대 보스(엔트·수정용·이프리트·가디언) 올클리어",
        "points": 100,
        "reward_coins": 30000,
        "check": lambda pet, inv, meta: len(set(getattr(pet, "raid_clears", {}).get("4", []) + getattr(pet, "raid_clears", {}).get(4, []))) >= 4
    },
    {
        "id": "ancient_kill_15_ent",
        "category": "raid",
        "title": "개미핥기",
        "name": "고대 엔트 15회 토벌",
        "desc": "Ancient 고대 엔트 누적 15회 토벌 달성",
        "points": 50,
        "reward_coins": 15000,
        "check": lambda pet, inv, meta: getattr(pet, "boss_kills", {}).get("5_1", 0) >= 15
    },
    {
        "id": "ancient_kill_15_dragon",
        "category": "raid",
        "title": "다이아몬드",
        "name": "크리스탈 드래곤 15회 토벌",
        "desc": "Ancient 크리스탈 드래곤 누적 15회 토벌 달성",
        "points": 50,
        "reward_coins": 15000,
        "check": lambda pet, inv, meta: getattr(pet, "boss_kills", {}).get("5_2", 0) >= 15
    },
    {
        "id": "ancient_kill_15_ifrit",
        "category": "raid",
        "title": "라그나로크",
        "name": "이프리트 15회 토벌",
        "desc": "Ancient 이프리트 누적 15회 토벌 달성",
        "points": 50,
        "reward_coins": 15000,
        "check": lambda pet, inv, meta: getattr(pet, "boss_kills", {}).get("5_3", 0) >= 15
    },
    {
        "id": "ancient_kill_15_guardian",
        "category": "raid",
        "title": "쉿!",
        "name": "성운 가디언 15회 토벌",
        "desc": "Ancient 성운 가디언 누적 15회 토벌 달성",
        "points": 50,
        "reward_coins": 15000,
        "check": lambda pet, inv, meta: getattr(pet, "boss_kills", {}).get("5_4", 0) >= 15
    },
    {
        "id": "ancient_kill_15_omega",
        "category": "raid",
        "title": "이클립스",
        "name": "오메가 15회 토벌",
        "desc": "Ancient 오메가 누적 15회 토벌 달성",
        "points": 100,
        "reward_coins": 50000,
        "check": lambda pet, inv, meta: getattr(pet, "boss_kills", {}).get("5_5", 0) >= 15
    },
    {
        "id": "ancient_master_all",
        "category": "zenith",
        "title": "태초의 별",
        "name": "고대 5대 보스 15회 완전 토벌",
        "desc": "개미핥기/다이아몬드/라그나로크/쉿!/이클립스 5대 칭호를 모두 획득한 지고의 전설",
        "points": 200,
        "reward_coins": 100000,
        "check": lambda pet, inv, meta: (
            getattr(pet, "boss_kills", {}).get("5_1", 0) >= 15 and
            getattr(pet, "boss_kills", {}).get("5_2", 0) >= 15 and
            getattr(pet, "boss_kills", {}).get("5_3", 0) >= 15 and
            getattr(pet, "boss_kills", {}).get("5_4", 0) >= 15 and
            getattr(pet, "boss_kills", {}).get("5_5", 0) >= 15
        )
    },

    # 👑 8. 엔드게임 최종 종합 졸업 (Zenith)
    {
        "id": "zenith_king",
        "category": "zenith",
        "title": "👑 신수왕",
        "name": "최고위 신수왕 달성",
        "desc": "Lv.99 만렙, 초월 20, 애정 10, 보물 +10, 방어구 +15 ★5, Ancient 오메가 클리어",
        "points": 250,
        "reward_coins": 200000,
        "check": lambda pet, inv, meta: (
            pet.level >= 99 and
            getattr(pet, "transcend_level", 0) >= 20 and
            pet.get_affection_state()[0] >= 10 and
            bool(inv.equipped_relic and inv.equipped_relic.get("level", 0) >= 10) and
            bool(inv.equipped_armor and inv.equipped_armor.get("stars", 0) >= 5) and
            "omega_ancient" in meta.get("cleared_bosses", [])
        )
    },
    {
        "id": "zenith_supreme",
        "category": "zenith",
        "title": "👑🌌 천상천하 신수독존",
        "name": "전 우주 유일무이 완전체",
        "desc": "PERFECT 500 IV 신수로 신수왕의 모든 조건을 달성",
        "points": 500,
        "reward_coins": 500000,
        "check": lambda pet, inv, meta: (
            pet.total_iv >= 500 and
            pet.level >= 99 and
            getattr(pet, "transcend_level", 0) >= 20 and
            pet.get_affection_state()[0] >= 10 and
            bool(inv.equipped_relic and inv.equipped_relic.get("level", 0) >= 10) and
            bool(inv.equipped_armor and inv.equipped_armor.get("stars", 0) >= 5) and
            "omega_ancient" in meta.get("cleared_bosses", [])
        )
    }
]

class AchievementManager:
    @staticmethod
    def check_and_claim(pet, inventory, meta: dict) -> list[str]:
        """새로 달성한 업적 체크, 칭호 해금 및 보상 자동 지급"""
        if "claimed_achievements" not in meta:
            meta["claimed_achievements"] = []
        if "unlocked_titles" not in meta:
            meta["unlocked_titles"] = []
        if "achievement_score" not in meta:
            meta["achievement_score"] = 0

        claimed_ids = meta["claimed_achievements"]
        new_logs = []

        for ach in ACHIEVEMENTS_DATABASE:
            ach_id = ach["id"]
            if ach_id not in claimed_ids:
                try:
                    if ach["check"](pet, inventory, meta):
                        claimed_ids.append(ach_id)
                        t_name = ach["title"]
                        if t_name not in meta["unlocked_titles"]:
                            meta["unlocked_titles"].append(t_name)
                        
                        pts = ach.get("points", 10)
                        meta["achievement_score"] += pts
                        
                        r_coins = ach.get("reward_coins", 0)
                        pet.coins += r_coins
                        
                        new_logs.append(
                            f"🏆 **[업적 달성!]** **「{ach['name']}」** 완료!\n"
                            f"└ 🏷️ 칭호 획득: **【{t_name}】** | 🌟 +{pts}점 | 💰 +{r_coins:,}G"
                        )
                except (KeyError, TypeError, ValueError) as e:
                    print(f"[ACHIEVEMENT ERROR] {type(e).__name__}: {e}")

        return new_logs

    @staticmethod
    def get_total_score(meta: dict) -> int:
        return meta.get("achievement_score", 0)

    @staticmethod
    def equip_title(meta: dict, title_name: str) -> tuple[bool, str]:
        titles = meta.get("unlocked_titles", [])
        if title_name not in titles:
            return False, f"⚠️ 아직 획득하지 못한 칭호입니다: **「{title_name}」**"
        
        meta["equipped_title"] = title_name
        return True, f"✨ 칭호를 **「{title_name}」**(으)로 장착했습니다!"

    @staticmethod
    def unequip_title(meta: dict) -> tuple[bool, str]:
        meta["equipped_title"] = None
        return True, "✨ 장착 중인 칭호를 해제했습니다."
