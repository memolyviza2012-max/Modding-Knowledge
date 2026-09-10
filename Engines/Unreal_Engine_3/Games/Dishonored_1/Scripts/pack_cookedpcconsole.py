# pack_cookedpcconsole.py
# Pack all CookedPCConsole TH YAML → UPK
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os, subprocess, shutil

# --- CONFIG ---
SOURCE_DIR = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame"
WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"
OUTPUT_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\CookedPCConsole"
UNPACK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\unpacked_cookedpcconsole"
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

def main():
    safe_print("=== Pack CookedPCConsole → TH UPK ===\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find all folders with _TH.yaml
    folders = [d for d in os.listdir(WORK_DIR) if os.path.isdir(os.path.join(WORK_DIR, d))]
    safe_print(f"Found {len(folders)} folders\n")

    success = 0
    failed = 0
    skipped = 0

    for i, folder in enumerate(sorted(folders)):
        th_yaml = os.path.join(WORK_DIR, folder, f"{folder}_TH.yaml")
        if not os.path.exists(th_yaml):
            safe_print(f"[{i+1}/{len(folders)}] {folder}: NO TH YAML — SKIP")
            skipped += 1
            continue

        upk_name = f"{folder}.upk"
        src_upk = os.path.join(SOURCE_DIR, "CookedPCConsole", upk_name)
        if not os.path.exists(src_upk):
            safe_print(f"[{i+1}/{len(folders)}] {folder}: SOURCE UPK NOT FOUND — SKIP")
            skipped += 1
            continue

        output_upk = os.path.join(OUTPUT_DIR, upk_name)
        if os.path.exists(output_upk):
            safe_print(f"[{i+1}/{len(folders)}] {folder}: OUTPUT EXISTS — SKIP")
            skipped += 1
            continue

        safe_print(f"[{i+1}/{len(folders)}] {folder}")

        # Step 1: Decompress
        decomp_path = decompress_upk(upk_name, os.path.join(SOURCE_DIR, "CookedPCConsole"))
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
            # Try alternative: check subedit output location
            alt_patched = os.path.join(os.path.dirname(decomp_path), f"{folder}_patched.upk")
            if os.path.exists(alt_patched):
                shutil.copy2(alt_patched, output_upk)
                safe_print(f"  [OK] Saved → {output_upk}")
                success += 1
            else:
                safe_print(f"  [FAIL] No _patched file found")
                failed += 1

    safe_print(f"\n=== DONE ===")
    safe_print(f"Success: {success} | Failed: {failed} | Skipped: {skipped} | Total: {len(folders)}")

if __name__ == "__main__":
    main()
