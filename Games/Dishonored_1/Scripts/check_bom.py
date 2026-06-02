import os

def check_bom_issue(base_path, base_name):
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
    for line in int_lines:
        if ':' in line:
            int_ids.append(line.split(':')[0])
    
    th_ids = []
    for line in th_lines:
        if ':' in line:
            th_ids.append(line.split(':')[0])
    
    th_ids_set = set(th_ids)
    int_ids_set = set(int_ids)
    
    missing = int_ids_set - th_ids_set
    extra = th_ids_set - int_ids_set
    
    return missing, extra, int_ids, th_ids

# L_Pub_FromFlooded_Script
base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script'
missing, extra, int_ids, th_ids = check_bom_issue(base, 'L_Pub_FromFlooded_Script')

print('L_Pub_FromFlooded_Script')
print(f'  Missing from TH: {missing}')
print(f'  Extra in TH: {extra}')
print(f'  INT IDs count: {len(int_ids)}')
print(f'  TH IDs count: {len(th_ids)}')

# The extra ID contains BOM
if extra:
    bom_id = list(extra)[0]
    print(f'  Extra ID (BOM): {repr(bom_id)}')
    print(f'  Extra ID bytes: {bom_id.encode("utf-8").hex()}')
    
    # Find this in TH lines
    with open(os.path.join(base, 'L_Pub_FromFlooded_Script_TH.yaml'), 'rb') as f:
        th_raw = f.read()
    th_text = th_raw.decode('utf-8', errors='replace')
    
    for i, line in enumerate(th_text.split('\n')):
        if '\ufeff' in line:
            print(f'  BOM found at line {i+1}: {repr(line[:100])}')
            break