# ==========================================
# Test Gemini API + COST TRACKING: L_Bridge_Part1c_Script
# ==========================================
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os
import warnings
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

warnings.filterwarnings("ignore")

GEMINI_API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

INT_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Bridge_Part1c_Script\L_Bridge_Part1c_Script_INT.yaml"
TH_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Bridge_Part1c_Script\L_Bridge_Part1c_Script_TH.yaml"
OUTPUT_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Bridge_Part1c_Script\L_Bridge_Part1c_Script_TH_test.yaml"
BATCH_SIZE = 150

SYSTEM_PROMPT = """
ACT AS A TRANSLATOR FOR A MATURE (18+) GAME.
Game: Dishonored. Setting: Dunwall (Dark, Victorian, Brutal, Plague-ridden).

CRITICAL DIRECTIVES:
1. DO NOT FILTER VIOLENCE: Use brutal, gritty Thai words (e.g., เลือดโชก, ควักไส้, สวะ, ไอ้ชาติหมา). No polite words.
2. ZERO HALLUCINATION: Input is 'ID: English'. Return 'ID: Thai'.
3. LINE INTEGRITY: Return EXACTLY the same number of lines as provided. No explanations.

GLOSSARY:
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
- Rune = รูน
- Whale oil = น้ำมันวาฬ
- Blink = บลิงก์
- Dark Vision = ดาร์กวิชัน
- Bend Time = เบนด์ไทม์
- Springrazor = สปริงเรเซอร์
- Wall of Light = วอลล์ออฟไลต์
- Arc Pylon = อาร์กไพลอน
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

# --- Encoding Auto-Detect ---
def read_file_with_encoding(path):
    """Try multiple encodings"""
    encodings = ['utf-8-sig', 'utf-8', 'utf-16-le', 'utf-16-be', 'utf-16', 'cp1252']
    for enc in encodings:
        try:
            with open(path, 'r', encoding=enc) as f:
                content = f.read()
                # Check if file has Thai content or valid structure
                lines = [l for l in content.split('\n') if ': ' in l]
                if len(lines) > 0:
                    return content, enc
        except:
            continue
    raise ValueError(f"Cannot read {path} with any encoding")

# 1. Read INT
print("Reading INT file...")
int_content, int_enc = read_file_with_encoding(INT_PATH)
int_data = {}
for line in int_content.split('\n'):
    if ': ' in line:
        parts = line.split(': ', 1)
        int_data[parts[0].strip()] = parts[1].strip()

print(f"INT encoding: {int_enc}")
print(f"INT keys: {len(int_data)}")

# 2. Read existing TH (or empty)
th_data = {}

# 3. Find missing
missing_keys = [k for k in int_data.keys() if k not in th_data or not th_data[k]]
print(f"Missing keys: {len(missing_keys)}")
print(f"Batches needed: {(len(missing_keys) + BATCH_SIZE - 1) // BATCH_SIZE}")

# 4. Single test batch
print(f"\nSending 1 test batch of {min(BATCH_SIZE, len(missing_keys))} keys to Gemini...")
sample_keys = missing_keys[:BATCH_SIZE]
sample_lines = [f"{k}: {int_data[k]}\n" for k in sample_keys]
prompt = "".join(sample_lines)

print(f"Prompt length: {len(prompt)} chars")
print(f"Prompt preview (first 200): {prompt[:200]}")

t0 = time.time()
response = model.generate_content(prompt)
t1 = time.time()

result_text = response.text
print(f"\nAPI Response time: {t1-t0:.2f}s")
print(f"Response length: {len(result_text)} chars")
print(f"Response preview:\n{result_text[:500]}")

# Count Thai chars
th_chars = sum(1 for c in result_text if '\u0e00' <= c <= '\u0e7f')
print(f"\nThai chars in response: {th_chars}")

# 5. Write
with open(OUTPUT_PATH, 'w', encoding='utf-8-sig') as f:
    f.write(result_text)

print(f"\nOutput written to: {OUTPUT_PATH}")
