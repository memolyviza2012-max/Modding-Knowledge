# ==========================================
# ไฟล์: translate_corrupt.py
# Purpose: Translate 149 CORRUPT TH files from INT .int files
# Mode: Read INT .int → Translate → Write TH .int
# ==========================================
import sys
import os
import warnings
import logging

# --- [SILENCER FIX: ปิดกั้น Warning และ Log กวนใจทุกรูปแบบ] ---
warnings.filterwarnings("ignore")
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("google.generativeai").setLevel(logging.CRITICAL)
logging.getLogger().setLevel(logging.CRITICAL)
os.environ['GRPC_PYTHON_LOG_LEVEL'] = 'error'
os.environ['GRPC_VERBOSITY'] = 'ERROR'

# จัดการ Encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
# ทริคสำคัญ: เบี่ยงกระแส stderr ให้ไปออก stdout ทำให้ PowerShell ไม่จับเป็น Exit Code 1
sys.stderr = sys.stdout 

import time, threading, re
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pythainlp import word_tokenize

# --- [CONFIG] ---
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
REPORT_PATH = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\translate_corrupt_report.txt'

# API Key from MEMORY
GEMINI_API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

BATCH_SIZE = 80
MAX_WORKERS = 4
RETRY_MAX = 3
RETRY_BASE_DELAY = 2

