# pack_failed.py - Re-pack only the failed files
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os, subprocess, shutil, time

SOURCE_DIR = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame"
WORK_DIR_CCC = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"
WORK_DIR_DLC = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC"
OUTPUT_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated"
UNPACK_DIR_CCC = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\unpacked_cookedpcconsole"
UNPACK_DIR_DLC = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\unpacked_dlc"
TOOL_DECOMPRESS = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\decompress.exe"
TOOL_SUBEDIT = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored-toolkit\subedit.py"

def safe_print(msg):
    print(msg)
    sys.stdout.flush()

def decompress_upk(upk_name, src_dir, unpack_dir):
    # Delete existing to force re-decompress
    out_path = os.path.join(unpack_dir, upk_name)
    if os.path.exists(out_path):
        os.remove(out_path)
    os.makedirs(unpack_dir, exist_ok=True)
    safe_print(f"  [DECOMPRESS] {upk_name}")
    result = subprocess.run(
        f'"{TOOL_DECOMPRESS}" -path="{src_dir}" -out="{unpack_dir}" "{upk_name}"',
        shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        safe_print(f"  [ERROR] {result.stderr}")
        return None
    return out_path if os.path.exists(out_path) else None

def patch_upk(decompressed_upk_path, th_yaml_path):
    safe_print(f"  [PATCH] {os.path.basename(decompressed_upk_path)}")
    result = subprocess.run(
        f'python "{TOOL_SUBEDIT}" "{decompressed_upk_path}" --input "{th_yaml_path}" --langCode INT',
        shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        safe_print(f"  [ERROR] Patch failed")
        return False
    return True

# CCC failed files
CCC_FAILED = [
    "L_Brothel_Script",
    "L_TowerRtrn_Int_Script",
]

# DLC failed files
DLC_FAILED = [
    ("DLC06", "DLC06_DaudBase_Script"),
    ("DLC06", "DLC06_Slaughter_Ext_Script"),
    ("DLC06", "DLC06_Slaughter_Int_Loot"),
    ("DLC06", "DLC06_Timsh_Estate_Patrol"),
    ("DLC07", "DLC07_Twk_Inv_Seekfree_SF"),
    ("DLC07", "L_DLC07_Brig_Ext_P"),
    ("DLC07", "L_DLC07_BaseIntro_Script"),
    ("DLC07", "L_DLC07_Brig_Ext_Loot"),
    ("DLC07", "L_DLC07_Brigmore_Void_P"),
    ("DLC07", "L_DLC07_Brigmore_Void_Script"),
    ("DLC07", "L_DLC07_Coldridge_P"),
    ("DLC07", "L_DLC07_DraperMill_Loot"),
    ("DLC07", "L_DLC07_DraperShip_Script"),
    ("DLC07", "L_DLC07_DraperStreets_P"),
    ("DLC07", "L_DLC07_GlobalStore"),
]

def main():
    safe_print("="*60)
    safe_print("RE-PACK FAILED FILES")
    safe_print("="*60)
    
    # Delete existing output files first
    output_ccc = os.path.join(OUTPUT_DIR, "CookedPCConsole")
    output_dlc = os.path.join(OUTPUT_DIR, "DLC", "DLC")
    
    # CCC
    safe_print("\n=== CookedPCConsole (2 files) ===")
    for folder in CCC_FAILED:
        upk_name = f"{folder}.upk"
        out_path = os.path.join(output_ccc, upk_name)
        if os.path.exists(out_path):
            os.remove(out_path)
            safe_print(f"  Deleted existing: {upk_name}")
    
    success = 0; failed = 0
    for folder in CCC_FAILED:
        th_yaml = os.path.join(WORK_DIR_CCC, folder, f"{folder}_TH.yaml")
        if not os.path.exists(th_yaml):
            safe_print(f"{folder}: NO TH YAML — SKIP")
            failed += 1; continue
        
        upk_name = f"{folder}.upk"
        src_upk = os.path.join(SOURCE_DIR, "CookedPCConsole", upk_name)
        
        safe_print(f"[CCC] {folder}")
        
        decomp = decompress_upk(upk_name, os.path.join(SOURCE_DIR, "CookedPCConsole"), UNPACK_DIR_CCC)
        if not decomp or not os.path.exists(decomp):
            safe_print(f"  [FAIL] Decompress"); failed += 1; continue
        
        if not patch_upk(decomp, th_yaml):
            safe_print(f"  [FAIL] Patch"); failed += 1; continue
        
        patched = f"{decomp}_patched"
        if os.path.exists(patched):
            shutil.copy2(patched, out_path)
            safe_print(f"  [OK]"); success += 1
        else:
            alt = os.path.join(os.path.dirname(decomp), f"{folder}_patched.upk")
            if os.path.exists(alt):
                shutil.copy2(alt, out_path)
                safe_print(f"  [OK]"); success += 1
            else:
                safe_print(f"  [FAIL] No patched file"); failed += 1
    
    # DLC
    safe_print("\n=== DLC (15 files) ===")
    for dlc_folder, folder in DLC_FAILED:
        upk_name = f"{folder}.upk"
        out_path = os.path.join(output_dlc, upk_name)
        if os.path.exists(out_path):
            os.remove(out_path)
            safe_print(f"  Deleted existing: {upk_name}")
    
    for dlc_folder, folder in DLC_FAILED:
        th_yaml = os.path.join(WORK_DIR_DLC, "PCConsole", dlc_folder, folder, f"{folder}_TH.yaml")
        if not os.path.exists(th_yaml):
            safe_print(f"{folder}: NO TH YAML — SKIP")
            failed += 1; continue
        
        upk_name = f"{folder}.upk"
        src_upk_dir = os.path.join(SOURCE_DIR, "DLC", "PCConsole", dlc_folder)
        
        safe_print(f"[DLC{dlc_folder[-2:]}] {folder}")
        
        decomp = decompress_upk(upk_name, src_upk_dir, UNPACK_DIR_DLC)
        if not decomp or not os.path.exists(decomp):
            safe_print(f"  [FAIL] Decompress"); failed += 1; continue
        
        if not patch_upk(decomp, th_yaml):
            safe_print(f"  [FAIL] Patch"); failed += 1; continue
        
        patched = f"{decomp}_patched"
        out_upk = os.path.join(output_dlc, upk_name)
        if os.path.exists(patched):
            shutil.copy2(patched, out_upk)
            safe_print(f"  [OK]"); success += 1
        else:
            alt = os.path.join(os.path.dirname(decomp), f"{folder}_patched.upk")
            if os.path.exists(alt):
                shutil.copy2(alt, out_upk)
                safe_print(f"  [OK]"); success += 1
            else:
                safe_print(f"  [FAIL] No patched file"); failed += 1
    
    safe_print("\n" + "="*60)
    safe_print(f"RESULT: {success} ok | {failed} fail")
    safe_print("="*60)

if __name__ == "__main__":
    main()