import requests
import time

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "google/gemma-4-e4b"

FILE_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH.yaml"
LOG_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\translate_log.txt"

PROMPT_TEMPLATE = """You are a professional Thai translator for the video game DISHONORED.

RULES:
- Keep the ID format exactly: "KeyID: Thai translation"
- Only translate the TEXT after the colon, not the ID
- Use natural Thai dialogue suitable for a dark stealth action game
- Character names: Corvo=คอร์โว, Emily=เอมิลี่, Outsider=เอาท์ไซเดอร์, Abbey=อาราม, Dunwall=ดันวอลล์, Void=วอยด์, Whale=วาฬ, Overseer=ผู้คุม, Lord Regent=ผู้สำเร็จราช, High Overseer=ผู้คุมกฎสูงสุด

Translate to Thai:

{lines}

THAI TRANSLATION:
"""

def translate_lines(lines, log):
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
        # Parse - keep only lines with : 
        if "THAI TRANSLATION:" in result:
            result = result.split("THAI TRANSLATION:")[-1]
        result_lines = [l.strip() for l in result.strip().split('\n') if l.strip() and ': ' in l]
        return result_lines
    except Exception as e:
        log.write(f"  Error: {e}\n")
        log.flush()
        return None

# Read file
with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = f.read().split('\n')

total = len(lines)

with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write(f"Total lines: {total}\n")
    log.flush()
    
    translated = []
    
    for i in range(0, total, 10):
        batch = lines[i:i+10]
        batch_num = i // 10 + 1
        total_batches = (total + 9) // 10
        
        log.write(f"\nBatch {batch_num}/{total_batches}: lines {i+1}-{min(i+10, total)}\n")
        log.flush()
        
        result = translate_lines(batch, log)
        
        if result and len(result) >= len(batch) * 0.7:
            translated.extend(result[:len(batch)])
            log.write(f"  -> OK ({len(result[:len(batch)])} lines)\n")
        else:
            log.write(f"  -> FAIL, keeping original\n")
            log.flush()
            translated.extend(batch)
        
        time.sleep(0.5)
    
    # Write output
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write('\n'.join(translated))
    
    log.write(f"\n=== DONE ===\n")
    log.write(f"Lines written: {len(translated)}\n")
    log.flush()

print("Done! Check translate_log.txt")