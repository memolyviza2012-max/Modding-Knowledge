# Dishonored Thai Translation - Shield Engine V.3 (Tier-Based Prompts)
# ใช้ร่วมกับ LM Studio (qwen3-14b) + PyThaiNLP

import re
import json
import urllib.request
import datetime
import os
from pythainlp import word_tokenize

LM_URL = "http://localhost:1234/v1/chat/completions"
MODEL = "qwen/qwen3-14b"
SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT"
OUTPUT_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated"
OUTPUT_LOG = r"C:\Users\WiT.Danaiwit\.openclaw\workspace\translate_v3_log.txt"

# ==========================================
# DISHONORED: DYNAMIC SYSTEM PROMPTS
# ==========================================

GLOSSARY_RULES = """
CRITICAL GLOSSARY & TERMINOLOGY (DO NOT TRANSLATE BLINDLY. USE THESE EXACT THAI TERMS):

[Characters & Titles]
- Corvo Attano: คอร์โว อัตตาโน
- Emily Kaldwin: เอมิลี่ คาลด์วิน
- Jessamine Kaldwin: เจสซามีน คาลด์วิน
- The Outsider: ดิ เอาท์ไซเดอร์
- Lord Regent: ผู้สำเร็จราชการ
- High Overseer: ผู้คุมกฎสูงสุด
- Royal Protector: ราชองครักษ์
- The Loyalists: กลุ่มผู้ภักดี

[Factions]
- Abbey of the Everyman: อารามแห่งสามัญชน
- Overseers: ผู้คุมกฎ
- City Watch: หน่วยยามรักษาเมือง
- Bottle Street Gang: แก๊งบอตเทิลสตรีต
- Hatters: แก๊งแฮตเตอร์
- Whalers: พวกเวลเลอร์

[Powers & Items]
- Blink: บลิงก์
- Dark Vision: เนตรมืด
- Bend Time: บิดเบือนเวลา
- Rune: รูน
- Bonecharm: เครื่องรางกระดูก
- Whale Oil: น้ำมันวาฬ
- Springrazor: สปริงเรเซอร์
- Wall of Light: กำแพงแสง
- Arc Pylon: เสาอาร์ก
- Sokolov's Elixir: ยาชูกำลังของโซโคลอฟ
- Piero's Spiritual Remedy: ยารักษาจิตวิญญาณของปิเอโร่

[Locations & Lore]
- Dunwall: ดันวอลล์
- The Void: เดอะวอยด์
- Rat Plague: กาฬโรคหนู
- Weepers: วีปเปอร์
- Tallboys: ทอลบอย
- Hound Pits Pub: ฮาวด์พิตส์ผับ
- The Golden Cat: เดอะโกลเด้นแคท
- Coldridge Prison: เรือนจำโคลดริดจ์

RULE: Do NOT translate or modify programming variables (e.g. %s, %d, {0}) or UI tags (e.g. <font color="#FFFFFF">, <br>). Keep them exactly as they are.
"""

