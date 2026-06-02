import os
import struct

startup_path = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\unpacked\Startup.upk"
carve_out_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\Startup_Carved"

print(f"Scanning: {startup_path}")
print(f"File size: {os.path.getsize(startup_path):,} bytes\n")

with open(startup_path, 'rb') as f:
    data = f.read()

# Search for any Flash signatures with no minimum size filter
signatures = [b'FWS', b'CWS', b'CFX']

for sig in signatures:
    idx = 0
    found_list = []
    while True:
        idx = data.find(sig, idx)
        if idx == -1:
            break
        
        version = data[idx+3] if idx+3 < len(data) else 0
        if version > 40:
            idx += 1
            continue
            
        try:
            file_size = struct.unpack('<I', data[idx+4:idx+8])[0]
        except:
            file_size = 0
            
        found_list.append((idx, version, file_size))
        idx += 1
        
    print(f"{sig.decode()}: found {len(found_list)} instances")
    for off, ver, sz in found_list[:10]:
        print(f"  Offset {hex(off)}: version={ver}, claimed_size={sz:,}")
    if len(found_list) > 10:
        print(f"  ... and {len(found_list)-10} more")
