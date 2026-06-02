import os

upk_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_LCZEHUNPOL_decompressed\DisFonts_LCZEHUNPOL_SF.upk'
with open(upk_path, 'rb') as f:
    data = f.read()

print(f'File size: {len(data)} bytes')

# Search for GFX signature
signatures = [b'GFX', b'FWS', b'CWS']
for sig in signatures:
    pos = data.find(sig)
    if pos != -1:
        print(f'Found {sig} at offset {pos} (0x{pos:X})')
        chunk = data[pos:pos+32]
        print(f'Header: {" ".join(f"{b:02X}" for b in chunk)}')