TIER_PROMPTS = {
    "Tier_1_UI": f"""You are an expert English-to-Thai video game localization specialist working on "Dishonored" (Dark Victorian Steampunk setting).
Your current task is translating Tier 1: UI, Menus, HUD, and System Messages.
Guidelines:
1. Keep the translation EXTREMELY concise, short, and clear.
2. Use standard gaming terminology in Thai (e.g., "บันทึกเกม" for Save, "ตั้งค่า" for Settings).
3. Do NOT use flowery language. Do NOT add periods (.) at the end of single words or menu items.
4. Output ONLY the translated Thai text.
{GLOSSARY_RULES}""",

    "Tier_2_Gameplay": f"""You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your current task is translating Tier 2: Items, Weapons, Upgrades, and In-world Interactables (Tweaks).
Guidelines:
1. Focus on clear, descriptive names for items and concise instructions for upgrades.
2. For interactables (e.g., "Locked", "Requires Key"), use direct and natural Thai phrases (e.g., "ถูกล็อก", "ต้องใช้กุญแจ").
3. Output ONLY the translated Thai text.
{GLOSSARY_RULES}""",

    "Tier_3_Subtitles": f"""You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your current task is translating Tier 3: Character Dialogues, Story Subtitles, and Voice-overs.
Guidelines:
1. Focus on emotional impact, conversational flow, and character voice.
2. The society in Dunwall is class-divided. Use appropriate Thai pronouns:
   - Royalty/Nobility: Use formal or royal Thai (คำราชาศัพท์เบื้องต้น).
   - Guards/Thugs/Gangs: Use rough, aggressive Thai (ข้า, เอ็ง, แก, ไอสวะ).
   - The Outsider: Use a calm, detached, and mysterious tone.
3. Output ONLY the translated Thai text.
{GLOSSARY_RULES}""",

    "Tier_4_Lore": f"""You are an expert English-to-Thai video game localization specialist working on "Dishonored".
Your current task is translating Tier 4: Books, Journals, Notes, and Lore documents.
Guidelines:
1. Use a highly descriptive, narrative, and slightly formal or archaic Thai style appropriate for Victorian-era literature.
2. Pay attention to paragraph structure and storytelling flow. Make it a joy to read.
3. Output ONLY the translated Thai text.
{GLOSSARY_RULES}"""
}

# ==========================================
# TIER DETECTION BY FILENAME
# ==========================================

def detect_tier(filename):
    """Detect which tier a file belongs to based on its name"""
    f = filename.lower()

    # Tier 1: UI, Menus, HUD
    ui_keywords = ["ui", "menu", "hud", "front-end", "tweak", "msg"]
    if any(k in f for k in ui_keywords):
        return "Tier_1_UI"

    # Tier 2: Gameplay (items, weapons, upgrades, interactables)
    gp_keywords = ["item", "weapon", "power", "bonecharm", "rune", "upgrade", "pickup", "tweak"]
    if any(k in f for k in gp_keywords):
        # Exclude files that are clearly UI tweaks
        if "twk" in f and any(k in f for k in ["ui", "menu", "hud"]):
            return "Tier_1_UI"
        return "Tier_2_Gameplay"

    # Tier 3: Subtitles, dialogues, scripts
    sub_keywords = ["subtitles", "vo", "dialog", "mission", "l_", "conv", "script", "story"]
    if any(k in f for k in sub_keywords):
        return "Tier_3_Subtitles"

    # Tier 4: Lore (books, notes, journals, audiographs)
    lore_keywords = ["book", "note", "journal", "lore", "audiograph", "text"]
    if any(k in f for k in lore_keywords):
        return "Tier_4_Lore"

    # System & Config files
    sys_keywords = ["engine", "system", "game", "config", "default", "online"]
    if any(k in f for k in sys_keywords):
        return "Tier_2_Gameplay"  # Treat system files as Gameplay tier

    # Others: default to Tier_2_Gameplay
    return "Tier_2_Gameplay"

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
    btn_combos = re.findall(r'[A-Za-z_]+\s*\+\s*[A-Za-z_]+', text)
    for combo in btn_combos:
        if combo not in tags and f'`{combo}`' not in text:
            tags.append(combo)

    # Pattern 5: Escape sequences \n \r
    escapes = re.findall(r'\\[nr]', text)
    tags.extend(escapes)

    # Deduplicate
    return list(dict.fromkeys(tags))

def mask_text(text, tags):
    """สวมหน้ากากให้ Tags ทั้งหมด"""
    masked = text
    for i, tag in enumerate(tags):
        masked = masked.replace(tag, f'[[T{i}]]')
    return masked

def unmask_text(text, tags):
    """ถอดหน้ากากคืน"""
    unmasked = text
    for i, tag in enumerate(tags):
        unmasked = unmasked.replace(f'[[T{i}]]', tag)
    return unmasked

