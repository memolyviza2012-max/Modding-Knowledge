import requests
import time

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "google/gemma-4-e4b"

FILE_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH.yaml"

PROMPT_TEMPLATE = """You are a professional Thai translator for the video game DISHONORED.

RULES:
- Keep the ID format exactly: "KeyID: Thai translation"
- Only translate the TEXT after the colon, not the ID
- Use natural Thai dialogue suitable for a dark stealth action game
- Character names: Corvo=คอร์โว, Emily=เอมิลี่, Outsider=เอาท์ไซเดอร์, Abbey=อาราม, Dunwall=ดันวอลล์, Void=วอยด์, Whale=วาฬ, Overseer=ผู้คุม, Lord Regent=ผู้สำเร็จราช, High Overseer=ผู้คุมกฎสูงสุด, Rune=รูน, Bonecharm=เครื่องรางกระดูก, Blink=บลิงก์, Dark Vision=เนตรมืด, Bend Time=บิดเบือนเวลา, Whale Oil=น้ำมันวาฬ, Weepers=วีปเปอร์, Tallboys=ทอลบอย

Translate the following English text to Thai:

{lines}

THAI TRANSLATION:
"""

def translate_lines(lines):
    text_to_translate = "\n".join(lines)
    prompt = PROMPT_TEMPLATE.format(lines=text_to_translate)

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        resp = requests.post(LM_URL, json=payload, timeout=180)
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"]
        # Parse - remove prompt text, keep only translations
        if "THAI TRANSLATION:" in result:
            result = result.split("THAI TRANSLATION:")[-1]
        result_lines = [l.strip() for l in result.strip().split('\n') if l.strip() and ': ' in l]
        return result_lines
    except Exception as e:
        print(f"  Error: {e}")
        return None

# Read file
with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = f.read().split('\n')

total = len(lines)
print(f"Total lines: {total}")

translated = []

for i in range(0, total, 15):
    batch = lines[i:i+15]
    batch_num = i // 15 + 1
    total_batches = (total + 14) // 15
    
    print(f"\nBatch {batch_num}/{total_batches}: lines {i+1}-{min(i+15, total)}")
    
    result = translate_lines(batch)
    
    if result and len(result) >= len(batch) * 0.7:
        translated.extend(result[:len(batch)])
        print(f"  -> OK ({len(result[:len(batch)])} lines)")
    else:
        print(f"  -> FAIL, keeping original")
        translated.extend(batch)
    
    time.sleep(0.5)

# Write output
with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write('\n'.join(translated))

print(f"\n=== DONE ===")
print(f"Lines written: {len(translated)}")