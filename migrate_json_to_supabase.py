# -*- coding: utf-8 -*-
"""
🔄 DAMAGOCHI JSON → Supabase 마이그레이션 스크립트 (v18)
discord_saves/*.json → Supabase user_saves 테이블 일괄 이전

실행 전 환경변수 설정 필수:
  SUPABASE_URL=https://ualknqxcsltqgtltusjj.supabase.co
  SUPABASE_SECRET_KEY=sb_secret_xxxxx

실행:
  python migrate_json_to_supabase.py

# 잡지식: PostgreSQL의 UPSERT(INSERT ON CONFLICT)는 2015년 9.5 버전에서 추가되었는데,
# 이전에는 개발자들이 CTE로 직접 구현해야 해서 엄청 고통스러웠다고 해용! ㅎㅎ
"""

import json
import os
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Windows cp949 콘솔 인코딩 에러 방지
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from save_backend import get_supabase, CURRENT_SAVE_VERSION, migrate_save

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SAVE_DIR = Path(os.path.join(PROJECT_ROOT, "discord_saves"))
BACKUP_DIR = Path(os.path.join(PROJECT_ROOT, "backup", f"discord_saves_{datetime.now().strftime('%Y_%m_%d_%H%M%S')}"))


def create_backup():
    """📦 마이그레이션 전 JSON 세이브 전체 백업"""
    if not SAVE_DIR.exists():
        print("⚠️ discord_saves/ 폴더가 존재하지 않습니다.")
        return False

    files = list(SAVE_DIR.glob("*.json"))
    if not files:
        print("⚠️ 이전할 JSON 세이브 파일이 없습니다.")
        return False

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        shutil.copy2(f, BACKUP_DIR / f.name)

    print(f"✅ 백업 완료: {BACKUP_DIR} ({len(files)}개 파일)")
    return True


def main():
    print("=" * 60)
    print("🔄 DAMAGOCHI JSON → Supabase 마이그레이션 시작")
    print("=" * 60)

    # 1단계: 백업
    print("\n📦 [STEP 1] JSON 세이브 백업 중...")
    if not create_backup():
        print("❌ 백업 실패. 마이그레이션을 중단합니다.")
        return

    # 2단계: Supabase 연결 확인
    print("\n🔌 [STEP 2] Supabase 연결 확인 중...")
    try:
        db = get_supabase()
        # 테이블 존재 확인 (빈 쿼리)
        db.table("user_saves").select("user_id").limit(1).execute()
        print("✅ Supabase user_saves 테이블 연결 성공!")
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        print("환경변수 SUPABASE_URL, SUPABASE_SECRET_KEY를 확인해 주세요.")
        return

    # 3단계: JSON 파일 이전
    print("\n📤 [STEP 3] JSON → Supabase 이전 중...")
    files = list(SAVE_DIR.glob("*.json"))
    print(f"마이그레이션 대상: {len(files)}개")

    success = 0
    failed = 0

    for path in files:
        user_id = path.stem

        try:
            with path.open("r", encoding="utf-8") as f:
                save_data = json.load(f)

            # save_version 자동 태깅 및 마이그레이션
            save_data = migrate_save(save_data)

            payload = {
                "user_id": str(user_id),
                "save_data": save_data,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }

            db.table("user_saves").upsert(
                payload,
                on_conflict="user_id"
            ).execute()

            success += 1
            pet_name = save_data.get("pet", {}).get("name", "?")
            pet_level = save_data.get("pet", {}).get("level", "?")
            print(f"  ✅ {user_id} → {pet_name} (Lv.{pet_level})")

        except Exception as e:
            failed += 1
            print(f"  ❌ {user_id}: {e}")

    # 4단계: 결과 보고
    print("\n" + "=" * 60)
    print(f"🏁 마이그레이션 완료!")
    print(f"  ✅ 성공: {success}개")
    print(f"  ❌ 실패: {failed}개")
    print(f"  📦 백업: {BACKUP_DIR}")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 모든 유저 세이브가 성공적으로 Supabase에 이전되었습니다!")
        print("Supabase Dashboard → Table Editor → user_saves 에서 확인해 주세요.")
    else:
        print(f"\n⚠️ {failed}개 파일이 실패했습니다. 로그를 확인해 주세요.")


if __name__ == "__main__":
    main()
