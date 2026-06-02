# Fix missing translations for L_Brothel_Script
import os, sys, time, threading
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

GEMINI_API_KEY = "AIzaSyD_Py1DrYEWkJYxzqggGZel_DvtcKDDZtU"
genai.configure(api_key=GEMINI_API_KEY)

BATCH_SIZE = 10
MAX_WORKERS = 3

SYSTEM_PROMPT = """
ACT AS A TRANSLATOR FOR A MATURE (18+) GAME. 
Game: Dishonored. Setting: Dunwall (Dark, Victorian, Brutal, Plague-ridden).

CRITICAL DIRECTIVES:
1. DO NOT FILTER VIOLENCE: Use brutal, gritty, raw Thai words.
2. ZERO HALLUCINATION: Input is 'ID: English'. Return 'ID: Thai'. 
3. LINE INTEGRITY: Return EXACTLY same number of lines. No explanations.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
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

def translate_batch(lines):
    try:
        response = model.generate_content("".join(lines))
        return response.text
    except Exception as e:
        safe_print(f"ERROR: {e}")
        return None

def main():
    base_path = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Brothel_Script"
    int_yaml = os.path.join(base_path, "L_Brothel_Script_INT.yaml")
    th_yaml = os.path.join(base_path, "L_Brothel_Script_TH.yaml")
    
    # Read INT
    int_data = {}
    with open(int_yaml, "r", encoding="utf-8") as f:
        for line in f:
            if ': ' in line:
                parts = line.split(': ', 1)
                int_data[parts[0].strip()] = parts[1].strip()
    
    # Read TH
    th_data = {}
    if os.path.exists(th_yaml):
        with open(th_yaml, "r", encoding="utf-8") as f:
            for line in f:
                if ': ' in line:
                    parts = line.split(': ', 1)
                    th_data[parts[0].strip()] = parts[1].strip()
    
    # Find missing
    missing_keys = [k for k in int_data.keys() if k not in th_data or not th_data[k]]
    print(f"INT lines: {len(int_data)}, TH lines: {len(th_data)}, MISSING: {len(missing_keys)}")
    
    if not missing_keys:
        print("Nothing to fix!")
        return
    
    # Translate missing
    print(f"Translating {len(missing_keys)} missing lines...")
    
    tasks = []
    for i in range(0, len(missing_keys), BATCH_SIZE):
        batch_keys = missing_keys[i:i+BATCH_SIZE]
        batch_lines = [f"{k}: {int_data[k]}\n" for k in batch_keys]
        tasks.append((batch_keys, batch_lines))
    
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    fixed = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(translate_batch, t[1]): t for t in tasks}
        for future in as_completed(futures):
            keys, _ = futures[future]
            res = future.result()
            if res:
                res_lines = [l.strip() for l in res.split('\n') if ': ' in l]
                for rl in res_lines:
                    p = rl.split(': ', 1)
                    if p[0].strip() in keys:
                        th_data[p[0].strip()] = p[1].strip()
                        fixed += 1
            time.sleep(0.3)
    
    print(f"Fixed {fixed}/{len(missing_keys)} lines")
    
    # Write final TH
    with open(th_yaml, "w", encoding="utf-8") as f:
        for k in int_data.keys():
            val = th_data.get(k, int_data[k])
            f.write(f"{k}: {val}\n")
    
    print(f"Written: {th_yaml}")
    
    # Verify
    th_count = len(open(th_yaml, "r", encoding="utf-8").readlines())
    print(f"Final TH lines: {th_count} (should be {len(int_data)})")

if __name__ == "__main__":
    main()
