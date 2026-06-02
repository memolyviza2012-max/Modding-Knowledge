import sys; sys.stdout.reconfigure(encoding='utf-8')
path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromOvrsr_Script\L_Pub_FromOvrsr_Script_TH.yaml'
with open(path, 'r', encoding='utf-8-sig') as f:
    content = f.read()
lines = content.split('\n')
q = '"'
count = 0
for i, line in enumerate(lines):
    if ': ' in line:
        idx = line.index(': ')
        value = line[idx+2:]
        qc = value.count(q)
        if qc >= 2:
            count += 1
            print(f'Line {i+1} ({qc} quotes): {repr(value[:60])}')
print(f'\nTotal: {count} lines with >=2 quotes')
