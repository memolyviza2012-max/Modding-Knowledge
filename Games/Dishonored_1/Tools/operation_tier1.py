import os
import re
import requests
import time
import sys

# Force UTF-8 stdout
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# Paths
SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT"
TARGET_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\INT"
URL = "http://127.0.0.1:1234/v1/chat/completions"

TARGET_FILES = [
    "Twk_InGameUI.int", "DLC07_Twk_UI.int", "DLC06_Twk_UI.int",
    "DLC06_Twk_UI_MainMenu.int", "Twk_UI_MainMenu.int",
    "GFxUI.int", "Twk_UI_MissionStats.int"
]

SYSTEM_PROMPT = """You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your current task is translating Tier 1: UI, Menus, HUD, and System Messages.
Guidelines:
1. Keep the translation extremely concise, short, and clear.
2. Use standard gaming terminology in Thai (e.g., "บันทึกเกม" for Save).
3. Output ONLY the translated Thai text. Do not add quotes unless they exist in the original.

CRITICAL GLOSSARY & TERMINOLOGY (DO NOT TRANSLATE BLINDLY):
- Corvo Attano: คอร์โว อัตตาโน
- The Outsider: ดิ เอาท์ไซเดอร์
- Lord Regent: ผู้สำเร็จราชการ
- High Overseer: ผู้คุมกฎสูงสุด
- Blink: บลิงก์
- Dark Vision: เนตรมืด
- Bend Time: บิดเบือนเวลา
- Rune: รูน
- Bonecharm: เครื่องรางกระดูก
- Whale Oil: น้ำมันวาฬ
- Dunwall: ดันวอลล์
- The Void: เดอะวอยด์
"""

os.makedirs(TARGET_DIR, exist_ok=True)

def translate_with_lmstudio(text):
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Translate to Thai:\n{text}"}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    try:
        response = requests.post(URL, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("[!] API Error: {0}".format(e))
        time.sleep(2)
        return text

def process_ue3_int_line(line):
    clean_line = line.strip()
    if not clean_line or (clean_line.startswith('[') and clean_line.endswith(']')) or clean_line.startswith((';', '//')):
        return line

    match = re.match(r'^([^=]+)=\(?[m_Description=]*"?(.*?)"?\)?\s*$', line)
    if not match:
        return line

    key, original_text = match.groups()
    if not original_text:
        return line

    # THE SHIELD: mask tags
    tags = re.findall(r'`[^`]+`|<[^>]+>|%[sdif]|\\[nr]', original_text)
    masked_text = original_text
    for i, tag in enumerate(tags):
        masked_text = masked_text.replace(tag, '{[[T{0}]]}'.format(i))

    # Translate
    translated_text = translate_with_lmstudio(masked_text)

    # Post-processing
    translated_text = translated_text.strip('"')
    translated_text = re.sub(r'(?<=[ก-๙])\s+(?=[ก-๙])', '', translated_text)
    translated_text = translated_text.replace('ผม', 'ฉัน').replace('ครับ', '').replace('ค่ะ', '')

    # Unmask
    for i, tag in enumerate(tags):
        translated_text = translated_text.replace('{[[T{0}]]}'.format(i), tag)

    if 'm_Description=' in line:
        return '{0}=(m_Description="{1}")\n'.format(key, translated_text)
    else:
        return '{0}="{1}"\n'.format(key, translated_text)

# ==========================================
# TRUE AUTO-RESUME SYSTEM
# ==========================================

def execute_tier_1():
    print("="*60)
    print("MATRIX REPORT - เมทริกซ์รายงาน")
    print("="*60)
    print("[*] เริ่มปฏิบัติการแปล Tier 1: UI & Menus (พร้อมระบบ True Auto-Resume)")
    print("[*] เป้าหมาย: {0} ไฟล์".format(len(TARGET_FILES)))
    print("="*60)

    os.makedirs(TARGET_DIR, exist_ok=True)

    total_translated = 0
    total_skipped = 0

    for filename in TARGET_FILES:
        source_path = os.path.join(SOURCE_DIR, filename)
        target_path = os.path.join(TARGET_DIR, filename)

        # ค้นหาไฟล์ใน sub-folder หากไม่เจอในโฟลเดอร์หลัก
        if not os.path.exists(source_path):
            for root, _, files in os.walk(SOURCE_DIR):
                if filename in files:
                    source_path = os.path.join(root, filename)
                    break

        if not os.path.exists(source_path):
            print("[!] ไม่พบไฟล์ {0} ข้ามการทำงาน...".format(filename))
            continue

        # อ่านไฟล์ต้นฉบับเตรียมไว้
        with open(source_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
            source_lines = f.readlines()

        start_line = 0
        file_mode = 'w'  # โหมดสร้างไฟล์ใหม่

        # ระบบ TRUE RESUME: เช็คว่ามีไฟล์แปลค้างไว้หรือไม่
        if os.path.exists(target_path):
            with open(target_path, 'r', encoding='utf-8-sig', errors='ignore') as f_check:
                translated_lines = f_check.readlines()
                start_line = len(translated_lines)

            if start_line >= len(source_lines):
                print("[>] ข้ามไฟล์ {0} (แปลเสร็จสมบูรณ์ 100% แล้ว)".format(filename))
                total_skipped += start_line
                continue
            else:
                print("[!] พบการแปลค้างไว้ที่ {0} (เสร็จไปแล้ว {1}/{2} บรรทัด)".format(
                    filename, start_line, len(source_lines)))
                print("    >> ระบบจะทำการแปลต่อจากจุดเดิม...")
                file_mode = 'a'  # เปลี่ยนเป็นโหมดเขียนต่อท้าย (Append)
        else:
            print("\nกำลังเริ่มแปลไฟล์ใหม่: {0} ...".format(filename))

        # เริ่มกระบวนการแปล (ต่อจาก start_line ที่หาได้)
        count = 0
        with open(target_path, file_mode, encoding='utf-8-sig') as f_out:
            for i in range(start_line, len(source_lines)):
                line = source_lines[i]
                translated_line = process_ue3_int_line(line)
                f_out.write(translated_line)
                f_out.flush()  # เซฟลงฮาร์ดดิสก์บรรทัดต่อบรรทัด

                if (i + 1) % 10 == 0:
                    print("  - เซฟความคืบหน้า: {0}/{1} บรรทัด".format(i + 1, len(source_lines)))
                count += 1

        print("[OK] {0} -> {1} lines translated".format(filename, count))
        total_translated += count

    print("\n" + "="*60)
    print("ปฏิบัติการ Tier 1 เสร็จสิ้น!")
    print("   รวม: {0} บรรทัดแปลแล้ว".format(total_translated))
    print("   ข้าม (เสร็จแล้ว): {0} บรรทัด".format(total_skipped))
    print("   บันทึกที่: {0}".format(TARGET_DIR))
    print("="*60)

if __name__ == "__main__":
    execute_tier_1()