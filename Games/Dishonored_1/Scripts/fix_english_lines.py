# fix_english_lines.py
# Bulletproof Sniper Logic — compares _INT vs _TH to find gaps, then translates only the broken lines
import os, re, time
from openai import OpenAI

# --- CONFIG ---
BASE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"
LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen/qwen3-14b"
client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio", timeout=600.0)

THAI_SPACING_SYSTEM = """## THAI SPACING RULE (CRITICAL)
Thai text must have spaces between distinct Thai phrases.
Before sending text for translation, insert spaces using PyThaiNLP:
  from pythainlp import word_tokenize
  text = 'สวัสดีครับท่านสมาชิก'
  tokenized = ' '.join(word_tokenize(text, engine='newmm'))
  # Result: 'สวัสดี ครับ ท่าน สมาชิก'
Apply this to EVERY Thai translation result."""

SYSTEM_PROMPT = f"""You are a professional Thai translator for the game Dishonored.

## GLOSSARY (MUST USE)
- Corvo Attano → คอร์โว อัตตาโน
- Emily Kaldwin → เอมิลี่ คาลด์วิน
- Jessamine Kaldwin → เจสซามีน คาลด์วิน
- The Outsider → ดิ เอาท์ไซเดอร์
- Lord Regent → อัครมหาเสนาบดี
- High Overseer → ไฮโอเวอร์เซียร์
- Overseer → โอเวอร์เซียร์
- Bottle Street Gang → แก๊งบอตเทิลสตรีต
- Whalers → พวกเวลเลอร์
- The Void → เดอะวอยด์
- Weepers → วีปเปอร์
- Tallboys → ทอลบอย
- Bonecharm → เครื่องราง
- Blink → บลิงก์
- Dunwall → ดันวอลล์
- Daud → ดาวด์

{THAI_SPACING_SYSTEM}

## RULES
1. Input: "ID: English text". Output: "ID: Thai translation"
2. Preserve all variables (%s, %d, {{0}}, \\n, \\r, <font>)
3. Match tone: dark, gritty, violent dialogue
4. SOUND EFFECTS like '* ... *' keep format exactly
5. NO COMMENTARY — output only translations
6. Return EXACT same number of lines as input
"""

def has_thai(text):
    return bool(re.search(r'[\u0e00-\u0e7f]', text))

def has_az(text):
    return bool(re.search(r'[a-zA-Z]', text))

def parse_yaml_dict(filepath):
    """Parse a _INT.yaml or _TH.yaml into a dict {key: value}."""
    data = {}
    with open(filepath, encoding='utf-8-sig') as f:
        for line in f:
            line = line.rstrip('\n\r')
            if ': ' not in line:
                continue
            # Find first ': ' separator (keys can have colons in them but values usually after first ': ')
            parts = line.split(': ', 1)
            if len(parts) == 2:
                k, v = parts[0].strip(), parts[1].strip()
                if k:
                    data[k] = v
    return data

def build_yaml_from_dict(data, ordered_keys):
    """Build lines preserving order from ordered_keys."""
    lines = []
    for k in ordered_keys:
        v = data.get(k, "")
        lines.append(f"{k}: {v}")
    return lines

