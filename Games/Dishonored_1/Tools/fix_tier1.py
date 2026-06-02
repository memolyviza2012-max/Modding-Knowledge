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
    "GFxUI.int",
    "Twk_GFxMoviePlayerMainMenu.int"
]

SYSTEM_PROMPT = """You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your current task is translating UI, Menus, and System Messages.
Guidelines:
1. Keep the translation concise and clear.
2. Use standard gaming terminology in Thai.
3. CRITICAL: For longer sentences, insert natural spaces (เว้นวรรค) between phrases or clauses to allow the game engine to word-wrap properly. DO NOT squash the whole sentence together.
4. Output ONLY the translated Thai text. Do not add quotes unless they exist in the original.

CRITICAL GLOSSARY & TERMINOLOGY:
- Corvo Attano: คอร์โว อัตตาโน
- The Outsider: ดิ เอาท์ไซเดอร์
- Lord Regent: ผู้สำเร็จราชการ
- Blink: บลิงก์
- Dark Vision: เนตรมืด
- Bend Time: บิดเบือนเวลา
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
    # Keep natural spacing - do NOT squash Thai words
    translated_text = translated_text.replace('ผม', 'ฉัน').replace('ครับ', '').replace('ค่ะ', '')

    for i, tag in enumerate(tags):
        translated_text = translated_text.replace('[[T{0}]]'.format(i), tag)

    if 'm_Description=' in line:
        return '{0}=(m_Description="{1}")\n'.format(key, translated_text)
    else:
        return '{0}="{1}"\n'.format(key, translated_text)

def fix_tier_1_files():
    print("="*60)
    print("MATRIX REPORT - เมทริกซ์รายงาน")
    print("="*60)
    print("[*] เริ่มปฏิบัติการซ่อมไฟล์: แก้ปัญหา Encoding และเว้นวรรค")
    print("[*] เป้าหมาย: {0} ไฟล์".format(len(TARGET_FILES)))
    print("="*60)

    os.makedirs(TARGET_DIR, exist_ok=True)

    total_translated = 0

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

        print("\nกำลังอ่านและแปลใหม่: {0} ...".format(filename))

        source_lines, detected_encoding = read_file_safely(source_path)
        print("  - ตรวจพบรูปแบบไฟล์: {0}".format(detected_encoding))

        save_encoding = 'utf-16-le' if 'utf-16' in detected_encoding else 'utf-8-sig'
        print("  - ใช้ Encoding สำหรับเซฟ: {0}".format(save_encoding))

        count = 0
        with open(target_path, 'w', encoding=save_encoding) as f_out:
            for i, line in enumerate(source_lines):
                translated_line = process_ue3_int_line(line)
                f_out.write(translated_line)
                f_out.flush()

                if (i + 1) % 10 == 0:
                    print("  - ความคืบหน้า: {0}/{1} บรรทัด".format(i + 1, len(source_lines)))
                count += 1

        print("[OK] {0} -> {1} lines translated".format(filename, count))
        total_translated += count

    print("\n" + "="*60)
    print("ซ่อมไฟล์สำเร็จ!")
    print("   รวม: {0} บรรทัดแปลแล้ว".format(total_translated))
    print("   บันทึกที่: {0}".format(TARGET_DIR))
    print("="*60)

if __name__ == "__main__":
    fix_tier_1_files()