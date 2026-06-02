# ==========================================
# persistent_runner.py
# รันต่อจากจุดเดิม พร้อม Auto-Resume & Auto-Restart
# ==========================================
import os, sys, shutil, subprocess, yaml, warnings, time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

warnings.filterwarnings("ignore")

# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyD_Py1DrYEWkJYxzqggGZel_DvtcKDDZtU"
genai.configure(api_key=GEMINI_API_KEY)

WORKSPACE = "D:\\Mod_Workspace\\Dishonored_Mod_Workspace"
SOURCE_DIR = f"{WORKSPACE}\\01_source"
WORK_DIR = f"{WORKSPACE}\\03_working"
OUTPUT_DIR = f"{WORKSPACE}\\02_translated"
TOOL_DECOMPRESS = "D:\\Mod_Workspace\\Tool\\UE3\\decompress\\decompress.exe"
TOOL_SUBEDIT = "D:\\Mod_Workspace\\Tool\\UE3\\dishonored-toolkit-main\\subedit.py"

# Gemini 2.5 Flash - Performance Tuned
BATCH_SIZE = 25
MAX_WORKERS = 8  # เพิ่มจาก 4 เพื่อ Parallel throughput
MAX_RETRIES = 3
RETRY_DELAY = 3
# ---------------------

SYSTEM_PROMPT = """
Act as a Master-Level English-to-Thai Video Game Localization Specialist. Your assignment is "Dishonored" — a dark, gritty, stealth-action game set in "Dunwall" (an industrial, steampunk/Victorian-era city plagued by a deadly rat disease and ruled by a corrupt government).

Your ultimate goal is to deliver highly natural, immersive, and culturally accurate Thai translations while strictly adhering to the game engine's technical constraints.

=== 1. FORMATTING RULES (ABSOLUTE LAWS) ===
- EXACT MATCH: The input consists of lines formatted as `ID: English Text`. You MUST keep the `ID: ` prefix exactly as it is. ONLY translate the text after the colon.
- LINE COUNT: Return exactly the same number of lines as the input. Do not add bullet points, explanations, or quotes.

=== 2. TONE & CONTEXTUAL RULES ===
- Atmosphere: Dark, serious, mature, and cynical.
- Dialogue & Lore: Make it read like a translated Victorian novel.
- Class-Based Pronouns: 
 > Nobility/Royalty (Empress, Lord Regent): Use กระหม่อม, ฝ่าบาท, ท่าน
 > Guards/Thugs/Lower Class: Use ข้า, เอ็ง, แก, สวะ, ไอ้
 > The Outsider: Use เรา, เจ้า
 > Fallback: Use ฉัน, คุณ, เขา

=== 3. TECHNICAL CONSTRAINTS ===
- ANTI-SQUISH: You MUST insert normal spaces ( ) between distinct Thai phrases or clauses. NEVER break a single word with a space.
- PRESERVE VARIABLES: Tags like %s, %d, {0}, [[T0]], \\n MUST remain intact.

=== 4. OFFICIAL GLOSSARY ===
- Corvo Attano = คอร์โว อัตตาโน
- Emily Kaldwin = เอมิลี่ คาลด์วิน
- Jessamine Kaldwin = เจสซามีน คาลด์วิน
- The Outsider = ดิ เอาท์ไซเดอร์
- Lord Regent = อัครมหาเสนาบดี
- High Overseer = ไฮโอเวอร์เซียร์
- Overseer = โอเวอร์เซียร์
- Abbey of the Everyman = นิกายเอเวอรีแมน
- Bottle Street Gang = แก๊งบอตเทิลสตรีต
- Whalers = พวกเวลเลอร์
- The Void = เดอะวอยด์
- Rat Plague = กาฬโรคหนู
- Weepers = วีปเปอร์
- Tallboys = ทอลบอย
- Bonecharm = เครื่องราง
- Rune = รูน
- Whale oil = น้ำมันวาฬ
- Blink = บลิงก์
- Dark Vision = ดาร์กวิชัน
- Bend Time = เบนด์ไทม์
- Springrazor = สปริงเรเซอร์
- Wall of Light = วอลล์ออฟไลต์
- Arc Pylon = อาร์กไพลอน
"""

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

