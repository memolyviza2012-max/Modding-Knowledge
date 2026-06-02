import sys; sys.stdout.reconfigure(encoding='utf-8')
import yaml

# Read actual file line 170
path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromOvrsr_Script\L_Pub_FromOvrsr_Script_TH.yaml'
with open(path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
line170 = lines[169].rstrip()
print('Line 170:', repr(line170[:80]))

idx = line170.index(': ')
key = line170[:idx]
value = line170[idx+2:]
print()
print('Key:', repr(key[:40]))
print('Value:', repr(value))
print('Value quote count:', value.count('"'))

# Test yaml parsing
try:
    data = yaml.safe_load(line170)
    print('YAML OK:', repr(data[key][:30]))
except Exception as e:
    print('YAML FAIL:', str(e)[:100])

# Now fix
stripped = value.strip()
if stripped.startswith('"') and stripped.endswith('"') and stripped.count('"') > 2:
    inner = stripped[1:-1]
    parts = inner.split('"')
    escaped = chr(92).join(parts)
    fixed_value = '"' + escaped + '"'
    fixed_line = key + ': ' + fixed_value
    print()
    print('Fixed value:', repr(fixed_value))
    try:
        data = yaml.safe_load(fixed_line)
        print('FIXED YAML OK:', repr(data[key]))
    except Exception as e:
        print('FIXED YAML FAIL:', str(e)[:100])
