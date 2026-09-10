import os, sys, shutil
from pathlib import Path

TOOLKIT = Path(r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main")
SOURCE = Path(r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole")
OUTPUT = Path(r"E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole_UnpackAll")

SKIP = {
    "L_Bridge_Part1b_Audio",
    "L_Distillery_Audio",
    "L_Pub_Assault_Audio",
    "L_Pub_Day_Audio",
    "L_Pub_Dusk_Audio",
    "L_Pub_Morning_Audio",
    "L_Pub_Night_Audio",
}

os.makedirs(OUTPUT, exist_ok=True)

audio_files = sorted([f for f in SOURCE.glob("*Audio*.upk")])

total = len(audio_files)
skipped_count = 0
success_count = 0
empty_count = 0
fail_count = 0

for upk in audio_files:
    stem = upk.stem
    
    if stem in SKIP:
        print(f"[SKIP] {upk.name} (already done)")
        skipped_count += 1
        continue
    
    out_dir = OUTPUT / stem
    # subedit.py appends .yaml itself, so we pass base path without .yaml
    yaml_base = out_dir / f"{stem}_INT"
    yaml_file = Path(str(yaml_base) + ".yaml")
    
    if yaml_file.exists():
        print(f"[EXISTS] {upk.name}")
        skipped_count += 1
        continue
    
    # Clean previous attempts
    dy_dir = TOOLKIT / "_DYextracted" / stem
    if dy_dir.exists():
        shutil.rmtree(dy_dir, ignore_errors=True)
    
    if out_dir.exists():
        shutil.rmtree(out_dir, ignore_errors=True)
    
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"[UNPACK] {upk.name}...")
    
    import subprocess
    cmd = [
        sys.executable,
        str(TOOLKIT / "subedit.py"),
        str(upk),
        "--output", str(yaml_base),
        "--langCode", "INT"
    ]
    
    result = subprocess.run(cmd, cwd=str(TOOLKIT), capture_output=True, text=True, timeout=120)
    
    if result.returncode != 0:
        print(f"  [FAIL] {upk.name}")
        print(f"  {result.stderr[:100]}")
        shutil.rmtree(out_dir, ignore_errors=True)
        fail_count += 1
        continue
    
    # Check if yaml was created
    if yaml_file.exists():
        yaml_size = yaml_file.stat().st_size
        print(f"  -> {stem}/ ({yaml_size} bytes)")
        success_count += 1
    else:
        print(f"  -> {stem}/ (no yaml output)")
        shutil.rmtree(out_dir, ignore_errors=True)
        empty_count += 1

print(f"\n=== DONE ===")
print(f"Total: {total}")
print(f"Skipped: {skipped_count}")
print(f"Success: {success_count}")
print(f"No YAML (removed): {empty_count}")
print(f"Failed: {fail_count}")