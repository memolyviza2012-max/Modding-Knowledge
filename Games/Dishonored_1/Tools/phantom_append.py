import os
import struct
import shutil
import re

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
user_font_dir = os.path.join(workspace_dir, "04_output", "fonts_extracted")
toolkit_dir = os.path.join(workspace_dir, "03_tools", "dishonored-toolkit")
dy_extracted = os.path.join(toolkit_dir, "_DYextracted")

game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame"
game_upk = os.path.join(game_dir, "CookedPCConsole", "DisFonts_SF.upk")
toc_path = os.path.join(game_dir, "PCConsoleTOC.txt")

base_upk = os.path.join(workspace_dir, "04_output", "Direct_JPEXS_Work", "unpacked", "DisFonts_SF.upk")
if not os.path.exists(base_upk):
    base_upk = game_upk + ".bak"

print(f"[Step 1] Reading base UPK: {os.path.basename(base_upk)}")
with open(base_upk, 'rb') as f:
    upk_data = bytearray(f.read())

targets = [
    ("fonts_efigs.3.SwfMovie", "fonts_efigs.swf"),
    ("gfxfontlib.4.SwfMovie", "gfxfontlib.swf")
]

success_count = 0
for orig_name, new_name in targets:
    orig_path = os.path.join(dy_extracted, orig_name)
    if not os.path.exists(orig_path): 
        print(f"Missing: {orig_path}")
        continue
    
    with open(orig_path, 'rb') as f:
        orig_obj = f.read()
    orig_size = len(orig_obj)
    
    # Find original offset
    orig_offset = upk_data.find(orig_obj[:256])
    if orig_offset == -1:
        print(f"Cant find {orig_name} in UPK!")
        continue
        
    # Find Export Table entry (size + offset pattern)
    search_pattern = struct.pack('<II', orig_size, orig_offset)
    table_offset = upk_data.find(search_pattern)
    
    if table_offset == -1:
        print(f"Cant find Export Table for {orig_name}!")
        continue
        
    print(f"\nProcessing: {orig_name}")
    print(f"   Table at offset: {table_offset}")
    
    # Build new payload
    new_path = os.path.join(user_font_dir, new_name)
    with open(new_path, 'rb') as f:
        new_swf = f.read()
        
    ue3_properties = orig_obj[:96]
    size_bytes = struct.pack('<I', len(new_swf))
    new_payload = ue3_properties + size_bytes + new_swf
    new_size = len(new_payload)
    
    # Append to end
    new_offset = len(upk_data)
    upk_data.extend(new_payload)
    
    # Update Export Table
    new_pattern = struct.pack('<II', new_size, new_offset)
    upk_data[table_offset:table_offset+8] = new_pattern
    
    print(f"   Moved from {orig_offset} to tail {new_offset}")
    success_count += 1

if success_count == 2:
    print("\n[Step 2] Saving and installing...")
    out_upk = os.path.join(workspace_dir, "04_output", "DisFonts_SF_Appended.upk")
    with open(out_upk, 'wb') as f:
        f.write(upk_data)
        
    shutil.copy(out_upk, game_upk)
    final_size = len(upk_data)
    print(f"   Installed! New size: {final_size:,} bytes")
    
    print("\n[Step 3] Updating TOC...")
    with open(toc_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    with open(toc_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if "DisFonts_SF.upk" in line:
                old_match = re.match(r'^(\d+)', line.strip())
                if old_match:
                    f.write(line.replace(f"{old_match.group(1)} ", f"{final_size} ", 1))
            else:
                f.write(line)
    print("   TOC updated!")
    print("\nDone! Thai fonts appended to end of UPK!")
else:
    print(f"Only {success_count}/2 processed")