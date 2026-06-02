import os, re

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Brothel_Script\L_Brothel_Script_TH.yaml'

with open(path, 'rb') as f:
    raw = f.read()

text = raw.decode('utf-8', errors='replace')

# Pattern: ID: * unquoted_text *
# Fix: add quotes around the value if it starts with *
def fix_yaml_value(line):
    # Match pattern: "ID: * something *"
    # Only fix if the value after ": " starts with * and is not already quoted
    match = re.match(r'^(\S.*?: )(\* .*\*)$', line)
    if match:
        prefix = match.group(1)
        value = match.group(2)
        # Add quotes around the value
        return prefix + '"' + value + '"'
    # Also handle case where value starts with * but has no closing *
    match2 = re.match(r'^(\S.*?: )(\*.*)$', line)
    if match2:
        prefix = match2.group(1)
        value = match2.group(2)
        # If not already quoted, quote it
        if not value.startswith('"'):
            return prefix + '"' + value + '"'
    return line

fixed_lines = []
changes = 0
for line in text.split('\n'):
    fixed = fix_yaml_value(line)
    if fixed != line:
        changes += 1
    fixed_lines.append(fixed)

fixed_text = '\n'.join(fixed_lines)

# Verify YAML is now valid
import yaml
try:
    yaml.safe_load(fixed_text)
    print(f'YAML valid! Fixed {changes} lines.')
except yaml.YAMLError as e:
    print(f'YAML still invalid: {e}')

# Write back
with open(path, 'w', encoding='utf-8') as f:
    f.write(fixed_text)

print(f'Written to {path}')