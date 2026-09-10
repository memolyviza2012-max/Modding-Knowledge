import os

base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P'
int_path = os.path.join(base, 'L_Distillery_P_INT.yaml')
th_path = os.path.join(base, 'L_Distillery_P_TH.yaml')

with open(int_path, 'r', encoding='utf-8', errors='replace') as f:
    int_lines = f.read().split('\n')

with open(th_path, 'rb') as f:
    raw = f.read()

print(f'INT lines: {len(int_lines)}')
print(f'TH raw bytes: {len(raw)}')
print(f'TH first bytes: {raw[:8].hex()}')

# Try to decode
try:
    th_text = raw.decode('utf-8')
    print(f'TH UTF-8: {len(th_text)} chars, {len(th_text.split(chr(10)))} lines')
except Exception as e:
    print(f'UTF-8 failed: {e}')
    try:
        th_text = raw.decode('utf-16-le')
        print(f'TH UTF-16-LE: {len(th_text)} chars, {len(th_text.split(chr(10)))} lines')
    except Exception as e2:
        print(f'UTF-16-LE failed: {e2}')

# Count actual lines
th_text = raw.decode('utf-8', errors='replace')
th_lines = th_text.split('\n')
print(f'TH split by newline: {len(th_lines)} lines')

# IDs
int_ids = set()
for line in int_lines:
    if ':' in line:
        int_ids.add(line.split(':')[0])

th_ids = set()
for line in th_lines:
    if ':' in line:
        th_ids.add(line.split(':')[0])

missing = int_ids - th_ids
print(f'Missing IDs: {len(missing)}')
if missing:
    sample = sorted(missing)[:5]
    for m in sample:
        print(f'  {m}')