PRINT_LOCK = threading.Lock()

def safe_log(log_file, message, print_console=True):
    with PRINT_LOCK:
        if print_console:
            print(message.strip())
        log_file.write(message)
        log_file.flush()

def translate_batch(lines, retry_count=0):
    prompt = "".join(lines)
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.3)
        )
        return response.text
    except Exception as e:
        if retry_count < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
            return translate_batch(lines, retry_count + 1)
        return None

def process_batch_task(task_args):
    rel_idx, batch_lines, batch_num, total_batches = task_args
    time.sleep(0.2)  # ลด delay เพิ่ม throughput
    result = translate_batch(batch_lines)
    retries = 0
    while not result and retries < 2:
        time.sleep(2)
        result = translate_batch(batch_lines)
        retries += 1
    return (rel_idx, result, batch_lines, batch_num, total_batches)

def run_command(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def clean_yaml(th_yaml_path, int_yaml_path):
    with open(int_yaml_path, "r", encoding="utf-8") as f:
        int_lines = {line.split(': ', 1)[0].strip(): line.split(': ', 1)[1].strip() for line in f if ': ' in line.strip()}
    if not os.path.exists(th_yaml_path):
        return False
    with open(th_yaml_path, "r", encoding="utf-8") as f:
        translated = {line.split(': ', 1)[0].strip(): line.split(': ', 1)[1].strip() if len(line.split(': ', 1)) > 1 else '' for line in f.read().split('\n') if line.strip() and ': ' in line}
    clean_data = {key: translated.get(key, int_lines[key]) for key in int_lines}
    with open(th_yaml_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(clean_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return True

def get_upk_list():
    upks = []
    folders = [
        ("CookedPCConsole", "CookedPCConsole"),
        ("DLC\\PCConsole\\DLC05", "DLC\\DLC05"),
        ("DLC\\PCConsole\\DLC06", "DLC\\DLC06"),
        ("DLC\\PCConsole\\DLC07", "DLC\\DLC07")
    ]
    for src_sub, work_sub in folders:
        src_path = f"{SOURCE_DIR}\\{src_sub}"
        if os.path.exists(src_path):
            for f in os.listdir(src_path):
                if f.lower().endswith('.upk'):
                    upks.append({'name': f, 'src_folder': src_sub, 'work_folder': work_sub})
    return upks

def process_upk(upk_info, log_file):
    name, work_folder = upk_info['name'], upk_info['work_folder']
    base_name, work_dir = name[:-4], f"{WORK_DIR}\\{work_folder}\\{name[:-4]}"
    os.makedirs(work_dir, exist_ok=True)
    
    safe_log(log_file, f"\n>>> Target UPK: {name} <<<\n")
    output_upk = f"{OUTPUT_DIR}\\{work_folder}\\{base_name}.upk"
    if os.path.exists(output_upk):
        safe_log(log_file, f" -> Already in Output. Skip.\n")
        return True
    
    try:
        src_dir = f"{SOURCE_DIR}\\{upk_info['src_folder']}"
        decompressed_path = f"{src_dir}\\unpacked\\{name}"
        final_upk = f"{work_dir}\\{base_name}.upk"
        
        if not os.path.exists(final_upk):
            if os.path.exists(decompressed_path):
                shutil.copy(decompressed_path, final_upk)
                safe_log(log_file, f" [1/5] Copying decompressed UPK...\n")
            else:
                safe_log(log_file, f" [1/5] Decompressing...\n")
                run_command(f'"{TOOL_DECOMPRESS}" "{name}"', cwd=src_dir)
                shutil.copy(decompressed_path, final_upk)
        
        int_yaml = f"{work_dir}\\{base_name}_INT.yaml"
        if not os.path.exists(int_yaml):
            safe_log(log_file, f" [2/5] Extracting Text...\n")
            os.makedirs(f"{work_dir}\\_DYextracted", exist_ok=True)
            run_command(f'python "{TOOL_SUBEDIT}" --output "{int_yaml}" --langCode INT "{final_upk}"', cwd=work_dir)
        
        th_yaml = f"{work_dir}\\{base_name}_TH.yaml"
        lines = open(int_yaml, "r", encoding="utf-8").readlines()
        total = len(lines)
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
        existing_lines = 0
        if os.path.exists(th_yaml):
            with open(th_yaml, "r", encoding="utf-8") as f:
                existing_lines = len([l for l in f.readlines() if l.strip() and ': ' in l])
        
        if existing_lines < total:
            safe_log(log_file, f" [3/5] Gemini 2.5 Flash Active. ({existing_lines}/{total} lines done, {total_batches} batches)\n")
            tasks, rel_idx = [], 0
            for idx in range(existing_lines, total, BATCH_SIZE):
                tasks.append((rel_idx, lines[idx:idx+BATCH_SIZE], (idx // BATCH_SIZE) + 1, total_batches))
                rel_idx += 1
            
            results_buffer, next_to_write = {}, 0
            with open(th_yaml, "a", encoding="utf-8") as f_out:
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    futures = {executor.submit(process_batch_task, t): t for t in tasks}
                    for future in as_completed(futures):
                        r_idx, result, orig_lines, b_num, t_batches = future.result()
                        status = "OK" if result else "FALLBACK"
                        safe_log(log_file, f" [Batch {b_num}/{t_batches}] {status} | Write: {next_to_write + 1}\n")
                        
                        results_buffer[r_idx] = (result, orig_lines)
                        while next_to_write in results_buffer:
                            res, orig = results_buffer.pop(next_to_write)
                            if res:
                                for rl in [l.strip() for l in res.split('\n') if l.strip()]:
                                    if ': ' in rl:
                                        parts = rl.split(': ', 1)
                                        f_out.write(f"{parts[0]}: {parts[1]}\n")
                                    else:
                                        f_out.write(rl + '\n')
                            else:
                                for line in orig:
                                    f_out.write(line.rstrip('\n') + '\n')
                            f_out.flush()
                            next_to_write += 1
        
        safe_log(log_file, f" [4/5] Repacking...\n")
        clean_yaml(th_yaml, int_yaml)
        run_command(f'python "{TOOL_SUBEDIT}" --input "{th_yaml}" --langCode INT "{final_upk}"', cwd=work_dir)
        
        if os.path.exists(f"{final_upk}_patched"):
            os.makedirs(f"{OUTPUT_DIR}\\{work_folder}", exist_ok=True)
            shutil.copy(f"{final_upk}_patched", output_upk)
            safe_log(log_file, f" [5/5] Done: {base_name}.upk\n")
            return True
        
        safe_log(log_file, f" [5/5] No patched output.\n")
        return False
    except Exception as e:
        safe_log(log_file, f"ERROR: {str(e)}\n")
        return False

def main():
    log_path = f"{WORK_DIR}\\batch_log.txt"
    os.makedirs(WORK_DIR, exist_ok=True)
    
    with open(log_path, "a", encoding="utf-8") as log_file:
        safe_log(log_file, "\n" + "="*60 + "\n", False)
        safe_log(log_file, "PERSISTENT RUNNER - Gemini 2.5 Flash Edition\n", False)
        safe_log(log_file, f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n", False)
        safe_log(log_file, "="*60 + "\n", False)
        
        upks = get_upk_list()
        total_upks = len(upks)
        completed, failed = 0, 0
        
        for i, upk in enumerate(upks):
            safe_log(log_file, f"\n[Queue {i+1}/{total_upks}] {upk['name']}\n")
            result = process_upk(upk, log_file)
            if result:
                completed += 1
            else:
                failed += 1
        
        current_output = 0
        if os.path.exists(OUTPUT_DIR):
            for _, _, files in os.walk(OUTPUT_DIR):
                current_output += len([f for f in files if f.endswith('.upk')])
        
        safe_log(log_file, f"\n{'='*60}\n", False)
        safe_log(log_file, f"COMPLETED: {completed} | FAILED: {failed} | OUTPUT: {current_output}/{total_upks}\n", False)
        safe_log(log_file, f"End Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n", False)
        safe_log(log_file, "="*60 + "\n", False)
        
        if failed > 0:
            safe_log(log_file, f"\n[RESTART] Retrying {failed} failed UPKs...\n", False)
            time.sleep(5)
            main()  # Auto-restart

if __name__ == "__main__":
    main()
