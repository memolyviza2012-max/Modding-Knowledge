import os

base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P'
int_path = os.path.join(base, 'L_Distillery_P_INT.yaml')
th_path = os.path.join(base, 'L_Distillery_P_TH.yaml')

with open(int_path, 'rb') as f:
    int_raw = f.read()
with open(th_path, 'rb') as f:
    th_raw = f.read()

print('INT first 8 bytes:', int_raw[:8].hex())
print('TH first 8 bytes:', th_raw[:8].hex())
print('INT ends with 0x0A:', int_raw.endswith(b'\n'))
print('TH ends with 0x0A:', th_raw.endswith(b'\n'))

# Count newlines
int_lf = int_raw.count(b'\n')
th_lf = th_raw.count(b'\n')
print(f'INT LF count: {int_lf}')
print(f'TH LF count: {th_lf}')

# Try reading as UTF-8 with errors
int_text = int_raw.decode('utf-8', errors='replace')
th_text = th_raw.decode('utf-8', errors='replace')

int_lines = int_text.split('\n')
th_lines = th_text.split('\n')

print(f'INT lines: {len(int_lines)}')
print(f'TH lines: {len(th_lines)}')

# The difference
print(f'Missing: {len(int_lines) - len(th_lines)}')

# Check last few INT lines
print()
print('Last 3 INT lines:')
for l in int_lines[-3:]:
    print(f'  [{repr(l)}]')

print()
print('Last 3 TH lines:')
for l in th_lines[-3:]:
    print(f'  [{repr(l)}]')