import os
import re
import requests
import time
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT"
TARGET_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\INT"
URL = "http://127.0.0.1:1234/v1/chat/completions"

# [IMPORTANT] Exclude GFxUI.int - it controls ALL game fonts. Translating it will destroy the game.
TARGET_FILES = [
    "Twk_InGameUI.int", "DLC07_Twk_UI.int", "DLC06_Twk_UI.int",
    "DLC06_Twk_UI_MainMenu.int", "Twk_UI_MainMenu.int",
    "Twk_UI_MissionStats.int"
]

SYSTEM_PROMPT = """You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your goal is to translate the text while strictly adhering to the technical constraints of the Unreal Engine 3 UI system.

CRITICAL FORMATTING RULES (ANTI-SQUISH & WORD WRAPPING):
1. Thai language does not use spaces between words, which breaks the game's UI engine, causing text to be squished.
2. You MUST insert normal spaces ( ) between distinct Thai phrases, clauses, or logical chunks to assist the game's word-wrapping engine.
   - Example: "เพื่อประสบการณ์ที่ดีที่สุด เราขอแนะนำให้ติดตั้งเกม ลงในฮาร์ดไดรฟ์"
3. NEVER insert a space in the middle of a Thai word.
4. PRESERVE ORIGINAL PACING: Place the masked tags (e.g., [[T0]], [[T1]]) at the exact logical equivalent points in your Thai translation.
5. Output ONLY the translated Thai text. Do not add quotes unless they exist in the original.

CRITICAL GLOSSARY:
- Corvo Attano: คอร์โว อัตตาโน
- The Outsider: ดิ เอาท์ไซเดอร์
- Lord Regent: ผู้สำเร็จราชการ
- Blink: บลิงก์
- Dark Vision: เนตรมืด
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

    # [PATCH V1.3]: .rstrip('\r\n') prevents double-line-ending bug
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

def run_translation():
    print("="*60)
    print("MATRIX REPORT - เมทริกซ์รายงาน")
    print("="*60)
    print("[*] ปฏิบัติการ: Clean & Re-Translate (V.1.4)")
    print("[*] GFxUI.int = SKIPPED (font control file - DO NOT TRANSLATE)")
    print("[*] เป้าหมาย: {0} ไฟล์ (ไม่รวม GFxUI)".format(len(TARGET_FILES)))
    print("="*60)

    os.makedirs(TARGET_DIR, exist_ok=True)

    total_translated = 0

    for filename in TARGET_FILES:
        source_path = ""
        for root, _, files in os.walk(SOURCE_DIR):
            if filename in files:
                source_path = os.path.join(root, filename)
                break

        if not source_path:
            print("[!] ไม่พบไฟล์ต้นฉบับ {0} ข้าม...".format(filename))
            continue

        print("\nกำลังประมวลผล: {0}".format(filename))
        source_lines, encoding = read_file_safely(source_path)
        save_encoding = 'utf-16-le' if 'utf-16' in encoding else 'utf-8-sig'
        print("  - Format: {0} | บรรทัดทั้งหมด: {1}".format(save_encoding, len(source_lines)))

        target_path = os.path.join(TARGET_DIR, filename)
        count = 0
        with open(target_path, 'w', encoding=save_encoding, newline='') as f_out:
            for i, line in enumerate(source_lines):
                translated_line = process_ue3_int_line(line)
                f_out.write(translated_line)
                f_out.flush()
                if (i + 1) % 20 == 0:
                    print("  - สำเร็จ {0}/{1} บรรทัด".format(i + 1, len(source_lines)))
                count += 1

        print("[OK] {0} -> {1} lines translated".format(filename, count))
        total_translated += count

    print("\n" + "="*60)
    print("ปฏิบัติการเสร็จสิ้น!")
    print("   รวม: {0} บรรทัดแปลแล้ว".format(total_translated))
    print("   GFxUI.int: SKIPPED (font control file - ข้ามเพื่อความปลอดภัย)")
    print("   บันทึกที่: {0}".format(TARGET_DIR))
    print("="*60)

if __name__ == "__main__":
    run_translation()