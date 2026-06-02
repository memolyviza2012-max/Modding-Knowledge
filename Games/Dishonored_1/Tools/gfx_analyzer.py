"""
DISHONORED-014: GFx Font Analyzer using FFDec
"""
import os
import subprocess

# FFDec path
ffdec_path = r"D:\Mod_Workspace\Tool\UE3\FFDec - Zipped\ffdec.exe"

# GFX files to analyze
gfx_files = [
    r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\gfx_extracted\DisFonts_SF_1.gfx",
    r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\gfx_extracted\DisFonts_SF_2.gfx"
]

print("DISHONORED-014: GFx Font Analyzer")
print("=" * 60)

# Check FFDec exists
if not os.path.exists(ffdec_path):
    print(f"[ERROR] FFDec not found at: {ffdec_path}")
else:
    print(f"[OK] FFDec found: {ffdec_path}\n")
    
    for gfx_file in gfx_files:
        if not os.path.exists(gfx_file):
            print(f"[SKIP] File not found: {gfx_file}")
            continue
            
        print(f"[SCANNING] {os.path.basename(gfx_file)}")
        print("-" * 50)
        
        try:
            command = [ffdec_path, "-info", gfx_file]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout + result.stderr
            
            # Filter for font-related info
            font_lines = [line for line in output.split('\n') 
                         if 'Font' in line or 'font' in line or 'FontID' in line]
            
            if font_lines:
                print(f"  [FOUND] Font entries:")
                for line in font_lines:
                    print(f"    -> {line.strip()}")
            else:
                print("  [EMPTY] No font entries found")
                # Show first few lines of output for debugging
                lines = output.split('\n')
                print(f"  First 5 lines of output:")
                for line in lines[:5]:
                    if line.strip():
                        print(f"    {line.strip()}")
                        
        except subprocess.TimeoutExpired:
            print(f"  [TIMEOUT] FFDec took too long")
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
        
        print()

print("=" * 60)
print("ANALYSIS COMPLETE")
