# -*- coding: utf-8 -*-
"""
🏛️ DAMAGOCHI Hall of Fame Storage & Royal Market System (v6.0)
외모력(Charm) & 애정도(Affection) 프리미엄 반영 왕실 경매소 모듈
"""

import os
import json
import time
import threading

from save_backend import SAVE_BACKEND

STORAGE_FILE = os.path.join(os.path.dirname(__file__), "pet_storage.json")
_STORAGE_LOCK = threading.RLock()

class StorageManager:
    @staticmethod
    def load_storage(user_id: str = "local", meta: dict = None) -> list:
        if meta is not None:
            return list(meta.get("hall_of_fame", []))
        if SAVE_BACKEND == "supabase":
            raise RuntimeError("Supabase 운영에서는 meta['hall_of_fame']을 사용해야 합니다.")
        with _STORAGE_LOCK:
            if not os.path.exists(STORAGE_FILE):
                return []
            try:
                with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(str(user_id), [])
            except (OSError, json.JSONDecodeError, TypeError) as e:
                print(f"[STORAGE LOAD ERROR] {type(e).__name__}: {e}")
                return []

    @staticmethod
    def store_pet(pet_obj, user_id: str = "local", meta: dict = None) -> bool:
        if hasattr(pet_obj, "to_dict"):
            p_dict = pet_obj.to_dict()
        elif isinstance(pet_obj, dict):
            p_dict = dict(pet_obj)
        else:
            p_dict = {"name": str(pet_obj)}

        p_dict["stored_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        if meta is not None:
            meta.setdefault("hall_of_fame", []).append(p_dict)
            return True
        if SAVE_BACKEND == "supabase":
            raise RuntimeError("Supabase 운영에서는 meta['hall_of_fame']에 저장해야 합니다.")

        with _STORAGE_LOCK:
            data = {}
            if os.path.exists(STORAGE_FILE):
                try:
                    with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except (OSError, json.JSONDecodeError, TypeError) as e:
                    print(f"[STORAGE LOAD ERROR] {type(e).__name__}: {e}")
                    return False

            user_list = data.get(str(user_id), [])
            user_list.append(p_dict)
            data[str(user_id)] = user_list

            temp_path = f"{STORAGE_FILE}.tmp"
            try:
                with open(temp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(temp_path, STORAGE_FILE)
                return True
            except (OSError, TypeError, ValueError) as e:
                print(f"[STORAGE SAVE ERROR] {type(e).__name__}: {e}")
                return False

class PetMarket:
    @staticmethod
    def calculate_sell_price(pet) -> int:
        """레벨, IV, 외모력(Charm), 애정도(Affection)를 종합한 왕실 경매 가치 산정"""
        base_price = pet.level * 1500 # Lv.99 기준 약 150,000G
        
        # IV 등급 보너스
        iv_total = getattr(pet, "total_iv", 350)
        multiplier = 1.0
        if iv_total >= 460:
            multiplier = 3.5 # 5V 레전드
        elif iv_total >= 400:
            multiplier = 2.5
        elif iv_total >= 330:
            multiplier = 1.8
        elif iv_total >= 250:
            multiplier = 1.3

        # 외모력(Charm) 보너스 (외모력 100이면 +100% 2배!)
        charm_val = getattr(pet, "charm", 70)
        charm_bonus = 1.0 + (charm_val / 100.0)
        
        # 애정도(Affection) 보너스 (애정도 100이면 +50%)
        aff_val = getattr(pet, "affection", 50)
        aff_bonus = 1.0 + (aff_val / 200.0)

        final_price = int(base_price * multiplier * charm_bonus * aff_bonus)
        
        if pet.level >= 99:
            final_price += 150000 # 만렙 프리미엄
            
        return final_price
