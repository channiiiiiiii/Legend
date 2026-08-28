# -*- coding: utf-8 -*-
"""
🎨 10대 신수 × 4단계 성장 진화 디스코드 카드 40장 일괄 자동 렌더링 스크립트
Pillow 기반 1:1 정방형 600x600 고품질 RPG 프로필 카드 생성
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = r"C:\G_drive\.Game\DAMAGOCHI\assets"

SPECIES_METADATA = {
    "tiger": {
        "name_kr": "백호", "title": "신성한 뇌광의 맹수", "emoji": "🐯",
        "color_primary": (0, 210, 255), "color_secondary": (20, 40, 80),
        "stages": {
            1: {"name": "아기 백호", "desc": "Lv.1~39 [유년기]", "icon": "🐾", "aura": (100, 220, 255)},
            2: {"name": "질풍의 백호", "desc": "Lv.40~69 [성장기]", "icon": "⚡", "aura": (0, 200, 255)},
            3: {"name": "극의 백호", "desc": "Lv.70~98 [각성기]", "icon": "🌪️", "aura": (50, 150, 255)},
            4: {"name": "👑 태초의 백호신", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "lion": {
        "name_kr": "사자", "title": "황금빛 태양의 수호왕", "emoji": "🦁",
        "color_primary": (255, 170, 0), "color_secondary": (80, 40, 10),
        "stages": {
            1: {"name": "아기 사자", "desc": "Lv.1~39 [유년기]", "icon": "🐾", "aura": (255, 200, 100)},
            2: {"name": "태양의 사자", "desc": "Lv.40~69 [성장기]", "icon": "☀️", "aura": (255, 160, 0)},
            3: {"name": "황금왕 사자", "desc": "Lv.70~98 [각성기]", "icon": "👑", "aura": (255, 120, 0)},
            4: {"name": "👑 태초의 태양신", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "wolf": {
        "name_kr": "늑대", "title": "달빛을 가르는 암살자", "emoji": "🐺",
        "color_primary": (130, 180, 255), "color_secondary": (20, 25, 50),
        "stages": {
            1: {"name": "아기 늑대", "desc": "Lv.1~39 [유년기]", "icon": "🐾", "aura": (180, 210, 255)},
            2: {"name": "달빛 늑대", "desc": "Lv.40~69 [성장기]", "icon": "🌙", "aura": (120, 160, 255)},
            3: {"name": "그림자 늑대", "desc": "Lv.70~98 [각성기]", "icon": "🌫️", "aura": (80, 120, 255)},
            4: {"name": "👑 태초의 월식신", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "dragon": {
        "name_kr": "드래곤", "title": "뇌운과 수룡의 파동", "emoji": "🐉",
        "color_primary": (0, 230, 180), "color_secondary": (10, 50, 40),
        "stages": {
            1: {"name": "아기 드래곤", "desc": "Lv.1~39 [유년기]", "icon": "🐣", "aura": (100, 255, 200)},
            2: {"name": "청룡 드래곤", "desc": "Lv.40~69 [성장기]", "icon": "🌊", "aura": (0, 220, 160)},
            3: {"name": "용제 드래곤", "desc": "Lv.70~98 [각성기]", "icon": "🌩️", "aura": (0, 180, 255)},
            4: {"name": "👑 태초의 청룡신", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "phoenix": {
        "name_kr": "불사조", "title": "영원 불멸의 홍련 주작", "emoji": "🦅",
        "color_primary": (255, 60, 30), "color_secondary": (70, 15, 10),
        "stages": {
            1: {"name": "아기 불사조", "desc": "Lv.1~39 [유년기]", "icon": "🐣", "aura": (255, 150, 100)},
            2: {"name": "화염의 주작", "desc": "Lv.40~69 [성장기]", "icon": "🔥", "aura": (255, 60, 20)},
            3: {"name": "불멸의 주작", "desc": "Lv.70~98 [각성기]", "icon": "🌋", "aura": (255, 30, 60)},
            4: {"name": "👑 태초의 불사신", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "turtle": {
        "name_kr": "현무", "title": "금강석보다 단단한 대지철벽", "emoji": "🐢",
        "color_primary": (50, 220, 120), "color_secondary": (15, 50, 30),
        "stages": {
            1: {"name": "아기 현무", "desc": "Lv.1~39 [유년기]", "icon": "🐾", "aura": (130, 255, 170)},
            2: {"name": "대지의 현무", "desc": "Lv.40~69 [성장기]", "icon": "🛡️", "aura": (40, 200, 100)},
            3: {"name": "금강의 현무", "desc": "Lv.70~98 [각성기]", "icon": "💎", "aura": (0, 180, 140)},
            4: {"name": "👑 태초의 북방신", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "fox": {
        "name_kr": "구미호", "title": "천년 요기를 품은 영호", "emoji": "🦊",
        "color_primary": (255, 120, 220), "color_secondary": (60, 20, 60),
        "stages": {
            1: {"name": "아기 여우", "desc": "Lv.1~39 [유년기]", "icon": "🐾", "aura": (255, 180, 230)},
            2: {"name": "신비의 삼미호", "desc": "Lv.40~69 [성장기]", "icon": "💋", "aura": (255, 100, 200)},
            3: {"name": "천년 구미호", "desc": "Lv.70~98 [각성기]", "icon": "🔮", "aura": (220, 50, 255)},
            4: {"name": "👑 태초의 구천선녀", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "griffin": {
        "name_kr": "그리핀", "title": "창공을 가르는 폭풍의 제왕", "emoji": "🪽",
        "color_primary": (255, 200, 50), "color_secondary": (60, 45, 15),
        "stages": {
            1: {"name": "아기 그리핀", "desc": "Lv.1~39 [유년기]", "icon": "🐣", "aura": (255, 230, 130)},
            2: {"name": "폭풍 그리핀", "desc": "Lv.40~69 [성장기]", "icon": "🌪️", "aura": (255, 190, 30)},
            3: {"name": "천공 그리핀", "desc": "Lv.70~98 [각성기]", "icon": "⚡", "aura": (255, 160, 0)},
            4: {"name": "👑 태초의 천공신", "desc": "Lv.99+ [초월 오메가]", "icon": "✨", "aura": (255, 215, 0)}
        }
    },
    "kirin": {
        "name_kr": "기린", "title": "천상의 조화와 오로라 성수", "emoji": "🦄",
        "color_primary": (180, 140, 255), "color_secondary": (40, 20, 60),
        "stages": {
            1: {"name": "아기 기린", "desc": "Lv.1~39 [유년기]", "icon": "🐾", "aura": (220, 190, 255)},
            2: {"name": "성광의 기린", "desc": "Lv.40~69 [성장기]", "icon": "🌈", "aura": (180, 130, 255)},
            3: {"name": "천계의 기린", "desc": "Lv.70~98 [각성기]", "icon": "✨", "aura": (150, 80, 255)},
            4: {"name": "👑 태초의 천계신", "desc": "Lv.99+ [초월 오메가]", "icon": "👑", "aura": (255, 215, 0)}
        }
    },
    "bahamut": {
        "name_kr": "바하무트", "title": "암흑 물질과 특이점 파괴신", "emoji": "🐲",
        "color_primary": (190, 50, 255), "color_secondary": (30, 10, 45),
        "stages": {
            1: {"name": "아기 바하무트", "desc": "Lv.1~39 [유년기]", "icon": "🐣", "aura": (210, 120, 255)},
            2: {"name": "심연 바하무트", "desc": "Lv.40~69 [성장기]", "icon": "🌌", "aura": (170, 30, 255)},
            3: {"name": "멸세 바하무트", "desc": "Lv.70~98 [각성기]", "icon": "👁️", "aura": (140, 0, 230)},
            4: {"name": "👑 태초의 창세파괴신", "desc": "Lv.99+ [초월 오메가]", "icon": "🪐", "aura": (255, 215, 0)}
        }
    }
}

def create_card(sp_key: str, stage_num: int, output_path: str):
    sp_info = SPECIES_METADATA[sp_key]
    st_info = sp_info["stages"][stage_num]

    width, height = 600, 600
    img = Image.new("RGB", (width, height), (15, 18, 25))
    draw = ImageDraw.Draw(img)

    # 1. 배경 그라데이션 원형 오라
    primary = sp_info["color_primary"]
    aura = st_info["aura"]
    
    for r in range(250, 50, -5):
        alpha = int(40 * (1 - r / 250.0))
        color = (
            int(aura[0] * (r / 250.0) * 0.4),
            int(aura[1] * (r / 250.0) * 0.4),
            int(aura[2] * (r / 250.0) * 0.4)
        )
        draw.ellipse([300 - r, 280 - r, 300 + r, 280 + r], fill=color)

    # 2. 외곽 테두리 (골드/오라 듀얼 보더)
    border_color = (255, 215, 0) if stage_num == 4 else aura
    draw.rectangle([12, 12, width - 12, height - 12], outline=border_color, width=4)
    draw.rectangle([18, 18, width - 18, height - 18], outline=(40, 45, 60), width=2)
    
    # 3. 코너 장식
    c_len = 25
    corners = [(12, 12), (width - 12, 12), (12, height - 12), (width - 12, height - 12)]
    for cx, cy in corners:
        draw.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=border_color)

    # 폰트 로드 (윈도우 맑은 고딕 또는 기본 폰트)
    try:
        font_title = ImageFont.truetype("malgunbd.ttf", 36)
        font_sub = ImageFont.truetype("malgun.ttf", 22)
        font_stage = ImageFont.truetype("malgunbd.ttf", 26)
        font_emoji = ImageFont.truetype("seguiemj.ttf", 100)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_stage = ImageFont.load_default()
        font_emoji = ImageFont.load_default()

    # 4. 상단 헤더: 종족 이름 & 단계 배지
    header_text = f"{sp_info['name_kr']} · Stage {stage_num}"
    draw.text((300, 55), header_text, fill=border_color, font=font_stage, anchor="mm")
    
    # 5. 중앙 원형 포탈 & 대형 심볼
    draw.ellipse([175, 155, 425, 405], outline=aura, width=4)
    draw.ellipse([185, 165, 415, 395], outline=(60, 70, 95), width=2)
    
    # 이모지/심볼 렌더링
    symbol_text = sp_info["emoji"]
    draw.text((300, 280), symbol_text, fill=(255, 255, 255), font=font_emoji, anchor="mm")

    # 6. 하단 정보 카드 영역
    draw.rounded_rectangle([35, 435, width - 35, height - 35], radius=15, fill=(22, 26, 38), outline=border_color, width=2)
    
    # 폼 타이틀
    st_title = f"{st_info['icon']} {st_info['name']}"
    draw.text((300, 475), st_title, fill=(255, 255, 255), font=font_title, anchor="mm")
    
    # 레벨 및 설명
    st_desc = f"{st_info['desc']} | {sp_info['title']}"
    draw.text((300, 525), st_desc, fill=(180, 195, 215), font=font_sub, anchor="mm")

    img.save(output_path, "JPEG", quality=92)

def generate_all():
    count = 0
    for sp_k in SPECIES_METADATA.keys():
        sp_dir = os.path.join(ASSETS_DIR, sp_k)
        if not os.path.exists(sp_dir):
            os.makedirs(sp_dir)
            
        for stage in [1, 2, 3, 4]:
            out_file = os.path.join(sp_dir, f"{sp_k}_stage{stage}.jpg")
            create_card(sp_k, stage, out_file)
            count += 1
            print(f"[{count:02d}/40] 생성 완료: {sp_k} Stage {stage} -> {out_file}")
            
    print(f"\n🎉 총 {count}장의 10대 신수 4단계 성장 진화 카드가 성공적으로 생성되었습니다!")

if __name__ == "__main__":
    generate_all()
