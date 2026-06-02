# ==========================================
# ไฟล์: localization_translate6.py (google.genai)
# แก้บรรทัด: index tracking, has_thai, checkpoint, deduplicate, mismatch check
# ==========================================
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, warnings, time, glob, re, json
from google import genai

warnings.filterwarnings("ignore")

GEMINI_API_KEY = "AIzaSyCyW-M_-dyfOEeDevVpZLQnIFfD99efyOw"
client = genai.Client(api_key=GEMINI_API_KEY)

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT"
REFERENCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT"
STATE_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\localization_state.json"
LOG_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\localization_batch_log.txt"
MAX_FILES = 5
MAX_RETRY = 3

SYSTEM_PROMPT = """You are a professional Thai translator for the game Dishonored.
The setting is Dunwall — a dark, plague-ridden, Victorian era steampunk city.

=== RULES ===
1. Input: "key=value". Output: "key=Thai". Exact line count, no additions.
2. NO COMMENTARY. Output only translation lines.
3. Preserve variables: %s %d {0} \\n \\r <font...>
4. Use glossary for proper nouns.
5. Do NOT translate text in [brackets] or after semicolons.

=== GLOSSARY ===
- Corvo Attano = คอร์โว อัตตาโน
- Emily Kaldwin = เอมิลี่ คาลด์วิน
- The Outsider = ดิ เอาท์ไซเดอร์
- Lord Regent = อัครมหาเสนาบดี
- High Overseer = ไฮโอเวอร์เซียร์
- Overseer = โอเวอร์เซียร์
- Weepers = วีปเปอร์
- Blink = บลิงก์
- Dunwall = ดันวอลล์
- Daud = ดาวด์

=== EXAMPLES ===
Input: m_Message="New mission objective added."
Output: m_Message="ภารกิจใหม่ถูกเพิ่มเข้ามาแล้ว"
Input: m_TargetName="Unknown contact"
Output: m_TargetName="ผู้ติดต่อไม่ระบุตัวตน"
"""

RE_THAI = re.compile(r'[\u0e00-\u0e7f]')

def safe_print(msg):
    print(msg)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except:
        pass

def has_thai(text):
    return bool(RE_THAI.search(text))

def detect_encoding(path):
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                f.read(100)
            return enc
        except:
            continue
    return 'utf-8'

def parse_int(content, enc):
    """Parse INT file. Returns list of (line_number_0indexed, key, value, raw_line)."""
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

def find_eng_lines_to_translate(target_parsed, ref_dict):
    """Find lines that need translation: target is English (no Thai) AND ref is English."""
    result = []
    for (line_idx, k, v, raw) in target_parsed:
        ref_v = ref_dict.get(k, "")
        # Skip if target already has Thai
        if has_thai(v):
            continue
        # Only translate if ref is also English
        if re.search(r'[a-zA-Z]{2,}', v) and re.search(r'[a-zA-Z]{2,}', ref_v):
            result.append((line_idx, k, v, raw))
    return result

def deduplicate(eng_lines):
    """Remove duplicate values, keeping first occurrence. Returns (unique, dup_map)."""
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
    prompt = SYSTEM_PROMPT + "\n\n## TEXT TO TRANSLATE:\n" + "\n".join(lines_for_api) + "\n\n[OUTPUT TRANSLATED LINES ONLY]"
    for attempt in range(MAX_RETRY):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            err = str(e)
            if '429' in err or 'RESOURCE_EXHAUSTED' in err:
                wait = 60 * (attempt + 1)
                safe_print(f" [!] Rate limited, wait {wait}s...")
                time.sleep(wait)
            else:
                if attempt < MAX_RETRY - 1:
                    wait = 5 * (2 ** attempt)
                    safe_print(f" [!] Attempt {attempt+1} fail: {err[:80]}")
                    time.sleep(wait)
                else:
                    safe_print(f" [X] Failed: {err[:80]}")
    return None

