#!/usr/bin/env python3
"""
Repack DisFonts_SF - pad to exact original size.
"""
import os
import struct
from pathlib import Path

SOURCE_UPK = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole\DisFonts_SF.upk"
EXTRACTED_DIR = r"E:\Mod_Workspace\Dishonored_Mod_Workspace\Mods\Dishonored_ModThai\DishonoredGame\CookedPCConsole_UnpackAll\DisFonts_SF"
OUTPUT_UPK = r"E:\Mod_Workspace\Dishonored_Mod_Workspace\Mods\Dishonored_ModThai\DishonoredGame\CookedPCConsole_Pack\DisFonts_SF.upk"

def repack():
    extracted_dir = Path(EXTRACTED_DIR)
    
    # Load header
    with open(extracted_dir / "_header", 'rb') as f:
        header = f.read()
    print(f"Header: {len(header)} bytes")
    
    # Load _objects.txt
    objects = []
    with open(extracted_dir / "_objects.txt", 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            if len(parts) >= 5:
                objects.append({
                    'name': parts[0].strip(),
                    'size_off': int(parts[1].strip()),
                    'size': int(parts[2].strip()),
                    'data_off': int(parts[3].strip()),
                    'offset': int(parts[4].strip())
                })
    print(f"Objects: {len(objects)}")
    
    # Load original UPK
    with open(SOURCE_UPK, 'rb') as f:
        original = bytearray(f.read())
    orig_size = len(original)
    print(f"Original: {orig_size} bytes")
    
    # Build new UPK = original size, swap object data
    new_upk = bytearray(original)
    
    for obj in objects:
        obj_file = extracted_dir / obj['name']
        orig_size_obj = obj['size']
        offset = obj['offset']
        
        if obj_file.exists():
            with open(obj_file, 'rb') as f:
                data = f.read()
            new_size = len(data)
        else:
            data = original[offset:offset + orig_size_obj]
            new_size = orig_size_obj
        
        # Force to original size exactly
        if new_size <= orig_size_obj:
            # Pad with zeros
            for i in range(new_size):
                new_upk[offset + i] = data[i]
            for i in range(new_size, orig_size_obj):
                new_upk[offset + i] = 0
        else:
            # Truncate to original size
            for i in range(orig_size_obj):
                new_upk[offset + i] = data[i]
        
        print(f"  {obj['name']}: {orig_size_obj} -> {min(new_size, orig_size_obj)} bytes")
    
    # Write output
    Path(OUTPUT_UPK).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_UPK, 'wb') as f:
        f.write(new_upk)
    
    print(f"\nOutput: {OUTPUT_UPK}")
    print(f"Size: {len(new_upk)} bytes (same as original: {len(new_upk) == orig_size})")

if __name__ == "__main__":
    repack()