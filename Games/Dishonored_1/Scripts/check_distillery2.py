import os

base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Distillery_P'
int_path = os.path.join(base, 'L_Distillery_P_INT.yaml')
th_path = os.path.join(base, 'L_Distillery_P_TH.yaml')

with open(int_path, 'r', encoding='utf-8', errors='replace') as f:
    int_lines = f.read().split('\n')

with open(th_path, 'rb') as f:
    raw = f.read()

th_text = raw.decode('utf-8', errors='replace')
th_lines = th_text.split('\n')

print('First 5 INT lines:')
for l in int_lines[:5]:
    print(f'  {l}')

print()
print('First 5 TH lines:')
for l in th_lines[:5]:
    print(f'  {l}')

print()
print('Last 5 INT lines:')
for l in int_lines[-5:]:
    print(f'  {l}')

print()
print('Last 5 TH lines:')
for l in th_lines[-5:]:
    print(f'  {l}')