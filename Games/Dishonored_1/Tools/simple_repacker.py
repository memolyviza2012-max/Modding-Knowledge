"""
Simple UPK Repacker for SwfMovie objects only
Bypasses texture2d dependency
"""
import os
import struct
from binary import BinaryStream

def repack_swf(upk_path, output_path, split_dir):
    """Repack modified SwfMovie files back into UPK"""
    
    with open(upk_path, 'rb') as f:
        original_data = f.read()
    
    # Read objects list
    objects_file = os.path.join(split_dir, '_objects.txt')
    with open(objects_file, 'r') as f:
        objects = {}
        for line in f:
            parts = line.strip().split(';')
            if len(parts) >= 6:
                name_full = parts[0]  # e.g., "fonts_efigs.3.SwfMovie"
                offset = int(parts[3])  # offset in file
                size = int(parts[2])  # original size
                
                # Extract name, id, type
                name_parts = name_full.split('.')
                name = name_parts[0]
                obj_id = name_parts[1]
                obj_type = '.'.join(name_parts[2:])
                
                objects[name] = {
                    'id': obj_id,
                    'type': obj_type,
                    'offset': offset,
                    'size': size
                }
    
    print(f"Found objects: {list(objects.keys())}")
    
    # Find modified SWF files in split_dir
    swf_files = {}
    for fname in os.listdir(split_dir):
        if fname.endswith('.swf'):
            fpath = os.path.join(split_dir, fname)
            with open(fpath, 'rb') as f:
                swf_files[fname] = f.read()
            print(f"Loaded modified {fname}: {len(swf_files[fname])} bytes")
    
    # Create new UPK
    with open(output_path, 'wb') as f:
        writer = BinaryStream(f)
        
        # For now, just copy original and note that manual editing is needed
        # A full implementation would rebuild the entire UPK structure
        writer.writeBytes(original_data)
    
    print(f"\nNote: This is a placeholder. Full repacking requires:")
    print("1. Rebuilding the UPK header")
    print("2. Updating object table with new offsets/sizes")
    print("3. Compressing blocks if needed")
    print(f"\nOutput written to: {output_path}")

# Usage
split_dir = r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main\_DYextracted"
upk_source = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_decompressed\DisFonts_SF.upk"
output = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\DisFonts_SF_Repacked.upk"

repack_swf(upk_source, output, split_dir)
