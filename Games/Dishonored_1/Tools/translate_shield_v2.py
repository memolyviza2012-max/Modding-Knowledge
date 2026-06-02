# Dishonored Thai Translation - Shield Engine V.2
# ใช้ร่วมกับ LM Studio (qwen3-14b) + PyThaiNLP

import re
import json
import urllib.request
import datetime
from pythainlp import word_tokenize

LM_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen/qwen3-14b"
INPUT_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Twk_InGameUI.int"
OUTPUT_LOG = r"C:\Users\WiT.Danaiwit\.openclaw\workspace\translate_v3_log.txt"

# ===== THE SHIELD ENGINE V.2 =====

def extract_tags(text):
    """THE SHIELD: สกัด Tags ทุกประเภทและแทนที่ด้วย placeholder [[Tn]]"""
    tags = []

    # Pattern 1: Backtick variables `GBA_Jump`, `KEY_LStick`, etc.
    backticks = re.findall(r'`[^`]+`', text)
    tags.extend(backticks)

    # Pattern 2: HTML/UI tags <br />, <br/>, <something>
    html_tags = re.findall(r'<[^>]+>', text)
    tags.extend(html_tags)

    # Pattern 3: Printf format specifiers %s, %d, %i, %f
    printf = re.findall(r'%[sdif]', text)
    tags.extend(printf)

    # Pattern 4: Button combinations like GBA_Block + GBA_Primary (no backticks)
    # Only match if it's part of a larger expression
    btn_combos = re.findall(r'[A-Za-z_]+\s*\+\s*[A-Za-z_]+', text)
    for combo in btn_combos:
        # Only add if not already in tags and not backtick-wrapped
        if combo not in tags and f'`{combo}`' not in text:
            tags.append(combo)

    # Pattern 5: Escape sequences \n \r
    escapes = re.findall(r'\\[nr]', text)
    tags.extend(escapes)

    # Pattern 6: Color code placeholders `c/`t
    color_codes = re.findall(r'`[^`]*`', text)
    # Merge with backticks to avoid duplicates
    tags = list(dict.fromkeys(tags))

    return tags

def mask_text(text, tags):
    """สวมหน้ากากให้ Tags ทั้งหมด"""
    masked = text
    for i, tag in enumerate(tags):
        # Replace each occurrence of the tag
        masked = masked.replace(tag, f'[[T{i}]]')
    return masked

def unmask_text(text, tags):
    """ถอดหน้ากากคืน"""
    unmasked = text
    for i, tag in enumerate(tags):
        unmasked = unmasked.replace(f'[[T{i}]]', tag)
    return unmasked

# ===== TRANSLATION ENGINE =====

def translate_via_lm(prompt_text, max_len=150):
    messages = [
        {"role": "system", "content": "You are a Thai video game UI translator. Translate English UI text to Thai. Keep it short (under 40 chars for buttons, 80 for messages). Reply with ONLY the Thai translation, no quotes, no explanation."},
        {"role": "user", "content": f'Translate to Thai: "{prompt_text}"'}
    ]
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_len,
        "temperature": 0.3
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        LM_URL,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[ERR:{e}]"

def tokenize_thai(text):
    """เติม space ระหว่างคำไทย (PyThaiNLP word_tokenize)"""
    if re.search(r'[\u0E00-\u0E7F]', text):
        tokens = word_tokenize(text, engine="newmm")
        return " ".join(tokens)
    return text

# ===== LINE PROCESSOR =====

def is_english_text(s):
    """ตรวจสอบว่าคุ้มค่าการแปลหรือไม่"""
    if not re.search(r'[a-zA-Z]{3,}', s):
        return False
    stripped = re.sub(r'\[\[T\d+\]\]', '', s).strip()
    if len(stripped) < 2:
        return False
    skip = {'Mash', 'Hold', 'Press', 'Use', 'Exit', 'Jump', 'Move', 'Zoom',
            'Sneak', 'Block', 'Parry', 'Pause', 'Sprint', 'Talk', 'Loot',
            'Carry', 'Disarm', 'Sword', 'Attack', 'Current Location',
            'You are here', '1st Floor', '2nd Floor', '3rd Floor', 'Entrance'}
    for phrase in skip:
        if stripped == phrase or stripped.startswith(phrase + ' '):
            return False
    return True

