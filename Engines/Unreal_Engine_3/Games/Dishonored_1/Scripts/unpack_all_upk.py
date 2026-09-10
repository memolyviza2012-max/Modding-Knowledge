import os, sys, shutil
from pathlib import Path
import time

TOOLKIT = Path(r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main")
SOURCE = Path(r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole")
OUTPUT = Path(r"E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole_UnpackAll")

# 36 Audio files that have no dialogue (already identified)
SKIP_AUDIO = {
    "AkAudio", "AudioGraph_Twk_SF", "L_ArtDealer_Audio", "L_Boyle_Ext_Audio",
    "L_Boyle_Int_Audio", "L_Bridge_Part1a_Audio", "L_Bridge_Part1c_Audio", "L_Bridge_Part2_Audio",
    "L_Brothel_Audio", "L_Distillery2_Audio", "L_Flooded_FAssassins_Audio", "L_Flooded_FGate_Audio",
    "L_Flooded_FIntro_Audio", "L_Flooded_FRefinery_Audio", "L_Flooded_FStreets_Audio", "L_Galvani1_Audio",
    "L_Isl_Audio_Master", "L_Isl_Audio_Slave", "L_Isl_HighChaos_Audio", "L_Isl_LowChaos_Audio",
    "L_LightH_Audio_Master", "L_LightH_Audio_Slave", "L_LightH_HighChaos_Audio", "L_LightH_LowChaos_Audio",
    "L_OutsiderDream_Audio", "L_Ovrsr_Audio", "L_Ovrsr_Back_Audio", "L_Ovrsr_Kennel_Audio",
    "L_Prison_Audio", "L_PrsnSewer_Audio", "L_Streets1_Audio", "L_Streets2_Audio",
    "L_Streetsewer_Audio", "L_Tower_Audio", "L_TowerRtrn_Int_Audio", "L_TowerRtrn_Yard_Audio"
}

# Folders already translated (don't re-unpack)
COOKED_PC = Path(r"E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole")
EXISTING_FOLDERS = {d.name for d in COOKED_PC.iterdir() if d.is_dir()} if COOKED_PC.exists() else set()

os.makedirs(OUTPUT, exist_ok=True)

# Get all UPK files
all_upk = sorted(SOURCE.glob("*.upk"))

total = len(all_upk)
skipped_audio = 0
skipped_existing = 0
success = 0
has_discov = 0
no_discov = 0
failed = 0

print(f"Total UPK files in game: {total}")
print(f"Skip {len(SKIP_AUDIO)} Audio files (no dialogue)")
print(f"Skip {len(EXISTING_FOLDERS)} existing folders (already translated)")
print()

for upk in all_upk:
    stem = upk.stem
    
    # Skip if in Audio list (no dialogue)
    if stem in SKIP_AUDIO:
        skipped_audio += 1
        continue
    
    # Skip if folder already exists (already translated)
    if stem in EXISTING_FOLDERS:
        skipped_existing += 1
        continue
    
    yaml_base = OUTPUT / f"{stem}_INT"
    yaml_file = Path(str(yaml_base) + ".yaml")
    
    # Clean previous attempts
    dy_dir = TOOLKIT / "_DYextracted" / stem
    if dy_dir.exists():
        shutil.rmtree(dy_dir, ignore_errors=True)
    
    print(f"[{len(SKIP_AUDIO)+skipped_existing+success+no_discov+failed}/{total}] {upk.name}...")
    
    import subprocess
    cmd = [
        sys.executable,
        str(TOOLKIT / "subedit.py"),
        str(upk),
        "--output", str(yaml_base),
        "--langCode", "INT"
    ]
    
    start_time = time.time()
    result = subprocess.run(cmd, cwd=str(TOOLKIT), capture_output=True, text=True, timeout=180)
    elapsed = time.time() - start_time
    
    if result.returncode != 0:
        print(f"  [FAIL] ({elapsed:.1f}s) - {result.stderr[:80]}")
        failed += 1
        continue
    
    # Check for DisConv content or yaml files
    has_yaml = yaml_file.exists()
    out_dir = OUTPUT / stem
    has_discov_files = False
    if out_dir.exists():
        has_discov_files = any(f.name.startswith("DisConv_") for f in out_dir.iterdir())
    
    if has_yaml or has_discov_files:
        print(f"  OK ({elapsed:.1f}s) - DisConv content found")
        success += 1
        has_discov += 1
    else:
        # No DisConv content, remove the folder
        print(f"  EMPTY ({elapsed:.1f}s) - no DisConv, removing")
        if out_dir.exists():
            shutil.rmtree(out_dir, ignore_errors=True)
        no_discov += 1

print()
print("=== SUMMARY ===")
print(f"Total UPK files: {total}")
print(f"Skipped (Audio no dialogue): {skipped_audio}")
print(f"Skipped (already exists): {skipped_existing}")
print(f"Success (has DisConv): {success}")
print(f"Removed (no DisConv): {no_discov}")
print(f"Failed: {failed}")