# --- [SYSTEM PROMPT] ---
SYSTEM_PROMPT = """You are a Master-Level Thai Localization Specialist for the AAA video game "Dishonored".
The setting is Dunwall — a dark, oppressive, plague-ridden, steampunk/Victorian-era industrial city.

=== 1. TRANSLATION RULES ===
1. TONE: Match dark, gritty atmosphere. Street Thai for guards/thugs, formal Thai for nobility.
2. ACCURACY: Mature-rated game. Translate violent/crude dialogue faithfully.
3. FORMAT: Input "ID: English". Output "ID: Thai". One line per entry.
4. LINE COUNT: Return EXACTLY same number of lines. No additions, no omissions.
5. NO COMMENTARY: Output translation lines only. No explanations, no markdown.
6. VARIABLES: Preserve %s, %d, {0}, \\n, \\r, <font color="..."> exactly as-is.
7. THAI SPACING: Insert spaces between distinct Thai phrases using PyThaiNLP newmm tokenizer. Never break a single word.
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

def detect_encoding(path):
    with open(path, 'rb') as f:
        raw = f.read(4)
    if raw[:2] == b'\xff\xfe':
        return 'utf-16-le'
    elif raw[:2] == b'\xfe\xff':
        return 'utf-16-be'
    elif raw[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    return 'utf-8'

def read_int_file(path):
    """Read INT .int file - return list of (id, text) tuples"""
    enc = detect_encoding(path)
    with open(path, 'r', encoding=enc, errors='replace') as f:
        raw = f.read()
    raw = raw.replace('\r\n', '\n').replace('\r', '\n')
    lines = raw.split('\n')
    
    entries = []
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Section header [Name ClassName]
        if line.startswith('[') and ']' in line:
            m = re.match(r'\[([^\]]+)', line)
            if m:
                current_section = m.group(1)
            entries.append((line, line))  # section header - keep as-is
        
        # Property line key=value or key="value"
        elif '=' in line and current_section:
            entries.append((line, line))
        
        # Comment line
        elif line.startswith(';'):
            entries.append((line, line))
        
        # Other non-empty line
        elif line and current_section:
            entries.append((line, line))
    
    return entries

def extract_translatable(lines):
    """Extract lines that need translation"""
    result = []
    for i, (raw, orig) in enumerate(lines):
        if raw.startswith('[') or raw.startswith(';') or not raw.strip():
            continue
        
        if '=' in raw:
            key_part = raw.split('=', 1)[0].strip()
            val_part = raw.split('=', 1)[1]
            
            if val_part.strip() not in ('""', "''", ''):
                result.append((i, raw, key_part, val_part))
    
    return result

def thai_tokenize(text):
    """Add spaces between Thai words using PyThaiNLP"""
    text = text.strip()
    if not text:
        return text
    
    has_thai = any('\u0e00' <= c <= '\u0e7f' for c in text)
    if not has_thai:
        return text
    
    try:
        tokens = word_tokenize(text, engine="newmm")
        return ' '.join(tokens)
    except:
        return text

def format_thai_output(text):
    """Format Thai text - tokenize if contains Thai"""
    text = text.strip()
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        text = text[1:-1]
    
    text = thai_tokenize(text)
    return text

def translate_batch(texts):
    """Translate a batch of texts via Gemini"""
    prompt = "Translate the following English lines to Thai. Output ONLY the translation lines.\n\n"
    prompt += texts
    
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

def parse_translation_response(res_text, key_map):
    """Parse Gemini response back to key->thai mappings"""
    result = {}
    lines = res_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if ': ' not in line:
            continue
        parts = line.split(': ', 1)
        key = parts[0].strip()
        if key in key_map:
            result[key] = parts[1].strip()
    
    return result

def process_file(int_path, th_path):
    """Translate a single INT file to TH"""
    name = os.path.basename(int_path)
    
    try:
        entries = read_int_file(int_path)
    except Exception as e:
        return False, f"Cannot read INT: {e}"
    
    if not entries:
        return True, "Empty INT file"
    
    int_enc = detect_encoding(int_path)
    translatable = extract_translatable(entries)
    
    if not translatable:
        with open(th_path, 'w', encoding=int_enc, newline='\n') as f:
            for raw, _ in entries:
                f.write(raw + '\n')
        return True, "No translatable content - copied INT"
    
    batches = []
    batch_entries = []
    batch_texts = ""
    
    for i, (idx, raw, key, val) in enumerate(translatable):
        batch_entries.append((idx, raw, key, val))
        batch_texts += f"{key}: {val}\n"
        
        if len(batch_entries) >= BATCH_SIZE or i == len(translatable) - 1:
            if batch_entries:
                batches.append(batch_entries)
            batch_entries = []
            batch_texts = ""
    
    translated = {}
    
    for batch in batches:
        texts = ""
        for _, raw, key, val in batch:
            texts += f"{key}: {val}\n"
        
        res = translate_batch(texts)
        
        if not res:
            safe_print(f" [✗] Batch failed for {name}")
            continue
        
        keys = {key for _, _, key, _ in batch}
        parsed = parse_translation_response(res, keys)
        translated.update(parsed)
    
    with open(th_path, 'w', encoding=int_enc, newline='\n') as f:
        for raw, _ in entries:
            if raw.startswith('[') or raw.startswith(';') or not raw.strip():
                f.write(raw + '\n')
            elif '=' in raw:
                key_part = raw.split('=', 1)[0].strip()
                if key_part in translated:
                    th_text = translated[key_part]
                    th_text = format_thai_output(th_text)
                    f.write(f"{key_part}={th_text}\n")
                else:
                    f.write(raw + '\n')
            else:
                f.write(raw + '\n')
    
    th_count = sum(1 for k, v in translated.items() if v and any('\u0e00' <= c <= '\u0e7f' for c in v))
    return True, f"Translated {th_count}/{len(translatable)} entries"

def main():
    safe_print("=== Dishonored TH Localization — translate_corrupt.py ===\n")
    
    corrupt_files = [
        "Boyle_Twk.int", "Bridge_MS.int", "Descriptions.int", "Distillery_MS.int",
        "ExampleGame.int", "Galvani_MS.int",
        "L_ArtDealer_Audio.int", "L_ArtDealer_Scripts.int",
        "L_BoyleStreet_Ext_Script.int", "L_Boyle_Ext_Audio.int",
        "L_Boyle_Ext_P.int", "L_Boyle_Ext_Script.int",
        "L_Boyle_Int_Audio.int", "L_Boyle_Int_P.int", "L_Boyle_Int_Script.int",
        "L_Bridge_Part1a_Audio.int", "L_Bridge_Part1a_Script.int",
        "L_Bridge_Part1b_Audio.int", "L_Bridge_Part1b_Script.int",
        "L_Bridge_Part1c_Audio.int", "L_Bridge_Part1c_Script.int",
        "L_Bridge_Part2_Audio.int", "L_Bridge_Part2_Script.int",
        "L_Brothel_Audio.int", "L_Brothel_Script.int",
        "L_Distillery2_Audio.int", "L_Distillery2_P.int", "L_Distillery2_Script.int",
        "L_Distillery_Audio.int", "L_Distillery_Loot.int", "L_Distillery_Strt1Script.int",
        "L_Flooded_FAssassins_Audio.int", "L_Flooded_FAssassins_P.int",
        "L_Flooded_FGate_Audio.int", "L_Flooded_FGate_P.int", "L_Flooded_FGate_Script.int",
        "L_Flooded_FRefinery_Audio.int", "L_Flooded_FRefinery_Intro.int",
        "L_Flooded_FRefinery_P.int", "L_Flooded_FRefinery_Script.int",
        "L_Flooded_FStreets_P.int", "L_Flooded_FStreets_Script.int",
        "L_Galvani1_Audio.int", "L_Galvani1_Scripts.int",
        "L_Galvani1_Strt1_Scripts.int", "L_Galvani1_Strt2_Scripts.int",
        "L_Isl_Audio_Master.int", "L_Isl_Audio_Slave.int",
        "L_Isl_Common_Master.int", "L_Isl_Common_Slave.int",
        "L_Isl_Geom_Master.int", "L_Isl_Geom_Slave.int",
        "L_Isl_HighChaos_Script.int", "L_Isl_LowChaos_Script.int",
        "L_Isl_Script_Master.int", "L_Isl_Script_Slave.int",
        "L_LightH_Audio_Master.int", "L_LightH_Audio_Slave.int",
        "L_LightH_HighChaos_Script.int", "L_LightH_LowChaos_Script.int",
        "L_LightH_Script_Master.int", "L_LightH_Script_Slave.int",
        "L_OutsiderDream_P.int", "L_OutsiderDream_Script.int",
        "L_Ovrsr_Audio.int", "L_Ovrsr_Back_Audio.int", "L_Ovrsr_Back_Script.int",
        "L_Ovrsr_Kennel_Audio.int", "L_Ovrsr_Kennel_Script.int",
        "L_Ovrsr_ReturnPath.int", "L_Ovrsr_Script.int",
        "L_Prison_Audio.int", "L_Prison_P.int",
        "L_PrsnSewer_geo.int", "L_PrsnSewer_P.int", "L_PrsnSewer_RatScene.int",
        "L_PrsnSewer_Script.int", "L_Pub_Assault_Env.int",
        "L_Pub_Day_Audio.int", "L_Pub_Day_Env.int",
        "L_Pub_Dusk_Audio.int", "L_Pub_Dusk_Env.int", "L_Pub_Dusk_P.int",
        "L_Pub_FromBoyle_Script.int", "L_Pub_FromBridge_Script.int",
        "L_Pub_FromBridge_Script_Sleep.int", "L_Pub_FromBrothel_Script.int",
        "L_Pub_FromFlooded_Script.int", "L_Pub_FromOvrsr_Script.int",
        "L_Pub_FromOvrsr_Script_Sleep.int", "L_Pub_FromPrison_Script.int",
        "L_Pub_FromPrison_Script_Sleep.int", "L_Pub_FromTwrReturn_Script.int",
        "L_Pub_Morning_Audio.int", "L_Pub_Morning_Env.int", "L_Pub_Morning_P.int",
        "L_Pub_Night_Audio.int", "L_Pub_Night_Env.int",
        "L_Streets1_Audio.int", "L_Streets1_P.int", "L_Streets1_Script.int",
        "L_Streets2_Audio.int", "L_Streets2_P.int", "L_Streets2_Script.int",
        "L_Streetsewer_Audio.int", "L_Streetsewer_P.int", "L_Streetsewer_Script.int",
        "L_Tower_Script.int",
        "L_TowerRtrn_Int_Audio.int", "L_TowerRtrn_Int_Script.int",
        "L_TowerRtrn_Yard_Audio.int", "L_TowerRtrn_Yard_P.int",
        "L_TowerRtrn_Yard_Roof_Script.int", "L_TowerRtrn_Yard_Script.int",
        "movable_twk.int", "Twk_EmptyHands.int", "Twk_EmptyHands_NPC.int",
        "Twk_UI_MainMenu.int", "Twk_UI_MissionStats.int",
        "WatchTower.int"
    ]
    
    corrupt_files = [f for f in corrupt_files if f != "GFxUI.int"]
    
    safe_print(f"Total CORRUPT files to translate: {len(corrupt_files)}\n")
    
    done = failed = 0
    details = []
    
    for i, fname in enumerate(corrupt_files, 1):
        int_path = os.path.join(INT_DIR, fname)
        th_path = os.path.join(TH_DIR, fname)
        
        if not os.path.exists(int_path):
            safe_print(f"[{i}/{len(corrupt_files)}] {fname}: INT not found - SKIP")
            failed += 1
            details.append(f"{fname}: INT not found")
            continue
        
        safe_print(f"[{i}/{len(corrupt_files)}] Processing: {fname}")
        ok, msg = process_file(int_path, th_path)
        
        if ok:
            done += 1
            safe_print(f" [✓] {fname}: {msg}")
            details.append(f"OK: {fname}: {msg}")
        else:
            failed += 1
            safe_print(f" [✗] {fname}: {msg}")
            details.append(f"FAIL: {fname}: {msg}")
        
        time.sleep(0.3)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as rep:
        rep.write('TRANSLATE CORRUPT RESULTS\n')
        rep.write('=' * 50 + '\n')
        rep.write(f'Total: {len(corrupt_files)}\n')
        rep.write(f'Done: {done}\n')
        rep.write(f'Failed: {failed}\n')
        rep.write('\nDETAILS:\n')
        rep.write('-' * 50 + '\n')
        for d in details:
            rep.write(d + '\n')
    
    safe_print(f"\n=== DONE === Done: {done} Failed: {failed}")
    safe_print(f"Report: {REPORT_PATH}")

if __name__ == "__main__":
    main()