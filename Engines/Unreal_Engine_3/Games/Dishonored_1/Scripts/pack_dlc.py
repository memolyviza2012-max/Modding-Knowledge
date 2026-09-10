# pack_dlc.py
# Pack all DLC TH YAML → UPK
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os, subprocess, shutil

# --- CONFIG ---
SOURCE_DIR = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame"
WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC"
OUTPUT_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\DLC"
UNPACK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\unpacked_dlc"
TOOL_DECOMPRESS = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\decompress.exe"
TOOL_SUBEDIT = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored-toolkit\subedit.py"

def safe_print(msg):
    print(msg)

def decompress_upk(upk_name, src_dir):
    """Decompress a single UPK file."""
    out_path = os.path.join(UNPACK_DIR, upk_name)
    if os.path.exists(out_path):
        safe_print(f"  [SKIP] Already decompressed: {upk_name}")
        return out_path

    os.makedirs(UNPACK_DIR, exist_ok=True)
    safe_print(f"  [DECOMPRESS] {upk_name}")
    result = subprocess.run(
        f'"{TOOL_DECOMPRESS}" -path="{src_dir}" -out="{UNPACK_DIR}" "{upk_name}"',
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        safe_print(f"  [ERROR] Decompress failed: {result.stderr}")
        return None
    return out_path if os.path.exists(out_path) else None

def patch_upk(decompressed_upk_path, th_yaml_path):
    """Patch a decompressed UPK with Thai YAML."""
    safe_print(f"  [PATCH] {os.path.basename(decompressed_upk_path)}")
    result = subprocess.run(
        f'python "{TOOL_SUBEDIT}" "{decompressed_upk_path}" --input "{th_yaml_path}" --langCode INT',
        shell=True,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        safe_print(f"  [ERROR] Patch failed: {result.stderr}")
        return False
    return True

def find_all_th_yaml(work_dir):
    """Find all _TH.yaml files in DLC work directory."""
    results = []
    for root, dirs, files in os.walk(work_dir):
        for f in files:
            if f.endswith('_TH.yaml'):
                # Get the base name (e.g., L_DLC07_DraperSewer_Script)
                base = f.replace('_TH.yaml', '')
                # The UPK name is the folder name (e.g., L_DLC07_DraperSewer_Script.upk)
                folder_name = os.path.basename(root)
                results.append({
                    'th_yaml': os.path.join(root, f),
                    'base': base,
                    'folder_name': folder_name,
                    'root': root
                })
    return results

def main():
    safe_print("=== Pack DLC → TH UPK ===\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find all TH.yaml files
    th_files = find_all_th_yaml(WORK_DIR)
    safe_print(f"Found {len(th_files)} TH YAML files\n")

    success = 0
    failed = 0
    skipped = 0

    for i, item in enumerate(sorted(th_files, key=lambda x: x['base'])):
        base = item['base']
        th_yaml = item['th_yaml']
        folder_name = item['folder_name']

        # Determine DLC folder (DLC05, DLC06, DLC07)
        dlc_folder = os.path.basename(os.path.dirname(item['root']))

        # Source UPK location
        src_upk_dir = os.path.join(SOURCE_DIR, "DLC", "PCConsole", dlc_folder)
        src_upk = os.path.join(src_upk_dir, f"{folder_name}.upk")

        if not os.path.exists(src_upk):
            safe_print(f"[{i+1}/{len(th_files)}] {base}: SOURCE UPK NOT FOUND ({src_upk}) — SKIP")
            skipped += 1
            continue

        output_upk = os.path.join(OUTPUT_DIR, f"{folder_name}.upk")
        if os.path.exists(output_upk):
            safe_print(f"[{i+1}/{len(th_files)}] {base}: OUTPUT EXISTS — SKIP")
            skipped += 1
            continue

        safe_print(f"[{i+1}/{len(th_files)}] {base} ({dlc_folder})")

        # Step 1: Decompress
        decomp_path = decompress_upk(f"{folder_name}.upk", src_upk_dir)
        if not decomp_path or not os.path.exists(decomp_path):
            safe_print(f"  [FAIL] Decompress failed")
            failed += 1
            continue

        # Step 2: Patch
        ok = patch_upk(decomp_path, th_yaml)
        if not ok:
            safe_print(f"  [FAIL] Patch failed")
            failed += 1
            continue

        # Step 3: Copy _patched to output
        patched_path = f"{decomp_path}_patched"
        if os.path.exists(patched_path):
            shutil.copy2(patched_path, output_upk)
            safe_print(f"  [OK] Saved → {output_upk}")
            success += 1
        else:
            alt_patched = os.path.join(os.path.dirname(decomp_path), f"{folder_name}_patched.upk")
            if os.path.exists(alt_patched):
                shutil.copy2(alt_patched, output_upk)
                safe_print(f"  [OK] Saved → {output_upk}")
                success += 1
            else:
                safe_print(f"  [FAIL] No _patched file found")
                failed += 1

    safe_print(f"\n=== DONE ===")
    safe_print(f"Success: {success} | Failed: {failed} | Skipped: {skipped} | Total: {len(th_files)}")

if __name__ == "__main__":
    main()