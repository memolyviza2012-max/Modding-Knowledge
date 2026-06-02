"""
DISHONORED Manual Mod - Phase 2: Unpack UPKs to ._INT and ._TH files
Requires: Decompressed UPKs in 01_source\*\unpacked\
"""
import os
import shutil
import subprocess
import yaml

SOURCE_DIR = "D:\\Mod_Workspace\\Dishonored_Mod_Workspace\\01_source"
MANUAL_DIR = "D:\\Mod_Workspace\\Dishonored_Mod_Workspace\\03_working_manual"
TOOL_SUBEDIT = "D:\\Mod_Workspace\\Tool\\UE3\\dishonored-toolkit-main\\subedit.py"

FOLDER_MAP = [
    ("CookedPCConsole\\unpacked", "CookedPCConsole"),
    ("DLC\\PCConsole\\DLC05\\unpacked", "DLC\\DLC05"),
    ("DLC\\PCConsole\\DLC06\\unpacked", "DLC\\DLC06"),
    ("DLC\\PCConsole\\DLC07\\unpacked", "DLC\\DLC07"),
]

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def unpack_upk_to_yaml(upk_path, base_name, work_dir):
    yaml_path = work_dir + "\\" + base_name + ".yaml"
    if os.path.exists(yaml_path):
        return yaml_path
    ensure_dir(work_dir)
    code, out, err = run_cmd('python "' + TOOL_SUBEDIT + '" --output "' + yaml_path + '" --langCode INT "' + upk_path + '"', cwd=work_dir)
    if os.path.exists(yaml_path):
        return yaml_path
    else:
        return None

def yaml_to_int_th(yaml_path, base_name, work_dir):
    if not yaml_path or not os.path.exists(yaml_path):
        return False
    int_file = work_dir + "\\" + base_name + "._INT"
    th_file = work_dir + "\\" + base_name + "._TH"
    if os.path.exists(int_file) and os.path.exists(th_file):
        return True
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return False
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                lines.append(key + ": " + item)
        else:
            lines.append(key + ": " + value)
    with open(int_file, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))
    shutil.copy(int_file, th_file)
    return True

def process_upk(upk_name, src_unpacked, work_folder):
    base_name = upk_name[:-4]
    upk_path = src_unpacked + "\\" + upk_name
    work_dir = ensure_dir(MANUAL_DIR + "\\" + work_folder + "\\" + base_name)
    int_file = work_dir + "\\" + base_name + "._INT"
    th_file = work_dir + "\\" + base_name + "._TH"
    if os.path.exists(int_file) and os.path.exists(th_file):
        return "skip", 0
    yaml_path = unpack_upk_to_yaml(upk_path, base_name, work_dir)
    if not yaml_path:
        return "fail", 0
    ok = yaml_to_int_th(yaml_path, base_name, work_dir)
    if not ok:
        return "fail", 0
    with open(int_file, "r", encoding="utf-8") as f:
        line_count = len(f.readlines())
    return "ok", line_count

def main():
    print("=" * 60)
    print("DISHONORED Manual - Phase 2: Unpack to INT/TH")
    print("=" * 60)
    print()
    print("NOTE: Run this script AFTER decompressing all UPKs.")
    print()
    
    total_upks = 0
    for src_sub, _ in FOLDER_MAP:
        src_path = SOURCE_DIR + "\\" + src_sub
        if os.path.exists(src_path):
            count = len([f for f in os.listdir(src_path) if f.endswith('.upk')])
            total_upks += count
    
    print("Total UPKs to process: " + str(total_upks))
    print()
    
    all_results = []
    
    for src_sub, work_folder in FOLDER_MAP:
        src_path = SOURCE_DIR + "\\" + src_sub
        if not os.path.exists(src_path):
            continue
        
        upk_files = [f for f in os.listdir(src_path) if f.endswith('.upk')]
        print("=" * 60)
        print("Processing " + str(len(upk_files)) + " UPKs from " + src_sub + "...")
        print("=" * 60)
        
        success = skipped = failed = 0
        
        for idx, upk_name in enumerate(upk_files, 1):
            result, lines = process_upk(upk_name, src_path, work_folder)
            
            if result == "ok":
                success += 1
                print("[" + str(idx) + "/" + str(len(upk_files)) + "] OK - " + upk_name + " (" + str(lines) + " lines)")
            elif result == "skip":
                skipped += 1
                print("[" + str(idx) + "/" + str(len(upk_files)) + "] SKIP - " + upk_name)
            else:
                failed += 1
                print("[" + str(idx) + "/" + str(len(upk_files)) + "] FAIL - " + upk_name)
        
        print("\n  " + str(success) + " ok, " + str(skipped) + " skipped, " + str(failed) + " failed")
        all_results.append((src_sub, success, skipped, failed))
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    total_ok = total_skip = total_fail = 0
    for src_sub, ok, skip, fail in all_results:
        print("  " + src_sub + ": " + str(ok) + " ok, " + str(skip) + " skipped, " + str(fail) + " failed")
        total_ok += ok
        total_skip += skip
        total_fail += fail
    
    print("\n  TOTAL: " + str(total_ok) + " ok, " + str(total_skip) + " skipped, " + str(total_fail) + " failed")
    print("=" * 60)

if __name__ == "__main__":
    main()