# ===== TRANSLATION ENGINE (Tier-Aware) =====

def translate_via_lm(prompt_text, tier, max_len=200):
    """Call LM Studio with tier-specific system prompt"""
    system_prompt = TIER_PROMPTS.get(tier, TIER_PROMPTS["Tier_1_UI"])

    messages = [
        {"role": "system", "content": system_prompt},
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
    thai_text = thai_text.strip('"').strip()
    thai_text = re.sub(r'(?<=[ก-๙])\s+(?=[ก-๙])', '', thai_text)
    thai_text = thai_text.replace('ผม', 'ฉัน')
    thai_text = thai_text.replace('ครับ', '').replace('ค่ะ', '')
    return thai_text

def process_ue3_int_line(line, translate_func, tier):
    """
    THE SHIELD ENGINE V.2 - ฟังก์ชันหลักในการประมวลผลบรรทัด .INT
    """
    clean_line = line.strip()

    if not clean_line:
        return line

    if clean_line.startswith('[') and clean_line.endswith(']'):
        return line

    if clean_line.startswith(';') or clean_line.startswith('//'):
        return line

    match_a = re.match(r'^([^=]+)="(.*)"\s*$', clean_line)
    match_b = re.match(r'^([^=]+)=\(m_Description="(.*)"\)\s*$', clean_line)

    if match_a:
        key, original_text = match_a.groups()
        fmt = 'A'
    elif match_b:
        key, original_text = match_b.groups()
        fmt = 'B'
    else:
        return line

    if not original_text:
        return line

    if not is_english_text(original_text):
        return line

    tags = extract_tags(original_text)
    masked_text = mask_text(original_text, tags)

    translated = translate_func(masked_text, tier)

    if translated.startswith('[ERR'):
        return line

    translated = post_process(translated)
    unmasked = unmask_text(translated, tags)

    if re.search(r'[\u0E00-\u0E7F]', unmasked):
        unmasked = tokenize_thai(unmasked)

    if fmt == 'B':
        return f'{key}=(m_Description="{unmasked}")\n'
    else:
        return f'{key}="{unmasked}"\n'

# ===== MAIN =====

def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    with open(OUTPUT_LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{ts}] {msg}\n")

def process_file(filepath, tier):
    """Process a single .int file with the specified tier"""
    log(f"=== Processing: {os.path.basename(filepath)} | Tier: {tier} ===")

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    translated = 0
    skipped = 0

    for i, line in enumerate(lines):
        result = process_ue3_int_line(line, translate_via_lm, tier)
        if result != line:
            translated += 1
        else:
            skipped += 1
        lines[i] = result

        if translated % 20 == 0 and translated > 0:
            log(f"  Progress: {translated} translated in {os.path.basename(filepath)}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    log(f"=== Done: {os.path.basename(filepath)} | {translated} translated, {skipped} skipped ===")
    return translated, skipped

def main():
    log("=== Shield Engine V.3 (Tier-Based) Started ===")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files_to_process = []
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith('.int'):
                files_to_process.append(os.path.join(root, file))

    log(f"Found {len(files_to_process)} .INT files to process")
    print(f"Found {len(files_to_process)} .INT files to process")

    total_translated = 0
    total_skipped = 0

    for filepath in files_to_process:
        filename = os.path.basename(filepath)
        tier = detect_tier(filename)

        # Copy to output dir (or process in place)
        out_path = os.path.join(OUTPUT_DIR, filename)
        if filepath != out_path:
            import shutil
            shutil.copy2(filepath, out_path)

        t, s = process_file(out_path, tier)
        total_translated += t
        total_skipped += s

    log(f"=== COMPLETE! Total: {total_translated} translated, {total_skipped} skipped ===")
    print(f"[OK] Done! {total_translated} lines translated, {total_skipped} skipped.")

if __name__ == "__main__":
    main()