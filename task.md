# 🎮 다마고치(DAMAGOCHI) v18 「Supabase DB 이전 + Render 무료 배포 통합」 Task

- **작업 상태:** GitHub Push 완료 ✅ (Render 배포 및 UptimeRobot 등록 단계)
- **개발 환경:** Windows Local, Python Virtualenv (`C:/Users/wmwm1/OneDrive/Desktop/work/.venv/Scripts/python.exe`)
- **담당 에이전트:** 수석 비서 제니 (Jenny)
- **GitHub 저장소:** `https://github.com/channiiiiiiii/Legend`

## 📌 핵심 목표
로컬 JSON 세이브 → Supabase JSONB 영구 저장 이전 + Render Web Service 24시간 무료 배포

## 🚨 2026-08-29 레이드 Discord Interaction 긴급 수정
- [x] 사용자 ID 검사 직후 `interaction.response.defer()` ACK 전송
- [x] 레이드 저장을 `asyncio.to_thread(save_user_pet, ...)`로 이벤트 루프에서 분리
- [x] 일반/승리/패배 턴 모두 상태 정산 완료 후 저장 1회로 단일화
- [x] defer 이후 `interaction.edit_original_response(...)`만 사용
- [x] 무시되던 예외를 traceback 로그와 ephemeral 오류 응답으로 교체
- [x] 지정 Home 가상환경 `py_compile` 구문 검사 통과
- [ ] 기존 `test_damagochi.py` 회귀 테스트 통과 (장비 제작 단계의 기존 `assert suc` 실패)

## 🛡️ 2026-08-29 new.md 안정성 P0→P2
- [x] P0 Supabase 조회 실패와 정상 row 없음 분리, 신규 유저 오판/UPSERT 차단
- [x] P0 버튼·던전·레이드·DB Slash 명령 ACK 선처리 및 동기 DB I/O 스레드 분리
- [x] P0 레이드 턴당 최종 저장 1회 AST 검증
- [x] P1 Supabase UPSERT 3회 제한 재시도 및 최종 실패 사용자 안내
- [x] P1 핵심 운영 경로 광범위 예외 삼키기 제거
- [x] P1 사용자별 재진입 Lock으로 상태변경 전체 직렬화
- [x] P1 Supabase 운영의 `pet_storage.json` 사용 차단 및 `meta["hall_of_fame"]` 저장
- [x] P1 단계별 v17→v18 마이그레이션 및 미래 버전 로드 차단
- [x] P2 시작 전 Supabase 설정 검증 및 health 상태 분리
- [x] `deploy.ps1` 지정 Python·필수 9개 모듈 preflight 강화
- [x] 각 단계별 `py_compile` 통과

## 💎 2026-09-01 신규 파밍 시스템 안정성 구현
- [x] 보물/방어구 각인 3슬롯, 옵션 중복 방지, 잠금별 1/4/9개 비용 구현
- [x] 난이도별 각인석 및 Lv.1~6 보석 드랍·하위 난이도 감쇠 구현
- [x] 동일 보석 2개 확정 합성, Lv.10 상한, 장착 절대 스탯·CP 반영
- [x] 성장 Stage 1~4 스킬 배율과 역할별 성장 방향 연결
- [x] Discord 파밍 관리 UI, interaction 선 ACK, 저장 실패 인벤토리 롤백 구현
- [x] 단계별 및 전체 `py_compile`, 핵심 도메인 테스트, 봇 import 검증 통과
- [ ] Render 배포 및 운영 봇 확인 (이번 작업 범위에서 미실행)

## ✅ 완료 체크리스트

### 코드 구현 및 DB 연동 (STEP 1~17)
- [x] `save_backend.py` 구현 (JSON/Supabase 듀얼 백엔드)
- [x] `migrate_json_to_supabase.py` 구현 (일괄 이전 스크립트)
- [x] `discord_bot.py` ← `save_backend` 통합 연결
- [x] `load_token()` 환경변수 우선 로드 (DISCORD_TOKEN)
- [x] `get_or_create_user_pet()` → `load_user_save()` 교체
- [x] `save_user_pet()` → `save_user_save()` 교체
- [x] `save_version: 18` 자동 태깅
- [x] aiohttp `/health` 헬스체크 서버 내장 (Render 무중단 대응)
- [x] `requirements.txt` 생성
- [x] `.gitignore` 생성 (시크릿, 세이브, node_modules 완벽 격리)
- [x] `supabase/migrations/00001_create_user_saves.sql` 생성
- [x] Supabase `user_saves` 테이블 연결 및 마이그레이션 실행 완료 (2명 유저 세이브 100% 이전)
- [x] Supabase 백엔드 E2E 통합 테스트 PASS
- [x] GitHub 원격 저장소(`main` 브랜치) Push 완료 (`f4fde1c`)

### Render 배포 및 모니터링 (STEP 18~24)
- [ ] Render Web Service 생성 (`https://dashboard.render.com`)
- [ ] Render 환경변수 4종 등록 (`DISCORD_TOKEN`, `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, `SAVE_BACKEND`)
- [ ] Render Deploy 시작 및 봇 온라인 확인
- [ ] UptimeRobot `/health` 5분 간격 Keep-Alive 등록
