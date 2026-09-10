import re, os, yaml

def fix_yaml_file(path):
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode('utf-8', errors='replace')
    lines = text.split('\n')
    
    fixed_count = 0
    new_lines = []
    
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        
        # Pattern 1: Line contains ': *' or ':*' at the value position (unquoted * at start)
        # Match: ID: *value* or ID: *value
        # Fix: quote the value
        
        # Pattern: ID: *something* (where * is not inside quotes)
        # Check if line has ': *' and the part after ': *' is unquoted
        if ': *' in line or ':*' in line:
            # Check if already quoted
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0]
                value_part = parts[1]
                # If value starts with * and is not quoted, fix it
                stripped = value_part.strip()
                if stripped.startswith('*') and not (stripped.startswith('"') or stripped.startswith("'")):
                    # Need to quote this value
                    new_value = '"' + value_part.strip() + '"'
                    line = key + ': ' + new_value
                    fixed_count += 1
        
        # Pattern 2: Line has unquoted : in the value
        # e.g., "ID: some text: with colon"
        # Fix: quote the entire value after :
        # Only fix if the value has : followed by text (and isn't already quoted)
        parts = line.split(':', 1)
        if len(parts) == 2:
            key = parts[0]
            value_part = parts[1]
            stripped = value_part.strip()
            # Check if this looks like an unquoted value with : in it
            # (not starting with " or ')
            if stripped and not stripped.startswith('"') and not stripped.startswith("'"):
                # Check if there's another : later in the value (indicating unquoted colon)
                if ':' in stripped:
                    # This is a value with unquoted colon - quote it
                    new_value = '"' + value_part.strip() + '"'
                    line = key + ': ' + new_value
                    fixed_count += 1
        
        new_lines.append(line)
    
    fixed_text = '\n'.join(new_lines)
    
    # Verify YAML is now valid
    try:
        yaml.safe_load(fixed_text)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        return fixed_count, True
    except yaml.YAMLError as e:
        return fixed_count, False, str(e)[:100]

files = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml', 'DLC06_DaudBase_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_TH.yaml', 'DLC06_Slaughter_Int_Loot'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml', 'DLC07_Twk_Inv_Seekfree_SF'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Brig_Ext_P\L_DLC07_Brig_Ext_P_TH.yaml', 'L_DLC07_Brig_Ext_P'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_BaseIntro_Script\L_DLC07_BaseIntro_Script_TH.yaml', 'L_DLC07_BaseIntro_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Brig_Ext_Loot\L_DLC07_Brig_Ext_Loot_TH.yaml', 'L_DLC07_Brig_Ext_Loot'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Brigmore_Void_Script\L_DLC07_Brigmore_Void_Script_TH.yaml', 'L_DLC07_Brigmore_Void_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Coldridge_P\L_DLC07_Coldridge_P_TH.yaml', 'L_DLC07_Coldridge_P'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_TH.yaml', 'L_DLC07_DraperShip_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_TH.yaml', 'L_DLC07_GlobalStore'),
]

results = []
for path, name in files:
    count, ok, *err = fix_yaml_file(path)
    if ok:
        results.append(f'OK: {name} ({count} fixes)')
    else:
        results.append(f'FAIL: {name} ({count} fixes) - {err[0]}')

for r in results:
    print(r)

print()
print('Done!')