def translate_file(target_path, ref_path):
    basename = os.path.basename(target_path)
    enc = detect_encoding(target_path)
    safe_print(f"\n[FILE] {basename}")

    with open(target_path, 'r', encoding=enc, newline='') as f:
        target_content = f.read()
    target_lines = target_content.split('\r\n') if enc == 'utf-16-le' else target_content.split('\n')

    ref_enc = detect_encoding(ref_path)
    with open(ref_path, 'r', encoding=ref_enc, newline='') as f:
        ref_content = f.read()
    ref_parsed = parse_int(ref_content, ref_enc)
    target_parsed = parse_int(target_content, enc)

    ref_dict = {k: v for (line_idx, k, v, raw) in ref_parsed}
    ref_keys = set(ref_dict.keys())
    target_keys = {k for (line_idx, k, v, raw) in target_parsed}
    target_dict = {k: v for (line_idx, k, v, raw) in target_parsed}

    # Key mismatch check
    missing = ref_keys - target_keys
    extra = target_keys - ref_keys
    if missing:
        safe_print(f" [!] Missing keys ({len(missing)}): {sorted(list(missing))[:5]}")
    if extra:
        safe_print(f" [!] Extra keys ({len(extra)}): {sorted(list(extra))[:5]}")

    # Find English lines to translate (includes has_thai check)
    eng_lines = find_eng_lines_to_translate(target_parsed, ref_dict)
    unique_eng, dup_map = deduplicate(eng_lines)

    if dup_map:
        safe_print(f" [i] {len(dup_map)} duplicates (will reuse translated values)")
    if not unique_eng:
        safe_print(f" [=] No English to translate (all Thai or no ref match)")
        return 0

    safe_print(f" [i] {len(unique_eng)} unique lines ({len(eng_lines)} total, {len(dup_map)} dupes)")

    # Build prompt lines from reference (ref has original English values)
    lines_for_api = [f"{k}={ref_dict.get(k, v)}" for (line_idx, k, v, raw) in unique_eng]

    # Checkpoint BEFORE translation
    checkpoint = target_path + ".checkpoint"
    with open(checkpoint, 'w', encoding=enc, newline='') as f:
        f.write(target_content)
    safe_print(f" [i] Checkpoint saved")

    res = translate_batch(lines_for_api)
    if not res:
        safe_print(f" [X] Translation failed, checkpoint kept")
        return 0

    # Parse response
    trans_dict = {}
    for line in res.split('\n'):
        line = line.strip()
        if '=' not in line:
            continue
        idx = line.index('=')
        k = line[:idx].strip()
        v = line[idx+1:].strip()
        if k:
            trans_dict[k] = v

    if len(trans_dict) != len(unique_eng):
        safe_print(f" [!] Sent {len(unique_eng)}, got {len(trans_dict)} — some may be malformed")

    # Apply translations using CORRECT line_idx from parsed data
    applied = 0
    for (line_idx, key, orig_value, raw_line) in unique_eng:
        th_val = trans_dict.get(key)
        if th_val:
            # Find separator in raw_line
            for sep in ('=', ': '):
                if sep in raw_line:
                    sep_pos = raw_line.index(sep)
                    target_lines[line_idx] = raw_line[:sep_pos+len(sep)] + th_val
                    applied += 1
                    break
        elif key in dup_map:
            # Reuse translated value from duplicate key
            orig_key = dup_map[key]
            th_val = trans_dict.get(orig_key)
            if th_val:
                for sep in ('=', ': '):
                    if sep in raw_line:
                        sep_pos = raw_line.index(sep)
                        target_lines[line_idx] = raw_line[:sep_pos+len(sep)] + th_val
                        applied += 1
                        break

    # Write output
    new_content = '\r\n'.join(target_lines) if enc == 'utf-16-le' else '\n'.join(target_lines)
    tmp = target_path + ".tmp"
    with open(tmp, 'w', encoding=enc, newline='') as f:
        f.write(new_content)
    os.replace(tmp, target_path)

    # Clean up checkpoint on success
    if os.path.exists(checkpoint):
        os.remove(checkpoint)

    safe_print(f" [OK] {basename} — {applied}/{len(unique_eng)}")
    return applied

def find_files():
    """Find files in SOURCE_DIR that have English lines needing translation."""
    results = []
    for path in glob.glob(SOURCE_DIR + "\\*.int"):
        enc = detect_encoding(path)
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                content = f.read()
            parsed = parse_int(content, enc)
            # Count lines that have English (no Thai)
            eng_count = sum(1 for (line_idx, k, v, raw) in parsed
                           if not has_thai(v) and re.search(r'[a-zA-Z]{2,}', v))
            if eng_count > 0:
                results.append((os.path.basename(path), eng_count, path))
        except:
            continue
    return sorted(results, key=lambda x: x[1])

def main():
    safe_print("=== Localization Translate v6 ===\n")
    files = find_files()
    safe_print(f"[i] Files with English: {len(files)}\n")

    if not files:
        safe_print("[X] No files need translation")
        return

    state = {"files_done": 0, "lines_done": 0}
    total = 0

    for idx, (fname, eng_count, target_path) in enumerate(files[:MAX_FILES]):
        ref_path = os.path.join(REFERENCE_DIR, fname)
        if not os.path.exists(ref_path):
            safe_print(f"[!] No ref: {fname}")
            continue

        safe_print(f"\n=== [{idx+1}/{MAX_FILES}] {fname} ({eng_count} eng lines) ===")
        count = translate_file(target_path, ref_path)
        total += count
        state["files_done"] += 1
        state["lines_done"] += count
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
        time.sleep(1)

    safe_print(f"\n=== DONE ===")
    safe_print(f"Files: {state['files_done']} | Lines: {total}")

if __name__ == "__main__":
    main()
