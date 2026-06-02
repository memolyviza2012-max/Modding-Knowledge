import sys; sys.stdout.reconfigure(encoding='utf-8')
import os

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromOvrsr_Script\L_Pub_FromOvrsr_Script_TH.yaml'
with open(path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

fixed = 0
new_lines = []

for line in lines:
    line = line.rstrip('\n\r')
    if ': ' not in line:
        new_lines.append(line)
        continue
    idx = line.index(': ')
    key = line[:idx]
    value = line[idx+2:]
    quote_count = value.count('"')
    if quote_count > 2:
        inner = value.strip()
        if inner.startswith('"') and inner.endswith('"'):
            inner = inner[1:-1]
        escaped = inner.replace('"', '\\"')
        new_value = '"' + escaped + '"'
        new_lines.append(key + ': ' + new_value)
        fixed += 1
        print(f'Fixed: {key[:40]}')
    else:
        new_lines.append(line)

print(f'Total fixed: {fixed}')
if fixed > 0:
    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(new_lines) + '\n')
    print('Written')
