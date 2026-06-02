import os
import re
import requests
import time
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT"
TARGET_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\INT"
URL = "http://127.0.0.1:1234/v1/chat/completions"

TARGET_FILES = [
    "Twk_InGameUI.int", "DLC07_Twk_UI.int", "DLC06_Twk_UI.int",
    "DLC06_Twk_UI_MainMenu.int", "Twk_UI_MainMenu.int",
    "GFxUI.int", "Twk_UI_MissionStats.int"
]

SYSTEM_PROMPT = """You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your goal is to translate the text while strictly adhering to the technical constraints of the Unreal Engine 3 UI system.

CRITICAL FORMATTING RULES (ANTI-SQUISH & WORD WRAPPING):
1. Thai language does not use spaces between words, which breaks the game's UI engine, causing text to be squished.
2. You MUST insert normal spaces ( ) between distinct Thai phrases, clauses, or logical chunks to assist the game's word-wrapping engine.
   - Good Example: "เพื่อประสบการณ์ที่ดีที่สุด เราขอแนะนำให้ติดตั้งเกม ลงในฮาร์ดไดรฟ์"
   - Bad Example (Squished): "เพื่อประสบการณ์ที่ดีที่สุดเราขอแนะนำให้ติดตั้งเกมลงในฮาร์ดไดรฟ์"
3. NEVER insert a space in the middle of a Thai word.
4. PRESERVE ORIGINAL PACING: Place the masked tags (e.g., [[T0]], [[T1]]) at the exact logical equivalent points in your Thai translation. These tags represent original line breaks or formatting. Do not move them to the end of the sentence if they were in the middle.
5. Output ONLY the translated Thai text.

CRITICAL GLOSSARY:
- Corvo Attano: คอร์โว อัตตาโน
- The Outsider: ดิ เอาท์ไซเดอร์
- Lord Regent: ผู้สำเร็จราชการ
- Blink: บลิงก์
- Dark Vision: เนตรมืด
- Bend Time: บิดเบือนเวลา
- Rune: รูน
- Bonecharm: เครื่องรางกระดูก
- Whale Oil: น้ำมันวาฬ
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

    tags = re.findall(r'`[^`]+`|<[^>]+>|%[sdif]|`[a-zA-Z]/`[a-zA-Z]|\\[nr]', original_text)
    masked_text = original_text
    for i, tag in enumerate(tags):
        masked_text = masked_text.replace(tag, '[[T{0}]]'.format(i))

    translated_text = translate_with_lmstudio(masked_text)

    translated_text = translated_text.strip('"')
    # Keep natural spacing - no space removal
    translated_text = translated_text.replace('ผม', 'ฉัน').replace('ครับ', '').replace('ค่ะ', '')

    for i, tag in enumerate(tags):
        translated_text = translated_text.replace('[[T{0}]]'.format(i), tag)

    if 'm_Description=' in line:
        return '{0}=(m_Description="{1}")\n'.format(key, translated_text)
    else:
        return '{0}="{1}"\n'.format(key, translated_text)

def execute_tier_1_final():
    print("="*60)
    print("MATRIX REPORT - เมทริกซ์รายงาน")
    print("="*60)
    print("[*] เริ่มปฏิบัติการแปล Tier 1: UI & Menus (V.1.2 - Ultimate Edition)")
    print("[*] เป้าหมาย: {0} ไฟล์".format(len(TARGET_FILES)))
    print("="*60)

    os.makedirs(TARGET_DIR, exist_ok=True)

    total_translated = 0
    total_skipped = 0

    for filename in TARGET_FILES:
        source_path = os.path.join(SOURCE_DIR, filename)
        target_path = os.path.join(TARGET_DIR, filename)

        if not os.path.exists(source_path):
            for root, _, files in os.walk(SOURCE_DIR):
                if filename in files:
                    source_path = os.path.join(root, filename)
                    break

        if not os.path.exists(source_path):
            print("[!] ไม่พบไฟล์ {0} ข้ามการทำงาน...".format(filename))
            continue

        source_lines, detected_encoding = read_file_safely(source_path)
        save_encoding = 'utf-16-le' if 'utf-16' in detected_encoding else 'utf-8-sig'

        start_line = 0
        file_mode = 'w'

        if os.path.exists(target_path):
            target_lines, _ = read_file_safely(target_path)
            start_line = len(target_lines)

            if start_line >= len(source_lines):
                print("[>] ข้ามไฟล์ {0} (แปลเสร็จสมบูรณ์แล้ว)".format(filename))
                total_skipped += start_line
                continue
            else:
                print("[!] พบการแปลค้างไว้ที่ {0} ({1}/{2} บรรทัด)".format(
                    filename, start_line, len(source_lines)))
                print("    >> แปลต่อจากจุดเดิม...")
                file_mode = 'a'
        else:
            print("\nกำลังเริ่มแปลไฟล์ใหม่: {0} (Format: {1}) ...".format(filename, detected_encoding))

        count = 0
        with open(target_path, file_mode, encoding=save_encoding) as f_out:
            for i in range(start_line, len(source_lines)):
                line = source_lines[i]
                translated_line = process_ue3_int_line(line)
                f_out.write(translated_line)
                f_out.flush()

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
    execute_tier_1_final()