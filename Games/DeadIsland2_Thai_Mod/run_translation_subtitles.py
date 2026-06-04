# -*- coding: utf-8 -*-
"""
run_translation_subtitles.py
========================
สคริปต์แปลภาษาอัตโนมัติสำหรับบทสนทนา (Subtitles) ของเกม Dead Island 2 ด้วย DeepSeek API
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import csv
import time
import requests
import os
import re
import warnings

warnings.filterwarnings("ignore")

# ==============================================================================
# [ส่วนที่ 1: ตั้งค่าระบบ]
# ==============================================================================
API_KEY      = "YOUR_API_KEY_HERE"  # <-- ใส่ API Key ของคุณที่นี่ครับ
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
MODEL        = "deepseek-chat"
TEMPERATURE  = 0.3
MAX_TOKENS   = 8192
MAX_RETRIES  = 5
RETRY_BASE_S = 5
BATCH_TARGET_CHARS = 3000  # ขนาดตัวอักษรรวมต่อ 1 Batch (ปลอดภัยจาก Rate Limit)

# ไฟล์เป้าหมาย (CSV ที่เรา extract ออกมาเมื่อกี้)
CSV_FILEPATH = r".\Translation\Dialogue_Subtitles.csv"

# คำหยาบ Canary ตรวจจับ AI หลอน
CANARY_WORDS = ["กีวางไร่อะ", "หลอนยา", "มั่วซั่ว"]

# ==============================================================================
# [ส่วนที่ 2: Master Prompt สำหรับแปลบทสนทนา (Subtitles)]
# ==============================================================================
SYSTEM_PROMPT = """I want you to act as a Master-Level English-to-Thai Video Game Localization Specialist. Your assignment is "Dead Island 2" — an action-packed, survival horror first-person action RPG set in a zombie-infested Los Angeles (dubbed "Hell-A").

You are translating SPOKEN DIALOGUE SUBTITLES. These are spoken lines by characters, players, NPCs, and enemies. 

=== 1. TONE & CONTEXTUAL RULES ===
- Tone: Natural, conversational, emotional, dramatic, dark humor, and pulpy.
- Swearing & Exclamations: High use of swearing and exclamations! Characters are survivors, gangsters, celebrities, and average people in Hell-A. Use natural, modern, and gritty Thai swearing matching the character's personality.
  * For common swears use: ไอ้สัส, ไอ้เหี้ย, บ้าเอ๊ย, ฉิบหาย, แม่ง, เวรเอ๊ย.
  * Adjust based on character (e.g., rough characters use "กู/มึง", classy/polite characters use polite forms like "ฉัน/คุณ").
  * Keep dialogue sounding like real spoken Thai, not robotic or Google-translated.
- Dialogue & Lore: Gritty, urban, modern, and sometimes sarcastic or humorous. Maintain the tension of survival horror, but keep the Hollywood "pulp" style.

=== 2. FORMATTING & TECHNICAL CONSTRAINTS (ABSOLUTE LAWS) ===
1. PRESERVE VARIABLES: Any text with placeholders like [TAG_0], [TAG_1] (which protect original codes like %s, {0}, <color=...>) MUST remain exactly intact.
2. ANTI-SQUISH (Chunk Spacing): Insert spaces ( ) ONLY between major clauses or full sentences. DO NOT space word-by-word.
3. EXACT OUTPUT FORMAT: You will receive a list of IDs and English text. You MUST return ONLY the translated text in this exact tab-separated format, one per line:
"ID_XXXXX" [TAB] "THAI_TRANSLATION"
Do not include any introductions, explanations, markdown formatting, or notes.

