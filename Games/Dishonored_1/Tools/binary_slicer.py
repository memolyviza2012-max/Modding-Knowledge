"""
DISHONORED-013: Binary Slicer - Extract GFX Blobs from UPK
"""
import os

upk_path = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole\DisFonts_SF.upk"
out_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\gfx_extracted"
ffdec_path = r"C:\Program Files (x86)\FFDec\ffdec.exe"

offsets = [752, 74528]

print("DISHONORED-013: Binary Slicer")
print("=" * 60)
os.makedirs(out_dir, exist_ok=True)

try:
    with open(upk_path, "rb") as f:
        data = f.read()

    print(f"UPK Size: {len(data):,} bytes\n")

    extracted_files = []
    for i, offset in enumerate(offsets):
        # Read GFX header - 8 bytes after signature
        # GFX header format: Signature(4) + Length(4) + more header data
        sig = data[offset:offset+4]
        length_field = data[offset+4:offset+8]
        length = int.from_bytes(length_field, 'little')
        
        # Read extended header to get actual size
        # Bytes 8-12 might contain more size info
        extra_size = int.from_bytes(data[offset+8:offset+12], 'little') if len(data) > offset+12 else 0
        
        print(f"[{i+1}] GFX at Offset {offset} (0x{offset:X})")
        print(f"    Signature: {sig.decode('ascii', errors='replace')}")
        print(f"    Length Field: {length} bytes")
        print(f"    Extra Size Field: {extra_size} bytes")
        
        # GFX files usually store size in bytes 8-12
        actual_size = extra_size if extra_size > length else length
        print(f"    Using size: {actual_size} bytes")
        
        # Extract
        blob = data[offset:offset+actual_size]
        
        out_file = os.path.join(out_dir, f"DisFonts_SF_{i+1}.gfx")
        with open(out_file, "wb") as f_out:
            f_out.write(blob)
            
        print(f"    [OK] Saved: DisFonts_SF_{i+1}.gfx ({len(blob):,} bytes)\n")
        extracted_files.append(out_file)
        
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print(f"Output directory: {out_dir}")
        
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