def translate_batch(lines_content, retries=3):
    """Send lines to Qwen3/LM Studio for translation."""
    prompt = SYSTEM_PROMPT + "\n\n## TEXT TO TRANSLATE (preserve IDs):\n"
    prompt += "\n".join(lines_content)
    prompt += "\n\nOutput only — one translation per line:"

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=LM_STUDIO_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            text = resp.choices[0].message.content
            translated = {}
            for line in text.strip().split("\n"):
                line = line.strip()
                line = re.sub(r"^[\d\.\)\-\*]+\s*", "", line)
                if ': ' not in line:
                    continue
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    k, v = parts[0].strip(), parts[1].strip()
                    if k:
                        translated[k] = v
            return translated
        except Exception as e:
            print(f"  [ERROR] Attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt * 2)
    return None

def fix_file(folder_name, th_filename, max_lines=200, expected_lines=None):
    """
    Bulletproof sniper logic:
    1. Load INT as baseline
    2. Load TH as current state
    3. Find targets: TH is empty OR TH == INT OR TH has no Thai chars
    4. Only flag if INT source has A-Z (needs real translation)
    5. Translate only those lines
    6. Rebuild TH from INT with updated translations
    """
    int_path = os.path.join(BASE_DIR, folder_name, th_filename.replace('_TH', '_INT'))
    th_path = os.path.join(BASE_DIR, folder_name, th_filename)

    if not os.path.exists(int_path):
        print(f"  [SKIP] INT not found: {int_path}")
        return False
    if not os.path.exists(th_path):
        print(f"  [SKIP] TH not found: {th_path}")
        return False

    int_data = parse_yaml_dict(int_path)
    th_data = parse_yaml_dict(th_path)

    # Use INT key order as canonical
    int_keys = list(int_data.keys())
    int_count = len(int_keys)
    th_count = len(th_data)

    if expected_lines and abs(int_count - expected_lines) > 5:
        print(f"  [WARN] Line count mismatch: INT={int_count}, expected={expected_lines}")

    # 3. Find sniper targets
    keys_to_translate = []
    for k, v_int in int_data.items():
        v_th = th_data.get(k, "")
        # Criteria: empty OR matches INT exactly OR has no Thai chars
        needs_fix = (
            not v_th.strip() or           # TH is empty
            v_th.strip() == v_int.strip() or  # TH identical to INT (untranslated)
            not has_thai(v_th)            # TH has no Thai at all
        )
        if needs_fix and has_az(v_int):   # Only translate if INT source has A-Z
            keys_to_translate.append(k)

    if not keys_to_translate:
        print(f"  [✓] {folder_name}: all {int_count} lines translated (sniper found no targets)")
        return True

    print(f"  🎯 {folder_name}: {len(keys_to_translate)}/{int_count} lines need fixing")

    # 4. Translate in one shot
    lines_to_translate = [f"{k}: {int_data[k]}" for k in keys_to_translate]
    translated = translate_batch(lines_to_translate)

    if translated is None:
        print(f"  [✗] Translation failed")
        return False

    # 5. Update TH data with translations
    fix_count = 0
    for k in keys_to_translate:
        if k in translated:
            th_data[k] = translated[k]
            fix_count += 1

    # 6. Rebuild TH from INT (preserves key order and any extra keys)
    # Start with INT baseline, overlay TH data
    final_lines = []
    for k in int_keys:
        v = th_data.get(k, int_data[k])  # TH translation or fall back to INT
        final_lines.append(f"{k}: {v}")

    with open(th_path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(final_lines))

    print(f"  [✓] Fixed {fix_count}/{len(keys_to_translate)} lines — file rebuilt 💾")
    return True


def main():
    PROBLEM_FILES = [
        ("L_Bridge_Part1c_Script",         "L_Bridge_Part1c_Script_TH.yaml"),
        ("L_Flooded_FStreets_Script",      "L_Flooded_FStreets_Script_TH.yaml"),
        ("L_Galvani1_Scripts",             "L_Galvani1_Scripts_TH.yaml"),
        ("L_Galvani1_Strt1_Scripts",       "L_Galvani1_Strt1_Scripts_TH.yaml"),
        ("L_Galvani1_Strt2_Scripts",       "L_Galvani1_Strt2_Scripts_TH.yaml"),
        ("L_Isl_HighChaos_Script",         "L_Isl_HighChaos_Script_TH.yaml"),
        ("L_Isl_LowChaos_Script",          "L_Isl_LowChaos_Script_TH.yaml"),
        ("L_Isl_Script_Master",            "L_Isl_Script_Master_TH.yaml"),
        ("L_Isl_Script_Slave",             "L_Isl_Script_Slave_TH.yaml"),
        ("L_LightH_HighChaos_Script",      "L_LightH_HighChaos_Script_TH.yaml"),
        ("L_LightH_LowChaos_Script",       "L_LightH_LowChaos_Script_TH.yaml"),
        ("L_Ovrsr_Back_Script",            "L_Ovrsr_Back_Script_TH.yaml"),
        ("L_Ovrsr_Kennel_Script",          "L_Ovrsr_Kennel_Script_TH.yaml"),
        ("L_Ovrsr_Script",                 "L_Ovrsr_Script_TH.yaml"),
        ("L_Prison_Script",                "L_Prison_Script_TH.yaml"),
        ("L_PrsnSewer_RatScene",           "L_PrsnSewer_RatScene_TH.yaml"),
        ("L_PrsnSewer_Script",             "L_PrsnSewer_Script_TH.yaml"),
        ("L_Pub_FromBoyle_Script",         "L_Pub_FromBoyle_Script_TH.yaml"),
        ("L_Pub_FromBridge_Script",        "L_Pub_FromBridge_Script_TH.yaml"),
        ("L_Pub_FromBridge_Script_Sleep",   "L_Pub_FromBridge_Script_Sleep_TH.yaml"),
        ("L_Pub_FromFlooded_Script",       "L_Pub_FromFlooded_Script_TH.yaml"),
        ("L_Pub_FromOvrsr_Script_Sleep",   "L_Pub_FromOvrsr_Script_Sleep_TH.yaml"),
        ("L_Pub_FromPrison_Script",        "L_Pub_FromPrison_Script_TH.yaml"),
        ("L_Pub_FromPrison_Script_Sleep",  "L_Pub_FromPrison_Script_Sleep_TH.yaml"),
        ("L_Pub_FromTwrReturn_Script",     "L_Pub_FromTwrReturn_Script_TH.yaml"),
        ("L_Streets1_Script",              "L_Streets1_Script_TH.yaml"),
        ("L_Streets2_Script",              "L_Streets2_Script_TH.yaml"),
        ("L_TowerRtrn_Int_Script",         "L_TowerRtrn_Int_Script_TH.yaml"),
        ("L_TowerRtrn_Yard_Roof_Script",   "L_TowerRtrn_Yard_Roof_Script_TH.yaml"),
        ("L_TowerRtrn_Yard_Script",        "L_TowerRtrn_Yard_Script_TH.yaml"),
    ]

    print(f"=== Sniper Fix — {len(PROBLEM_FILES)} files ===\n")
    success = 0
    failed = 0

    for folder, th in PROBLEM_FILES:
        print(f"[{folder}]")
        ok = fix_file(folder, th)
        if ok:
            success += 1
        else:
            failed += 1
        time.sleep(0.5)

    print(f"\n=== SUMMARY ===")
    print(f"OK: {success} | Failed: {failed}")


if __name__ == "__main__":
    main()
