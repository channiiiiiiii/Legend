# -*- coding: utf-8 -*-
"""
🎲 DAMAGOCHI Minigames Module
놀아주기 & 코인/경험치 파밍을 위한 미니게임 3종 세트
"""

import random
import time

# 잡지식: 가위바위보의 역사는 중국 한나라 시절 '수시령(手勢令)'에서 유래하여 전 세계로 퍼졌답니다!

class Minigames:
    @staticmethod
    def play_number_guess(pet) -> tuple[int, int, str]:
        """
        1) 숫자 업다운 (High-Low) 게임
        반환: (획득 코인, 획득 경험치, 결과 메시지)
        """
        target = random.randint(1, 50)
        attempts = 5
        print("\n" + "="*45)
        print("🎯 [미니게임] 1~50 숫자 맞추기 (기회: 5번)")
        print("="*45)

        for i in range(1, attempts + 1):
            try:
                raw = input(f"[{i}/{attempts}번째 시도] 숫자를 입력하세요 (1~50): ").strip()
                if not raw.isdigit():
                    print("⚠️ 올바른 숫자를 입력해주세요!")
                    continue
                guess = int(raw)
                
                if guess == target:
                    coins = (6 - i) * 60 + 50
                    exp = (6 - i) * 20 + 20
                    pet.happiness = min(100, pet.happiness + 25)
                    return coins, exp, f"🎉 정답입니다! [{target}]을(를) {i}번째에 맞췄습니다! (보너스 코인 획득!)"
                elif guess < target:
                    print("📈 UP! 더 큰 숫자입니다!")
                else:
                    print("📉 DOWN! 더 작은 숫자입니다!")
            except ValueError:
                continue
        
        pet.happiness = min(100, pet.happiness + 10)
        return 30, 10, f"😢 아쉽게도 기회를 모두 소진했습니다. 정답은 [{target}]이었습니다!"

    @staticmethod
    def play_rock_paper_scissors(pet) -> tuple[int, int, str]:
        """
        2) 펫과의 가위바위보 대결 (3전 2선승제)
        """
        choices = {"1": "가위 ✌️", "2": "바위 ✊", "3": "보 🖐️"}
        options = ["가위 ✌️", "바위 ✊", "보 🖐️"]
        
        user_wins = 0
        pet_wins = 0
        
        print("\n" + "="*45)
        print(f"✌️✊🖐️ [미니게임] {pet.name}와(과)의 가위바위보 대결 (3전 2선승)")
        print("="*45)
        
        round_cnt = 1
        while user_wins < 2 and pet_wins < 2 and round_cnt <= 5:
            print(f"\n--- Round {round_cnt} (현재 스코어 | 선배님: {user_wins} vs {pet.name}: {pet_wins}) ---")
            print("1. 가위 ✌️ | 2. 바위 ✊ | 3. 보 🖐️")
            u_choice = input("선택 (1~3): ").strip()
            if u_choice not in choices:
                print("⚠️ 1, 2, 3 중에서 골라주세요!")
                continue
            
            u_hand = choices[u_choice]
            p_hand = random.choice(options)
            
            print(f"선배님: {u_hand}  vs  {pet.name}: {p_hand}")
            
            if u_hand == p_hand:
                print("🤝 무승부! 다시 승부합니다.")
            elif (u_hand.startswith("가위") and p_hand.startswith("보")) or \
                 (u_hand.startswith("바위") and p_hand.startswith("가위")) or \
                 (u_hand.startswith("보") and p_hand.startswith("바위")):
                print("🔥 선배님 승리!")
                user_wins += 1
            else:
                print(f"🐾 {pet.name} 승리!")
                pet_wins += 1
            
            round_cnt += 1
            time.sleep(0.5)

        if user_wins >= 2:
            pet.happiness = min(100, pet.happiness + 30)
            return 200, 50, f"🏆 대승리! {pet.name}이(가) 패배를 인정하며 박수를 칩니다! 👏"
        elif pet_wins >= 2:
            pet.happiness = min(100, pet.happiness + 20)
            return 80, 25, f"🐾 {pet.name}이(가) 승리하여 기뻐서 펄쩍펄쩍 뜁니다! 😆"
        else:
            return 50, 15, "🤝 박빙의 무승부 명승부였습니다!"

    @staticmethod
    def play_quiz(pet) -> tuple[int, int, str]:
        """
        3) 제니의 두뇌 풀가동 퀴즈
        """
        quizzes = [
            {
                "q": "파이썬에서 리스트의 길이를 반환하는 내장 함수는?",
                "choices": ["1. count()", "2. size()", "3. len()", "4. length()"],
                "ans": "3"
            },
            {
                "q": "다마고치 캐릭터의 가장 높은 최종 진화 단계는?",
                "choices": ["1. 어덜트", "2. 베이비", "3. 틴", "4. 초월체(Legend)"],
                "ans": "4"
            },
            {
                "q": "CPU의 핵심 역할이 아닌 것은 무엇일까요?",
                "choices": ["1. 연산 장치", "2. 영구 대용량 파일 저장", "3. 제어 장치", "4. 명령어 해석"],
                "ans": "2"
            },
            {
                "q": "개발자 수석 비서 제니가 선배님을 부르는 호칭은?",
                "choices": ["1. 선배님", "2. 사장님", "3. 대장님", "4. 부장님"],
                "ans": "1"
            },
            {
                "q": "파이썬에서 불변(Immutable) 시퀀스 자료형은?",
                "choices": ["1. List", "2. Tuple", "3. Set", "4. Dict"],
                "ans": "2"
            }
        ]
        
        quiz = random.choice(quizzes)
        print("\n" + "="*45)
        print("💡 [미니게임] 제니의 두뇌 풀가동 상식 퀴즈!")
        print("="*45)
        print(f"질문: {quiz['q']}\n")
        for ch in quiz["choices"]:
            print(f"  {ch}")
        
        ans = input("\n정답 번호 입력 (1~4): ").strip()
        if ans == quiz["ans"]:
            pet.happiness = min(100, pet.happiness + 30)
            return 150, 60, "🧠 천재만재 선배님 정답! 지능 스탯 대폭 상승 효과!"
        else:
            pet.happiness = min(100, pet.happiness + 10)
            return 30, 15, f"앗! 오답입니다ㅠㅠ 정답은 {quiz['ans']}번이었습니다!"
