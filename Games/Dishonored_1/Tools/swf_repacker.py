"""
DISHONORED-021: Simple UPK Repacker for SwfMovie
Creates a new UPK with modified SWF files
"""
import os
import struct
import lzo

class SimpleUPKRepacker:
    def __init__(self, source_upk, output_upk):
        self.source_upk = source_upk
        self.output_upk = output_upk
        self.header_size = 0
        
    def read_objects_list(self, split_dir):
        """Read the _objects.txt to get object info"""
        objects = {}
        with open(os.path.join(split_dir, '_objects.txt'), 'r') as f:
            for line in f:
                parts = [p.strip() for p in line.split(';')]
                if len(parts) >= 6:
                    name_full = parts[0]
                    size = int(parts[2])
                    offset = int(parts[3])
                    
                    name_parts = name_full.split('.')
                    name = name_parts[0]
                    obj_id = name_parts[1]
                    obj_type = '.'.join(name_parts[2:])
                    
                    objects[name] = {
                        'id': obj_id,
                        'type': obj_type,
                        'orig_offset': offset,
                        'orig_size': size
                    }
        return objects
    
    def read_names_list(self, split_dir):
        """Read the _names.txt"""
        names = []
        with open(os.path.join(split_dir, '_names.txt'), 'r') as f:
            for line in f:
                name = line.strip()
                if name:
                    names.append(name)
        return names
    
    def repack(self, split_dir):
        """Main repacking method"""
        print(f"Source: {self.source_upk}")
        print(f"Output: {self.output_upk}")
        
        # Read original UPK
        with open(self.source_upk, 'rb') as f:
            original_data = f.read()
        
        print(f"Original size: {len(original_data):,} bytes")
        
        # Read object info
        objects = self.read_objects_list(split_dir)
        print(f"Objects: {list(objects.keys())}")
        
        # Read modified SWF files
        swf_data = {}
        for fname in os.listdir(split_dir):
            if fname.endswith('.swf'):
                fpath = os.path.join(split_dir, fname)
                with open(fpath, 'rb') as f:
                    swf_data[fname] = f.read()
                print(f"Loaded {fname}: {len(swf_data[fname]):,} bytes")
        
        # For a simple repack, we copy original and note the changes needed
        # Full implementation would rebuild the entire UPK structure
        # This is complex because we need to:
        # 1. Update the header
        # 2. Rebuild the names table
        # 3. Rebuild the imports table
        # 4. Rebuild the exports table with new offsets
        # 5. Copy/update object data at new offsets
        
        print("\n" + "="*60)
        print("NOTE: Full UPK repacking is complex.")
        print("This script shows what would be needed.")
        print("="*60)
        
        # For now, just copy original as placeholder
        with open(self.output_upk, 'wb') as f:
            f.write(original_data)
        
        print(f"\nPlaceholder written to: {self.output_upk}")
        return False


# Main
if __name__ == "__main__":
    source = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_decompressed\DisFonts_SF.upk"
    output = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\DisFonts_SF_Repacked.upk"
    split_dir = r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main\_DYextracted"
    
    repacker = SimpleUPKRepacker(source, output)
    repacker.repack(split_dir)
    
    print("\nTo complete repacking, either:")
    print("1. Install ImageMagick and use patch.py")
    print("2. Manually edit the UPK with a hex editor")
    print("3. Wait for a full repacking implementation")
