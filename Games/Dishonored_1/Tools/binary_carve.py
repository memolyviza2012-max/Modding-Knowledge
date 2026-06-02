import os
import struct

base_dir = r"D:\Mod_Workspace\Tool\UE3\Reverse Engineering"
donor_swf_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\Donor_Fonts_Carved"

print("[Step 1] Creating output directory...")
os.makedirs(donor_swf_dir, exist_ok=True)

signatures = [b'FWS', b'CWS', b'CFX']

target_upks = []
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.lower().endswith('.upk'):
            target_upks.append(os.path.join(root, file))

print(f"\n[Step 2] Binary carving from {len(target_upks)} UPK files...")

total_carved = 0

for upk_path in target_upks:
    game_name = os.path.basename(os.path.dirname(os.path.dirname(upk_path)))
    if len(game_name) < 2: game_name = "Unknown"
    
    try:
        with open(upk_path, 'rb') as f:
            data = f.read()
            
        found_in_file = 0
        for sig in signatures:
            idx = 0
            while True:
                idx = data.find(sig, idx)
                if idx == -1:
                    break
                
                version = data[idx+3]
                if version > 30:
                    idx += 3
                    continue
                    
                try:
                    file_size = struct.unpack('<I', data[idx+4:idx+8])[0]
                    
                    if 1024 < file_size < 20000000:
                        swf_data = data[idx:idx+file_size]
                        
                        ext = ".swf" if sig in [b'FWS', b'CWS'] else ".gfx"
                        out_name = f"{game_name}_{os.path.basename(upk_path)}_carved_{found_in_file}{ext}"
                        out_path = os.path.join(donor_swf_dir, out_name)
                        
                        with open(out_path, 'wb') as out_f:
                            out_f.write(swf_data)
                            
                        print(f"   [CARVED] {out_name} ({file_size:,} bytes)")
                        total_carved += 1
                        found_in_file += 1
                        idx += file_size
                    else:
                        idx += 3
                except:
                    idx += 3
                    
    except Exception as e:
        print(f"Error with {os.path.basename(upk_path)}: {e}")

print("\n========================================")
if total_carved > 0:
    print(f"SUCCESS! Carved {total_carved} Flash files!")
    print(f"Location: {donor_swf_dir}")
else:
    print("No Flash signatures found in these UPK files.")
print("========================================")
