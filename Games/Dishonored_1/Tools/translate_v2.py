import requests
import json
import time

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "qwen/qwen3-14b"

FILE_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH.yaml"
OUTPUT_FILE = FILE_PATH

BATCH_SIZE = 15

def translate_lines(lines):
    text_to_translate = "\n".join(lines)
    
    prompt = f"""Translate to Thai. Keep format exactly. Only output the translation.
{text_to_translate}"""

    payload = {{
        "model": MODEL,
        "messages": [{{"role": "user", "content": prompt}}],
        "temperature": 0.3,
        "max_tokens": 2000
    }}

    for attempt in range(3):
        try:
            resp = requests.post(LM_URL, json=payload, timeout=120)
            resp.raise_for_status()
            result = resp.json()["choices"][0]["message"]["content"]
            # Parse result - split by newlines
            result_lines = [l.strip() for l in result.strip().split('\n') if l.strip()]
            return result_lines
        except Exception as e:
            print(f"  Attempt {{attempt+1}} failed: {{e}}")
            time.sleep(3)
    return None

# Read file
with open(FILE_PATH, "r", encoding="utf-8") as f:
    lines = f.read().split('\n')

total = len(lines)
print(f"Total lines: {{total}}")

translated = []
batch_num = 0

for i in range(0, total, BATCH_SIZE):
    batch = lines[i:i+BATCH_SIZE]
    batch_num += 1
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\nBatch {{batch_num}}/{{total_batches}}: lines {{i+1}}-{{min(i+BATCH_SIZE, total)}}")
    
    result = translate_lines(batch)
    
    if result and len(result) >= len(batch) * 0.8:
        # Take only the right number of lines
        translated.extend(result[:len(batch)])
        print(f"  -> OK ({{len(result[:len(batch)])}} lines)")
    else:
        print(f"  -> FAIL ({{len(result) if result else 0}} lines), keeping original")
        translated.extend(batch)
    
    time.sleep(0.5)

# Write output
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write('\n'.join(translated))

print(f"\n=== DONE ===")
print(f"Lines written: {{len(translated)}}")