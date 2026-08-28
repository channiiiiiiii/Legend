# -*- coding: utf-8 -*-
"""
💾 DAMAGOCHI Save Backend (v18)
Supabase JSONB + 로컬 JSON 듀얼 백엔드 세이브 매니저

운영(Render): SAVE_BACKEND=supabase → Supabase JSONB
로컬(테스트): SAVE_BACKEND=json    → discord_saves/*.json

# 잡지식: Supabase는 Firebase의 오픈소스 대안으로, PostgreSQL 위에 REST API를 올린 구조라
# SQL 쿼리와 실시간 구독이 동시에 되는 꿀 조합이에용! ㅎㅎ
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 환경변수 로드 (.env 파일 지원)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 미설치 시 os.environ 직접 사용

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.environ.get("SUPABASE_SECRET_KEY")
SAVE_BACKEND = os.environ.get("SAVE_BACKEND", "json").lower()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SAVES_DIR = os.path.join(PROJECT_ROOT, "discord_saves")

# 세이브 데이터 버전 (향후 마이그레이션용)
CURRENT_SAVE_VERSION = 18

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Supabase 클라이언트 (싱글턴)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
_supabase = None


def get_supabase():
    """Supabase 클라이언트 싱글턴 반환 (세이브할 때마다 새로 생성하지 않는다)"""
    global _supabase

    if _supabase is None:
        if not SUPABASE_URL:
            raise RuntimeError("SUPABASE_URL 환경변수가 없습니다.")
        if not SUPABASE_SECRET_KEY:
            raise RuntimeError("SUPABASE_SECRET_KEY 환경변수가 없습니다.")

        from supabase import create_client
        _supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)

    return _supabase


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 세이브 버전 마이그레이션
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def migrate_save(data: dict) -> dict:
    """
    세이브 데이터를 최신 버전으로 자동 마이그레이션
    - 신규 필드는 반드시 data.get("new_field", default) 방식으로 읽는다
    - 기존 유저 데이터에 값이 없어도 자동으로 기본값을 사용한다
    """
    version = data.get("save_version", 17)

    if version < 18:
        # v17 → v18: save_version 필드 추가 (구조 변경 없음, 버전 태깅만)
        data["save_version"] = 18

        # 구버전 방어구 ID 호환 처리
        inv = data.get("inventory", {})
        eq_armor = inv.get("equipped_armor")
        if eq_armor and eq_armor.get("armor_id") == "ancient_god_armor":
            eq_armor["armor_id"] = "mythic_celestial_armor"

    data["save_version"] = CURRENT_SAVE_VERSION
    return data


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JSON 백엔드 (로컬 파일시스템)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _ensure_saves_dir():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR, exist_ok=True)


def load_from_json(user_id: str) -> dict | None:
    """로컬 JSON 파일에서 세이브 로드"""
    _ensure_saves_dir()
    path = os.path.join(SAVES_DIR, f"{user_id}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ JSON 로드 에러: user={user_id} / {e}")
        return None


def save_to_json(user_id: str, save_data: dict) -> bool:
    """로컬 JSON 파일에 세이브 저장 (원자적 임시 파일 교체)"""
    _ensure_saves_dir()
    path = os.path.join(SAVES_DIR, f"{user_id}.json")
    temp_path = f"{path}.tmp_{os.getpid()}_{int(time.time() * 1000)}"

    for attempt in range(3):
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, path)
            return True
        except Exception:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            if attempt == 2:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(save_data, f, ensure_ascii=False, indent=2)
                    return True
                except Exception as final_e:
                    print(f"❌ JSON 세이브 에러 (최종 실패): user={user_id} / {final_e}")
            time.sleep(0.05)
    return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Supabase 백엔드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def load_from_supabase(user_id: str) -> dict | None:
    """Supabase user_saves 테이블에서 세이브 로드"""
    try:
        db = get_supabase()
        result = (
            db.table("user_saves")
            .select("save_data")
            .eq("user_id", str(user_id))
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return result.data[0]["save_data"]
    except Exception as e:
        print(f"❌ Supabase 로드 에러: user={user_id} / {e}")
        return None


def save_to_supabase(user_id: str, save_data: dict) -> bool:
    """Supabase user_saves 테이블에 UPSERT 저장"""
    try:
        db = get_supabase()
        payload = {
            "user_id": str(user_id),
            "save_data": save_data,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        db.table("user_saves").upsert(
            payload,
            on_conflict="user_id"
        ).execute()
        return True
    except Exception as e:
        print(f"❌ Supabase 세이브 에러: user={user_id} / {e}")
        return False


def delete_from_supabase(user_id: str) -> bool:
    """Supabase user_saves 테이블에서 특정 유저 세이브 삭제"""
    try:
        db = get_supabase()
        db.table("user_saves").delete().eq("user_id", str(user_id)).execute()
        return True
    except Exception as e:
        print(f"❌ Supabase 삭제 에러: user={user_id} / {e}")
        return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 통합 인터페이스 (Discord Bot은 이것만 호출)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def load_user_save(user_id: str) -> dict | None:
    """
    세이브 로드 통합 인터페이스
    - SAVE_BACKEND=supabase → Supabase에서 로드
    - SAVE_BACKEND=json     → 로컬 JSON에서 로드
    - 로드 후 자동 마이그레이션 적용
    """
    if SAVE_BACKEND == "supabase":
        data = load_from_supabase(user_id)
    else:
        data = load_from_json(user_id)

    if data is not None:
        data = migrate_save(data)

    return data


def save_user_save(user_id: str, save_data: dict) -> bool:
    """
    세이브 저장 통합 인터페이스
    - save_version 자동 태깅
    - SAVE_BACKEND에 따라 저장 대상 결정
    """
    save_data["save_version"] = CURRENT_SAVE_VERSION

    if SAVE_BACKEND == "supabase":
        return save_to_supabase(user_id, save_data)
    else:
        return save_to_json(user_id, save_data)


def delete_user_save(user_id: str) -> bool:
    """세이브 삭제 통합 인터페이스"""
    if SAVE_BACKEND == "supabase":
        return delete_from_supabase(user_id)
    else:
        path = os.path.join(SAVES_DIR, f"{user_id}.json")
        try:
            if os.path.exists(path):
                os.remove(path)
            return True
        except Exception as e:
            print(f"❌ JSON 삭제 에러: user={user_id} / {e}")
            return False


def get_backend_info() -> str:
    """현재 사용 중인 백엔드 정보 반환 (디버그/헬스체크용)"""
    return f"Backend: {SAVE_BACKEND.upper()} | Version: v{CURRENT_SAVE_VERSION}"