=== 3. OFFICIAL GLOSSARY (EXACT MATCH) ===
- Hell-A = เฮล-เอ
- Zombie = ซอมบี้
- Zombies = ซอมบี้
- Slayer = ผู้รอดชีวิต / นักล่าซอมบี้
- Slayers = ผู้รอดชีวิต / นักล่าซอมบี้
- Autophage = ออโตเฟจ
- Numen = นูเมน
- Numens = นูเมน
- Halperin Hotel = โรงแรมแฮลเพริน
- Bel-Air = เบลแอร์
- Beverly Hills = เบเวอร์ลีฮิลส์
- Venice Beach = เวนิสบีช
- Santa Monica = ซานตาโมนิกา
- Shambler = แชมเบลอร์
- Walker = วอล์กเกอร์
- Runner = รันเนอร์
- Crusher = ครัชเชอร์
- Screamer = สกรีมเมอร์
- Slobber = สล็อบเบอร์
- Butcher = บุชเชอร์
- Mutator = มิวเตเตอร์
"""

# ==============================================================================
# [ส่วนที่ 3: ระบบปกป้องฟังก์ชันและวิเคราะห์ประโยค]
# ==============================================================================

def is_thai(text):
    if not text or not isinstance(text, str):
        return False
    return bool(re.search(r'[\u0E00-\u0E7F]', text))

def mask_tags(text):
    tag_pattern = r'(<[^>]+>|\\n|\\r|\n|\r|%[sdiefg]|\{\d+\}|\[\[[^\]]+\]\])'
    tags = re.findall(tag_pattern, text)

    masked_text = text
    placeholders = {}
    for idx, tag in enumerate(tags):
        placeholder = f"[TAG_{idx}]"
        if placeholder not in placeholders:
            placeholders[placeholder] = tag
        masked_text = masked_text.replace(tag, placeholder, 1)

    return masked_text, placeholders

def unmask_tags(translated_text, placeholders):
    unmasked = translated_text
    for placeholder, original_tag in placeholders.items():
        unmasked = unmasked.replace(placeholder, original_tag)
    return unmasked

# ==============================================================================
# [ส่วนที่ 4: ระบบเชื่อมต่อ API & ประมวลผลกลุ่มข้อความ (Batch Engine)]
# ==============================================================================

def translate_batch(batch_tasks, batch_num, total_batches):
    lines = []
    for task in batch_tasks:
        lines.append(f'"{task["id"]}"\t"{task["masked_text"]}"')
    user_prompt = f"Translate these {len(batch_tasks)} entries:\n" + "\n".join(lines)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user",   "content": user_prompt.strip()}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                DEEPSEEK_URL, json=payload, headers=headers, timeout=120
            )

            if response.status_code == 429:
                sleep_time = RETRY_BASE_S * (2 ** (attempt - 1))
                print(f"  [429] Rate Limit ชน! นอนรอ {sleep_time} วินาที... (รอบที่ {attempt}/{MAX_RETRIES})")
                time.sleep(sleep_time)
                continue

            if response.status_code == 401:
                print("  [401] API Key ไม่ถูกต้องหรือหมดอายุ กรุณาตรวจสอบ API_KEY ครับบอส!")
                return None

            if response.status_code != 200:
                print(f"  [HTTP {response.status_code}] เกิดข้อผิดพลาดจากเซิร์ฟเวอร์: {response.text[:200]}")
                time.sleep(RETRY_BASE_S)
                continue

            res_json = response.json()

            if not res_json.get('choices'):
                print(f"  [ERROR] API ตอบกลับแบบผิดปกติ (ไม่มี choices): {res_json}")
                time.sleep(RETRY_BASE_S)
                continue

            reply = res_json['choices'][0]['message']['content'].strip()

            for bad_word in CANARY_WORDS:
                if bad_word in reply:
                    print(f"  [WARNING] ตรวจเจอคำหยาบหลอนจาก AI: '{bad_word}'! บล็อกการบันทึก!")
                    return None

            reply = re.sub(r'^```[^\n]*\n?', '', reply, flags=re.MULTILINE)
            reply = re.sub(r'\n?```$', '', reply, flags=re.MULTILINE)

            results = {}
            for line in reply.split('\n'):
                line = line.strip()
                if not line or '\t' not in line:
                    continue
                parts = line.split('\t', 1)
                if len(parts) < 2:
                    continue
                res_id    = parts[0].strip().strip('"')
                res_thai  = parts[1].strip().strip('"')
                results[res_id] = res_thai

            if len(results) < len(batch_tasks):
                missing = len(batch_tasks) - len(results)
                print(f"  [WARN] AI ตอบกลับมาไม่ครบ: ขาดหาย {missing} รายการ")

            return results

        except requests.exceptions.Timeout:
            sleep_time = RETRY_BASE_S * (2 ** (attempt - 1))
            print(f"  [TIMEOUT] หมดเวลาเชื่อมต่อ รอบที่ {attempt}/{MAX_RETRIES} — รอ {sleep_time} วินาที...")
            time.sleep(sleep_time)

        except requests.exceptions.ConnectionError:
            sleep_time = RETRY_BASE_S * (2 ** (attempt - 1))
            print(f"  [CONNECTION ERROR] ไม่สามารถเชื่อมต่อ DeepSeek API รอบที่ {attempt}/{MAX_RETRIES} — รอ {sleep_time} วินาที...")
            time.sleep(sleep_time)

        except Exception as e:
            sleep_time = RETRY_BASE_S * (2 ** (attempt - 1))
            print(f"  [ERROR] ข้อผิดพลาดไม่คาดคิด: {e} — รอ {sleep_time} วินาที...")
            time.sleep(sleep_time)

    print(f"  [FAIL] หมดรอบ Retry ({MAX_RETRIES} ครั้ง) สำหรับ Batch นี้")
    return None

def save_csv_checkpoint(headers, rows, filepath):
    """ระบบบันทึกไฟล์แบบ Atomic Save สำหรับ CSV ป้องกันไฟล์เสียหายกลางคัน"""
    tmp_file = filepath + ".tmp"
    import time
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(tmp_file, 'w', encoding='utf-16', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        # Retry replace up to 5 times in case of Windows file locking
        for attempt in range(5):
            try:
                os.replace(tmp_file, filepath)
                break
            except PermissionError:
                if attempt == 4:
                    raise
                print(f"  [WARN] File locked. Retrying save... ({attempt + 1}/5)")
                time.sleep(1)
    except Exception as e:
        print(f"  [ERROR] บันทึกไฟล์ไม่สำเร็จ: {e}")
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except:
                pass
        raise

# ==============================================================================
# [ส่วนที่ 5: ฟังก์ชันหลักการทำงาน]
# ==============================================================================

def main():
    print("=" * 60)
    print("   Dead Island 2 - Subtitles Translation Engine")
    print("=" * 60)

    if API_KEY == "" or API_KEY == "YOUR_DEEPSEEK_API_KEY":
        print("[CRITICAL] บอสยังไม่ได้ใส่ API_KEY ในสคริปต์ครับ! กรุณาใส่ก่อนรัน")
        return

    if not os.path.exists(CSV_FILEPATH):
        print(f"[ERROR] ไม่พบไฟล์ CSV ที่: {CSV_FILEPATH}")
        return

    csv_rows = []
    csv_headers = []
    
    print(f"[1/4] กำลังอ่านไฟล์ CSV: {CSV_FILEPATH}")
    try:
        with open(CSV_FILEPATH, 'r', encoding='utf-16', newline='') as f:
            reader = csv.reader(f)
            try:
                csv_headers = next(reader)
            except StopIteration:
                print("[ERROR] ไฟล์ CSV ว่างเปล่า!")
                return
            
            for row in reader:
                # คอลัมน์: Source, XmlPath, Key, English, Type, Thai (index 5)
                while len(row) < 6:
                    row.append("")
                csv_rows.append(row)
    except Exception as e:
        print(f"[ERROR] เปิดไฟล์ไม่สำเร็จ: {e}")
        return

    print(f"[2/4] โหลดข้อมูลเสร็จสิ้น: จำนวนทั้งสิ้น {len(csv_rows):,} รายการ")

    pending_tasks = []
    
    for row_idx, row in enumerate(csv_rows):
        source_text = row[3]  # English column
        current_translation = row[5]  # Thai column
        
        if is_thai(current_translation):
            continue  # แปลเป็นภาษาไทยแล้ว ข้ามเลย
            
        if not source_text or not source_text.strip():
            continue  # ไม่มีข้อความให้แปล
            
        masked_text, placeholders = mask_tags(source_text)
        
        stripped_masked = re.sub(r'\[TAG_\d+\]', '', masked_text).strip()
        if not stripped_masked:
            # มีแต่โค้ดก้อนเดียว คัดลอกไปได้เลย
            row[5] = source_text
            continue
            
        pending_tasks.append({
            "id": f"ID_{row_idx:05d}",
            "row_idx": row_idx,
            "raw_text": source_text,
            "masked_text": masked_text,
            "placeholders": placeholders
        })

    print(f"[3/4] ตรวจสอบเสร็จสิ้น: มีข้อความรอแปลทั้งสิ้น {len(pending_tasks):,} รายการ")
    if not pending_tasks:
        print("      ยินดีด้วยครับบอส! บทสนทนาทั้งหมดได้รับการแปลไทยครบ 100% เรียบร้อยแล้ว!")
        return

    batches       = []
    current_batch = []
    current_chars = 0

    for task in pending_tasks:
        current_batch.append(task)
        current_chars += len(task["masked_text"])
        if current_chars >= BATCH_TARGET_CHARS:
            batches.append(current_batch)
            current_batch = []
            current_chars = 0
    if current_batch:
        batches.append(current_batch)

    print(f"      แบ่งกลุ่มทำงาน (Batches): {len(batches)} กลุ่ม (~{BATCH_TARGET_CHARS} ตัวอักษรต่อกลุ่ม)")
    print("\n[4/4] เริ่มเดินเครื่องแปลภาษาไทยด้วย DeepSeek...")

    translated_count = 0
    failed_count     = 0
    start_time       = time.time()

    for idx, batch in enumerate(batches, 1):
        elapsed = time.time() - start_time
        print(f"\n  --- กำลังรันกลุ่มที่ {idx}/{len(batches)} (มีทั้งหมด {len(batch)} ข้อความ) ---")
        print(f"  เวลาที่ใช้ไปแล้ว: {int(elapsed // 60)} นาที {int(elapsed % 60)} วินาที")

        api_results = translate_batch(batch, idx, len(batches))

        if api_results is None:
            print(f"  [FAIL] กลุ่มที่ {idx} แปลไม่สำเร็จ ยกยอดไปรอบหน้าเพื่อความปลอดภัย")
            failed_count += len(batch)
            continue

        for task in batch:
            tid = task["id"]
            if tid in api_results:
                thai_translation = api_results[tid]
                final_thai = unmask_tags(thai_translation, task["placeholders"])
                
                # นำคำแปลกลับไปใส่ใน row[5] (Thai column)
                row_idx = task["row_idx"]
                csv_rows[row_idx][5] = final_thai
                translated_count += 1
            else:
                print(f"  [WARN] ไม่พบผลลัพธ์สำหรับ {tid} ({task['raw_text'][:50]}...)")
                failed_count += 1

        print(f"  สำเร็จสะสม: {translated_count} ข้อความ  |  ตกหล่น: {failed_count} ข้อความ")

        # บันทึก CSV หลังรันเสร็จแต่ละ Batch
        save_csv_checkpoint(csv_headers, csv_rows, CSV_FILEPATH)

        if idx < len(batches):
            time.sleep(1)

    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("      ปฏิบัติการแปลบทสนทนาไทยสำเร็จเสร็จสิ้น!")
    print("=" * 60)
    print(f"  - แปลเสร็จสิ้นทั้งหมด  : {translated_count:,} ข้อความ")
    print(f"  - ข้อความที่ข้าม/ตกหล่น: {failed_count:,} ข้อความ")
    print(f"  - เวลารวม               : {int(total_time // 60)} นาที {int(total_time % 60)} วินาที")
    print(f"  - อัปเดตคลังแสงที่      : {CSV_FILEPATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
