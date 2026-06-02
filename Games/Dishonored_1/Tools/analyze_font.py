import os
import zlib

files = [
    (r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_SF.upk", 74561),
    (r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_LCZEHUNPOL_SF.upk", 51011)
]

for fpath, font_offset in files:
    print(f"=== {os.path.basename(fpath)} ===")
    print(f"Font data offset: {font_offset} (0x{font_offset:X})")
    
    with open(fpath, 'rb') as f:
        data = f.read()
    
    # The gfxfontlib starts shortly after the "font" keyword
    # Let's find gfxfontlib
    gfxfontlib_pos = data.find(b'gfxfontlib', font_offset - 100)
    print(f"gfxfontlib at: {gfxfontlib_pos} (0x{gfxfontlib_pos:X})")
    
    # Try to find the start of GFX data
    # Look backwards from gfxfontlib for GFX signature
    search_start = max(0, gfxfontlib_pos - 200)
    gfx_pos = data.rfind(b'GFX', search_start, gfxfontlib_pos)
    print(f"GFX signature before gfxfontlib at: {gfx_pos} (0x{gfx_pos:X})")
    
    if gfx_pos != -1:
        # Try decompressing from there
        compressed = data[gfx_pos:]
        print(f"Data from GFX to end: {len(compressed)} bytes")
        
        # Try zlib
        try:
            decompressed = zlib.decompress(compressed)
            print(f"  ZLIB SUCCESS: {len(decompressed)} bytes decompressed")
            
            # Save
            out_path = fpath.replace('.upk', '_font_decompressed.bin')
            with open(out_path, 'wb') as f:
                f.write(decompressed)
            print(f"  Saved to: {os.path.basename(out_path)}")
        except Exception as e:
            print(f"  ZLIB failed: {e}")
            
            # Try raw deflate
            try:
                decompressed = zlib.decompress(compressed, -15)
                print(f"  Raw deflate SUCCESS: {len(decompressed)} bytes")
            except Exception as e2:
                print(f"  Raw deflate failed: {e2}")
    
    print()
