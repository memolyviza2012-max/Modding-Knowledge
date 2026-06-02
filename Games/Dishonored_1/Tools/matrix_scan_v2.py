# Matrix Scanner V.2 - สแกนและจัดหมวดหมู่ไฟล์ .INT ใน 01_source\INT

import os
import sys
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT"

def scan_and_categorize_files():
    print(f"[*] เมทริกซ์กำลังวิเคราะห์โครงสร้างใน: {SOURCE_DIR}")
    
    if not os.path.exists(SOURCE_DIR):
        print(f"[!] ข้อผิดพลาด: ไม่พบโฟลเดอร์ {SOURCE_DIR}")
        return

    categories = defaultdict(list)
    total_files = 0
    total_lines = 0

    keywords = {
        "1. UI & Menus (อินเทอร์เฟซและเมนู)": ["ui", "menu", "hud", "front-end", "tweak", "msg"],
        "2. Subtitles & Story (ซับไตเติลและเนื้อเรื่อง)": ["subtitles", "vo", "dialog", "mission", "l_", "conv"],
        "3. Lore & Books (จดหมายและหนังสือในเกม)": ["book", "note", "journal", "lore", "audiograph", "text"],
        "4. Gameplay & Items (ไอเทมและระบบเกม)": ["item", "weapon", "power", "bonecharm", "rune", "upgrade"],
        "5. System & Config (ระบบเอนจินเกม)": ["engine", "system", "game", "config", "default", "online"]
    }

    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith('.int'):
                total_files += 1
                filepath = os.path.join(root, file)
                filename_lower = file.lower()
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines_count = sum(1 for line in f if line.strip() and not line.strip().startswith((';', '[', '//')) and '=' in line)
                        total_lines += lines_count
                except:
                    lines_count = 0

                categorized = False
                for cat, keys in keywords.items():
                    if any(k in filename_lower for k in keys):
                        categories[cat].append((file, lines_count))
                        categorized = True
                        break
                
                if not categorized:
                    categories["6. Others (ไฟล์อื่นๆ ที่รอการระบุ)"].append((file, lines_count))

    print("\n" + "="*70)
    print("📊 MATRIX REPORT: File Categorization & Priority Analysis")
    print("="*70)
    print(f"📂 สแกนพบไฟล์ .INT ทั้งหมด: {total_files} ไฟล์")
    print(f"📝 ประมาณการบรรทัดที่ต้องแปล: ~{total_lines} บรรทัด\n")
    
    for cat in sorted(categories.keys()):
        items = categories[cat]
        if not items:
            continue
        cat_lines = sum(count for _, count in items)
        print(f"📌 {cat} ({len(items)} ไฟล์ | รวม ~{cat_lines} บรรทัด)")
        
        sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
        for i, (fname, lcount) in enumerate(sorted_items[:5]):
            print(f"    - {fname} ({lcount} บรรทัด)")
        if len(items) > 5:
            print(f"    ... และอื่นๆ อีก {len(items) - 5} ไฟล์")
        print("-" * 50)

if __name__ == "__main__":
    scan_and_categorize_files()