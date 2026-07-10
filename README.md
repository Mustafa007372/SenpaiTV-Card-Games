# Karta-Kolleksiya Telegram Bot — MVP

Bu MVP fazasi uchun tayyorlangan boshlang'ich kod bazasi. `Loyiha_Rejasi_Tolik.md`
faylidagi FAZA 1 (MVP) funksiyalariga mos ravishda tuzilgan.

## Tuzilma

```
telegram_card_bot/
├── bot/
│   ├── config.py          — sozlamalar (token, admin ID'lar)
│   ├── database.py        — SQLite bazasi va yordamchi funksiyalar
│   ├── keyboards.py        — inline/reply klaviaturalar
│   ├── main.py             — botni ishga tushirish nuqtasi
│   └── handlers/
│       ├── start.py        — ro'yxatdan o'tish + referral
│       ├── daily.py        — kunlik gacha tortish
│       ├── collection.py   — kolleksiya + filtrlash
│       ├── pve.py          — PvE jang (server-side hisoblash)
│       ├── shop.py         — Stars → gems do'kon
│       └── admin.py        — karta qo'shish, user bloklash
├── backup.py               — kunlik avtomatik backup skripti
├── requirements.txt
└── .env.example
```

## O'rnatish

1. Python 3.11+ o'rnatilgan bo'lishi kerak
2. Kutubxonalarni o'rnating:
   ```
   pip install -r requirements.txt
   ```
3. `.env.example` faylini `.env` deb nusxalang va o'z BOT_TOKEN va ADMIN_IDS
   qiymatlaringizni kiriting
4. Botni ishga tushiring:
   ```
   python -m bot.main
   ```

## Backup

`backup.py` skriptini kuniga bir marta ishga tushirish uchun cron (Linux) yoki
Task Scheduler (Windows) sozlang. Masalan Linux'da:

```
0 3 * * * /usr/bin/python3 /path/to/telegram_card_bot/backup.py
```

Bu har kuni soat 03:00 da `database.db` faylining nusxasini `backups/` papkasiga
saqlaydi.

## Muhim eslatmalar

- Bu kod **MVP darajasi** — rejadagi FAZA 2/3 funksiyalari (PostgreSQL, Battle
  Pass, P2P bozor, auksion) hali kiritilmagan.
- Do'kon (shop.py) da Telegram Stars to'lov integratsiyasi uchun haqiqiy
  `provider_token` va invoice sozlamalari to'ldirilishi kerak — hozircha
  struktura va oqim (flow) tayyor, lekin siz o'z Stars sozlamalaringizni
  qo'shishingiz kerak.
- Har bir foydalanuvchi harakati server tomonida tekshiriladi (client
  ma'lumotiga ishonilmaydi) — bu cheat/firibgarlikning oldini olish uchun.
