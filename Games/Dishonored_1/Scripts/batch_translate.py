# ==========================================
# ไฟล์: batch_translate.py (V10.6 - Checkpoint)
# ==========================================
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, warnings, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

warnings.filterwarnings("ignore")

# --- [CONFIG] ---
GEMINI_API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)
WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working"

BATCH_SIZE = 150
MAX_WORKERS = 4
RETRY_MAX = 3
RETRY_BASE_DELAY = 2

# --- [SYSTEM PROMPT] ---
SYSTEM_PROMPT = """
You are a Master-Level Thai Localization Specialist for the AAA video game "Dishonored".
The setting is Dunwall — a dark, oppressive, plague-ridden, steampunk/Victorian-era industrial city.

=== 1. TRANSLATION RULES ===
1. TONE: Match dark, gritty atmosphere. Street Thai for guards/thugs, formal Thai for nobility.
2. ACCURACY: Mature-rated game. Translate violent/crude dialogue faithfully.
3. FORMAT: Input "ID: English". Output "ID: Thai". One line per entry.
4. LINE COUNT: Return EXACTLY same number of lines. No additions, no omissions.
5. NO COMMENTARY: Output translation lines only. No explanations, no markdown.
6. VARIABLES: Preserve %s, %d, {0}, \\n, \\r, <font color="..."> exactly as-is.
7. THAI SPACING: Insert spaces between distinct Thai phrases. Never break a single word.
8. NAMES: Use glossary for all proper nouns — no exceptions.
9. SOUND EFFECTS: If original text is wrapped like `'* Cough. *'`, output MUST use exact same format `'* ไอ *'`.

=== 2. CHARACTER VOICE GUIDE ===
- Corvo Attano: Silent protagonist — no spoken lines
- Emily Kaldwin: Young, innocent — gentle/childlike Thai (หนู, ค่ะ)
- The Outsider: Mysterious, poetic — elevated archaic Thai (เรา, เจ้า)
- Overseers: Fanatical, rigid — formal Thai (ข้า, ท่าน)
- Guards/Thugs: Crude, aggressive — street Thai (มึง, กู, ไอ้สวะ)
- Aristocrats: Condescending — polite but cold Thai (ฉัน, กระหม่อม)
- Weepers: Delirious — fragmented speech, stutters required
- Sokolov: Arrogant genius — sharp, clipped Thai
- Piero: Paranoid, obsessive — anxious, rushed Thai
- Slackjaw: Crime boss — rough, intimidating

=== 3. MANDATORY GLOSSARY ===
- Corvo Attano = คอร์โว อัตตาโน
- Emily Kaldwin = เอมิลี่ คาลด์วิน
- Jessamine Kaldwin = เจสซามีน คาลด์วิน
- The Outsider = ดิ เอาท์ไซเดอร์ [NEVER translate as คนนอก]
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
- Rune = รูน
- Blink = บลิงก์
- Dark Vision = ดาร์กวิชัน
- Bend Time = เบนด์ไทม์
- Wall of Light = วอลล์ออฟไลต์
- Dunwall = ดันวอลล์
- Daud = ดาวด์
- Granny Rags = แกรนนี่แร็กส์
- Lady Boyle = เลดี้บอยล์
- Piero = เปียโร
- Sokolov = โซโคลอฟ
- Admiral Havelock = พลเรือเอกเฮฟล็อค
- Samuel = ซามูเอล
- Callista = คาลลิสต้า

=== 4. FEW-SHOT EXAMPLES ===
Input:
UI_Message_01: Press %s to use Blink.
Guard_Bark_12: Trespass and we'll feed your guts to the hagfish.
Weeper_Moan_03: No...biting...stop...stop...heeelp!
Output:
UI_Message_01: กด %s เพื่อใช้ บลิงก์
Guard_Bark_12: บุกรุกเข้ามาเมื่อไหร่ ข้าจะควักไส้แกไปให้ปลาแฮกฟิชกิน!
Weeper_Moan_03: ไม่...อย่ากัด...หยุด...หยุดนะ...ช่ววววยด้วยยย!
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

LOCK = threading.Lock()


def safe_print(msg):
    with LOCK:
        print(msg)


def read_yaml(path):
    for enc in ('utf-8-sig', 'utf-8', 'utf-16-le', 'utf-16-be', 'cp1252'):
        try:
            data = {}
            with open(path, 'r', encoding=enc) as f:
                for line in f:
                    if ': ' in line:
                        k, v = line.split(': ', 1)
                        data[k.strip()] = v.strip()
            if data:
                return data, enc
        except Exception:
            continue
    raise ValueError(f"Cannot read: {path}")


def translate_batch(lines):
    prompt = "".join(lines)
    for attempt in range(RETRY_MAX):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            wait = RETRY_BASE_DELAY * (2 ** attempt)
            safe_print(f" [!] Attempt {attempt+1}/{RETRY_MAX} fail: {e} — wait {wait}s")
            if attempt < RETRY_MAX - 1:
                time.sleep(wait)
    return None


def parse_response(res_text, valid_keys):
    result = {}
    for line in res_text.split('\n'):
        line = line.strip()
        if ': ' not in line:
            continue
        parts = line.split(': ', 1)
        key = parts[0].strip()
        if key in valid_keys:
            result[key] = parts[1].strip()
    return result


def sync_translate(int_data, th_data, th_yaml_path):
    missing_keys = [k for k in int_data if not th_data.get(k)]
    if not missing_keys:
        safe_print(" [✓] All entries already translated")
        return th_data

    total = len(missing_keys)
    n_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    safe_print(f" [→] {total} missing | {n_batches} batches | {MAX_WORKERS} workers")

    tasks = [
        (missing_keys[i:i + BATCH_SIZE],
         [f"{k}: {int_data[k]}\n" for k in missing_keys[i:i + BATCH_SIZE]])
        for i in range(0, total, BATCH_SIZE)
    ]
    valid_keys = set(missing_keys)
    total_matched = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(translate_batch, lines): keys
            for keys, lines in tasks
        }
        for future in as_completed(futures):
            keys = futures[future]
            res = future.result()

            if not res:
                safe_print(f" [✗] Batch '{keys[0]}…' failed after {RETRY_MAX} retries")
                continue

            parsed = parse_response(res, valid_keys)

            with LOCK:
                th_data.update(parsed)
                total_matched += len(parsed)

            # [V10.6] Checkpoint — บันทึกทันทีหลังแต่ละ batch
            with open(th_yaml_path, 'w', encoding='utf-8-sig') as f:
                for k in int_data:
                    f.write(f"{k}: {th_data.get(k, int_data[k])}\n")

            safe_print(f" [✓] {len(parsed)}/{len(keys)} matched — Checkpoint Saved 💾")
            time.sleep(0.5)

    safe_print(f" [→] Total: {total_matched}/{total} translated")
    return th_data


def process_file(int_yaml_path):
    name = os.path.basename(os.path.dirname(int_yaml_path))
    th_yaml_path = int_yaml_path.replace('_INT.yaml', '_TH.yaml')
    safe_print(f"\n Processing: {name}")

    try:
        int_data, _ = read_yaml(int_yaml_path)
    except Exception as e:
        safe_print(f" [✗] Cannot read INT: {e}")
        return False

    if not int_data:
        safe_print(" [⚠] INT file empty — skip")
        return True

    th_data = {}
    if os.path.exists(th_yaml_path):
        try:
            th_data, _ = read_yaml(th_yaml_path)
        except Exception:
            pass

    th_data = sync_translate(int_data, th_data, th_yaml_path)

    th_count = sum(
        1 for v in th_data.values()
        if v and any('\u0e00' <= c <= '\u0e7f' for c in str(v))
    )
    safe_print(f" [✓] Done: {name} — {th_count}/{len(int_data)} Thai entries")
    return True


def main():
    safe_print("=== Dishonored TH Localization — V10.6 ===\n")

    int_files = [
        os.path.join(root, f)
        for root, _, files in os.walk(WORK_DIR)
        for f in files if f.endswith('_INT.yaml')
    ]

    if not int_files:
        safe_print(f"[✗] No _INT.yaml files found in:\n {WORK_DIR}")
        return

    safe_print(f"Found {len(int_files)} INT files\n")
    done = failed = 0

    for i, path in enumerate(int_files, 1):
        safe_print(f"[{i}/{len(int_files)}]")
        if process_file(path):
            done += 1
        else:
            failed += 1

    safe_print(f"\n=== DONE === Completed: {done} Failed: {failed}")


if __name__ == "__main__":
    main()
