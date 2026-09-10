# pack_repack.py - Re-pack failed files from pack_all.py
# Also pack DLC properly
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
    out_path = os.path.join(unpack_dir, upk_name)
    if os.path.exists(out_path):
        return out_path
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

def pack_folder(work_dir, output_subdir, unpack_subdir, label):
    os.makedirs(os.path.join(OUTPUT_DIR, output_subdir), exist_ok=True)
    folders = [d for d in os.listdir(work_dir) if os.path.isdir(os.path.join(work_dir, d))]
    safe_print(f"\n=== {label}: {len(folders)} folders ===\n")
    
    success = 0; failed = 0; skipped = 0
    total = len(folders)
    
    for i, folder in enumerate(sorted(folders)):
        th_yaml = os.path.join(work_dir, folder, f"{folder}_TH.yaml")
        if not os.path.exists(th_yaml):
            safe_print(f"[{i+1}/{total}] {folder}: NO TH YAML — SKIP")
            skipped += 1; continue
        
        upk_name = f"{folder}.upk"
        src_upk = os.path.join(SOURCE_DIR, output_subdir, upk_name)
        if not os.path.exists(src_upk):
            safe_print(f"[{i+1}/{total}] {folder}: SOURCE NOT FOUND — SKIP")
            skipped += 1; continue
        
        out_upk = os.path.join(OUTPUT_DIR, output_subdir, upk_name)
        
        safe_print(f"[{i+1}/{total}] {folder}")
        
        decomp = decompress_upk(upk_name, os.path.join(SOURCE_DIR, output_subdir), unpack_subdir)
        if not decomp or not os.path.exists(decomp):
            safe_print(f"  [FAIL] Decompress"); failed += 1; continue
        
        if not patch_upk(decomp, th_yaml):
            safe_print(f"  [FAIL] Patch"); failed += 1; continue
        
        patched = f"{decomp}_patched"
        if os.path.exists(patched):
            shutil.copy2(patched, out_upk)
            safe_print(f"  [OK] → {out_upk}"); success += 1
        else:
            alt = os.path.join(os.path.dirname(decomp), f"{folder}_patched.upk")
            if os.path.exists(alt):
                shutil.copy2(alt, out_upk)
                safe_print(f"  [OK] → {out_upk}"); success += 1
            else:
                safe_print(f"  [FAIL] No patched file"); failed += 1
    
    safe_print(f"\n=== {label} DONE: {success} ok | {failed} fail | {skipped} skip ===\n")
    return success, failed, skipped

def pack_dlc():
    """Pack DLC - finds all _TH.yaml recursively and maps to correct DLC folder."""
    safe_print("\n=== DLC (recursive scan) ===\n")
    
    os.makedirs(os.path.join(OUTPUT_DIR, "DLC"), exist_ok=True)
    
    # Find all TH YAML files recursively
    th_files = []
    for root, dirs, files in os.walk(WORK_DIR_DLC):
        for f in files:
            if f.endswith('_TH.yaml'):
                base = f.replace('_TH.yaml', '')
                folder_name = os.path.basename(root)
                # Determine DLC folder from path
                path_parts = root.split(os.sep)
                dlc_folder = None
                for part in path_parts:
                    if part.startswith('DLC'):
                        dlc_folder = part
                        break
                th_files.append({
                    'base': base,
                    'th_yaml': os.path.join(root, f),
                    'folder_name': folder_name,
                    'dlc_folder': dlc_folder
                })
    
    safe_print(f"Found {len(th_files)} TH YAML files in DLC\n")
    
    success = 0; failed = 0; skipped = 0
    total = len(th_files)
    
    for i, item in enumerate(sorted(th_files, key=lambda x: x['base'])):
        base = item['base']
        th_yaml = item['th_yaml']
        folder_name = item['folder_name']
        dlc_folder = item['dlc_folder']
        
        if not dlc_folder:
            safe_print(f"[{i+1}/{total}] {base}: Cannot determine DLC folder — SKIP")
            skipped += 1; continue
        
        src_upk_dir = os.path.join(SOURCE_DIR, "DLC", "PCConsole", dlc_folder)
        src_upk = os.path.join(src_upk_dir, f"{folder_name}.upk")
        
        if not os.path.exists(src_upk):
            safe_print(f"[{i+1}/{total}] {base}: SOURCE NOT FOUND ({src_upk}) — SKIP")
            skipped += 1; continue
        
        out_upk = os.path.join(OUTPUT_DIR, "DLC", f"{folder_name}.upk")
        
        safe_print(f"[{i+1}/{total}] {base} ({dlc_folder})")
        
        decomp = decompress_upk(f"{folder_name}.upk", src_upk_dir, UNPACK_DIR_DLC)
        if not decomp or not os.path.exists(decomp):
            safe_print(f"  [FAIL] Decompress"); failed += 1; continue
        
        if not patch_upk(decomp, th_yaml):
            safe_print(f"  [FAIL] Patch"); failed += 1; continue
        
        patched = f"{decomp}_patched"
        if os.path.exists(patched):
            shutil.copy2(patched, out_upk)
            safe_print(f"  [OK] → {out_upk}"); success += 1
        else:
            alt = os.path.join(os.path.dirname(decomp), f"{folder_name}_patched.upk")
            if os.path.exists(alt):
                shutil.copy2(alt, out_upk)
                safe_print(f"  [OK] → {out_upk}"); success += 1
            else:
                safe_print(f"  [FAIL] No patched file"); failed += 1
    
    safe_print(f"\n=== DLC DONE: {success} ok | {failed} fail | {skipped} skip ===\n")
    return success, failed, skipped

def main():
    start = time.time()
    safe_print("="*60)
    safe_print("RE-PACK: CCC (failed only) + DLC")
    safe_print("="*60)
    
    # Re-pack CCC failed files
    ccc_ok, ccc_fail, ccc_skip = pack_folder(WORK_DIR_CCC, "CookedPCConsole", UNPACK_DIR_CCC, "CookedPCConsole (re-pack)")
    
    # Pack DLC
    dl_ok, dl_fail, dl_skip = pack_dlc()
    
    elapsed = time.time() - start
    safe_print("="*60)
    safe_print("=== ALL DONE ===")
    safe_print(f"CookedPCConsole: {ccc_ok} ok | {ccc_fail} fail | {ccc_skip} skip")
    safe_print(f"DLC: {dl_ok} ok | {dl_fail} fail | {dl_skip} skip")
    safe_print(f"Total time: {elapsed:.1f} seconds")
    safe_print("="*60)

if __name__ == "__main__":
    main()