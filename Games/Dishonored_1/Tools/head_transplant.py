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

print("[Step 1] Preparing _DYpatched...")
if os.path.exists(dy_patched):
    shutil.rmtree(dy_patched)
os.makedirs(dy_patched, exist_ok=True)

targets = [
    ("fonts_efigs.3.SwfMovie", "fonts_efigs.swf"),
    ("gfxfontlib.4.SwfMovie", "gfxfontlib.swf")
]

signatures = [b'FWS', b'CWS', b'CFX']

for orig_name, new_name in targets:
    orig_path = os.path.join(dy_extracted, orig_name)
    new_path = os.path.join(user_font_dir, new_name)
    out_path = os.path.join(dy_patched, orig_name + "_patched")
    
    print(f"\nProcessing: {orig_name}")
    
    with open(orig_path, 'rb') as f:
        orig_data = f.read()
        
    header_offset = -1
    for sig in signatures:
        idx = orig_data.find(sig)
        if idx != -1:
            header_offset = idx
            break
            
    if header_offset == -1:
        print(f"  No signature found in original!")
        continue
        
    ue3_header = bytearray(orig_data[:header_offset])
    actual_swf_size = len(orig_data) - header_offset
    
    with open(new_path, 'rb') as f:
        new_data = f.read()
    new_size = len(new_data)
    
    print(f"  Old SWF size: {actual_swf_size:,} bytes")
    print(f"  New SWF size: {new_size:,} bytes")
    
    old_size_bytes = struct.pack('<I', actual_swf_size)
    new_size_bytes = struct.pack('<I', new_size)
    
    header_replaced = ue3_header.replace(old_size_bytes, new_size_bytes)
    
    if header_replaced != ue3_header:
        print("  Header size updated!")
    else:
        print("  No size match in header")
        
    with open(out_path, 'wb') as f:
        f.write(header_replaced)
        f.write(new_data)
    print(f"  Saved to _DYpatched")

print("\n[Step 2] Running patch.py...")
os.chdir(toolkit_dir)
subprocess.run(["python", "patch.py", source_upk], capture_output=True)

patched_file = source_upk + "_patched"
if os.path.exists(patched_file):
    shutil.copy(patched_file, game_upk)
    print(f"\nInstalled! Size: {os.path.getsize(game_upk):,} bytes")
else:
    print("Failed: no patched file")