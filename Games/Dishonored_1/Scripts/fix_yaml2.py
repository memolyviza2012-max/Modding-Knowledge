import os, shutil, re

# Files that need fixing
files = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml', 'DLC06_DaudBase_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_TH.yaml', 'DLC06_Slaughter_Int_Loot'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml', 'DLC07_Twk_Inv_Seekfree_SF'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_TH.yaml', 'L_DLC07_DraperShip_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_TH.yaml', 'L_DLC07_GlobalStore'),
]

def backup_and_read(path):
    backup = path + '.bak2'
    shutil.copy2(path, backup)
    with open(path, 'rb') as f:
        return f.read().decode('utf-8', errors='replace')

def save(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def fix_file(path, name):
    text = backup_and_read(path)
    lines = text.split('\n')
    fixed = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Find the first colon that separates key from value
        # The key may contain dots and numbers, value is everything after the first colon
        colon_pos = line.find(':')
        if colon_pos == -1:
            continue
        
        key = line[:colon_pos]
        rest = line[colon_pos+1:]  # includes the colon and space
        
        # Check if rest starts with space then *
        if rest.startswith(': *') or rest.startswith(':*'):
            # Unquoted * at start of value - needs quotes
            # Convert ": *text*" to ": \"*text*\""
            new_rest = rest[1:]  # remove second colon
            new_rest = '"' + new_rest.strip() + '"'
            lines[i] = key + ': ' + new_rest
            fixed += 1
        elif rest.startswith(': "') or rest.startswith(":'"):
            # Already quoted, skip
            pass
        elif rest.startswith(': '):
            value_part = rest[2:]  # skip ": "
            # Check if value contains unquoted * or : issues
            # If it starts with * and no quote, need to add quotes
            if value_part.startswith('*') and not (value_part.startswith('"') or value_part.startswith("'")):
                new_rest = ': "' + value_part + '"'
                lines[i] = key + new_rest
                fixed += 1
            # Check for embedded unquoted colons - but only if not already quoted
            elif not (value_part.startswith('"') or value_part.startswith("'")):
                # For values with colons, add quotes
                if ':' in value_part and not value_part.endswith('*'):
                    new_rest = ': "' + value_part + '"'
                    lines[i] = key + new_rest
                    fixed += 1
    
    new_text = '\n'.join(lines)
    save(path, new_text)
    return fixed, name, len(lines)

for path, name in files:
    count, name_out, total = fix_file(path, name)
    print(f'Fixed {count} lines in {name_out} ({total} total lines)')

print('Done!')