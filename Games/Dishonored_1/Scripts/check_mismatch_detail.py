import os

def check_mismatch_detail(base_path, base_name):
    int_path = os.path.join(base_path, base_name + '_INT.yaml')
    th_path = os.path.join(base_path, base_name + '_TH.yaml')
    
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
    
    print(f'INT IDs range: {int_ids[0] if int_ids else "N/A"} ... {int_ids[-1] if int_ids else "N/A"} ({len(int_ids)} entries)')
    print(f'TH IDs range: {th_ids[0] if th_ids else "N/A"} ... {th_ids[-1] if th_ids else "N/A"} ({len(th_ids)} entries)')
    print(f'INT line count: {len(int_lines)}, TH line count: {len(th_lines)}')
    
    # Check overlap
    int_set = set(int_ids)
    th_set = set(th_ids)
    overlap = int_set & th_set
    print(f'Overlapping IDs: {len(overlap)}')
    print()

cases = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P', 'L_Distillery_P'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Boyle_Int_Script', 'L_Boyle_Int_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script', 'L_Pub_FromFlooded_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperShip_Script', 'L_DLC07_DraperShip_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\L_DLC07_DraperSewer_Script', 'L_DLC07_DraperSewer_Script'),
]

for base_path, base_name in cases:
    print('='*60)
    print(f'Checking: {base_name}')
    print('='*60)
    check_mismatch_detail(base_path, base_name)