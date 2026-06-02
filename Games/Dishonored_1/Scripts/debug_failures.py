import os, yaml, re

files_to_check = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml', 'DLC06_DaudBase_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_TH.yaml', 'DLC06_Slaughter_Int_Loot'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml', 'DLC07_Twk_Inv_Seekfree_SF'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_TH.yaml', 'L_DLC07_DraperShip_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_TH.yaml', 'L_DLC07_GlobalStore'),
]

output = []
for path, name in files_to_check:
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8', errors='replace')
    lines = text.split('\n')
    
    try:
        yaml.safe_load(text)
        output.append(f'OK: {name}')
    except yaml.YAMLError as e:
        err_str = str(e)
        m = re.search(r'line (\d+)', err_str)
        if m:
            actual_line = int(m.group(1))
            output.append(f'FAIL: {name} at line {actual_line}')
            if actual_line <= len(lines):
                line_content = lines[actual_line-1]
                output.append(f'  Line {actual_line}: [first 120 chars] {line_content[:120]}')
        else:
            output.append(f'FAIL: {name} - no line info')
            output.append(f'  Error: {err_str[:100]}')
    output.append('')

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\debug_failures.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print('Written to debug_failures.txt')
for line in output:
    print(line)