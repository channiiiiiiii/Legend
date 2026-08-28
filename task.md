# 🎮 다마고치(DAMAGOCHI) v18 「Supabase DB 이전 + Render 무료 배포 통합」 Task

- **작업 상태:** 코드 구현 완료 ✅ → Supabase Migration Push & Render 배포 대기
- **개발 환경:** Windows Local, Python Virtualenv (`C:/Users/wmwm1/OneDrive/Desktop/work/.venv/Scripts/python.exe`)
- **담당 에이전트:** 수석 비서 제니 (Jenny)

## 📌 핵심 목표
로컬 JSON 세이브 → Supabase JSONB 영구 저장 이전 + Render Web Service 24시간 무료 배포

## ✅ 완료 체크리스트

### 코드 구현 (STEP 7~15)
- [x] `save_backend.py` 구현 (JSON/Supabase 듀얼 백엔드)
- [x] `migrate_json_to_supabase.py` 구현 (일괄 이전 스크립트)
- [x] `discord_bot.py` ← `save_backend` 통합 연결
- [x] `load_token()` 환경변수 우선 로드 (DISCORD_TOKEN)
- [x] `get_or_create_user_pet()` → `load_user_save()` 교체
- [x] `save_user_pet()` → `save_user_save()` 교체
- [x] `save_version: 18` 자동 태깅
- [x] aiohttp `/health` 헬스체크 서버 내장
- [x] `requirements.txt` 생성
- [x] `.gitignore` 생성
- [x] `supabase/migrations/00001_create_user_saves.sql` 생성
- [x] 로컬 JSON 백엔드 통합 테스트 PASS

### Supabase & 배포 (STEP 1~6, 16~24)
- [ ] Supabase CLI 연결 (`supabase link`)
- [ ] `supabase db push` 테이블 생성
- [ ] JSON → Supabase 마이그레이션 실행
- [ ] 유저 세이브 데이터 검증
- [ ] GitHub Push
- [ ] Render Web Service 생성 & 환경변수 등록
- [ ] Discord Bot 온라인 확인
- [ ] Render 재배포 후 세이브 유지 확인
- [ ] UptimeRobot /health 5분 체크 설정
