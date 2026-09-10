import yaml, os, sys

files = [
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml', 'DLC06_DaudBase_Script'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_TH.yaml', 'DLC06_Slaughter_Int_Loot'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml', 'DLC07_Twk_Inv_Seekfree_SF'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Brig_Ext_P\L_DLC07_Brig_Ext_P_TH.yaml', 'L_DLC07_Brig_Ext_P'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_BaseIntro_Script\L_DLC07_BaseIntro_Script_TH.yaml', 'L_DLC07_BaseIntro_Script'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Brig_Ext_Loot\L_DLC07_Brig_Ext_Loot_TH.yaml', 'L_DLC07_Brig_Ext_Loot'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Brigmore_Void_Script\L_DLC07_Brigmore_Void_Script_TH.yaml', 'L_DLC07_Brigmore_Void_Script'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_Coldridge_P\L_DLC07_Coldridge_P_TH.yaml', 'L_DLC07_Coldridge_P'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_TH.yaml', 'L_DLC07_DraperShip_Script'),
    (r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_TH.yaml', 'L_DLC07_GlobalStore'),
]

out = []
for path, name in files:
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        text = raw.decode('utf-8', errors='replace')
        yaml.safe_load(text)
        out.append(f'OK: {name}')
    except yaml.YAMLError as e:
        err_str = str(e)
        # Find line number
        line_info = ''
        if 'line' in err_str:
            import re
            m = re.search(r'line (\d+)', err_str)
            if m:
                line_num = int(m.group(1))
                lines = text.split('\n')
                if line_num <= len(lines):
                    line_info = f'  Line {line_num}: {repr(lines[line_num-1][:100])}'
        out.append(f'FAIL: {name}')
        out.append(f'  Error: {err_str[:200]}')
        if line_info:
            out.append(line_info)
        out.append('')

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\yaml_errors.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))

print('Written to yaml_errors.txt')
for line in out:
    print(line)