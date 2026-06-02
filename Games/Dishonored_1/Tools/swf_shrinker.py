import os
import zlib

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
font_dir = os.path.join(workspace_dir, "04_output", "fonts_extracted")

targets = ["fonts_efigs.swf", "gfxfontlib.swf"]

print("[Step 1] Starting SWF compression...")

for fname in targets:
    fpath = os.path.join(font_dir, fname)
    outpath = os.path.join(font_dir, fname.replace(".swf", "_compressed.swf"))
    
    if not os.path.exists(fpath):
        print(f"Not found: {fname}")
        continue
        
    with open(fpath, 'rb') as f:
        data = f.read()
        
    if data[:3] == b'CWS':
        print(f"[{fname}] Already compressed! Skipping.")
        continue
    elif data[:3] != b'FWS':
        print(f"[{fname}] Not a valid uncompressed SWF!")
        continue
        
    version = data[3:4]
    file_len = data[4:8]
    payload = data[8:]
    
    comp_payload = zlib.compress(payload)
    
    with open(outpath, 'wb') as f:
        f.write(b'CWS')
        f.write(version)
        f.write(file_len)
        f.write(comp_payload)
        
    old_size = len(data)
    new_size = len(comp_payload) + 8
    print(f"   [{fname}] Compressed!")
    print(f"      {old_size:,} -> {new_size:,} bytes")

print("\n========================================")
print("Done! Thai fonts compressed to CWS format!")
print("========================================")