# ==========================================
# ไฟล์: localization_batch_translate.py (V10.6 Lite v3G)
# แปลไฟล์ .int ทั้งหมดใน Localization/INT
# ==========================================
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, warnings, time, glob, re
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

warnings.filterwarnings("ignore")

# --- [CONFIG] ---
GEMINI_API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT"
OUTPUT_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT"

BATCH_SIZE = 100
MAX_WORKERS = 3
RETRY_MAX = 3
RETRY_BASE_DELAY = 2

# --- [SYSTEM PROMPT] ---
SYSTEM_PROMPT = """
You are a Master-Level Thai Localization Specialist for the AAA video game "Dishonored".
The setting is Dunwall — a dark, oppressive, plague-ridden, steampunk/Victorian-era industrial city.

=== 1. TRANSLATION RULES ===
1. TONE: Match dark, gritty atmosphere. Street Thai for guards/thugs, formal Thai for nobility.
2. ACCURACY: Mature-rated game. Translate violent/crude dialogue faithfully.
3. FORMAT: Input "key=value". Output "key=Thai". One line per entry.
4. LINE COUNT: Return EXACTLY same number of lines. No additions, no omissions.
5. NO COMMENTARY: Output translation lines only. No explanations, no markdown.
6. VARIABLES: Preserve %s, %d, {0}, \\n, \\r, <font color="..."> exactly as-is.
7. THAI SPACING: Insert spaces between distinct Thai phrases using PyThaiNLP word_tokenize.
8. NAMES: Use glossary for all proper nouns — no exceptions.
9. SOUND EFFECTS: If original text is like '* Cough. *', output MUST use same format '* ไอ *'.
10. Do NOT translate strings inside [brackets] or after semicolons (comments).

=== 2. CHARACTER VOICE GUIDE ===
- Emily Kaldwin: Young, innocent — gentle/childlike Thai (หนู, ค่ะ)
- The Outsider: Mysterious, poetic — elevated archaic Thai (เรา, เจ้า)
- Overseers: Fanatical, rigid — formal Thai (ข้า, ท่าน)
- Guards/Thugs: Crude, aggressive — street Thai (มึง, กู, ไอ้สวะ)
- Aristocrats: Condescending — polite but cold Thai (ฉัน, กระหม่อม)
- Weepers: Delirious — fragmented speech, stutters required

=== 3. MANDATORY GLOSSARY ===
- Corvo Attano = คอร์โว อัตตาโน
- Emily Kaldwin = เอมิลี่ คาลด์วิน
- Jessamine Kaldwin = เจสซามีน คาลด์วิน
- The Outsider = ดิ เอาท์ไซเดอร์
- Lord Regent = อัครมหาเสนาบดี
- High Overseer = ไฮโอเวอร์เซียร์
- Overseer = โอเวอร์เซียร์
- Abbey of the Everyman = นิกายเอเวอรีแมน
- Bottle Street Gang = แก๊งบอตเทิลสตรีต
- Whalers = พวกเวลเลอร์
- The Void = เดอะวอยด์
- Rat Plague = กาฬโรคหนู
- Weepers = วีปเปอร์
- Tallboys = ทอลบอย
- Bonecharm = เครื่องราง
- Blink = บลิงก์
- Dunwall = ดันวอลล์
- Daud = ดาวด์
- Granny Rags = แกรนนี่แร็กส์
- Lady Boyle = เลดี้บอยล์
- Piero = เปียโร
- Sokolov = โซโคลอฟ
- Admiral Havelock = พลเรือเอกเฮฟล็อค
- Samuel = ซามูเอล

=== 4. FEW-SHOT EXAMPLES ===
Input:
m_Message="New mission objective added."
m_TargetName="Unknown contact"
Output:
m_Message="ภารกิจใหม่ถูกเพิ่มเข้ามาแล้ว"
m_TargetName="ผู้ติดต่อไม่ระบุตัวตน"
"""

def safe_print(msg):
    print(msg)

def detect_encoding(path):
    """Auto-detect file encoding."""
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                f.read(100)
            return enc
        except:
            continue
    return 'utf-8'

def add_thai_spacing(text):
    """Insert spaces between Thai words for UE2/UE3 compatibility."""
    try:
        from pythainlp import word_tokenize
        # Strip outer quotes if present
        stripped = text.strip()
        if stripped.startswith('"') and stripped.endswith('"'):
            stripped = stripped[1:-1]
        tokenized = ' '.join(word_tokenize(stripped, engine='newmm'))
        while '  ' in tokenized:
            tokenized = tokenized.replace('  ', ' ')
        return tokenized
    except:
        return text

