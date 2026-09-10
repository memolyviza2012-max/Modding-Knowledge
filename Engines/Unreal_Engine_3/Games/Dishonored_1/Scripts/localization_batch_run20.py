# ==========================================
# ไฟล์: localization_batch_run20.py (V10.6 Lite v3G)
# แปลแค่ 20 ไฟล์แรกใน Localization/INT
# หยุดเมื่อครบ 20 ไฟล์
# ==========================================
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, warnings, time, glob, re, json
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

warnings.filterwarnings("ignore")

# --- [CONFIG] ---
GEMINI_API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT"
STATE_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\localization_state.json"
LOG_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\localization_batch_log.txt"

MAX_FILES = 20
BATCH_SIZE = 100
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

=== 4. FEW-SHOT EXAMPLES ===
Input:
m_Message="New mission objective added."
m_TargetName="Unknown contact"
Output:
m_Message="ภารกิจใหม่ถูกเพิ่มเข้ามาแล้ว"
m_TargetName="ผู้ติดต่อไม่ระบุตัวตน"
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

def safe_print(msg):
    print(msg)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except:
        pass

def detect_encoding(path):
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                f.read(100)
            return enc
        except:
            continue
    return 'utf-8'

def add_thai_spacing(text):
    try:
        from pythainlp import word_tokenize
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
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if attempt < retries - 1:
                wait = RETRY_BASE_DELAY * (2 ** attempt)
                safe_print(f" [!] Attempt {attempt+1} fail: {str(e)[:50]} — wait {wait}s")
                time.sleep(wait)
    return None

def translate_file(filepath, enc, state):
    basename = os.path.basename(filepath)
    safe_print(f"\n[FILE] {basename}")

    with open(filepath, 'r', encoding=enc, newline='') as f:
        content = f.read()

    parsed = parse_int_file(content, enc)
    if not parsed:
        safe_print(f" [=] No English lines")
        return 0

    safe_print(f" [i] {len(parsed)} English lines")

    batches = []
    for i in range(0, len(parsed), BATCH_SIZE):
        batches.append(parsed[i:i+BATCH_SIZE])

    translated_count = 0
    for batch_idx, batch in enumerate(batches):
        lines_to_translate = [f"{key}={value}" for (_, key, value, _) in batch]
        safe_print(f" [>>] Batch {batch_idx+1}/{len(batches)} ({len(lines_to_translate)} lines)")

        res = translate_batch(lines_to_translate)
        if not res:
            safe_print(f" [X] Batch {batch_idx+1} failed")
            continue

        # Parse response
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
        lines_list = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
        for (line_num, key, value, raw_line) in batch:
            if key in trans_dict:
                th_val = add_thai_spacing(trans_dict[key])
                for sep in ('=', ': '):
                    if sep in raw_line:
                        sep_pos = raw_line.index(sep)
                        lines_list[line_num] = raw_line[:sep_pos+len(sep)] + th_val
                        content = '\r\n'.join(lines_list) if enc == 'utf-16-le' else '\n'.join(lines_list)
                        batch_translated += 1
                        break

        translated_count += batch_translated
        state['batches_sent'] = state.get('batches_sent', 0) + 1
        state['lines_translated'] = state.get('lines_translated', 0) + batch_translated
        safe_print(f" [<<] Batch {batch_idx+1} done: {batch_translated}/{len(batch)} lines")

    with open(filepath, 'w', encoding=enc, newline='') as f:
        f.write(content)

    safe_print(f" [OK] {basename} — {translated_count}/{len(parsed)} lines translated")
    return translated_count

def main():
    safe_print("=== Localization Batch Run (20 files) ===\n")

    state = {"batches_sent": 0, "lines_translated": 0, "files_done": 0, "started_at": str(time.time())}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                old = json.load(f)
            state.update(old)
        except:
            pass

    int_files = glob.glob(SOURCE_DIR + "\\*.int")
    safe_print(f"[i] Found {len(int_files)} .int files")

    # Filter files with English
    files_to_process = []
    for path in sorted(int_files):
        enc = detect_encoding(path)
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                content = f.read()
            lines = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
            eng_lines = [l for l in lines if re.search(r'[a-zA-Z]{2,}', l) and not l.strip().startswith(';') and not l.strip().startswith('[') and ('=' in l or ': ' in l)]
            if eng_lines:
                files_to_process.append((path, enc, len(eng_lines)))
        except:
            continue

    safe_print(f"[i] Files with English: {len(files_to_process)}")
    safe_print(f"[i] Processing up to {MAX_FILES} files\n")

    total_translated = 0
    files_done = 0

    for idx, (filepath, enc, eng_count) in enumerate(files_to_process[:MAX_FILES]):
        safe_print(f"\n=== [{idx+1}/{MAX_FILES}] {os.path.basename(filepath)} ({eng_count} lines) ===")
        count = translate_file(filepath, enc, state)
        total_translated += count
        files_done += 1
        state['files_done'] = state.get('files_done', 0) + 1

        # Save state after each file
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)

        time.sleep(0.5)

    safe_print(f"\n=== DONE (first {MAX_FILES} files) ===")
    safe_print(f"Files done: {files_done}")
    safe_print(f"Total lines translated: {total_translated}")
    safe_print(f"Batches sent: {state.get('batches_sent', 0)}")
    safe_print(f"State saved to: {STATE_FILE}")

if __name__ == "__main__":
    main()
