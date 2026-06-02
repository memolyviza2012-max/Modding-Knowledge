import os
import subprocess
import shutil
import datetime

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
toolkit_dir = os.path.join(workspace_dir, "03_tools", "dishonored-toolkit")
dy_extracted = os.path.join(toolkit_dir, "_DYextracted")
dy_patched = os.path.join(toolkit_dir, "_DYpatched")
user_font_dir = os.path.join(workspace_dir, "04_output", "fonts_extracted")
game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"
game_upk = os.path.join(game_dir, "DisFonts_SF.upk")
source_upk = os.path.join(workspace_dir, "01_source", "upk_files", "unpacked", "DisFonts_SF.upk")

print("[Step 1] Cleaning folders...")
if os.path.exists(dy_patched):
    shutil.rmtree(dy_patched)
if os.path.exists(dy_extracted):
    shutil.rmtree(dy_extracted)
os.makedirs(dy_patched, exist_ok=True)
os.makedirs(dy_extracted, exist_ok=True)

print("\n[Step 2] Unpacking DisFonts_SF.upk to get structure...")
os.chdir(toolkit_dir)
subprocess.run(["python", "unpack.py", source_upk], capture_output=True)

print("\n[Step 3] Importing Thai fonts to _DYpatched with _patched suffix...")
src_efigs = os.path.join(user_font_dir, "fonts_efigs.swf")
src_gfx = os.path.join(user_font_dir, "gfxfontlib.swf")

# Naming format: name.objectId.type_patched (required by patch.py!)
dst_efigs = os.path.join(dy_patched, "fonts_efigs.3.SwfMovie_patched")
dst_gfx = os.path.join(dy_patched, "gfxfontlib.4.SwfMovie_patched")

shutil.copy(src_efigs, dst_efigs)
shutil.copy(src_gfx, dst_gfx)
print(f"   fonts_efigs.3.SwfMovie_patched -> {os.path.getsize(dst_efigs):,} bytes")
print(f"   gfxfontlib.4.SwfMovie_patched -> {os.path.getsize(dst_gfx):,} bytes")

print("\n[Step 4] Running patch.py...")
os.chdir(toolkit_dir)
result = subprocess.run(["python", "patch.py", source_upk], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)

print("\n[Step 5] Installing to game...")
patched_file = source_upk + "_patched"
if os.path.exists(patched_file):
    file_size = os.path.getsize(patched_file)
    print(f"Patched! Size: {file_size:,} bytes (was 211,744)")
    shutil.copy(patched_file, game_upk)
    print(f"Installed! Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
    if file_size != 211744:
        print("\nWARNING: File size changed! Update TOC!")
else:
    print("FAILED: No patched file produced")