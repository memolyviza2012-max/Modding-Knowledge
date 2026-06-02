import os

files = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_INT.yaml', 
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml',
     'DLC06_DaudBase_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_INT.yaml', 
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_TH.yaml',
     'DLC06_Slaughter_Int_Loot'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_INT.yaml', 
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml',
     'DLC07_Twk_Inv_Seekfree_SF'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_INT.yaml', 
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_TH.yaml',
     'L_DLC07_DraperShip_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_INT.yaml', 
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_TH.yaml',
     'L_DLC07_GlobalStore'),
]

output = []
for int_path, th_path, name in files:
    # Read INT to get exact format
    with open(int_path, 'rb') as f:
        raw = f.read()
    # Detect encoding
    if raw[:2] == b'\xff\xfe':
        enc = 'utf-16-le'
    elif raw[:2] == b'\xfe\xff':
        enc = 'utf-16-be'
    elif raw.startswith(b'\xef\xbb\xbf'):
        enc = 'utf-8-sig'
    else:
        enc = 'utf-8'
    
    int_text = raw.decode(enc, errors='replace')
    # Normalize line endings for counting
    int_normalized = int_text.replace('\r\n', '\n').replace('\r', '\n')
    int_lines = int_normalized.split('\n')
    
    # Read TH
    with open(th_path, 'rb') as f:
        th_raw = f.read()
    # Detect encoding
    if th_raw[:2] == b'\xff\xfe':
        th_enc = 'utf-16-le'
    elif th_raw[:2] == b'\xfe\xff':
        th_enc = 'utf-16-be'
    elif th_raw.startswith(b'\xef\xbb\xbf'):
        th_enc = 'utf-8-sig'
    else:
        th_enc = 'utf-8'
    
    th_text = th_raw.decode(th_enc, errors='replace')
    th_normalized = th_text.replace('\r\n', '\n').replace('\r', '\n')
    th_lines = th_normalized.split('\n')
    
    output.append(f'=== {name} ===')
    output.append(f'  INT: {len(int_lines)} lines, encoding={enc}')
    output.append(f'  TH: {len(th_lines)} lines, encoding={th_enc}')
    output.append(f'  Match: {len(int_lines) == len(th_lines)}')
    
    # Check first and problem lines
    if len(int_lines) > 0:
        output.append(f'  INT line 1: {repr(int_lines[0][:80])}')
    if len(th_lines) > 0:
        output.append(f'  TH line 1: {repr(th_lines[0][:80])}')

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\format_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('Written to format_check.txt')
for line in output:
    print(line)