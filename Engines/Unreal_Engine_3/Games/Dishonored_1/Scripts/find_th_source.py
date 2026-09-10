import os

# Analyze L_Distillery_P in detail
base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P'
int_path = os.path.join(base, 'L_Distillery_P_INT.yaml')
th_path = os.path.join(base, 'L_Distillery_P_TH.yaml')

with open(int_path, 'rb') as f:
    int_raw = f.read()
with open(th_path, 'rb') as f:
    th_raw = f.read()

int_text = int_raw.decode('utf-8', errors='replace')
th_text = th_raw.decode('utf-8', errors='replace')

int_lines = int_text.split('\n')
th_lines = th_text.split('\n')

# Get ALL TH IDs
th_ids = []
for line in th_lines:
    if ':' in line:
        th_ids.append(line.split(':')[0])

print(f'TH has {len(th_ids)} IDs')
print(f'First TH ID: {th_ids[0]}')
print(f'Last TH ID: {th_ids[-1]}')

# Search for which INT file has the first TH ID
target_id = th_ids[0]
print(f'\nSearching for INT file containing: {target_id}')

for root, dirs, files in os.walk(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole'):
    for f in files:
        if f.endswith('_INT.yaml'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as fh:
                    raw = fh.read()
                text = raw.decode('utf-8', errors='replace')
                if target_id in text:
                    base_name = os.path.basename(path)
                    # Get ID range
                    lines = text.split('\n')
                    ids = [l.split(':')[0] for l in lines if ':' in l]
                    print(f'  FOUND in {base_name}: {ids[0]} ... {ids[-1]} ({len(ids)} IDs)')
            except:
                pass