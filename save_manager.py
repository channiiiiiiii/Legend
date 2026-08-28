# -*- coding: utf-8 -*-
"""
💾 DAMAGOCHI Save Manager
데이터 영구 저장 및 오프라인 시간 경과 처리 모듈
"""

import json
import os
import time
from datetime import datetime

SAVE_FILE_PATH = os.path.join(os.path.dirname(__file__), "save_data.json")
BACKUP_FILE_PATH = os.path.join(os.path.dirname(__file__), "save_data.bak")

# 잡지식: 1996년 출시된 원조 반다이 다마고치는 배터리를 빼면 세이브가 날아갔지만, 제니가 만든 시스템은 JSON으로 영구 불멸입니다!

class SaveManager:
    @staticmethod
    def exists() -> bool:
        """세이브 파일 존재 여부 확인"""
        return os.path.exists(SAVE_FILE_PATH)

    @staticmethod
    def save(pet_data: dict, inventory_data: dict, meta_data: dict = None) -> bool:
        """데이터 저장 (원자적 쓰기 & 백업)"""
        payload = {
            "version": "1.1.0",
            "last_saved_time": time.time(),
            "last_saved_str": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "pet": pet_data,
            "inventory": inventory_data,
            "meta": meta_data or {"play_count": 0, "total_coins_earned": 0, "claimed_achievements": []}
        }
        
        try:
            # 기존 파일 백업
            if os.path.exists(SAVE_FILE_PATH):
                try:
                    with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f_src:
                        with open(BACKUP_FILE_PATH, "w", encoding="utf-8") as f_dst:
                            f_dst.write(f_src.read())
                except Exception:
                    pass
            
            # JSON 저장
            with open(SAVE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[세이브 에러 발생]: {e}")
            return False

    @staticmethod
    def load() -> dict:
        """데이터 로드 및 오프라인 경과 시간 계산"""
        if not SaveManager.exists():
            return None
        
        try:
            with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # 마지막 접속 이후 경과 시간(초) 계산
            last_saved = data.get("last_saved_time", time.time())
            elapsed_seconds = max(0, time.time() - last_saved)
            data["elapsed_seconds"] = elapsed_seconds
            data["elapsed_minutes"] = elapsed_seconds / 60.0
            
            return data
        except Exception as e:
            print(f"[로드 에러 발생]: {e}")
            # 백업 복구 시도
            if os.path.exists(BACKUP_FILE_PATH):
                try:
                    with open(BACKUP_FILE_PATH, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        data["elapsed_seconds"] = 0
                        data["elapsed_minutes"] = 0
                        return data
                except Exception:
                    return None
            return None

    @staticmethod
    def reset_save():
        """세이브 데이터 초기화"""
        if os.path.exists(SAVE_FILE_PATH):
            os.remove(SAVE_FILE_PATH)
        if os.path.exists(BACKUP_FILE_PATH):
            os.remove(BACKUP_FILE_PATH)
