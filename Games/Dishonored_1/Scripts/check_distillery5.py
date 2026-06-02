import os

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

print('INT lines:', len(int_lines))
print('TH lines:', len(th_lines))

# Get first 10 IDs from each
int_ids = []
for line in int_lines:
    if ':' in line:
        int_ids.append(line.split(':')[0])
        if len(int_ids) >= 10:
            break

th_ids = []
for line in th_lines:
    if ':' in line:
        th_ids.append(line.split(':')[0])
        if len(th_ids) >= 10:
            break

print()
print('First 10 INT IDs:')
for i, id in enumerate(int_ids):
    print(f'  {i}: {id}')

print()
print('First 10 TH IDs:')
for i, id in enumerate(th_ids):
    print(f'  {i}: {id}')

# Check the difference in LF count
print()
print('INT ends with newline:', int_text.endswith('\n'))
print('TH ends with newline:', th_text.endswith('\n'))
print('INT last char:', repr(int_text[-1]) if int_text else 'EMPTY')
print('TH last char:', repr(th_text[-1]) if th_text else 'EMPTY')