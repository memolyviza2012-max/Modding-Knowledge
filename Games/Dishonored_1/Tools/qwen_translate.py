import requests
import time
import re

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "qwen/qwen3-14b"

FILE_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH.yaml"
LOG_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\qwen_translate_log.txt"

def translate_lines(lines, log):
    # Just send the text - LM Studio system prompt will handle the rest
    text_to_translate = "\n".join(lines)
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": text_to_translate}],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        resp = requests.post(LM_URL, json=payload, timeout=180)
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"]
        
        # Parse output between <thai_translation> tags
        match = re.search(r'<thai_translation>(.*?)</thai_translation>', result, re.DOTALL)
        if match:
            result_text = match.group(1).strip()
        else:
            # Fallback: try to parse lines with :
            result_text = result
        
        # Split into lines and clean
        result_lines = []
        for line in result_text.split("\n"):
            line = line.strip()
            if line:
                result_lines.append(line)
        
        return result_lines
    except Exception as e:
        log.write(f"  Error: {e}\n")
        log.flush()
        return None

# Read file
with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = f.read().split("\n")

total = len(lines)

with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write(f"Total lines: {total}\n")
    log.write(f"Model: {MODEL}\n")
    log.write(f"Prompt: LM Studio system prompt\n")
    log.flush()
    
    translated = []
    
    for i in range(0, total, 15):
        batch = lines[i:i+15]
        batch_num = i // 15 + 1
        total_batches = (total + 14) // 15
        
        log.write(f"\nBatch {batch_num}/{total_batches}: lines {i+1}-{min(i+15, total)}\n")
        log.flush()
        
        result = translate_lines(batch, log)
        
        if result and len(result) >= len(batch) * 0.7:
            translated.extend(result[:len(batch)])
            log.write(f"  -> OK ({len(result[:len(batch)])} lines)\n")
            log.flush()
            print(f"Batch {batch_num}/{total_batches} OK ({len(result[:len(batch)])} lines)")
        else:
            log.write(f"  -> FAIL, keeping original ({len(result) if result else 0} lines)\n")
            log.flush()
            translated.extend(batch)
            print(f"Batch {batch_num}/{total_batches} FAIL")
        
        time.sleep(0.3)
    
    # Write output
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(translated))
    
    log.write(f"\n=== DONE ===\n")
    log.write(f"Lines written: {len(translated)}\n")
    log.flush()

print(f"\n=== ALL DONE ===")
print(f"Check log: {LOG_FILE}")