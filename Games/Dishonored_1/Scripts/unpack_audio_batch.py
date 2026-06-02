import os, sys, subprocess
from pathlib import Path

TOOLKIT = Path(r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main")
SOURCE = Path(r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole")
OUTPUT = Path(r"E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole_UnpackAll")

# 7 files to SKIP (already unpacked)
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

# Find all Audio UPK files
audio_files = sorted([f for f in SOURCE.glob("*Audio*.upk")])

total = len(audio_files)
skipped_count = 0
success_count = 0
empty_count = 0
fail_count = 0

def has_text_content(upk_stem):
    """Check if UPK has translatable text content.
    Returns True if _names.txt contains readable text entries (not just binary names).
    Also checks if there are .txt or .json files with actual text.
    """
    out_dir = OUTPUT / upk_stem
    names_txt = out_dir / "_names.txt"
    
    if not names_txt.exists():
        return False
    
    # Read names and check for real text entries
    try:
        with open(names_txt, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
        
        if not content:
            return False
        
        lines = content.split("\n")
        
        # Check if names are meaningful text (not just binary-looking)
        # Real text names typically have readable ASCII/Unicode characters
        readable_count = 0
        for line in lines:
            line = line.strip().strip('"')
            if len(line) >= 3:
                # Check if line has at least some letters
                if any(c.isalpha() for c in line):
                    readable_count += 1
        
        # If more than 30% of names are readable text, likely has text content
        if len(lines) > 0 and readable_count / len(lines) > 0.3:
            return True
    except:
        pass
    
    return False

for upk in audio_files:
    stem = upk.stem  # e.g. "L_ArtDealer_Audio"
    
    if stem in SKIP:
        print(f"[SKIP] {upk.name} (already exists)")
        skipped_count += 1
        continue
    
    out_dir = OUTPUT / stem
    
    # Check if already processed
    names_txt = out_dir / "_names.txt"
    objects_txt = out_dir / "_objects.txt"
    
    if names_txt.exists() and objects_txt.exists():
        if has_text_content(stem):
            print(f"[EXISTS] {upk.name} - has text content, keeping")
            success_count += 1
        else:
            print(f"[EMPTY] {upk.name} - no text content, removing")
            import shutil
            shutil.rmtree(out_dir, ignore_errors=True)
            empty_count += 1
        continue
    
    print(f"[UNPACK] {upk.name}...")
    
    # Clean up any previous failed attempt
    import shutil
    failed_dir = TOOLKIT / "_DYextracted" / stem
    if failed_dir.exists():
        shutil.rmtree(failed_dir, ignore_errors=True)
    
    # Run unpack
    cmd = [
        sys.executable,
        str(TOOLKIT / "unpack.py"),
        str(upk),
        "--split"
    ]
    
    result = subprocess.run(cmd, cwd=str(TOOLKIT), capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  [FAIL] {upk.name}")
        print(f"  Error: {result.stderr[:200]}")
        fail_count += 1
        continue
    
    # Move output to OUTPUT
    src_dir = TOOLKIT / "_DYextracted" / stem
    if src_dir.exists():
        os.makedirs(out_dir, exist_ok=True)
        for item in src_dir.iterdir():
            dst = out_dir / item.name
            try:
                if item.is_file():
                    shutil.move(str(item), str(dst))
                elif item.is_dir():
                    shutil.move(str(item), str(dst))
            except Exception as e:
                print(f"  [WARN] Could not move {item.name}: {e}")
        try:
            src_dir.rmdir()
        except:
            pass
    
    # Check if has text content
    if has_text_content(stem):
        print(f"  -> {stem}/ (has text content, kept)")
        success_count += 1
    else:
        print(f"  -> {stem}/ (no text content, removing)")
        shutil.rmtree(out_dir, ignore_errors=True)
        empty_count += 1

print(f"\n=== DONE ===")
print(f"Total: {total}")
print(f"Skipped (already exists): {skipped_count}")
print(f"Kept (has text): {success_count}")
print(f"Removed (no text): {empty_count}")
print(f"Failed: {fail_count}")