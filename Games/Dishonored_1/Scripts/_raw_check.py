import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromOvrsr_Script\L_Pub_FromOvrsr_Script_TH.yaml'
with open(path, 'rb') as f:
    raw = f.read()
lines = raw.split(b'\n')
line170 = lines[169]
print('Length:', len(line170))
# Find ALL quote bytes (0x22) in line 170
for i, b in enumerate(line170):
    if b == 0x22:
        ctx = repr(line170[max(0,i-5):i+6])
        print(f'Quote at byte {i}: {ctx}')
