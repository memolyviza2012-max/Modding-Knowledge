import os

base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P'
int_path = os.path.join(base, 'L_Distillery_P_INT.yaml')
th_path = os.path.join(base, 'L_Distillery_P_TH.yaml')

with open(int_path, 'rb') as f:
    int_raw = f.read()
with open(th_path, 'rb') as f:
    th_raw = f.read()

LF = b'\n'

print('INT LF count:', int_raw.count(LF))
print('TH LF count:', th_raw.count(LF))

# Read as UTF-8
int_text = int_raw.decode('utf-8', errors='replace')
th_text = th_raw.decode('utf-8', errors='replace')

int_lines = int_text.split('\n')
th_lines = th_text.split('\n')

int_ids = set()
for line in int_lines:
    if ':' in line:
        int_ids.add(line.split(':')[0])

th_ids = set()
for line in th_lines:
    if ':' in line:
        th_ids.add(line.split(':')[0])

missing = int_ids - th_ids
print('Missing IDs:', len(missing))

if missing:
    sorted_missing = sorted(missing)
    print('First 10 missing IDs:')
    for m in sorted_missing[:10]:
        print(' ', m)
    
    first_missing = sorted_missing[0]
    print()
    print('Looking for:', first_missing)
    
    found = th_text.find(first_missing)
    if found >= 0:
        print('Found in TH at position', found)
        print('Context:', repr(th_text[max(0,found-20):found+100]))
    else:
        print('Not found in TH text at all')
    
    extra = th_ids - int_ids
    print('Extra IDs in TH:', len(extra))