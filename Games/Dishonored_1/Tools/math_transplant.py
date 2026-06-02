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
os.makedirs(dy_patched, exist_ok=True)

targets = [
    ("fonts_efigs.3.SwfMovie", "fonts_efigs.swf"),
    ("gfxfontlib.4.SwfMovie", "gfxfontlib.swf")
]

success_count = 0

for orig_name, new_name in targets:
    orig_path = os.path.join(dy_extracted, orig_name)
    new_path = os.path.join(user_font_dir, new_name)
    out_path = os.path.join(dy_patched, orig_name)
    
    print(f"\nAnalyzing: {orig_name}")
    
    with open(orig_path, 'rb') as f:
        orig_data = f.read()
        
    with open(new_path, 'rb') as f:
        new_swf = f.read()
        
    header_end = -1
    array_size = 0
    for i in range(len(orig_data) - 4):
        val = struct.unpack('<I', orig_data[i:i+4])[0]
        if val == len(orig_data) - i - 4:
            header_end = i
            array_size = val
            break
            
    if header_end != -1:
        print(f"   Found UE3 header at offset {header_end} (size: {array_size:,})")
        print(f"   Old SWF: {array_size:,} bytes -> New SWF: {len(new_swf):,} bytes")
        
        ue3_header = orig_data[:header_end]
        new_size_bytes = struct.pack('<I', len(new_swf))
        
        with open(out_path, 'wb') as f:
            f.write(ue3_header)
            f.write(new_size_bytes)
            f.write(new_swf)
            
        print("   SUCCESS: Head transplant complete!")
        success_count += 1
    else:
        print("   FAILED: Cannot find header pattern")

if success_count == 2:
    print("\n[Step 2] Running patch.py...")
    os.chdir(toolkit_dir)
    subprocess.run(["python", "unpack.py", source_upk], capture_output=True)
    subprocess.run(["python", "patch.py", source_upk], capture_output=True)
    
    patched_file = source_upk + "_patched"
    if os.path.exists(patched_file):
        shutil.copy(patched_file, game_upk)
        print(f"\nInstalled! UPK size: {os.path.getsize(game_upk):,} bytes")
    else:
        print("Failed: no patched file")
else:
    print(f"\nOnly {success_count}/2 fonts processed")