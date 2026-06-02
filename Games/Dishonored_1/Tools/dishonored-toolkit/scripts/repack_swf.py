#!/usr/bin/env python3
"""
Repack modified files back into a UPK.
DisFonts_SF contains SwfMovie objects.
"""
import os
import struct
from pathlib import Path

# Paths
SOURCE_UPK = r"E:\Mod_Workspace\Dishonored_Mod_Workspace\Mods\Dishonored_ModThai\DishonoredGame\CookedPCConsole\DisFonts_SF.upk"
EXTRACTED_DIR = r"E:\Mod_Workspace\Dishonored_Mod_Workspace\Mods\Dishonored_ModThai\DishonoredGame\CookedPCConsole_UnpackAll\DisFonts_SF"
OUTPUT_UPK = r"E:\Mod_Workspace\Dishonored_Mod_Workspace\Mods\Dishonored_ModThai\DishonoredGame\CookedPCConsole_Pack\DisFonts_SF.upk"

def repack_upk():
    extracted_dir = Path(EXTRACTED_DIR)
    
    # Load header
    header_path = extracted_dir / "_header"
    with open(header_path, 'rb') as f:
        header = f.read()
    header_size = len(header)
    print(f"Header: {header_size} bytes")
    
    # Load _objects.txt
    objects_path = extracted_dir / "_objects.txt"
    objects = []
    with open(objects_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            if len(parts) >= 5:
                name = parts[0].strip()  # e.g. "fonts_efigs.3.SwfMovie"
                size_off = int(parts[1].strip())
                size = int(parts[2].strip())
                data_off = int(parts[3].strip())
                offset = int(parts[4].strip())
                objects.append({
                    'name': name,
                    'size_off': size_off,
                    'size': size,
                    'data_off': data_off,
                    'offset': offset
                })
    
    print(f"Objects: {len(objects)}")
    
    # Load original UPK
    with open(SOURCE_UPK, 'rb') as f:
        original_data = bytearray(f.read())
    original_size = len(original_data)
    print(f"Original UPK: {original_size} bytes")
    
    # Read modified files from extracted dir
    modified_files = {}
    for obj in objects:
        obj_file = extracted_dir / obj['name']
        if obj_file.exists():
            with open(obj_file, 'rb') as f:
                data = f.read()
            modified_files[obj['name']] = {
                'data': data,
                'size': len(data),
                'offset': obj['offset'],
                'orig_size': obj['size']
            }
            print(f"  {obj['name']}: {obj['size']} -> {len(data)} bytes")
    
    # Build new UPK
    # Start with header
    new_upk = bytearray(header)
    
    # Copy each object (use modified data if available, else copy from original)
    for obj in objects:
        obj_name = obj['name']
        obj_offset = obj['offset']
        obj_size = obj['size']
        
        if obj_name in modified_files:
            obj_data = modified_files[obj_name]['data']
        else:
            # Copy from original
            obj_data = original_data[obj_offset:obj_offset + obj_size]
        
        # Ensure we have enough space
        needed = obj_offset + len(obj_data)
        if needed > len(new_upk):
            new_upk.extend(b'\x00' * (needed - len(new_upk)))
        
        # Write object data
        for i, b in enumerate(obj_data):
            new_upk[obj_offset + i] = b
        
        # Zero out remaining space if new data is smaller
        if obj_name in modified_files:
            new_size = len(obj_data)
            orig_size = modified_files[obj_name]['orig_size']
            if new_size < orig_size:
                for i in range(new_size, orig_size):
                    if obj_offset + i < len(new_upk):
                        new_upk[obj_offset + i] = 0
    
    # Write output
    Path(OUTPUT_UPK).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_UPK, 'wb') as f:
        f.write(new_upk)
    
    print(f"\nOutput: {OUTPUT_UPK}")
    print(f"Size: {len(new_upk)} bytes")

if __name__ == "__main__":
    repack_upk()