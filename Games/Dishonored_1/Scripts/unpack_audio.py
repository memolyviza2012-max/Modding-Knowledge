import os, subprocess

SUBEDIT = r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main\subedit.py"
SOURCE = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"
OUTPUT = r"E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole_UnpackAll"

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def process_upk(upk_name):
    base_name = upk_name[:-4]
    work_dir = os.path.join(OUTPUT, base_name)
    os.makedirs(work_dir, exist_ok=True)
    
    yaml_path = os.path.join(work_dir, f"{base_name}.yaml")
    
    # Skip if already processed with content
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content.strip()) >= 50:
            line_count = len([l for l in content.split('\n') if l.strip()])
            print(f"  [EXISTS] {upk_name} ({line_count} lines)")
            return True
    
    upk_path = os.path.join(SOURCE, upk_name)
    if not os.path.exists(upk_path):
        print(f"  [MISSING] {upk_name}")
        return False
    
    # Run subedit to extract text
    cmd = f'python "{SUBEDIT}" --output "{yaml_path}" --langCode INT "{upk_path}"'
    rc, stdout, stderr = run_cmd(cmd, cwd=work_dir)
    
    if rc != 0:
        # Skip on any error (compressed, corrupted, etc.)
        print(f"  [SKIP] {upk_name}")
        return False
    
    if not os.path.exists(yaml_path):
        print(f"  [SKIP] {upk_name} - no output")
        return False
    
    # Check if has text
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    if len(content) < 50:
        os.remove(yaml_path)
        print(f"  [SKIP] {upk_name} - empty")
        return False
    
    line_count = len([l for l in content.split('\n') if l.strip()])
    
    # Create INT and TH copies
    int_path = os.path.join(work_dir, f"{base_name}_INT.yaml")
    th_path = os.path.join(work_dir, f"{base_name}_TH.yaml")
    
    with open(int_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    with open(th_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  [OK] {upk_name} ({line_count} lines)")
    return True

def main():
    print("=== UNPACK AUDIO UPKs (skip problems) ===\n")
    
    audio_upks = [f for f in os.listdir(SOURCE) if f.endswith('.upk') and 'Audio' in f]
    audio_upks.sort()
    
    print(f"Found {len(audio_upks)} Audio UPKs\n")
    
    processed = 0
    skipped = 0
    
    for upk_name in audio_upks:
        result = process_upk(upk_name)
        if result:
            processed += 1
        else:
            skipped += 1
    
    print(f"\n=== DONE ===")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    
    if processed > 0:
        print(f"\n=== SUCCESSFUL FILES ===")
        for d in os.listdir(OUTPUT):
            yaml = os.path.join(OUTPUT, d, f"{d}_INT.yaml")
            if os.path.exists(yaml):
                lines = len([l for l in open(yaml, "r", encoding="utf-8").read().split('\n') if l.strip()])
                print(f"  {d} ({lines} lines)")

if __name__ == "__main__":
    main()