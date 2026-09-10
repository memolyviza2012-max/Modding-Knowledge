import os

folder = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script'
int_path = os.path.join(folder, 'L_Pub_FromFlooded_Script_INT.yaml')
th_path = os.path.join(folder, 'L_Pub_FromFlooded_Script_TH.yaml')

print('INT path:', int_path)
print('TH path:', th_path)
print('INT exists:', os.path.exists(int_path))
print('TH exists:', os.path.exists(th_path))

# Read using same method as validate_check.py
with open(int_path, 'r', encoding='utf-8', errors='replace') as f:
    int_lines = f.read().split('\n')
with open(th_path, 'r', encoding='utf-8', errors='replace') as f:
    th_lines = f.read().split('\n')

print()
print('INT lines:', len(int_lines))
print('TH lines:', len(th_lines))
print('Difference:', len(int_lines) - len(th_lines))

# Verify IDs
int_ids = set()
for line in int_lines:
    if ':' in line:
        int_ids.add(line.split(':')[0])
th_ids = set()
for line in th_lines:
    if ':' in line:
        th_ids.add(line.split(':')[0])

print()
print('INT IDs:', len(int_ids))
print('TH IDs:', len(th_ids))
print('Overlap:', len(int_ids & th_ids))
print('Missing:', len(int_ids - th_ids))
print('Extra:', len(th_ids - int_ids))