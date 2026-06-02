import os
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT"

TIER_2_KEYWORDS = ["item", "weapon", "power", "bonecharm", "rune", "upgrade", "twk", "interactive", "pickup", "doors", "money", "movable"]

EXCLUDE_KEYWORDS = ["ui", "menu", "hud", "front-end", "msg", "gfx", "subtitles", "vo", "dialog", "mission", "book", "note", "journal", "lore", "audiograph"]

def scan_tier_2_files():
    print("="*60)
    print("MATRIX REPORT - เมทริกซ์รายงาน")
    print("="*60)
    print("[*] สแกนเป้าหมาย Tier 2 (Gameplay & Items)")

    tier_2_files = []
    total_lines = 0

    if not os.path.exists(SOURCE_DIR):
        print("[!] ไม่พบโฟลเดอร์: {0}".format(SOURCE_DIR))
        return

    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith('.int'):
                filename_lower = file.lower()

                if any(k in filename_lower for k in TIER_2_KEYWORDS) and not any(ex in filename_lower for ex in EXCLUDE_KEYWORDS):
                    filepath = os.path.join(root, file)

                    try:
                        with open(filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
                            lines_count = sum(1 for line in f if '=' in line and not line.strip().startswith((';', '[')))

                        if lines_count > 0:
                            tier_2_files.append((file, lines_count))
                            total_lines += lines_count
                    except Exception as e:
                        print("[!] ผิดพลาด: {0} - {1}".format(file, e))

    tier_2_files.sort(key=lambda x: x[1], reverse=True)

    print("")
    print("="*60)
    print("รายชื่อไฟล์เป้าหมาย Tier 2 (Gameplay & World Items)")
    print("="*60)

    if not tier_2_files:
        print("ไม่พบไฟล์ที่ตรงกับเงื่อนไข Tier 2")
    else:
        print("พบไฟล์เป้าหมายทั้งหมด: {0} ไฟล์".format(len(tier_2_files)))
        print("รวมปริมาณงานที่ต้องแปล: ~{0} บรรทัด".format(total_lines))
        print("")
        print("Top 10 ไฟล์ที่ใหญ่ที่สุด:")
        for i, (fname, cnt) in enumerate(tier_2_files[:10], 1):
            print("  {0}. {1} ({2} บรรทัด)".format(i, fname, cnt))

        if len(tier_2_files) > 10:
            print("  ... และไฟล์ขนาดเล็กอื่นๆ อีก {0} ไฟล์".format(len(tier_2_files) - 10))

    print("="*60)

if __name__ == "__main__":
    scan_tier_2_files()