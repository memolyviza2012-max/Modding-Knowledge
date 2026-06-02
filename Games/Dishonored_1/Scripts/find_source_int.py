import os

# Search for INT file that contains ID 5035
folder = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole'
target_ids = ['DisConv_Blurb.5035', 'DisConv_Blurb.5040', 'DisConv_Blurb.5100']

found_in = []

for root, dirs, files in os.walk(folder):
    for f in files:
        if f.endswith('_INT.yaml'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as fh:
                    raw = fh.read()
                text = raw.decode('utf-8', errors='replace')
                lines = text.split('\n')
                ids_in_file = set()
                for line in lines:
                    if ':' in line:
                        ids_in_file.add(line.split(':')[0])
                
                for tid in target_ids:
                    if tid in ids_in_file:
                        base = os.path.basename(path)
                        found_in.append(base)
                        print(f'Found {tid} in {base}')
                        # Show range
                        sorted_ids = sorted(ids_in_file)
                        if sorted_ids:
                            print(f'  Range: {sorted_ids[0]} ... {sorted_ids[-1]} ({len(sorted_ids)} IDs)')
            except Exception as e:
                pass

print()
print('=== Check what INT file has range 5035-5229 ===')
for root, dirs, files in os.walk(folder):
    for f in files:
        if f.endswith('_INT.yaml'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as fh:
                    raw = fh.read()
                text = raw.decode('utf-8', errors='replace')
                lines = text.split('\n')
                ids_in_file = set()
                for line in lines:
                    if ':' in line:
                        ids_in_file.add(line.split(':')[0])
                
                # Check if this file has IDs in 5035-5229 range
                has_5035 = any('DisConv_Blurb.5035' in id for id in ids_in_file)
                if has_5035:
                    base = os.path.basename(path)
                    sorted_ids = sorted(ids_in_file)
                    print(f'File with 5035: {base}')
                    print(f'  Total IDs: {len(ids_in_file)}')
                    print(f'  Range: {sorted_ids[0]} ... {sorted_ids[-1]}')
            except:
                pass