"""
DISHONORED Manual Mod - Phase 1: Unpack & Create INT/TH files
Unpack UPK files from source, create ._INT (original English) and ._TH (for Thai translation)
"""
import os
import sys
import shutil
import subprocess
import yaml
from pathlib import Path

WORKSPACE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
SOURCE_DIR = f"{WORKSPACE}\\01_source"
MANUAL_DIR = f"{WORKSPACE}\\03_working_manual"
STEAM_COOKED = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"
TOOL_DECOMPRESS = r"D:\Mod_Workspace\Tool\UE3\decompress\decompress.exe"
TOOL_SUBEDIT = r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main\subedit.py"

STEAM_FOLDERS = {
    "CookedPCConsole": STEAM_COOKED,
    "DLC05": r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\DLC\PCConsole\DLC05",
    "DLC06": r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\DLC\PCConsole\DLC06",
    "DLC07": r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\DLC\PCConsole\DLC07",
}

SOURCE_FOLDERS = {
    "CookedPCConsole": f"{SOURCE_DIR}\\CookedPCConsole",
    "DLC05": f"{SOURCE_DIR}\\DLC\\PCConsole\\DLC05",
    "DLC06": f"{SOURCE_DIR}\\DLC\\PCConsole\\DLC06",
    "DLC07": f"{SOURCE_DIR}\\DLC\\PCConsole\\DLC07",
}

def run_cmd(cmd, cwd=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return result.returncode, result.stdout, result.stderr

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def get_upk_list():
    """Get all UPK files from source folders"""
    upks = []
    mappings = [
        ("CookedPCConsole", "CookedPCConsole"),
        ("DLC05", "DLC\\DLC05"),
        ("DLC06", "DLC\\DLC06"),
        ("DLC07", "DLC\\DLC07"),
    ]
    for src_key, work_sub in mappings:
        src_path = SOURCE_FOLDERS[src_key]
        if os.path.exists(src_path):
            for f in os.listdir(src_path):
                if f.lower().endswith('.upk'):
                    upks.append({
                        'name': f,
                        'src_key': src_key,
                        'work_folder': work_sub
                    })
    return upks

def decompress_upk(upk_name, src_key):
    """Decompress a UPK file to source unpacked folder"""
    src_dir = SOURCE_FOLDERS[src_key]
    unpacked_dir = f"{src_dir}\\unpacked"
    decompressed_path = f"{unpacked_dir}\\{upk_name}"
    
    if os.path.exists(decompressed_path):
        return decompressed_path
    
    ensure_dir(unpacked_dir)
    
    # Run decompress from Steam game folder (required for game detection)
    steam_dir = STEAM_FOLDERS[src_key]
    if src_key != "CookedPCConsole":
        # For DLC, we need to run from the DLC folder itself
        steam_dir = os.path.dirname(steam_dir)
    
    code, out, err = run_cmd(f'"{TOOL_DECOMPRESS}" -out="{unpacked_dir}" "{upk_name}"', cwd=steam_dir)
    
    if os.path.exists(decompressed_path):
        return decompressed_path
    else:
        print(f"    [WARN] decompress output not found: {decompressed_path}")
        print(f"    stdout: {out[:200]}")
        print(f"    stderr: {err[:200]}")
        return None

def unpack_to_yaml(upk_path, base_name, work_dir):
    """Unpack UPK to YAML using subedit.py"""
    yaml_path = f"{work_dir}\\{base_name}.yaml"
    
    if os.path.exists(yaml_path):
        return yaml_path
    
    ensure_dir(work_dir)
    
    code, out, err = run_cmd(
        f'python "{TOOL_SUBEDIT}" --output "{yaml_path}" --langCode INT "{upk_path}"',
        cwd=work_dir
    )
    
    if os.path.exists(yaml_path):
        return yaml_path
    else:
        print(f"    [WARN] subedit failed")
        print(f"    stdout: {out[:300]}")
        print(f"    stderr: {err[:300]}")
        return None

def create_int_th_files(yaml_path, base_name, work_dir):
    """Create ._INT and ._TH files from YAML"""
    if not yaml_path or not os.path.exists(yaml_path):
        return False
    
    int_file = f"{work_dir}\\{base_name}._INT"
    th_file = f"{work_dir}\\{base_name}._TH"
    
    if os.path.exists(int_file) and os.path.exists(th_file):
        return True
    
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    lines = []
    if data:
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    lines.append(f"{key}: {item}")
            else:
                lines.append(f"{key}: {value}")
    
    with open(int_file, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))
    
    shutil.copy(int_file, th_file)
    
    print(f"    [OK] {base_name}._INT ({len(lines)} lines)")
    
    return True

def main():
    print("=" * 60)
    print("DISHONORED Manual - Phase 1: Unpack & Create INT/TH")
    print("=" * 60)
    
    upks = get_upk_list()
    total = len(upks)
    print(f"Found {total} UPK files\n")
    
    success = 0
    failed = []
    skipped = 0
    
    for idx, upk_info in enumerate(upks, 1):
        name = upk_info['name']
        src_key = upk_info['src_key']
        work_folder = upk_info['work_folder']
        base_name = name[:-4]
        
        print(f"[{idx}/{total}] {work_folder}\\{name}")
        
        work_dir = ensure_dir(f"{MANUAL_DIR}\\{work_folder}\\{base_name}")
        
        # Check if already done
        int_file = f"{work_dir}\\{base_name}._INT"
        th_file = f"{work_dir}\\{base_name}._TH"
        if os.path.exists(int_file) and os.path.exists(th_file):
            print(f"    [SKIP] Already exists")
            skipped += 1
            continue
        
        # Step 1: Decompress
        print(f"    [1/3] Decompressing...")
        decompressed = decompress_upk(name, src_key)
        if not decompressed:
            print(f"    [FAIL] Could not decompress")
            failed.append(f"{work_folder}\\{name}")
            continue
        
        # Step 2: Unpack to YAML
        print(f"    [2/3] Unpacking...")
        yaml_path = unpack_to_yaml(decompressed, base_name, work_dir)
        if not yaml_path:
            print(f"    [FAIL] Could not unpack")
            failed.append(f"{work_folder}\\{name}")
            continue
        
        # Step 3: Create _INT and _TH files
        print(f"    [3/3] Creating INT/TH files...")
        ok = create_int_th_files(yaml_path, base_name, work_dir)
        if ok:
            success += 1
        else:
            failed.append(f"{work_folder}\\{name}")
    
    print("\n" + "=" * 60)
    print(f"DONE: {success}/{total} success, {skipped} skipped")
    if failed:
        print(f"FAILED: {len(failed)} files")
        for f in failed:
            print(f"  - {f}")
    print("=" * 60)

if __name__ == "__main__":
    main()