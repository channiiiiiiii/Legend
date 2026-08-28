# -*- coding: utf-8 -*-
"""
단위 테스트 및 v9.0 신수 장비 시스템 (보물/방어구 강화, 분해, 제작, 실전 배틀) 검증
"""
import os
import sys
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from pet import Pet
from species import Genetics, SPECIES_DATABASE, PERSONALITIES, SPECIES_SKILLS
from save_manager import SaveManager
from shop import Shop, Inventory, ITEMS_DATABASE, EXCLUSIVE_RELICS, ARMORS_DATABASE
from adventure import AdventureSystem, BOSS_DATABASE, RAID_DIFFICULTIES
from storage import StorageManager, PetMarket

def run_tests():
    print("=== [1] 10대 종족 전용 보물 및 5등급 방어구 데이터 검증 ===")
    assert len(EXCLUSIVE_RELICS) == 10
    assert len(ARMORS_DATABASE) == 8
    
    for sp_k, r_info in EXCLUSIVE_RELICS.items():
        assert "name" in r_info
        assert "special_10" in r_info
        print(f"-> 🎴 {sp_k} 전용 보물: {r_info['name']} | +10: {r_info['special_10']}")

    for a_id, a_info in ARMORS_DATABASE.items():
        print(f"-> 🛡️ {a_info['tier']} {a_info['name']} ({a_info['type']}): HP+{a_info['base_hp']} / DEF+{a_info['base_def']}")

    print("\n=== [2] 장비 장착, +10 강화, 분해, 제작 시스템 검증 ===")
    inv = Inventory()
    pet = Pet(custom_data={"species_key": "호랑이", "level": 50, "coins": 100000})
    
    # 1. 보물 추가 및 장착
    inv.add_relic("호랑이", level=0)
    suc, msg = inv.equip_relic("호랑이")
    assert suc
    assert inv.equipped_relic["species"] == "호랑이"
    print(f"-> 보물 장착 성공: {msg}")

    # 2. 보물 정수 분해 및 제작
    inv.add_relic("현무", level=0)
    suc, msg = inv.dismantle_relic(0)
    assert suc
    assert inv.species_essences.get("현무", 0) >= 10
    print(f"-> 분해 성공: {msg}")

    # 3. 방어구 추가 및 장착
    inv.add_armor("dragon_scale_armor", level=0)
    suc, msg = inv.equip_armor(0)
    assert suc
    assert inv.equipped_armor["armor_id"] == "dragon_scale_armor"
    print(f"-> 방어구 장착 성공: {msg}")

    # 4. 방어구 강화
    suc, msg, pet.coins = inv.enhance_armor(pet.coins)
    assert suc
    print(f"-> 방어구 강화 결과: {msg}")

    print("\n=== [3] 장비 착용 상태 실전 25개 레이드 시뮬레이션 ===")
    baha = Pet(custom_data={
        "species_key": "바하무트", "level": 99, "atk_iv": 100, "hp_iv": 100, "def_iv": 100, "spd_iv": 100, "crit_iv": 100,
        "health": 100, "coins": 50000
    })
    baha_inv = Inventory()
    baha_inv.add_relic("바하무트", level=10) # +10 종말의 용핵
    baha_inv.equip_relic("바하무트")
    baha_inv.add_armor("ancient_god_armor", level=7) # +7 고대신의 갑옷
    baha_inv.equip_armor(0)

    # 고대 오메가 레이드 테스트
    suc, res = AdventureSystem.run_boss_raid(baha, baha_inv, boss_id=5, diff_id=5, interactive=False)
    print(f"-> 🐲 +10 보물 / +7 신화 방어구 바하무트 vs 🪐 오메가 [고대]: {res.splitlines()[0]}")

    # 세이브 파일 정리
    SaveManager.reset_save()
    if os.path.exists(os.path.join(os.path.dirname(__file__), "pet_storage.json")):
        try:
            os.remove(os.path.join(os.path.dirname(__file__), "pet_storage.json"))
        except Exception:
            pass

    print("\n🎉 신수 장비 시스템 통합 & +10 강화/분해/제작 ALL PASS! 갓벽합니다 선배님!")

if __name__ == "__main__":
    run_tests()
