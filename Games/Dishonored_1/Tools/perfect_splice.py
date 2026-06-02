import os
import shutil
import struct
import subprocess

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
toolkit_dir = os.path.join(workspace_dir, "03_tools", "dishonored-toolkit")
dy_extracted = os.path.join(toolkit_dir, "_DYextracted")
dy_patched = os.path.join(toolkit_dir, "_DYpatched")
user_font_dir = os.path.join(workspace_dir, "04_output", "fonts_extracted")
game_upk = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole\DisFonts_SF.upk"
source_upk = os.path.join(workspace_dir, "01_source", "upk_files", "unpacked", "DisFonts_SF.upk")

print("[Step 1] Cleaning _DYpatched...")
if os.path.exists(dy_patched):
    shutil.rmtree(dy_patched)
if os.path.exists(dy_extracted):
    shutil.rmtree(dy_extracted)
os.makedirs(dy_patched, exist_ok=True)
os.makedirs(dy_extracted, exist_ok=True)

# Unpack first to get original structure
os.chdir(toolkit_dir)
subprocess.run(["python", "unpack.py", source_upk], capture_output=True)

targets = [
    ("fonts_efigs.3.SwfMovie", "fonts_efigs.swf"),
    ("gfxfontlib.4.SwfMovie", "gfxfontlib.swf")
]

for orig_name, new_name in targets:
    orig_path = os.path.join(dy_extracted, orig_name)
    new_path = os.path.join(user_font_dir, new_name)
    
    with open(orig_path, 'rb') as f:
        orig_data = f.read()
    ue3_properties = orig_data[:96]
    
    with open(new_path, 'rb') as f:
        new_swf = f.read()
    new_size = len(new_swf)
    
    size_bytes = struct.pack('<I', new_size)
    
    # Create without _patched first
    temp_path = os.path.join(dy_patched, orig_name)
    final_payload = ue3_properties + size_bytes + new_swf
    
    with open(temp_path, 'wb') as f:
        f.write(final_payload)
    
    print(f"   Created temp: {orig_name} ({len(final_payload):,} bytes)")
    
    # Now rename with _patched suffix (required by patch.py)
    patched_path = os.path.join(dy_patched, orig_name + "_patched")
    os.rename(temp_path, patched_path)
    print(f"   Renamed to: {orig_name}_patched")

print("\n[Step 2] Running patch.py...")
os.chdir(toolkit_dir)
subprocess.run(["python", "patch.py", source_upk], capture_output=True)

print("\n[Step 3] Installing to game...")
patched_file = source_upk + "_patched"
if os.path.exists(patched_file):
    shutil.copy(patched_file, game_upk)
    print(f"Installed! UPK size: {os.path.getsize(game_upk):,} bytes")
else:
    print("Failed: no patched file")