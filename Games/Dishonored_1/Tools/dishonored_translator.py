"""
DISHONORED-003: UI Dictionary Filter & LM Studio Translator
"""
import re
import os
import sys
import urllib.request
import json
import time
import traceback

# Ensure UTF-8 output
try:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
except Exception:
    pass

# ==========================================
# CONFIG
# ==========================================
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MODEL_NAME = "qwen/qwen3-14b"
LM_API_TOKEN = "sk-lm-LJjFSyER:mi5apRc5vKLGK9lCrSy9"

WORKSPACE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
SOURCE_DIR = os.path.join(WORKSPACE, "01_source")
TRANSLATED_DIR = os.path.join(WORKSPACE, "02_translated")

# ==========================================
# 1. LM Studio Connection (Qwen3-14B)
# ==========================================
def translate_with_qwen3(text, system_prompt=None):
    """Call Qwen3-14B via LM Studio"""
    if system_prompt is None:
        system_prompt = """คุณคือนักแปลภาษาอังกฤษ→ไทยสำหรับเกม Dishonored
แปลให้ natural สำหรับ UI เกม ใช้สำนวนไทยที่เข้าใจง่าย
ทับศัพท์: Dishonored, Corvo, Daud, Whalers, Outsider, The Void
ห้ามแก้แท็กระบบ เช่น <br>, [と], ฯลฯ
ตอบเฉพาะข้อความแปล ไม่ต้องมี markdown"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"แปลเป็นไทย:\n{text}"}
    ]

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 2048,
        "stream": False
    }

    for attempt in range(3):
        try:
            req = urllib.request.Request(
                LM_STUDIO_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LM_API_TOKEN}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"    [Retry {attempt+1}/3] {e}")
            time.sleep(2)
    
    return None


# ==========================================
# 2. Clean LLM Output (remove <think> tags)
# ==========================================
def clean_llm_output(text):
    """ตัด <think> และ </think> ออกจาก output ของ LLM"""
    if not text:
        return ""
    # ลบ <think>...</think> แบบ multiline
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # ตัด whitespaces ซ้ำ
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


# ==========================================
# 3. UI Dictionary (บังคับแก้คำสั้นในเมนู)
# ==========================================
def apply_ui_dictionary(text):
    """
    THE UI DICTIONARY - พจนานุกรมบังคับสำหรับเมนู
    ใช้ Regex ^$ เพื่อให้แมตช์คำตรงๆ เท่านั้น
    """
    ui_dict = {
        r"^OK$": "ตกลง",
        r"^Cancel$": "ยกเลิก",
        r"^Accept$": "ยอมรับ",
        r"^Back$": "กลับ",
        r"^Play$": "เล่นเกม",
        r"^Continue$": "เล่นต่อ",
        r"^Options$": "ตัวเลือก",
        r"^Settings$": "การตั้งค่า",
        r"^Quit$": "ออกจากเกม",
        r"^Yes$": "ใช่",
        r"^No$": "ไม่ใช่",
        r"^Apply$": "ใช้งาน",
        r"^Save$": "บันทึก",
        r"^Load$": "โหลด",
        r"^Stealth$": "ลอบเร้น",
        r"^Chaos$": "ความโกลาหล",
        r"^Low$": "ต่ำ",
        r"^Medium$": "ปานกลาง",
        r"^High$": "สูง",
        r"^Off$": "ปิด",
        r"^On$": "เปิด",
        r"^Easy$": "ง่าย",
        r"^Normal$": "ปกติ",
        r"^Hard$": "ยาก",
        r"^New Game$": "เกมใหม่",
        r"^Load Game$": "โหลดเกม",
        r"^Settings Menu$": "เมนูตั้งค่า",
        r"^Credits$": "เครดิต",
        r"^Exit$": "ออก",
        r"^Resume$": "กลับสู่เกม",
        r"^Main Menu$": "เมนูหลัก",
    }

    cleaned_text = text.strip()

    for pattern, replacement in ui_dict.items():
        if re.match(pattern, cleaned_text, re.IGNORECASE):
            return replacement

    return cleaned_text


# ==========================================
# 4. Process .int File
# ==========================================
def detect_encoding(path):
    """ตรวจจับ encoding ของไฟล์ .int"""
    with open(path, "rb") as f:
        raw = f.read(4)
    if raw[:2] == b"\xff\xfe":
        return "utf-16-le"
    elif raw[:2] == b"\xfe\xff":
        return "utf-16-be"
    else:
        return "utf-8"


def split_int_line(line):
    """แยก key กับ value ออกจากบรรทัด .int"""
    if '="' not in line:
        return None, None
    idx = line.index('="')
    key = line[:idx + 1]
    value = line[idx + 1:]
    return key, value


def process_int_file(input_path, output_path, dry_run=False):
    """
    อ่านไฟล์ .int และเขียนผลลัพธ์การแปล
    Pipeline: Original -> Qwen3 -> Clean -> Dictionary -> Output
    """
    print(f"\n{'='*60}")
    print(f"PROCESSING: {os.path.basename(input_path)}")
    print(f"{'='*60}")

    if not os.path.exists(input_path):
        print(f"[ERROR] ไม่พบไฟล์: {input_path}")
        return False

    # ตรวจจับ encoding อัตโนมัติ
    enc = detect_encoding(input_path)
    print(f"  Detected encoding: {enc}")

    with open(input_path, "r", encoding=enc) as f:
        lines = f.readlines()

    print(f"  อ่านได้ {len(lines)} บรรทัด")

    translated_lines = []
    translate_count = 0
    skip_count = 0
    dict_count = 0

    for i, line in enumerate(lines):
        line = line.rstrip("\r\n")

        # ข้ามบรรทัดว่าง
        if not line.strip():
            translated_lines.append("\n")
            continue

        # ข้าม comment หรือ metadata
        if line.strip().startswith("//") or line.strip().startswith("["):
            translated_lines.append(line + "\n")
            continue

        key, value = split_int_line(line)

        if not key or not value:
            translated_lines.append(line + "\n")
            continue

        # ตัด quote ทั้งเปิดและปิดออก
        original_text = value.strip("\"\n")
        if not original_text.strip():
            translated_lines.append(line + "\n")
            continue

        print(f"\n[{i+1}/{len(lines)}] Original: {original_text}")

        # 1. ตรวจ Dictionary ก่อน
        dict_result = apply_ui_dictionary(original_text)
        if dict_result != original_text:
            # Dictionary แมตช์
            final_text = dict_result
            print(f"    [DICT] {original_text} -> {final_text}")
            print(f"    [OK] {final_text}")
            dict_count += 1
            translate_count += 1
        else:
            # 2. เรียก Qwen3 แปล
            final_text = original_text
            try:
                raw_translation = translate_with_qwen3(original_text)
                
                if raw_translation:
                    # 3. ลบ <think>...</think> ออก
                    cleaned = clean_llm_output(raw_translation)
                    print(f"    [Cleaned] {cleaned}")

                    # 4. Dictionary fallback
                    final_text = apply_ui_dictionary(cleaned)
                    print(f"    [OK] {final_text}")
                    translate_count += 1
                else:
                    # LLM returned None
                    print(f"    [SKIP] ใช้ต้นฉบับ")
                    skip_count += 1
            except Exception as e:
                print(f"    [ERROR] {type(e).__name__}: {e}")
                final_text = original_text
                skip_count += 1

        # ประกอบบรรทัดใหม่
        new_line = f'{key}"{final_text}"\n'
        translated_lines.append(new_line)

        # Delay เพื่อไม่ให้ LM Studio ล้น
        time.sleep(0.5)

    # เขียนไฟล์ output
    if not dry_run:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(translated_lines)
        print(f"\n[WRITTEN] {output_path}")

    print(f"\n[SUMMARY] แปล {translate_count} (Dict: {dict_count}), ข้าม {skip_count}")
    return True


# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    try:
        print("DISHONORED-003: UI Dictionary + Qwen3-14B Translator")
        print("=" * 60)

        test_file = "Twk_InGameUI.int"
        input_file = os.path.join(SOURCE_DIR, test_file)
        output_file = os.path.join(TRANSLATED_DIR, test_file)

        print(f"\n[INPUT ] {input_file}")
        print(f"[OUTPUT] {output_file}")

        print("\n[REAL MODE - Writing file]")
        process_int_file(input_file, output_file, dry_run=False)

        print("\n" + "=" * 60)
        print("TRANSLATION COMPLETE!")
    except Exception as e:
        print(f"\n[FATAL ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        sys.exit(1)
