# Matrix Workspace & File Categorization Scanner
# ให้เมทริกซ์วิเคราะห์โครงสร้างไฟล์ทั้งหมดใน Workspace

import os
import sys
import io
from collections import defaultdict

# Force UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"

def scan_and_categorize_files():
    print(f"[*] เมทริกซ์กำลังเริ่มวิเคราะห์โครงสร้างใน: {WORKSPACE_DIR}")
    
    if not os.path.exists(WORKSPACE_DIR):
        print(f"[!] ไม่พบโฟลเดอร์ {WORKSPACE_DIR} โปรดตรวจสอบว่าบอสนำไฟล์ 658 ไฟล์มาไว้ที่นี่แล้วหรือยัง")
        return

    categories = defaultdict(list)
    total_files = 0
    total_lines = 0

    keywords = {
        "UI & Menus": ["ui", "menu", "hud", "front-end", "tweak"],
        "Subtitles (Main Story)": ["subtitles", "vo", "dialog", "mission", "l_"],
        "Lore & Books": ["book", "note", "journal", "lore", "audiograph"],
        "Gameplay & Items": ["item", "weapon", "power", "bonecharm", "rune"],
        "System & Config": ["engine", "system", "game", "config", "default"]
    }

    for root, _, files in os.walk(WORKSPACE_DIR):
        for file in files:
            if file.lower().endswith('.int'):
                total_files += 1
                filepath = os.path.join(root, file)
                filename_lower = file.lower()
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines_count = sum(1 for line in f if line.strip() and not line.strip().startswith((';', '[', '//')))
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
                    categories["Others (Uncategorized)"].append((file, lines_count))

    print("\n" + "="*70)
    print("📊 MATRIX REPORT: File Categorization & Priority Analysis")
    print("="*70)
    print(f"📂 สแกนพบไฟล์ .INT ทั้งหมด: {total_files} ไฟล์")
    print(f"📝 ประมาณการบรรทัดข้อความที่ต้องแปล: ~{total_lines} บรรทัด\n")
    
    for cat, items in categories.items():
        cat_lines = sum(count for _, count in items)
        print(f"📌 หมวดหมู่: {cat} ({len(items)} ไฟล์ | รวม ~{cat_lines} บรรทัด)")
        
        sorted_items = sorted(items, key=lambda x: x[1], reverse=True)
        for i, (fname, lcount) in enumerate(sorted_items[:3]):
            print(f"    - {fname} ({lcount} บรรทัด)")
        if len(items) > 3:
            print(f"    ... และอื่นๆ อีก {len(items) - 3} ไฟล์")
        print("-" * 50)

if __name__ == "__main__":
    scan_and_categorize_files()