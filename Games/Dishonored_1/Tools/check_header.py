import os

upk_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_decompressed\DisFonts_SF.upk'
with open(upk_path, 'rb') as f:
    data = f.read()

# Check bytes at offset 1166 (fonts_efigs) and 106330 (gfxfontlib)
for name, offset in [('fonts_efigs', 1166), ('gfxfontlib', 106330)]:
    chunk = data[offset:offset+32]
    print(f'{name} at {offset}:')
    print(f'  Hex: {" ".join(f"{b:02X}" for b in chunk)}')
    print(f'  ASCII: {"".join(chr(b) if 32<=b<127 else "." for b in chunk)}')
    print()
