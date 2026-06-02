import os, subprocess, shutil

SUBEDIT = r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main\subedit.py"
WORKSPACE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working"

STEAM_COOKED = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"
STEAM_DLC_BASE = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\DLC\PCConsole"

FOLDERS = [
    ("CookedPCConsole", STEAM_COOKED),
    ("DLC05", os.path.join(STEAM_DLC_BASE, "DLC05")),
    ("DLC06", os.path.join(STEAM_DLC_BASE, "DLC06")),
    ("DLC07", os.path.join(STEAM_DLC_BASE, "DLC07")),
]

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def process_upk(upk_name, src_dir, work_base, folder_name):
    base_name = upk_name[:-4]
    work_dir = os.path.join(work_base, folder_name, base_name)
    os.makedirs(work_dir, exist_ok=True)
    
    yaml_path = os.path.join(work_dir, f"{base_name}.yaml")
    
    # Skip if already processed
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content.strip()) >= 50:
            line_count = len([l for l in content.split('\n') if l.strip()])
            print(f"  [EXISTS] {upk_name} ({line_count} lines)")
            return True
    
    upk_path = os.path.join(src_dir, upk_name)
    
    # Run subedit to extract text
    cmd = f'python "{SUBEDIT}" --output "{yaml_path}" --langCode INT "{upk_path}"'
    run_cmd(cmd, cwd=work_dir)
    
    if not os.path.exists(yaml_path):
        print(f"  [FAIL] {upk_name} - no yaml output")
        return False
    
    # Check if has text
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    
    if len(content) < 50:
        # No text
        os.remove(yaml_path)
        print(f"  [EMPTY] {upk_name}")
        return False
    
    line_count = len([l for l in content.split('\n') if l.strip()])
    
    # Create INT and TH copies
    int_path = os.path.join(work_dir, f"{base_name}_INT.yaml")
    th_path = os.path.join(work_dir, f"{base_name}_TH.yaml")
    
    with open(yaml_path, "r", encoding="utf-8") as f:
        lines = f.read()
    
    with open(int_path, "w", encoding="utf-8") as f:
        f.write(lines)
    
    with open(th_path, "w", encoding="utf-8") as f:
        f.write(lines)
    
    print(f"  [OK] {upk_name} ({line_count} lines)")
    return True

def main():
    print("=== SMART UNPACK WITH TEXT FILTER ===\n")
    
    total_upks = 0
    processed = 0
    skipped = 0
    
    for folder_name, src_path in FOLDERS:
        print(f"\n=== Processing {folder_name} ===")
        
        if not os.path.exists(src_path):
            print(f"  [SKIP] Path not found: {src_path}")
            continue
        
        upk_files = [f for f in os.listdir(src_path) if f.lower().endswith('.upk')]
        print(f"  Found {len(upk_files)} UPKs")
        total_upks += len(upk_files)
        
        for upk_name in upk_files:
            result = process_upk(upk_name, src_path, WORKSPACE, folder_name)
            if result:
                processed += 1
            else:
                skipped += 1
    
    print(f"\n=== DONE ===")
    print(f"Processed (with text): {processed}")
    print(f"Skipped (no text): {skipped}")
    print(f"Total UPKs: {total_upks}")

if __name__ == "__main__":
    main()