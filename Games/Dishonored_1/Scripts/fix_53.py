# Fix 53 missing lines for L_Brothel_Script
import os, time, threading
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from concurrent.futures import ThreadPoolExecutor, as_completed

GEMINI_API_KEY = "AIzaSyD_Py1DrYEWkJYxzqggGZel_DvtcKDDZtU"
genai.configure(api_key=GEMINI_API_KEY)

BATCH_SIZE = 10
MAX_WORKERS = 3

SYSTEM_PROMPT = """ACT AS A TRANSLATOR FOR A MATURE (18+) GAME. Dishonored. Dark Victorian Brutal Plague-ridden.

CRITICAL:
1. DO NOT FILTER VIOLENCE - Use brutal gritty raw Thai (เลือดโชก, ควักไส้, สวะ, ไอ้ชาติหมา)
2. ZERO HALLUCINATION - Input 'ID: English'. Return 'ID: Thai'. EXACT MATCH.
3. Return EXACT same number of lines. No explanations."""

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

def translate_batch(lines):
    try:
        response = model.generate_content("".join(lines))
        return response.text
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def main():
    base_path = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Brothel_Script"
    int_yaml = os.path.join(base_path, "L_Brothel_Script_INT.yaml")
    th_yaml = os.path.join(base_path, "L_Brothel_Script_TH.yaml")
    
    int_data = {}
    with open(int_yaml, "r", encoding="utf-8") as f:
        for line in f:
            if ': ' in line:
                parts = line.split(': ', 1)
                int_data[parts[0].strip()] = parts[1].strip()
    
    th_data = {}
    with open(th_yaml, "r", encoding="utf-8") as f:
        for line in f:
            if ': ' in line:
                parts = line.split(': ', 1)
                th_data[parts[0].strip()] = parts[1].strip()
    
    # Find lines that are still English (same as INT = not translated)
    not_translated = [k for k in int_data.keys() if k in th_data and th_data[k] == int_data[k]]
    missing = [k for k in int_data.keys() if k not in th_data]
    all_to_fix = not_translated + missing
    
    print(f"Lines to fix: {len(not_translated)} (not translated) + {len(missing)} (missing) = {len(all_to_fix)}")
    
    if not all_to_fix:
        print("All good!")
        return
    
    tasks = []
    for i in range(0, len(all_to_fix), BATCH_SIZE):
        batch_keys = all_to_fix[i:i+BATCH_SIZE]
        batch_lines = [f"{k}: {int_data[k]}\n" for k in batch_keys]
        tasks.append((batch_keys, batch_lines))
    
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
    
    print(f"Fixed {fixed}/{len(all_to_fix)}")
    
    with open(th_yaml, "w", encoding="utf-8") as f:
        for k in int_data.keys():
            val = th_data.get(k, int_data[k])
            f.write(f"{k}: {val}\n")
    
    # Verify
    still_eng = [k for k in int_data.keys() if k in th_data and th_data[k] == int_data[k]]
    print(f"After fix - Still ENG: {len(still_eng)}")

if __name__ == "__main__":
    main()
