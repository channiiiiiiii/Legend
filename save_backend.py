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


class SaveBackendUnavailable(RuntimeError):
    """저장소 조회 자체가 실패하여 신규/기존 사용자를 판별할 수 없는 상태."""


class SaveVersionUnsupported(SaveBackendUnavailable):
    """현재 코드보다 미래 버전인 세이브의 안전한 로드 중단."""


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


def validate_backend_config() -> None:
    """운영 백엔드 설정 누락을 네트워크 요청 전에 검증한다."""
    if SAVE_BACKEND not in {"json", "supabase"}:
        raise RuntimeError(f"지원하지 않는 SAVE_BACKEND: {SAVE_BACKEND!r}")
    if SAVE_BACKEND == "supabase":
        missing = [
            name for name, value in (
                ("SUPABASE_URL", SUPABASE_URL),
                ("SUPABASE_SECRET_KEY", SUPABASE_SECRET_KEY),
            )
            if not value
        ]
        if missing:
            raise RuntimeError(
                "Supabase 운영 환경변수가 누락되었습니다: " + ", ".join(missing)
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 세이브 버전 마이그레이션
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _migrate_v17_to_v18(data: dict) -> dict:
    data["save_version"] = 18
    inv = data.get("inventory", {})
    eq_armor = inv.get("equipped_armor")
    if eq_armor and eq_armor.get("armor_id") == "ancient_god_armor":
        eq_armor["armor_id"] = "mythic_celestial_armor"
    return data


SAVE_MIGRATIONS = {
    17: _migrate_v17_to_v18,
}


def migrate_save(data: dict) -> dict:
    """
    세이브 데이터를 최신 버전으로 자동 마이그레이션
    - 신규 필드는 반드시 data.get("new_field", default) 방식으로 읽는다
    - 기존 유저 데이터에 값이 없어도 자동으로 기본값을 사용한다
    """
    version = data.get("save_version", 17)
    if not isinstance(version, int):
        raise SaveVersionUnsupported(f"잘못된 save_version 형식: {version!r}")
    if version > CURRENT_SAVE_VERSION:
        print(
            f"[SAVE VERSION ERROR] future={version} current={CURRENT_SAVE_VERSION}"
        )
        raise SaveVersionUnsupported(
            f"미래 세이브 버전 v{version}은 현재 v{CURRENT_SAVE_VERSION}에서 지원되지 않습니다."
        )

    while version < CURRENT_SAVE_VERSION:
        migration = SAVE_MIGRATIONS.get(version)
        if migration is None:
            raise SaveVersionUnsupported(
                f"v{version} 마이그레이션 단계가 정의되지 않았습니다."
            )
        data = migration(data)
        version = data["save_version"]

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
        except (OSError, TypeError, ValueError) as e:
            print(
                f"[JSON SAVE ERROR] user={user_id} attempt={attempt + 1}/3 "
                f"/ {type(e).__name__}: {ascii(str(e))}"
            )
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as cleanup_error:
                    print(
                        f"[JSON TEMP CLEANUP ERROR] {type(cleanup_error).__name__}: "
                        f"{ascii(str(cleanup_error))}"
                    )
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
        print(f"[SUPABASE LOAD ERROR] user={user_id} / {type(e).__name__}: {ascii(str(e))}")
        raise SaveBackendUnavailable(
            f"Supabase에서 user={user_id} 세이브를 조회하지 못했습니다."
        ) from e


def save_to_supabase(user_id: str, save_data: dict) -> bool:
    """Supabase user_saves 테이블에 UPSERT 저장"""
    payload = {
        "user_id": str(user_id),
        "save_data": save_data,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    for attempt in range(3):
        try:
            db = get_supabase()
            db.table("user_saves").upsert(
                payload,
                on_conflict="user_id"
            ).execute()
            return True
        except Exception as e:
            print(
                f"[SUPABASE SAVE ERROR] user={user_id} "
                f"attempt={attempt + 1}/3 / {type(e).__name__}: {ascii(str(e))}"
            )
            if attempt < 2:
                time.sleep(0.1 * (2 ** attempt))
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
