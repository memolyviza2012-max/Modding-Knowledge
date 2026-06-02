# sniper_cron_monitor.py
# Runs as cron every 10 minutes.
# Logic:
#   - If files with English remain and run_count < 2: run sniper, increment count
#   - If files with English remain and run_count >= 2: stop (give up)
#   - If no files with English: done, report
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os, json, subprocess

WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"
STATE_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\sniper_state.json"
SNIPER_SCRIPT = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\sniper_translate.py"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"run_count": 0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def count_english_files():
    """Return list of (folder, eng_count) for files with English lines."""
    import re
    results = []
    if not os.path.exists(WORK_DIR):
        return results
    for entry in os.listdir(WORK_DIR):
        subdir = os.path.join(WORK_DIR, entry)
        if not os.path.isdir(subdir):
            continue
        th_files = [f for f in os.listdir(subdir) if f.endswith('_TH.yaml')]
        if not th_files:
            continue
        th_path = os.path.join(subdir, th_files[0])
        try:
            for enc in ('utf-8-sig', 'utf-8'):
                with open(th_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
        except:
            continue
        eng_lines = [l for l in content.split('\n') if l.strip() and re.match(r"^[^:]+:\s*[A-Za-z]", l)]
        if eng_lines:
            results.append((entry, len(eng_lines)))
    return results

def is_sniper_running():
    """Check if a python process is running the sniper script."""
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline') or []
            if any('sniper_translate' in str(c) for c in cmdline):
                return True
        except:
            pass
    return False

def main():
    state = load_state()
    remaining = count_english_files()
    total_files = len(remaining)
    total_eng_lines = sum(c for _, c in remaining)

    print(f"[SNIPER MONITOR] run_count={state['run_count']} | files_with_english={total_files} | total_lines={total_eng_lines}")

    if total_files == 0:
        print("[SNIPER MONITOR] === ALL CLEAN — DONE ===")
        # Clean up state file
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        return "DONE"

    if is_sniper_running():
        print("[SNIPER MONITOR] Sniper still running, skipping...")
        return "RUNNING"

    if state['run_count'] >= 2:
        print(f"[SNIPER MONITOR] Run count exhausted ({state['run_count']}/2). Remaining {total_files} files with English. Giving up.")
        return "EXHAUSTED"

    # Run sniper
    print(f"[SNIPER MONITOR] Starting sniper (run {state['run_count']+1}/2)...")
    state['run_count'] += 1
    save_state(state)

    try:
        result = subprocess.run(
            ['python', SNIPER_SCRIPT],
            capture_output=False,
            cwd=os.path.dirname(SNIPER_SCRIPT),
            timeout=600,
        )
        print(f"[SNIPER MONITOR] Sniper finished with code {result.returncode}")
    except subprocess.TimeoutExpired:
        print("[SNIPER MONITOR] Sniper timed out!")
    except Exception as e:
        print(f"[SNIPER MONITOR] Sniper error: {e}")

    return "RAN"

if __name__ == "__main__":
    main()
