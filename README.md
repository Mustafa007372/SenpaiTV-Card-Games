# Anime TCG Bot — FAZA 1 (MVP)

Telegram orqali anime kartalar yig'ish, kunlik gacha, PvE jang va Stars orqali
gems sotib olish imkonini beruvchi bot.

## Nima bor (F1 — MVP)

- ✅ Ro'yxatdan o'tish + referral tizimi (deep link orqali)
- ✅ Kunlik bonus (streak bilan o'sib boruvchi)
- ✅ Gacha (karta tortish) — ehtimollik FAQAT serverda hisoblanadi
- ✅ Kolleksiya ko'rish (rarity bo'yicha filtr, PIL orqali generatsiya qilingan karta rasmi)
- ✅ Oddiy PvE jang (server-side hisob-kitob)
- ✅ Do'kon — Telegram Stars orqali gems sotib olish
- ✅ Support — foydalanuvchi/admin aloqasi
- ✅ Admin panel — statistika, foydalanuvchi boshqaruvi, karta qo'shish, broadcast
- ✅ Rate limiting (spam himoyasi)
- ✅ Atomic transaction (gems balansi hech qachon yarim holatda qolmaydi)

## Nima yo'q (keyingi fazalarga qoldirilgan — ataylab)

- ❌ P2P savdo/bozor, auksion (F3 — eng xavfli qism, kod pishgandan keyin)
- ❌ Real vaqtli PvP (F2/F3 — murakkab sinxronizatsiya talab qiladi)
- ❌ Holografik/gradient karta dizayni (F2 — hozircha oddiy rang-blok)
- ❌ Battle Pass, reyting jadvali (F2)
- ❌ PostgreSQL (F2'da o'tiladi — hozir SQLite yetarli)

## O'rnatish

```bash
cd tcg_bot
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env faylni oching va BOT_TOKEN, ADMIN_IDS ni to'ldiring
```

## Shriftlar (ixtiyoriy, lekin tavsiya etiladi)

`image_generator/fonts/README.txt` faylidagi ko'rsatmaga qarang.
Shriftlar bo'lmasa ham bot ishlayveradi (default shrift bilan).

## Boshlang'ich kartalarni qo'shish

```bash
python seed_cards.py
```

Bu 15 ta test karta qo'shadi (turli rarity va anime'lardan). Ishlab
chiqarishda buni o'chirib, `/admin` panel orqali real kartalarni qo'shing.

## Ishga tushirish

```bash
python main.py
```

## Railway'ga deploy qilish

1. Loyihani GitHub'ga push qiling (`.env` faylni **hech qachon** qo'shmang — `.gitignore`da bor)
2. Railway'da yangi project yarating, GitHub repo'ni ulang
3. Railway "Variables" bo'limida `BOT_TOKEN` va `ADMIN_IDS` ni kiriting
4. Start command: `python main.py` (yoki avval `python seed_cards.py && python main.py`)

## Keyingi qadam (F2 rejasi)

MVP ishga tushib, birinchi real foydalanuvchilar va gems xaridlari
kelganda — quyidagilar qo'shiladi:

1. PostgreSQL'ga migratsiya (faqat `DATABASE_URL` o'zgaradi, kod deyarli o'zgarmaydi)
2. To'liq vizual dizayn (gradient, holografik UR kartalar)
3. Battle Pass va mavsumiy tizim
4. Reyting jadvali (global/do'stlar)
5. Statistika dashboard kengaytirilgan ko'rinishda

F3 (market/savdo) faqat F2 barqaror ishlagandan va foydalanuvchi bazasi
yetarli o'sgandan keyin boshlanadi — chunki bu eng yuqori moliyaviy
xavf tug'diruvchi qism.
