import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import os, warnings, time, glob, re
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

warnings.filterwarnings("ignore")

GEMINI_API_KEY = "AIzaSyCyW-M_-dyfOEeDevVpZLQnIFfD99efyOw"
genai.configure(api_key=GEMINI_API_KEY)

TEST_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DLC07_Blueprints_twk.int"

SYSTEM_PROMPT = """You are a Master-Level Thai Localization Specialist for the AAA video game "Dishonored".
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
- Aristocrats: Condescending — polite but cold Thai (ฉัน, �กระหม่อม)

=== 3. MANDATORY GLOSSARY ===
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

def add_thai_spacing(text):
    try:
        from pythainlp import word_tokenize
        tokenized = ' '.join(word_tokenize(text, engine='newmm'))
        while '  ' in tokenized:
            tokenized = tokenized.replace('  ', ' ')
        return tokenized
    except:
        return text

def detect_encoding(path):
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                f.read(100)
            return enc
        except:
            continue
    return 'utf-8'

enc = detect_encoding(TEST_FILE)
print(f"Encoding: {enc}")
print(f"File: {os.path.basename(TEST_FILE)}")

with open(TEST_FILE, 'r', encoding=enc, newline='') as f:
    content = f.read()

print(f"Content:\n{content}")
print("---")

lines = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
print(f"Total lines: {len(lines)}")

for i, l in enumerate(lines):
    stripped = l.strip()
    if stripped and not stripped.startswith(';') and not stripped.startswith('['):
        for sep in ('=', ': '):
            if sep in l:
                key = l[:l.index(sep)].strip()
                value = l[l.index(sep)+len(sep):].strip()
                if key and value and re.search(r'[a-zA-Z]{2,}', value):
                    print(f"Line {i+1}: key={key}")
                    print(f"  Value: {value}")

                    # Translate
                    res = model.generate_content(f"TEXT TO TRANSLATE:\n{key}={value}\n\n[OUTPUT TRANSLATED LINES ONLY]")
                    raw = res.text
                    print(f"Raw response: {repr(raw[:200])}")

                    # Parse
                    if '=' in raw:
                        idx = raw.index('=')
                        th_val = raw[idx+1:].strip()
                        th_spaced = add_thai_spacing(th_val)
                        print(f"Translated: {th_val}")
                        print(f"With spacing: {th_spaced}")
                    break
