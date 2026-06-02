import os

def analyze_one(base_path, base_name):
    int_path = os.path.join(base_path, base_name + '_INT.yaml')
    th_path = os.path.join(base_path, base_name + '_TH.yaml')
    
    with open(int_path, 'rb') as f:
        int_raw = f.read()
    with open(th_path, 'rb') as f:
        th_raw = f.read()
    
    # Decode as UTF-8 (replace errors)
    int_text = int_raw.decode('utf-8', errors='replace')
    th_text = th_raw.decode('utf-8', errors='replace')
    
    # Count LF
    int_lf = int_raw.count(b'\n')
    th_lf = th_raw.count(b'\n')
    
    # Split lines
    int_lines = int_text.split('\n')
    th_lines = th_text.split('\n')
    
    # Get IDs (first field before colon)
    def get_ids(lines):
        ids = []
        for line in lines:
            if ':' in line:
                ids.append(line.split(':')[0])
        return ids
    
    int_ids = get_ids(int_lines)
    th_ids = get_ids(th_lines)
    
    int_id_set = set(int_ids)
    th_id_set = set(th_ids)
    
    overlap = len(int_id_set & th_id_set)
    missing = len(int_id_set - th_id_set)
    extra = len(th_id_set - int_id_set)
    
    print(f'File: {base_name}')
    print(f'  LF count: INT={int_lf} TH={th_lf} (diff={int_lf - th_lf})')
    print(f'  Line count: INT={len(int_lines)} TH={len(th_lines)}')
    print(f'  ID count: INT={len(int_ids)} TH={len(th_ids)}')
    print(f'  Overlap: {overlap} | Missing: {missing} | Extra: {extra}')
    
    if int_ids and th_ids:
        print(f'  INT IDs range: {int_ids[0]} ... {int_ids[-1]}')
        print(f'  TH IDs range: {th_ids[0]} ... {th_ids[-1]}')
    
    if missing > 0 and missing <= 5:
        print(f'  Missing IDs: {sorted(int_id_set - th_id_set)[:5]}')
    if extra > 0 and extra <= 5:
        print(f'  Extra IDs: {sorted(th_id_set - int_id_set)[:5]}')
    
    print()
    return {
        'lf_diff': int_lf - th_lf,
        'line_diff': len(int_lines) - len(th_lines),
        'id_count': len(int_ids),
        'overlap': overlap,
        'missing': missing,
        'extra': extra
    }

# Problem 1-7: CookedPCConsole files with issues
files_to_fix = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P', 'L_Distillery_P'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Boyle_Int_Script', 'L_Boyle_Int_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script', 'L_Pub_FromFlooded_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_LightH_HighChaos_Script', 'L_LightH_HighChaos_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_PrsnSewer_RatScene', 'L_PrsnSewer_RatScene'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromBridge_Script_Sleep', 'L_Pub_FromBridge_Script_Sleep'),
]

for base_path, base_name in files_to_fix:
    analyze_one(base_path, base_name)