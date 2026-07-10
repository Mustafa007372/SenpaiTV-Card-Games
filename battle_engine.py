"""
PvE jang tizimi (MVP).
Barcha hisob-kitob serverda — foydalanuvchi faqat "qaysi kartam bilan jang qilaman"
degan tanlovni yuboradi, natijani o'zi hech qachon hisoblamaydi.

PvP (real vaqtli o'yinchiga qarshi) F2/F3'da qo'shiladi — bu ancha murakkab
va sinxronizatsiya talab qiladi, MVP uchun shart emas.
"""
import random
from dataclasses import dataclass

from database.models import Card


@dataclass
class BattleResult:
    win: bool
    log: list[str]
    reward_gems: int
    exp_gained: int


# Oddiy bot dushmanlar — daraja qancha yuqori bo'lsa shuncha kuchli
ENEMY_TEMPLATES = [
    {"name": "Yovvoyi Slime", "atk": 15, "hp": 60, "spd": 10, "min_level": 1},
    {"name": "Soya Ninjasi", "atk": 25, "hp": 90, "spd": 20, "min_level": 3},
    {"name": "Ajdaho Bolasi", "atk": 40, "hp": 150, "spd": 15, "min_level": 6},
    {"name": "Qorong'u Ritsar", "atk": 55, "hp": 220, "spd": 25, "min_level": 10},
]


def pick_enemy(user_level: int) -> dict:
    eligible = [e for e in ENEMY_TEMPLATES if e["min_level"] <= user_level]
    return random.choice(eligible) if eligible else ENEMY_TEMPLATES[0]


def simulate_battle(card: Card, user_level: int) -> BattleResult:
    """Oddiy navbat-navbat jang simulyatsiyasi (turn-based, server-side)."""
    enemy = pick_enemy(user_level)

    player_hp = card.hp
    enemy_hp = enemy["hp"]
    log = [f"⚔️ {card.name} vs {enemy['name']}"]

    turn = 1
    # Kim tezroq (SPD) — birinchi zarba shu tomondan
    player_first = card.spd >= enemy["spd"]

    while player_hp > 0 and enemy_hp > 0 and turn <= 30:
        if player_first:
            enemy_hp -= max(1, card.atk - random.randint(0, 5))
            if enemy_hp <= 0:
                break
            player_hp -= max(1, enemy["atk"] - random.randint(0, 5))
        else:
            player_hp -= max(1, enemy["atk"] - random.randint(0, 5))
            if player_hp <= 0:
                break
            enemy_hp -= max(1, card.atk - random.randint(0, 5))
        turn += 1

    win = enemy_hp <= 0 and player_hp > 0

    if win:
        reward = random.randint(8, 20) + enemy["min_level"] * 2
        exp = 10 + enemy["min_level"] * 3
        log.append(f"✅ G'alaba! +{reward} gems, +{exp} exp")
    else:
        reward = 2  # yutqazsa ham ozgina tasalli mukofoti
        exp = 3
        log.append(f"❌ Mag'lubiyat. +{reward} gems (tasalli), +{exp} exp")

    return BattleResult(win=win, log=log, reward_gems=reward, exp_gained=exp)
