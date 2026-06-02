# ==========================================
# Test: Single file translation (output → TH directly)
# ==========================================
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
import warnings
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

warnings.filterwarnings("ignore")

GEMINI_API_KEY = "AIzaSyCyW-M_-dyfOEeDevVpZLQnIFfD99efyOw"
genai.configure(api_key=GEMINI_API_KEY)

INT_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_Ext_Script\L_Distillery_Ext_Script_INT.yaml"
TH_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_Ext_Script\L_Distillery_Ext_Script_TH.yaml"
BATCH_SIZE = 150

SYSTEM_PROMPT = """
You are a Master-Level Thai Localization Specialist for the AAA video game "Dishonored".
The setting is Dunwall — a dark, oppressive, plague-ridden, steampunk/Victorian-era industrial city.

=== 1. TRANSLATION RULES ===
1. TONE: Match dark, gritty atmosphere. Street Thai for guards/thugs, formal Thai for nobility.
2. ACCURACY: This is a Mature-rated game. Translate violent/crude dialogue faithfully.
3. FORMAT: Input "ID: English text". Output "ID: Thai text". One line per entry.
4. LINE COUNT: Return EXACTLY the same number of lines as input. No additions, no omissions.
5. NO COMMENTARY: Output translation lines only. No explanations, no markdown.
6. VARIABLES: Preserve %s, %d, {0}, \n, \r, <font color="..."> and all tags exactly as-is.
7. SOUND EFFECTS: If the original text is wrapped in single quotes and asterisks like `'* ... *'` (e.g., `'* Cough. *'`), the translation MUST also be wrapped in the exact same format (e.g., `'* ไอ *'`). Do not remove them.
8. THAI SPACING: Insert spaces between distinct Thai phrases/clauses. Never break a single word with a space.
9. NAMES: Use glossary for all proper nouns — no exceptions.

=== 2. CHARACTER VOICE GUIDE ===
- Corvo Attano: Silent protagonist — no spoken lines
- Emily Kaldwin: Young, innocent — gentle/childlike Thai (หนู, ค่ะ)
- The Outsider: Mysterious, poetic, ancient — elevated archaic Thai (เรา, เจ้า)
- Overseers: Fanatical, authoritative — formal rigid Thai (ข้า, ท่าน)
- Guards/Thugs: Crude, aggressive — street Thai (มึง, กู, ไอ้สวะ)
- Aristocrats: Condescending — polite but cold Thai (ฉัน, กระหม่อม)
- Weepers: Delirious, plague-maddened — fragmented speech, stutters required
- Sokolov: Arrogant genius, impatient — sharp, clipped Thai
- Piero: Paranoid, obsessive — anxious, rushed Thai
- Slackjaw: Crime boss — rough, business-minded, intimidating

=== 3. MANDATORY GLOSSARY ===
- Corvo Attano = คอร์โว อัตตาโน
- Emily Kaldwin = เอมิลี่ คาลด์วิน
- Jessamine Kaldwin = เจสซามีน คาลด์วิน
- The Outsider = ดิ เอาท์ไซเดอร์ [NEVER translate as คนนอก]
- Lord Regent = อัครมหาเสนาบดี
- High Overseer = ไฮโอเวอร์เซียร์
- Overseer = โอเวอร์เซียร์
- Spymaster = หัวหน้าสายลับ
- Abbey of the Everyman = นิกายเอเวอรีแมน
- Bottle Street Gang = แก๊งบอตเทิลสตรีต
- Whalers = พวกเวลเลอร์
- The Void = เดอะวอยด์
- Rat Plague = กาฬโรคหนู
- Weepers = วีปเปอร์
- Tallboys = ทอลบอย
- Bonecharm = เครื่องราง
- Rune = รูน
- Whale oil = น้ำมันวาฬ
- Blink = บลิงก์
- Dark Vision = ดาร์กวิชัน
- Bend Time = เบนด์ไทม์
- Possession = พอสเซสชัน
- Windblast = วินด์บลาสต์
- Devouring Swarm = เดโวริงสวอร์ม
- Springrazor = สปริงเรเซอร์
- Wall of Light = วอลล์ออฟไลต์
- Arc Pylon = อาร์กไพลอน
- Dunwall = ดันวอลล์
- Coldridge Prison = เรือนจำโคลด์ริดจ์
- Flooded District = เขตน้ำท่วม
- Dunwall Tower = หอคอยดันวอลล์
- Kaldwin's Bridge = สะพานคาลด์วิน
- The Golden Cat = เดอะโกลเดนแคท
- Distillery District = ย่านโรงกลั่น
- Estate District = ย่านคฤหาสน์
- Admiral Havelock = พลเรือเอกเฮฟล็อค
- Callista = คาลลิสต้า
- Samuel = ซามูเอล
- Piero = เปียโร
- Sokolov = โซโคลอฟ
- Lady Boyle = เลดี้บอยล์
- Daud = ดาวด์
- Granny Rags = แกรนนี่แร็กส์

=== 4. FEW-SHOT EXAMPLES ===
Input:
UI_Message_01: Press %s to use Blink.
Guard_Bark_12: Trespass and we'll feed your guts to the hagfish.
Weeper_Moan_03: No...biting...stop...stop...heeelp!
Aristocrat_Chat_04: Is everything alright, sir? You aren't looking quite yourself this evening.
Outsider_Monologue_01: Your life has taken a turn, has it not?

Output:
UI_Message_01: กด %s เพื่อใช้ บลิงก์
Guard_Bark_12: บุกรุกเข้ามาเมื่อไหร่ ข้าจะควักไส้แกไปให้ปลาแฮกฟิชกิน!
Weeper_Moan_03: ไม่...อย่ากัด...หยุด...หยุดนะ...ช่ววววยด้วยยย!
Aristocrat_Chat_04: ทุกอย่างเรียบร้อยดีไหมคะท่าน? ค่ำคืนนี้ท่านดูไม่ค่อยเป็นตัวของตัวเองเลยนะคะ
Outsider_Monologue_01: ชีวิตของเจ้าพลิกผันไปแล้ว ไม่ใช่หรือ?
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
    response = model.generate_content(prompt)
    return response.text


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


# 1. Read INT
print("Reading INT file...")
int_data, enc = read_yaml(INT_PATH)
print(f"Encoding: {enc}")
print(f"INT keys: {len(int_data)}")

# 2. Read existing TH (empty to force full retranslate)
th_data = {}

# 3. Find missing
missing_keys = [k for k in int_data if k not in th_data or not th_data[k]]
print(f"Missing: {len(missing_keys)}")
print(f"Batches: {(len(missing_keys) + BATCH_SIZE - 1) // BATCH_SIZE}")

# 4. Translate
start_time = time.time()
total_matched = 0

for i in range(0, len(missing_keys), BATCH_SIZE):
    batch_keys = missing_keys[i:i + BATCH_SIZE]
    batch_lines = [f"{k}: {int_data[k]}\n" for k in batch_keys]

    batch_num = i // BATCH_SIZE + 1
    print(f"\nBatch {batch_num}: {len(batch_keys)} keys")

    t0 = time.time()
    res = translate_batch(batch_lines)
    t1 = time.time()

    if res:
        parsed = parse_response(res, set(missing_keys))
        total_matched += len(parsed)
        th_data.update(parsed)
        print(f"  API time: {t1-t0:.1f}s | Matched: {len(parsed)}/{len(batch_keys)}")
    else:
        print(f"  FAILED")

    time.sleep(0.5)

elapsed = time.time() - start_time

# 5. Write output (overwrite TH directly)
with open(TH_PATH, 'w', encoding='utf-8-sig') as f:
    for k in int_data:
        f.write(f"{k}: {th_data.get(k, int_data[k])}\n")

# 6. Stats
th_count = sum(1 for v in th_data.values()
               if v and any('\u0e00' <= c <= '\u0e7f' for c in str(v)))

print(f"\n=== SUMMARY ===")
print(f"Total keys: {len(int_data)}")
print(f"Translated: {len(th_data)}")
print(f"Thai entries: {th_count}")
print(f"Time: {elapsed:.1f}s")
print(f"Output: {TH_PATH}")
