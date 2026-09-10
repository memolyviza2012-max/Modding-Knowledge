import yaml, os, shutil

def fix_yaml(int_path, th_path):
    with open(int_path, 'rb') as f:
        int_raw = f.read()
    if int_raw[:2] == b'\xff\xfe':
        int_enc = 'utf-16-le'
    elif int_raw[:2] == b'\xfe\xff':
        int_enc = 'utf-16-be'
    elif int_raw.startswith(b'\xef\xbb\xbf'):
        int_enc = 'utf-8-sig'
    else:
        int_enc = 'utf-8'
    int_text = int_raw.decode(int_enc, errors='replace')
    int_lines = int_text.split('\n')

    with open(th_path, 'rb') as f:
        th_raw = f.read()
    if th_raw[:2] == b'\xff\xfe':
        th_enc = 'utf-16-le'
    elif th_raw[:2] == b'\xfe\xff':
        th_enc = 'utf-16-be'
    elif th_raw.startswith(b'\xef\xbb\xbf'):
        th_enc = 'utf-8-sig'
    else:
        th_enc = 'utf-8'
    th_text = th_raw.decode(th_enc, errors='replace')
    th_norm = th_text.replace('\r\n', '\n').replace('\r', '\n')
    th_lines = th_norm.split('\n')

    if len(int_lines) != len(th_lines):
        return False, f'Line mismatch INT={len(int_lines)} TH={len(th_lines)}'

    shutil.copy2(th_path, th_path + '.bak3')

    fixed = 0
    new_lines = []
    for line in th_lines:
        if not line.strip() or line.strip().startswith('#'):
            new_lines.append(line)
            continue
        cp = line.find(':')
        if cp == -1:
            new_lines.append(line)
            continue
        key = line[:cp]
        val = line[cp+1:]
        s = val.strip()
        if s.startswith('*') and not s.startswith('"') and not s.startswith("'"):
            new_val = '"' + s + '"'
            line = key + ': ' + new_val
            fixed += 1
        elif not s.startswith('"') and not s.startswith("'"):
            v2 = line[cp+1:].strip()
            if v2.count(':') > 1 and not v2.startswith('"'):
                new_val = '"' + v2 + '"'
                line = key + ': ' + new_val
                fixed += 1
        elif s.startswith("'") and not s.endswith("'"):
            new_val = '"' + s + '"'
            line = key + ': ' + new_val
            fixed += 1
        new_lines.append(line)

    le = '\r\n' if '\r\n' in int_text else '\r' if '\r' in int_text else '\n'
    fixed_text = le.join(new_lines)
    try:
        yaml.safe_load(fixed_text)
        with open(th_path, 'w', encoding=th_enc) as f:
            f.write(fixed_text)
        return True, f'Fixed {fixed} lines'
    except yaml.YAMLError as e:
        return False, str(e)[:100]

files = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_INT.yaml',
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml', 'DLC06_DaudBase_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_INT.yaml',
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Int_Loot\DLC06_Slaughter_Int_Loot_TH.yaml', 'DLC06_Slaughter_Int_Loot'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_INT.yaml',
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml', 'DLC07_Twk_Inv_Seekfree_SF'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_INT.yaml',
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script\L_DLC07_DraperShip_Script_TH.yaml', 'L_DLC07_DraperShip_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_INT.yaml',
     r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_GlobalStore\L_DLC07_GlobalStore_TH.yaml', 'L_DLC07_GlobalStore'),
]

ok_list = []
fail_list = []

for int_path, th_path, name in files:
    ok, msg = fix_yaml(int_path, th_path)
    if ok:
        ok_list.append((name, msg))
    else:
        fail_list.append((name, msg))

check_files = [
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
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Slaughter_Ext_Script\DLC06_Slaughter_Ext_Script_TH.yaml', 'DLC06_Slaughter_Ext_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_Timsh_Estate_Patrol\DLC06_Timsh_Estate_Patrol_TH.yaml', 'DLC06_Timsh_Estate_Patrol'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperMill_Loot\L_DLC07_DraperMill_Loot_TH.yaml', 'L_DLC07_DraperMill_Loot'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperStreets_P\L_DLC07_DraperStreets_P_TH.yaml', 'L_DLC07_DraperStreets_P'),
]

ok_names = []
fail_names = []
for path, name in check_files:
    try:
        with open(path, 'rb') as f:
            yaml.safe_load(f.read().decode('utf-8', errors='replace'))
        ok_names.append(name)
    except:
        fail_names.append(name)

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\fix_result.txt', 'w', encoding='utf-8') as f:
    f.write('=== FIX RESULTS ===\n')
    for name, msg in ok_list:
        f.write(f'OK: {name} - {msg}\n')
    for name, msg in fail_list:
        f.write(f'FAIL: {name} - {msg}\n')
    f.write('\n=== VERIFY ===\n')
    f.write(f'OK: {len(ok_names)} - {ok_names}\n')
    f.write(f'FAIL: {len(fail_names)} - {fail_names}\n')

print('Done')