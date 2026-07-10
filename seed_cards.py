"""
Boshlang'ich kartalarni bazaga qo'shish uchun bir martalik skript.
Ishga tushirish: python seed_cards.py

Bu — MVP'ni tezda sinab ko'rish uchun. Ishlab chiqarishda admin
/admin -> Karta qo'shish orqali real kartalarni qo'shadi.
"""
import asyncio
from database.db import init_db, async_session
from database import crud

STARTER_CARDS = [
    dict(name="Naruto Uzumaki", anime="Naruto", rarity="rare", atk=45, hp=120, spd=35,
         ability_name="Rasengan", ability_desc="Kuchli spiral zarba beradi"),
    dict(name="Sakura Haruno", anime="Naruto", rarity="common", atk=25, hp=90, spd=30,
         ability_name="Shifo kuchi", ability_desc="Jang davomida HP tiklaydi"),
    dict(name="Luffy", anime="One Piece", rarity="epic", atk=60, hp=140, spd=40,
         ability_name="Gear Second", ability_desc="Tezlik va kuchni oshiradi"),
    dict(name="Zoro", anime="One Piece", rarity="rare", atk=55, hp=110, spd=32,
         ability_name="Uch qilich uslubi", ability_desc="Bir vaqtda uch marta zarba beradi"),
    dict(name="Goku", anime="Dragon Ball", rarity="legendary", atk=90, hp=200, spd=55,
         ability_name="Kamehameha", ability_desc="Massiv energiya to'lqini bilan zarba beradi"),
    dict(name="Vegeta", anime="Dragon Ball", rarity="epic", atk=80, hp=170, spd=48,
         ability_name="Final Flash", ability_desc="Yuqori zarar beruvchi energiya hujumi"),
    dict(name="Levi Ackerman", anime="Attack on Titan", rarity="legendary", atk=85, hp=150, spd=60,
         ability_name="ODM Gear", ability_desc="Aylanma tezkor hujumlar"),
    dict(name="Eren Yeager", anime="Attack on Titan", rarity="epic", atk=70, hp=180, spd=30,
         ability_name="Titan transformatsiya", ability_desc="Vaqtincha HP va ATK oshadi"),
    dict(name="Saitama", anime="One Punch Man", rarity="mythic", atk=999, hp=250, spd=45,
         ability_name="One Punch", ability_desc="Bir zarbada deyarli har qanday dushmanni yengadi"),
    dict(name="Rimuru Tempest", anime="Slime Datta Ken", rarity="legendary", atk=88, hp=210, spd=50,
         ability_name="Predator", ability_desc="Dushman qobiliyatlarini o'zlashtiradi"),
    dict(name="Genos", anime="One Punch Man", rarity="rare", atk=50, hp=130, spd=38,
         ability_name="Incineration Cannon", ability_desc="Olovli energiya zarbasi"),
    dict(name="Tanjiro Kamado", anime="Demon Slayer", rarity="rare", atk=48, hp=115, spd=42,
         ability_name="Suv nafasi", ability_desc="Aniq va tez qilich zarbalari"),
    dict(name="Nezuko Kamado", anime="Demon Slayer", rarity="epic", atk=58, hp=145, spd=50,
         ability_name="Qon jin texnikasi", ability_desc="Kuchli himoya va zarba beradi"),
    dict(name="Ainz Ooal Gown", anime="Overlord", rarity="mythic", atk=95, hp=230, spd=25,
         ability_name="Death magic", ability_desc="Yuqori darajali qora sehr bilan yo'q qiladi"),
    dict(name="Slime (Common)", anime="Generic", rarity="common", atk=15, hp=60, spd=15,
         ability_name="", ability_desc=""),
]


async def main():
    await init_db()
    async with async_session() as session:
        for data in STARTER_CARDS:
            card = await crud.create_card(session, **data)
            print(f"Qo'shildi: {card.name} ({card.rarity})")
    print(f"\nJami {len(STARTER_CARDS)} ta karta qo'shildi.")


if __name__ == "__main__":
    asyncio.run(main())
