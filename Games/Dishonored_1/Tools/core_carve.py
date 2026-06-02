import os
import struct

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
startup_path = os.path.join(workspace_dir, "01_source", "upk_files", "unpacked", "Startup.upk")
carve_out_dir = os.path.join(workspace_dir, "04_output", "Startup_Carved")

print("[Step 1] Preparing carving site...")
os.makedirs(carve_out_dir, exist_ok=True)

if not os.path.exists(startup_path):
    print(f"File not found: {startup_path}!")
    exit()

print(f"\n[Step 2] Scanning Flash signatures (FWS, CWS, CFX) in Startup.upk...")
signatures = [b'FWS', b'CWS', b'CFX']

try:
    with open(startup_path, 'rb') as f:
        data = f.read()
        
    found_count = 0
    for sig in signatures:
        idx = 0
        while True:
            idx = data.find(sig, idx)
            if idx == -1:
                break
            
            try:
                file_size = struct.unpack('<I', data[idx+4:idx+8])[0]
                
                if 50000 < file_size < 10000000:
                    ext = ".swf" if sig in [b'FWS', b'CWS'] else ".gfx"
                    out_name = f"Startup_Offset_{hex(idx)}{ext}"
                    out_path = os.path.join(carve_out_dir, out_name)
                    
                    with open(out_path, 'wb') as out_f:
                        out_f.write(data[idx:idx+file_size])
                        
                    print(f"   [LOCKED] Found at Offset: {hex(idx)} (sig: {sig.decode()}, size: {file_size:,} bytes)")
                    found_count += 1
                
                idx += 3
            except:
                idx += 3
                
    print("\n========================================")
    if found_count > 0:
        print(f"X-Ray complete! Found {found_count} Flash files hidden in Startup.upk!")
        print(f"Location: {carve_out_dir}")
    else:
        print("No large Flash files found in Startup.upk (may be compressed).")
    print("========================================")

except Exception as e:
    print(f"Error: {e}")