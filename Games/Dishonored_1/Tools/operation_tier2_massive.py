import os
import re
import requests
import time
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT"
TARGET_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\INT"
URL = "http://127.0.0.1:1234/v1/chat/completions"

TIER_2_KEYWORDS = ["item", "weapon", "power", "bonecharm", "rune", "upgrade", "twk", "interactive", "pickup", "doors", "money", "movable"]
EXCLUDE_KEYWORDS = ["ui", "menu", "hud", "front-end", "msg", "gfx", "subtitles", "vo", "dialog", "mission", "book", "note", "journal", "lore", "audiograph"]

SYSTEM_PROMPT = """You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your current task is Tier 2: Gameplay, Items, Weapons, Powers, and In-world Interactables (Tweaks).

CRITICAL FORMATTING & PACING RULES:
1. Insert normal spaces ( ) between distinct Thai phrases to assist the game's word-wrapping engine. NEVER insert spaces inside a single word.
2. PRESERVE ORIGINAL PACING: Keep masked tags (e.g., [[T0]]) in their exact logical positions.
3. Keep action prompts VERY punchy and natural. (e.g., "Loot" -> "ขโมย", "Locked" -> "ถูกล็อก", "Requires Key" -> "ต้องใช้กุญแจ").
4. Output ONLY the translated Thai text. Do not add quotes unless they exist in the original.

CRITICAL GLOSSARY:
- Corvo Attano: คอร์โว อัตตาโน
- The Outsider: ดิ เอาท์ไซเดอร์
- Lord Regent: ผู้สำเร็จราชการ
- Overseer: ผู้คุมกฎ
- Blink: บลิงก์
- Dark Vision: เนตรมืด
- Bend Time: บิดเบือนเวลา
- Rune: รูน
- Bonecharm: เครื่องรางกระดูก
- Whale Oil: น้ำมันวาฬ
- Springrazor: สปริงเรเซอร์
- Wall of Light: กำแพงแสง
- Arc Pylon: เสาอาร์ก
- Dunwall: ดันวอลล์
- The Void: เดอะวอยด์
"""

def read_file_safely(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()
    if raw.startswith(b'\xff\xfe'):
        return raw.decode('utf-16-le').splitlines(True), 'utf-16-le'
    elif raw.startswith(b'\xfe\xff'):
        return raw.decode('utf-16-be').splitlines(True), 'utf-16-be'
    else:
        return raw.decode('utf-8-sig', errors='ignore').splitlines(True), 'utf-8-sig'

def translate_with_lmstudio(text):
    headers = {"Content-Type": "application/json"}
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Translate to Thai:\n{0}".format(text)}
        ],
        "temperature": 0.3,
        "max_tokens": 1000
    }
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("[!] API Error: {0} | กำลังพักเครื่อง 5 วินาที...".format(e))
        time.sleep(5)
        return text

def process_ue3_int_line(line):
    clean_line = line.strip()
    if not clean_line or (clean_line.startswith('[') and clean_line.endswith(']')) or clean_line.startswith((';', '//')):
        return line.rstrip('\r\n') + '\r\n'

    match = re.match(r'^([^=]+)=\(?[m_Description=]*"?(.*?)"?\)?\s*$', line)
    if not match:
        return line.rstrip('\r\n') + '\r\n'

    key, original_text = match.groups()
    if not original_text:
        return line.rstrip('\r\n') + '\r\n'

    tags = re.findall(r'`[^`]+`|<[^>]+>|%[sdif]|`[a-zA-Z]/`[a-zA-Z]|\\[nr]', original_text)
    masked_text = original_text
    for i, tag in enumerate(tags):
        masked_text = masked_text.replace(tag, '[[T{0}]]'.format(i))

    translated_text = translate_with_lmstudio(masked_text)

    translated_text = translated_text.strip('"').strip()
    translated_text = translated_text.replace('ผม', 'ฉัน').replace('ครับ', '').replace('ค่ะ', '')

    for i, tag in enumerate(tags):
        translated_text = translated_text.replace('[[T{0}]]'.format(i), tag)

    if 'm_Description=' in line:
        return '{0}=(m_Description="{1}")\r\n'.format(key, translated_text)
    else:
        return '{0}="{1}"\r\n'.format(key, translated_text)

def execute_tier_2():
    print("="*60)
    print("MATRIX REPORT - เมทริกซ์รายงาน")
    print("="*60)
    print("[*] ปฏิบัติการแปล Tier 2: The World (Massive Batch Edition)")
    print("[*] Shield Engine + Auto-Resume + Smart Pacing พร้อมทำงาน")
    print("="*60)

    os.makedirs(TARGET_DIR, exist_ok=True)

    target_files = []
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith('.int'):
                fname_lower = file.lower()
                if any(k in fname_lower for k in TIER_2_KEYWORDS) and not any(ex in fname_lower for ex in EXCLUDE_KEYWORDS):
                    target_files.append(os.path.join(root, file))

    print("[*] ตรวจพบเป้าหมาย {0} ไฟล์ พร้อมเดินเครื่อง...".format(len(target_files)))
    print("="*60)

    total_translated = 0
    total_skipped = 0
    total_errors = 0

    for source_path in sorted(target_files):
        filename = os.path.basename(source_path)
        target_path = os.path.join(TARGET_DIR, filename)

        source_lines, detected_encoding = read_file_safely(source_path)
        save_encoding = 'utf-16-le' if 'utf-16' in detected_encoding else 'utf-8-sig'

        start_line = 0
        file_mode = 'w'

        if os.path.exists(target_path):
            target_lines, _ = read_file_safely(target_path)
            start_line = len(target_lines)

            if start_line >= len(source_lines):
                print("[>] ข้าม {0} (แปลครบ 100%)".format(filename))
                total_skipped += start_line
                continue
            else:
                print("[!] Resume {0} ({1}/{2} บรรทัด)".format(
                    filename, start_line, len(source_lines)))
                file_mode = 'a'
        else:
            print("\n[+] เริ่มไฟล์ใหม่: {0} ({1} lines, {2})".format(
                filename, len(source_lines), save_encoding))

        count = 0
        errors = 0
        with open(target_path, file_mode, encoding=save_encoding, newline='') as f_out:
            for i in range(start_line, len(source_lines)):
                line = source_lines[i]
                translated_line = process_ue3_int_line(line)

                if not translated_line.endswith('\r\n') and translated_line.endswith('\n'):
                    translated_line = translated_line.replace('\n', '\r\n')

                f_out.write(translated_line)
                f_out.flush()
                count += 1

                if (i + 1) % 50 == 0:
                    print("  - {0} คืบหน้า: {1}/{2} บรรทัด".format(
                        filename, i + 1, len(source_lines)))

        print("[OK] {0} -> {1} lines translated".format(filename, count))
        total_translated += count

    print("\n" + "="*60)
    print("ปฏิบัติการ Tier 2 เสร็จสิ้น!")
    print("   แปลแล้ว: {0} บรรทัด".format(total_translated))
    print("   ข้าม (เสร็จแล้ว): {0} บรรทัด".format(total_skipped))
    print("   บันทึกที่: {0}".format(TARGET_DIR))
    print("="*60)

if __name__ == "__main__":
    execute_tier_2()