import os
import subprocess
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
tools_dir = os.path.join(workspace_dir, "03_tools")
toolkit_dir = os.path.join(tools_dir, "dishonored-toolkit")
decompress_exe = os.path.join(tools_dir, "decompress.exe")
game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"

print("Step 2: Preparing DisFonts_SF.upk from game...")
upk_source_dir = os.path.join(workspace_dir, "01_source", "upk_files")
os.makedirs(upk_source_dir, exist_ok=True)
game_upk = os.path.join(game_dir, "DisFonts_SF.upk")
work_upk = os.path.join(upk_source_dir, "DisFonts_SF.upk")
uncompressed_upk = os.path.join(upk_source_dir, "unpacked", "DisFonts_SF.upk")

shutil.copy(game_upk, work_upk)
os.chdir(upk_source_dir)
subprocess.run([decompress_exe, "DisFonts_SF.upk"])
print("Done: DisFonts_SF.upk decompressed!")

print("\nStep 3: Unpacking with dishonored-toolkit...")
os.chdir(toolkit_dir)
result = subprocess.run(["python", "unpack.py", "-f", "SwfMovie", uncompressed_upk], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

print("\nStep 4: Setting up patch folder (_DYpatched)...")
dy_extracted = os.path.join(toolkit_dir, "_DYextracted")
dy_patched = os.path.join(toolkit_dir, "_DYpatched")

# Clean and create _DYpatched
if os.path.exists(dy_patched):
    shutil.rmtree(dy_patched)
os.makedirs(dy_patched)

# Copy the Thai fonts to _DYpatched
user_font_dir = os.path.join(workspace_dir, "04_output", "fonts_extracted")
thai_efigs = os.path.join(user_font_dir, "fonts_efigs.swf")
thai_fontlib = os.path.join(user_font_dir, "gfxfontlib.swf")

shutil.copy(thai_efigs, os.path.join(dy_patched, "fonts_efigs.swf"))
shutil.copy(thai_fontlib, os.path.join(dy_patched, "gfxfontlib.swf"))
print("Done: Thai fonts copied to _DYpatched!")

print("\nStep 5: Repacking with patch.py...")
os.chdir(toolkit_dir)
# patch.py saves as <filename>_patched in the same folder as the input file
output_patched = os.path.join(upk_source_dir, "DisFonts_SF_patched.upk")
result = subprocess.run(["python", "patch.py", uncompressed_upk], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Check if patched file was created
if os.path.exists(output_patched):
    print(f"SUCCESS! Repacked file size: {os.path.getsize(output_patched):,} bytes")
    
    # Backup original and install
    backup_path = game_upk + ".bak"
    if not os.path.exists(backup_path):
        shutil.move(game_upk, backup_path)
        print(f"Backup saved to: {backup_path}")
    else:
        os.remove(game_upk)
        print("Backup already exists, removing original")
        
    shutil.copy(output_patched, game_upk)
    print("INSTALLED! Thai font mod is now in the game folder!")
else:
    print("FAILED: Repack did not produce expected output file!")
    # Check what files were created
    print("Files in upk_source_dir:")
    for f in os.listdir(upk_source_dir):
        print(f"  {f}")
