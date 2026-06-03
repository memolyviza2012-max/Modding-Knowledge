# ==========================================
# ไฟล์: localization_translate8.py (The Masterpiece)
# อัปเดต: ซ่อมบั๊ก Duplicate, คืนชีพ Batch Size, เพิ่ม Safety Settings
# ==========================================
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, warnings, time, glob, re, json
from google import genai
from google.genai import types # [FIX 3] นำเข้า types สำหรับตั้งค่า Safety

warnings.filterwarnings("ignore")

GEMINI_API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=GEMINI_API_KEY)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT"
REFERENCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT"
STATE_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\localization_state.json"
LOG_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\localization_batch_log.txt"

MAX_FILES = 9999 # รันจริงทั้งหมด
MAX_RETRY = 3
BATCH_SIZE = 150 # [FIX 2] กำหนดขนาด Batch เพื่อไม่ให้ AI หลอน

SYSTEM_PROMPT = """You are a professional Thai translator for the game Dishonored.
The setting is Dunwall — a dark, plague-ridden, Victorian era steampunk city.

=== RULES ===
1. Input: "key=English". Output: "key=Thai". Exact line count, no additions.
2. NO COMMENTARY. Output only translation lines.
3. Preserve variables: %s %d {0} \\n \\r <font...>
4. Use glossary for proper nouns.
5. Do NOT translate text in [brackets] or after semicolons.
6. Mature-rated game — translate violent/crude dialogue faithfully.

=== GLOSSARY ===
Corvo Attano=คอร์โว อัตตาโน | Emily Kaldwin=เอมิลี่ คาลด์วิน | The Outsider=ดิ เอาท์ไซเดอร์
Lord Regent=อัครมหาเสนาบดี | High Overseer=ไฮโอเวอร์เซียร์ | Overseer=โอเวอร์เซียร์
Weepers=วีปเปอร์ | Blink=บลิงก์ | Dunwall=ดันวอลล์ | Daud=ดาวด์
Rat Plague=กาฬโรคหนู | Bonecharm=เครื่องราง | Granny Rags=แกรนนี่แร็กส์

=== EXAMPLES ===
m_Message=New mission objective added.
m_Message=ภารกิจใหม่ถูกเพิ่มเข้ามาแล้ว
m_TargetName=Unknown contact
m_TargetName=ผู้ติดต่อไม่ระบุตัวตน
"""

RE_THAI = re.compile(r'[\u0e00-\u0e7f]')
RE_ENG2 = re.compile(r'[a-zA-Z]{2,}')

def safe_print(msg):
    print(msg)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass

def has_thai(text):
    return bool(RE_THAI.search(text))

def detect_encoding(path):
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                f.read(100)
            return enc
        except Exception:
            continue
    return 'utf-8'

def parse_int(content, enc):
    lines = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
    result = []
    for line_idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith(';') or stripped.startswith('['):
            continue
        for sep in ('=', ': '):
            if sep in line:
                idx = line.index(sep)
                key = line[:idx].strip()
                value = line[idx+len(sep):].strip()
                if key:
                    result.append((line_idx, key, value, line))
                break
    return result

def find_eng_lines(target_parsed, ref_dict):
    result = []
    for (line_idx, k, v, raw) in target_parsed:
        if has_thai(v):
            continue
        ref_v = ref_dict.get(k, "")
        if RE_ENG2.search(v) and RE_ENG2.search(ref_v):
            result.append((line_idx, k, v, raw))
    return result

def deduplicate(eng_lines):
    seen = {}
    unique = []
    dup_map = {}
    for item in eng_lines:
        (line_idx, k, v, raw) = item
        if v not in seen:
            seen[v] = k
            unique.append(item)
        else:
            dup_map[k] = seen[v]
    return unique, dup_map

def translate_batch(lines_for_api):
    prompt = "## TEXT TO TRANSLATE:\n" + "\n".join(lines_for_api) + "\n[OUTPUT TRANSLATED LINES ONLY]"

    # [FIX 3] เพิ่ม Safety Settings แบบเต็มสูบทะลวงการเซ็นเซอร์
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.3,
        safety_settings=[
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_NONE),
        ]
    )

    for attempt in range(MAX_RETRY):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            err = str(e)
            if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                wait = 60 * (attempt + 1)
                safe_print(f" [!] Rate limited — wait {wait}s")
                time.sleep(wait)
            else:
                wait = 5 * (2 ** attempt)
                safe_print(f" [!] Attempt {attempt+1}/{MAX_RETRY} fail: {err[:80]}")
                if attempt < MAX_RETRY - 1:
                    time.sleep(wait)
    safe_print(" [✗] Translation failed after all retries")
    return None

