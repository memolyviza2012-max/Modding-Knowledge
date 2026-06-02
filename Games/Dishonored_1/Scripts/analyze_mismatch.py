import os

def analyze_file(int_path, th_path):
    with open(int_path, 'rb') as f:
        int_raw = f.read()
    with open(th_path, 'rb') as f:
        th_raw = f.read()
    
    int_text = int_raw.decode('utf-8', errors='replace')
    th_text = th_raw.decode('utf-8', errors='replace')
    
    int_lines = int_text.split('\n')
    th_lines = th_text.split('\n')
    
    int_ids = []
    th_ids = []
    
    for line in int_lines:
        if ':' in line:
            int_ids.append(line.split(':')[0])
    
    for line in th_lines:
        if ':' in line:
            th_ids.append(line.split(':')[0])
    
    int_set = set(int_ids)
    th_set = set(th_ids)
    
    missing_from_th = int_set - th_set
    extra_in_th = th_set - int_set
    overlap = int_set & th_set
    
    return {
        'int_count': len(int_lines),
        'th_count': len(th_lines),
        'int_id_count': len(int_ids),
        'th_id_count': len(th_ids),
        'missing_from_th': len(missing_from_th),
        'extra_in_th': len(extra_in_th),
        'overlap': len(overlap),
        'missing_ids_sample': sorted(missing_from_th)[:5],
        'extra_ids_sample': sorted(extra_in_th)[:5]
    }

# Analyze problematic files
cases = [
    ('CookedPCConsole', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P', 'L_Distillery_P'),
    ('CookedPCConsole', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Boyle_Int_Script', 'L_Boyle_Int_Script'),
    ('CookedPCConsole', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script', 'L_Pub_FromFlooded_Script'),
    ('CookedPCConsole', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_LightH_HighChaos_Script', 'L_LightH_HighChaos_Script'),
    ('CookedPCConsole', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_PrsnSewer_RatScene', 'L_PrsnSewer_RatScene'),
    ('CookedPCConsole', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromBridge_Script_Sleep', 'L_Pub_FromBridge_Script_Sleep'),
    ('DLC', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06', 'DLC06_Slaughter_Ext_Script'),
    ('DLC', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperSewer_Script', 'L_DLC07_DraperSewer_Script'),
    ('DLC', r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script', 'L_DLC07_DraperShip_Script'),
]

for folder, base_path, base_name in cases:
    int_path = os.path.join(base_path, base_name + '_INT.yaml')
    th_path = os.path.join(base_path, base_name + '_TH.yaml')
    
    print(f'[{folder}] {base_name}')
    r = analyze_file(int_path, th_path)
    print(f'  Line counts: INT={r["int_count"]} TH={r["th_count"]} diff={r["int_count"]-r["th_count"]}')
    print(f'  ID counts: INT={r["int_id_count"]} TH={r["th_id_count"]}')
    print(f'  Missing from TH: {r["missing_from_th"]} | Extra in TH: {r["extra_in_th"]} | Overlap: {r["overlap"]}')
    if r['missing_from_th'] > 0 and r['missing_from_th'] <= 10:
        print(f'  Missing IDs: {r["missing_ids_sample"]}')
    if r['extra_in_th'] > 0 and r['extra_in_th'] <= 10:
        print(f'  Extra IDs: {r["extra_ids_sample"]}')
    print()