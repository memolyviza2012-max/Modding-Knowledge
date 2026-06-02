import os
import re

game_dir = r'F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole'
upk_dir = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files'

priority = [
    'Startup.upk',
    'DishonoredGame.upk', 
    'GlobalPersistentCookerData.upk',
    'DisFonts_SF.upk',
    'DisFonts_LCZEHUNPOL_SF.upk'
]

print('PRIORITY FONT SCAN')
print('='*60)

for fname in priority:
    for base in [game_dir, upk_dir]:
        path = os.path.join(base, fname)
        if not os.path.exists(path):
            continue
        
        print(f'[{fname}] ({os.path.getsize(path):,} bytes)')
        print(f'  Path: {path}')
        
        with open(path, 'rb') as f:
            data = f.read()
        
        strings = re.findall(b'[\\x20-\\x7e]{6,50}', data)
        
        font_strings = []
        for s in strings:
            lower = s.lower()
            if any(fw in lower for fw in [b'font', b'emerge', b'eurostile', b'chalet', b'cologne', b'glyph', b'thai']):
                font_strings.append(s.decode('ascii', errors='replace'))
        
        if font_strings:
            print(f'  Font-related strings:')
            for s in sorted(set(font_strings))[:15]:
                print(f'    {s}')
        else:
            print('  No font-related strings found')
        print()