def translate_file(target_path, ref_path):
    basename = os.path.basename(target_path)
    enc = detect_encoding(target_path)
    safe_print(f"\n[FILE] {basename} (enc: {enc})")

    with open(target_path, 'r', encoding=enc, newline='') as f:
        target_content = f.read()
    target_lines = target_content.split('\r\n') if enc == 'utf-16-le' else target_content.split('\n')

    ref_enc = detect_encoding(ref_path)
    with open(ref_path, 'r', encoding=ref_enc, newline='') as f:
        ref_content = f.read()

    ref_parsed = parse_int(ref_content, ref_enc)
    target_parsed = parse_int(target_content, enc)

    ref_dict = {k: v for (_, k, v, _) in ref_parsed}
    ref_keys = set(ref_dict)
    target_keys = {k for (_, k, v, _) in target_parsed}

    missing = ref_keys - target_keys
    extra = target_keys - ref_keys
    if missing:
        safe_print(f" [!] Missing keys ({len(missing)}): {sorted(missing)[:5]}")
    if extra:
        safe_print(f" [!] Extra keys ({len(extra)}): {sorted(extra)[:5]}")

    eng_lines = find_eng_lines(target_parsed, ref_dict)
    unique_eng, dup_map = deduplicate(eng_lines)

    if not unique_eng:
        safe_print(" [=] No English to translate")
        return 0

    safe_print(f" [i] {len(unique_eng)} unique | {len(dup_map)} dupes | {len(eng_lines)} total")

    lines_for_api = [f"{k}={ref_dict.get(k, v)}" for (_, k, v, _) in unique_eng]

    # Checkpoint ก่อนแปล
    checkpoint = target_path + ".checkpoint"
    with open(checkpoint, 'w', encoding=enc, newline='') as f:
        f.write(target_content)

    trans_dict = {}

    # [FIX 2] หั่น Batch ป้องกัน AI หลอนและลดภาระ API
    for i in range(0, len(lines_for_api), BATCH_SIZE):
        batch = lines_for_api[i:i+BATCH_SIZE]
        safe_print(f" [→] Translating batch {i//BATCH_SIZE + 1}...")
        res = translate_batch(batch)

        if not res:
            safe_print(" [✗] Batch failed, aborting file (checkpoint kept)")
            return 0

        # Parse response
        for line in res.split('\n'):
            line = line.strip()
            if '=' not in line:
                continue
            idx = line.index('=')
            k = line[:idx].strip()
            v = line[idx+1:].strip()
            if k:
                trans_dict[k] = v
        time.sleep(1) # พักหายใจระหว่าง Batch นิดหน่อย

    if len(trans_dict) != len(unique_eng):
        safe_print(f" [!] ส่ง {len(unique_eng)} ได้กลับ {len(trans_dict)} — บางบรรทัดอาจหาย")

    # [FIX 1] วนลูปจาก eng_lines ทั้งหมด เพื่อให้ประโยคที่ซ้ำกัน (Duplicate) ถูกแปลด้วย
    applied = 0
    for (line_idx, key, orig_value, raw_line) in eng_lines:
        th_val = trans_dict.get(key)

        # ถ้าไม่มีใน trans_dict ลอง reuse จาก dup_map
        if not th_val and key in dup_map:
            orig_key = dup_map[key]
            th_val = trans_dict.get(orig_key)

        if not th_val:
            continue

        for sep in ('=', ': '):
            if sep in raw_line:
                sep_pos = raw_line.index(sep)
                target_lines[line_idx] = raw_line[:sep_pos+len(sep)] + th_val
                applied += 1
                break

    # Atomic write
    new_content = '\r\n'.join(target_lines) if enc == 'utf-16-le' else '\n'.join(target_lines)
    tmp = target_path + ".tmp"
    with open(tmp, 'w', encoding=enc, newline='') as f:
        f.write(new_content)
    os.replace(tmp, target_path)

    if os.path.exists(checkpoint):
        os.remove(checkpoint)

    safe_print(f" [✓] {basename} — {applied}/{len(eng_lines)} applied")
    return applied

def find_files():
    results = []
    for path in glob.glob(SOURCE_DIR + "\\*.int"):
        ref_path = os.path.join(REFERENCE_DIR, os.path.basename(path))
        if not os.path.exists(ref_path):
            continue
        enc = detect_encoding(path)
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                content = f.read()
            parsed = parse_int(content, enc)
            eng_count = sum(1 for (_, k, v, _) in parsed
                            if not has_thai(v) and RE_ENG2.search(v))
            if eng_count > 0:
                results.append((os.path.basename(path), eng_count, path))
        except Exception:
            continue
    return sorted(results, key=lambda x: x[1])

def main():
    safe_print("=== Localization Translate V8 (Masterpiece) ===\n")
    files = find_files()
    safe_print(f"[i] ไฟล์ที่ต้องแปล: {len(files)}\n")

    if not files:
        safe_print("[✗] ไม่มีไฟล์ที่ต้องแปล")
        return

    state = {"files_done": 0, "lines_done": 0}
    total = 0

    for idx, (fname, eng_count, target_path) in enumerate(files[:MAX_FILES]):
        ref_path = os.path.join(REFERENCE_DIR, fname)
        safe_print(f"\n=== [{idx+1}/{min(MAX_FILES, len(files))}] {fname} ({eng_count} eng lines) ===")
        count = translate_file(target_path, ref_path)
        total += count
        state["files_done"] += 1
        state["lines_done"] += count
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        time.sleep(1)

    safe_print(f"\n=== DONE === Files: {state['files_done']} | Lines: {total}")

if __name__ == "__main__":
    main()
