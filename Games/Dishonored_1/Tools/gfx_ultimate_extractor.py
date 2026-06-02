"""
DISHONORED-016: Dual Approach - FFDec UPK + Overslice
"""
import os
import subprocess

ffdec_path = r"D:\Mod_Workspace\Tool\UE3\FFDec - Zipped\ffdec.exe"
upk_file_1 = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_SF.upk"
upk_file_2 = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_LCZEHUNPOL_SF.upk"
out_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\gfx_extracted"

os.makedirs(out_dir, exist_ok=True)

print("DISHONORED-016: Dual Approach - FFDec + Overslice")
print("=" * 60)

# Step 1: Try FFDec on UPK directly
print("\n[STEP 1] FFDec reading UPK directly...")
print(f"  Target: {os.path.basename(upk_file_2)}")

result = subprocess.run([ffdec_path, "-info", upk_file_2], 
                       capture_output=True, text=True, timeout=30)

print("  First 500 chars of stdout:")
print("  " + result.stdout[:500].replace("\n", "\n  "))

if result.stderr:
    print(f"\n  STDERR (first 300 chars):")
    print("  " + result.stderr[:300].replace("\n", "\n  "))

# Step 2: Overslice extraction
print("\n" + "=" * 60)
print("[STEP 2] Overslice Extraction (GFX to End of File)")

# From DisFonts_LCZEHUNPOL_SF.upk: offsets at 776 and 50978
offsets = [776, 50978]

with open(upk_file_2, "rb") as f:
    data = f.read()

print(f"  UPK file size: {len(data):,} bytes")

for i, offset in enumerate(offsets):
    # Overslice: extract from offset to END of file
    blob = data[offset:]
    
    out_path = os.path.join(out_dir, f"DisFonts_LCZEHUNPOL_Overslice_{i+1}.gfx")
    with open(out_path, "wb") as f_out:
        f_out.write(blob)
    print(f"\n  [{i+1}] Offset {offset} (0x{offset:X})")
    print(f"      Oversliced size: {len(blob):,} bytes")
    print(f"      Saved: {os.path.basename(out_path)}")
    
    # Check with FFDec
    print(f"      Checking with FFDec...")
    result2 = subprocess.run([ffdec_path, "-info", out_path],
                           capture_output=True, text=True, timeout=30)
    
    # Look for font mentions
    font_found = False
    for line in result2.stdout.split('\n'):
        if 'Font' in line or 'font' in line or 'Eurostile' in line:
            print(f"      *** FONT FOUND: {line.strip()}")
            font_found = True
    
    if not font_found:
        print(f"      No 'Font' keyword found in output")
    
    if "Premature end" in result2.stderr:
        print(f"      WARNING: Premature end of stream error")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
