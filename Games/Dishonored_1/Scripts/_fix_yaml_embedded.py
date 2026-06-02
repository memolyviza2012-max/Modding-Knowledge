import sys; sys.stdout.reconfigure(encoding='utf-8')
import yaml

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromOvrsr_Script\L_Pub_FromOvrsr_Script_TH.yaml'
with open(path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
line170 = lines[169].rstrip()
idx = line170.index(': ')
key = line170[:idx]
value = line170[idx+2:]
print('Original value:', repr(value))

stripped = value.strip()
qc = stripped.count('"')
print('Quote count:', qc)

if qc >= 2:
    positions = [i for i, c in enumerate(stripped) if c == '"']
    print('Positions:', positions)
    # Escape internal quotes (all except first and last)
    result = list(stripped)
    # Insert backslashes before internal quotes
    offset = 0
    for i in positions[1:-1]:
        result.insert(i + offset, chr(92))
        offset += 1
    fixed_manual = ''.join(result)
    print('Fixed:', repr(fixed_manual))
    fixed_line = key + ': ' + fixed_manual
    try:
        data = yaml.safe_load(fixed_line)
        print('SUCCESS:', repr(data[key]))
    except Exception as e:
        print('FAIL:', str(e)[:80])
