"""
Karta rasmini PIL orqali generatsiya qiladi.

MVP versiyasi: oddiy rang-blok fon + ramka (gradient/holografik emas —
bu F2'da qo'shiladi, chunki gradient render vaqtni ko'p yeydi va
MVP bosqichida tezlik muhimroq).

Rarity ranglari — kelajakdagi F2 dizayn palitrasi bilan mos keladigan
qilib oldindan tanlangan, shunda F2'ga o'tishda faqat shu fayl almashtiriladi.
"""
import io
import os
from typing import TYPE_CHECKING
from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    # Faqat tip tekshirish uchun import qilinadi — image_generator moduli
    # database qatlamiga ishga tushish vaqtida bog'liq bo'lmasligi kerak
    # (masalan alohida test yoki boshqa xizmatda ishlatilishi mumkin).
    from database.models import Card

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")

CARD_W, CARD_H = 600, 840

RARITY_COLORS = {
    "common":    {"bg": (74, 74, 74), "border": (139, 139, 139), "label": "COMMON"},
    "rare":      {"bg": (30, 58, 138), "border": (96, 165, 250), "label": "RARE"},
    "epic":      {"bg": (91, 33, 182), "border": (192, 132, 252), "label": "EPIC"},
    "legendary": {"bg": (180, 83, 9),  "border": (252, 211, 77), "label": "LEGENDARY"},
    "mythic":    {"bg": (127, 29, 29), "border": (248, 113, 113), "label": "MYTHIC/UR"},
}

STAT_COLORS = {
    "atk": (239, 68, 68),
    "hp": (34, 197, 94),
    "spd": (250, 204, 21),
}


def _load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def render_card(card: "Card", character_image: Image.Image | None = None) -> bytes:
    """Karta uchun PNG rasm generatsiya qiladi, bytes qaytaradi
    (Telegramga to'g'ridan-to'g'ri yuborish uchun).
    """
    style = RARITY_COLORS.get(card.rarity, RARITY_COLORS["common"])

    img = Image.new("RGB", (CARD_W, CARD_H), style["bg"])
    draw = ImageDraw.Draw(img)

    border_width = 10
    draw.rectangle(
        [0, 0, CARD_W - 1, CARD_H - 1],
        outline=style["border"], width=border_width,
    )

    title_font = _load_font("title.ttf", 40)
    small_font = _load_font("regular.ttf", 24)
    stat_font = _load_font("stat.ttf", 32)

    # Rarity belgisi (yuqori chap burchak)
    draw.rectangle([20, 20, 180, 60], fill=style["border"])
    draw.text((30, 27), style["label"], font=small_font, fill=(20, 20, 20))

    # Personaj rasmi joyi (60% balandlik)
    img_area_h = int(CARD_H * 0.55)
    img_box = (30, 80, CARD_W - 30, 80 + img_area_h)
    if character_image:
        char = character_image.convert("RGB")
        char.thumbnail((img_box[2] - img_box[0], img_box[3] - img_box[1]))
        paste_x = img_box[0] + (img_box[2] - img_box[0] - char.width) // 2
        paste_y = img_box[1] + (img_box[3] - img_box[1] - char.height) // 2
        img.paste(char, (paste_x, paste_y))
    else:
        draw.rectangle(img_box, fill=(30, 30, 30))
        draw.text((img_box[0] + 20, img_box[1] + img_area_h // 2), "[ rasm yo'q ]",
                   font=small_font, fill=(150, 150, 150))

    y = img_box[3] + 15
    draw.text((30, y), card.name, font=title_font, fill=(255, 255, 255))
    y += 50
    draw.text((30, y), f"« {card.anime} »", font=small_font, fill=(210, 210, 210))
    y += 45

    # Statistika — 3 ustun
    col_w = (CARD_W - 60) // 3
    stats = [("⚔ ATK", card.atk, "atk"), ("❤ HP", card.hp, "hp"), ("⚡ SPD", card.spd, "spd")]
    for i, (label, value, key) in enumerate(stats):
        x = 30 + i * col_w
        draw.text((x, y), label, font=small_font, fill=(200, 200, 200))
        draw.text((x, y + 32), str(value), font=stat_font, fill=STAT_COLORS[key])

    y += 90
    if card.ability_name:
        draw.line([(30, y), (CARD_W - 30, y)], fill=style["border"], width=2)
        y += 15
        draw.text((30, y), card.ability_name, font=small_font, fill=(255, 255, 255))
        y += 30
        # tavsifni bir necha qatorga bo'lish (oddiy word-wrap)
        desc = card.ability_desc or ""
        words = desc.split()
        line = ""
        for w in words:
            test = f"{line} {w}".strip()
            if len(test) > 45:
                draw.text((30, y), line, font=small_font, fill=(180, 180, 180))
                y += 26
                line = w
            else:
                line = test
        if line:
            draw.text((30, y), line, font=small_font, fill=(180, 180, 180))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()
