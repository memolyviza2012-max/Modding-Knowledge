import sys; sys.stdout.reconfigure(encoding='utf-8')
import yaml

# Read actual file line 170
path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromOvrsr_Script\L_Pub_FromOvrsr_Script_TH.yaml'
with open(path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
line170 = lines[169].rstrip()
idx = line170.index(': ')
key = line170[:idx]
value = line170[idx+2:]

print('Value:', repr(value))
print('Quote positions:')
for i, c in enumerate(value):
    if c == '"':
        print(f'  {i}: {repr(value[max(0,i-5):i+6])}')

# Strategy: find all quote positions
# If value has more than 2 quotes and starts with ",
# escape ALL quotes (so the whole thing is one quoted string)
stripped = value.strip()
qc = stripped.count('"')
print(f'\nQuote count: {qc}')

if qc >= 2 and stripped.startswith('"'):
    # Escape ALL quotes in the value
    escaped = stripped.replace('"', '\\"')
    fixed_value = escaped
    fixed_line = key + ': ' + fixed_value
    print('Fixed value:', repr(fixed_value))
    try:
        data = yaml.safe_load(fixed_line)
        print('SUCCESS:', repr(data[key]))
    except Exception as e:
        print('FAIL:', str(e)[:100])
