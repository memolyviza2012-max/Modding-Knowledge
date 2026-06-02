import os

out_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\gfx_extracted"

for fname in ['DisFonts_SF_1.gfx', 'DisFonts_SF_2.gfx']:
    path = os.path.join(out_dir, fname)
    with open(path, 'rb') as f:
        data = f.read()
    
    print(f'{fname} ({len(data)} bytes)')
    
    # Search for SWF signatures
    for sig in [b'FWS', b'CWS', b'ZWS']:
        pos = data.find(sig)
        if pos != -1:
            print(f'  Found {sig.decode()} at pos {pos}')
            chunk = data[pos:pos+16]
            print(f'    Hex: {" ".join(f"{b:02X}" for b in chunk)}')
    
    # Also check start bytes
    print(f'  First 20 bytes: {" ".join(f"{b:02X}" for b in data[:20])}')
    
    # Check if data might be LZMA
    if data[0:3] == b'GFX':
        print('  Valid GFX header detected')
    
    print()
