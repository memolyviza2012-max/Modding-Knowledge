import requests
import time

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "google/gemma-4-e4b"

FILE_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH.yaml"
LOG_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\translate_log2.txt"

def translate_lines(lines, log):
    # Simple prompt - just give lines and ask for Thai
    text_to_translate = "\n".join(lines)
    prompt = f"Translate to Thai:\n{text_to_translate}"
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        resp = requests.post(LM_URL, json=payload, timeout=120)
        resp.raise_for_status()
        result = resp.json()["choices"][0]["message"]["content"]
        # Split by lines and filter valid ones
        result_lines = []
        for line in result.strip().split('\n'):
            line = line.strip()
            if line and ': ' in line:
                result_lines.append(line)
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
            log.write(f"  -> FAIL ({len(result) if result else 0} lines), keeping original\n")
            log.flush()
            translated.extend(batch)
        
        time.sleep(0.3)
    
    # Write output
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        f.write('\n'.join(translated))
    
    log.write(f"\n=== DONE ===\n")
    log.write(f"Lines written: {len(translated)}\n")
    log.flush()

print("Done!")