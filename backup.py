"""
Kunlik avtomatik backup skripti.

Reja hujjatidagi "Backup tizimi yo'q edi" degan kamchilikni to'ldiradi.
Cron yoki Task Scheduler orqali kuniga 1 marta ishga tushirish tavsiya
etiladi:

    0 3 * * * /usr/bin/python3 /path/to/telegram_card_bot/backup.py

Skript database.db faylining vaqt belgili nusxasini backups/ papkasiga
saqlaydi va oxirgi 30 kunlik nusxalarni saqlab, undan eskilarini avtomatik
o'chiradi (disk to'lib qolmasligi uchun).
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path

DB_PATH = Path("database.db")
BACKUP_DIR = Path("backups")
KEEP_LAST_N_BACKUPS = 30


def run_backup() -> None:
    if not DB_PATH.exists():
        print(f"XATO: {DB_PATH} topilmadi. Backup bekor qilindi.", file=sys.stderr)
        sys.exit(1)

    BACKUP_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = BACKUP_DIR / f"database_{timestamp}.db"

    shutil.copy2(DB_PATH, backup_filename)
    print(f"✅ Backup yaratildi: {backup_filename}")

    cleanup_old_backups()


def cleanup_old_backups() -> None:
    backups = sorted(BACKUP_DIR.glob("database_*.db"), key=lambda p: p.stat().st_mtime)
    if len(backups) > KEEP_LAST_N_BACKUPS:
        for old_backup in backups[: len(backups) - KEEP_LAST_N_BACKUPS]:
            old_backup.unlink()
            print(f"🗑️ Eski backup o'chirildi: {old_backup}")


if __name__ == "__main__":
    run_backup()
