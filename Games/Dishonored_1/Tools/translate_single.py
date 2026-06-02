import requests
import json

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "qwen/qwen3-14b"

FILE_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH.yaml"

def translate_batch(lines, batch_num):
    prompt = """You are a professional Thai translator for the game Dishonored.
Translate the following English text to Thai. Keep the ID format (key: value) unchanged. Only translate the text after the colon.
Use natural Thai suitable for video game dialogue.

"""
    for line in lines:
        prompt += line.rstrip('\n') + "\n"

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 4000
    }

    try:
        resp = requests.post(LM_URL, json=payload, timeout=300)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error: {e}")
        return None

# Read file
with open(FILE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
total = len(lines)
print(f"Total lines: {total}")

# Translate in batches
BATCH_SIZE = 30
translated_lines = []
failed_lines = []

for i in range(0, total, BATCH_SIZE):
    batch = lines[i:i+BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\nTranslating batch {batch_num}/{total_batches} (lines {i+1}-{min(i+BATCH_SIZE, total)})...")
    
    result = translate_batch(batch, batch_num)
    
    if result:
        # Parse result
        result_lines = result.strip().split('\n')
        translated_lines.extend(result_lines)
        print(f"  -> OK ({len(result_lines)} lines translated)")
    else:
        print(f"  -> FAIL, using original")
        translated_lines.extend(batch)
        failed_lines.append(i)

# Write back
with open(FILE_PATH, "w", encoding="utf-8") as f:
    f.write('\n'.join(translated_lines))

print(f"\n=== DONE ===")
print(f"Total lines written: {len(translated_lines)}")
print(f"Batches failed: {len(failed_lines)}")
if failed_lines:
    print(f"Failed batch indices: {failed_lines}")