def parse_int_file(content, enc):
    """Parse .int file, return list of (line_num, key, value, raw_line)."""
    lines = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
    result = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith(';') or stripped.startswith('['):
            continue
        for sep in ('=', ': '):
            if sep in line:
                idx = line.index(sep)
                key = line[:idx].strip()
                value = line[idx+len(sep):].strip()
                if key and value and re.search(r'[a-zA-Z]{2,}', value):
                    result.append((i, key, value, line))
                break
    return result

def translate_batch(lines_content, retries=RETRY_MAX):
    prompt = SYSTEM_PROMPT + "\n\n## TEXT TO TRANSLATE:\n" + "\n".join(lines_content) + "\n\n[OUTPUT TRANSLATED LINES ONLY — NO COMMENTARY]"
    for attempt in range(retries):
        try:
            response = genai.generate_text(
                model="gemini-2.0-flash",
                prompt=prompt,
                temperature=0.3,
                max_output_tokens=2048,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                }
            )
            return response.candidates[0].content
        except Exception as e:
            if attempt < retries - 1:
                wait = RETRY_BASE_DELAY * (2 ** attempt)
                safe_print(f" [!] Attempt {attempt+1} fail: {str(e)[:50]} — wait {wait}s")
                time.sleep(wait)
            else:
                safe_print(f" [X] All attempts failed: {str(e)[:50]}")
    return None

def translate_file(filepath, enc):
    """Translate a single .int file. Returns (success, file_count)."""
    basename = os.path.basename(filepath)
    safe_print(f"\n[FILE] {basename}")

    with open(filepath, 'r', encoding=enc, newline='') as f:
        content = f.read()

    parsed = parse_int_file(content, enc)
    if not parsed:
        safe_print(f" [=] No English lines to translate")
        return True, 0

    safe_print(f" [i] {len(parsed)} English lines found")

    # Group into batches
    batches = []
    for i in range(0, len(parsed), BATCH_SIZE):
        batch = parsed[i:i+BATCH_SIZE]
        batches.append(batch)

    translated_count = 0
    for batch_idx, batch in enumerate(batches):
        lines_to_translate = [f"{key}={value}" for (_, key, value, _) in batch]
        safe_print(f" [>>] Batch {batch_idx+1}/{len(batches)} ({len(lines_to_translate)} lines)")

        res = translate_batch(lines_to_translate)
        if not res:
            safe_print(f" [X] Batch {batch_idx+1} failed")
            continue

        # Parse response into dict
        trans_dict = {}
        for line in res.split('\n'):
            line = line.strip()
            if '=' in line:
                idx = line.index('=')
                k = line[:idx].strip()
                v = line[idx+1:].strip()
                if k:
                    trans_dict[k] = v

        # Apply translations back
        batch_translated = 0
        for (line_num, key, value, raw_line) in batch:
            if key in trans_dict:
                th_val = add_thai_spacing(trans_dict[key])
                # Replace value in raw_line
                for sep in ('=', ': '):
                    if sep in raw_line:
                        sep_pos = raw_line.index(sep)
                        raw_lines_list = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
                        raw_lines_list[line_num] = raw_line[:sep_pos+len(sep)] + th_val
                        content = '\r\n'.join(raw_lines_list) if enc == 'utf-16-le' else '\n'.join(raw_lines_list)
                        batch_translated += 1
                        break

        translated_count += batch_translated
        safe_print(f" [<<] Batch {batch_idx+1} done: {batch_translated}/{len(batch)} lines")

    # Write back
    with open(filepath, 'w', encoding=enc, newline='') as f:
        f.write(content)

    safe_print(f" [OK] {basename} — {translated_count}/{len(parsed)} lines translated")
    return True, translated_count

def main():
    safe_print("=== Localization Batch Translate V10.6 Lite v3G ===\n")
    safe_print(f"Source : {SOURCE_DIR}")
    safe_print(f"Files  : *.int")
    safe_print(f"Batch  : {BATCH_SIZE} | Workers: {MAX_WORKERS}\n")

    int_files = glob.glob(SOURCE_DIR + "\\*.int")
    safe_print(f"[i] Found {len(int_files)} .int files\n")

    if not int_files:
        safe_print("[X] No .int files found")
        return

    total_translated = 0
    total_files = 0

    for filepath in sorted(int_files):
        enc = detect_encoding(filepath)
        ok, count = translate_file(filepath, enc)
        if ok and count > 0:
            total_translated += count
            total_files += 1
        time.sleep(0.5)

    safe_print(f"\n=== DONE ===")
    safe_print(f"Files translated: {total_files}")
    safe_print(f"Total lines: {total_translated}")

if __name__ == "__main__":
    main()
