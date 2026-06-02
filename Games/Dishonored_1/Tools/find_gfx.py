import os

upk_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_decompressed\DisFonts_SF.upk'
with open(upk_path, 'rb') as f:
    data = f.read()

# Search for SWF/GFX signatures
signatures = [b'FWS', b'CWS', b'ZWS', b'GFX']
for sig in signatures:
    pos = data.find(sig)
    while pos != -1:
        print(f'Found {sig} at {pos} (0x{pos:X})')
        chunk = data[pos:pos+32]
        print(f'  Hex: {" ".join(f"{b:02X}" for b in chunk)}')
        pos = data.find(sig, pos + 1)
    if data.find(sig) == -1:
        print(f'{sig}: NOT FOUND')