def post_process(thai_text):
    """POST-PROCESSING: ฟิลเตอร์ทำความสะอาดหลังแปล"""
    # ลบอัญประกาศส่วนเกิน
    thai_text = thai_text.strip('"').strip()

    # แก้ปัญหา AI เว้นวรรคระหว่างคำไทย
    # ถ้า AI แปลเป็น "ก ร ะ โ ด ด" ให้รวมกลับเป็น "กระโดด"
    thai_text = re.sub(r'(?<=[ก-๙])\s+(?=[ก-๙])', '', thai_text)

    # กฎปรับคำศัพท์ (ทำในภาษาไทยโดยตรง)
    thai_text = thai_text.replace('ผม', 'ฉัน')
    thai_text = thai_text.replace('ครับ', '').replace('ค่ะ', '')

    return thai_text

def process_ue3_int_line(line, translate_func):
    """
    THE SHIELD ENGINE V.2 - ฟังก์ชันหลักในการประมวลผลบรรทัด .INT
    """
    clean_line = line.strip()

    # 1. Bypass บรรทัดว่าง
    if not clean_line:
        return line

    # 2. Bypass Section Header
    if clean_line.startswith('[') and clean_line.endswith(']'):
        return line

    # 3. Bypass Comments
    if clean_line.startswith(';') or clean_line.startswith('//'):
        return line

    # 4. Parsing: สกัด Key และ Value
    # Format A: Key="Value"
    match_a = re.match(r'^([^=]+)="(.*)"\s*$', clean_line)
    # Format B: Key=(m_Description="Value")
    match_b = re.match(r'^([^=]+)=\(m_Description="(.*)"\)\s*$', clean_line)

    if match_a:
        key, original_text = match_a.groups()
        fmt = 'A'
    elif match_b:
        key, original_text = match_b.groups()
        fmt = 'B'
    else:
        return line  # หลุด pattern → คืนค่าเดิมเพื่อความปลอดภัย

    # ถ้า Value ว่างเปล่า ข้าม
    if not original_text:
        return line

    # ข้ามถ้าไม่ใช่ภาษาอังกฤษที่คุ้มค่าการแปล
    if not is_english_text(original_text):
        return line

    # --- THE SHIELD: Masking ---
    tags = extract_tags(original_text)
    masked_text = mask_text(original_text, tags)

    # --- SEND TO AI ---
    translated = translate_func(masked_text)

    if translated.startswith('[ERR'):
        return line  # ถ้า error ให้คืนค่าเดิม

    # --- POST-PROCESSING ---
    translated = post_process(translated)

    # --- UNMASKING ---
    unmasked = unmask_text(translated, tags)

    # --- TOKENIZE THAI ---
    if re.search(r'[\u0E00-\u0E7F]', unmasked):
        unmasked = tokenize_thai(unmasked)

    # 5. Reassembly
    if fmt == 'B':
        return f'{key}=(m_Description="{unmasked}")\n'
    else:
        return f'{key}="{unmasked}"\n'

# ===== MAIN =====

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    with open(OUTPUT_LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {msg}\n")

def main():
    log("=== Shield Engine V.2 Started ===")

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total = len(lines)
    translated = 0
    skipped = 0
    errors = 0

    for i, line in enumerate(lines):
        result = process_ue3_int_line(line, translate_via_lm)

        if result != line:
            translated += 1
            # Extract key for logging
            clean = line.strip()
            if '=' in clean:
                key = clean.split('=')[0]
                log(f"TX [{key}]")
        else:
            skipped += 1

        lines[i] = result

        if translated % 10 == 0 and translated > 0:
            log(f"Progress: {translated} translated")

    with open(INPUT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    log(f"=== DONE! {translated} lines translated, {skipped} skipped, {errors} errors ===")
    print(f"[OK] Done! {translated} translated, {skipped} skipped. Saved to: {INPUT_FILE}")

if __name__ == "__main__":
    main()