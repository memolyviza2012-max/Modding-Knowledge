import yaml, os, sys

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Brothel_Script\L_Brothel_Script_TH.yaml'
out_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\debug_brothel_out.txt'

with open(path, 'rb') as f:
    raw = f.read()
text = raw.decode('utf-8', errors='replace')
lines = text.split('\n')

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(f'Total lines: {len(lines)}\n\n')
    
    # Check line 2403
    if len(lines) > 2402:
        f.write(f'Line 2403 (index 2402):\n')
        f.write(repr(lines[2402]) + '\n\n')
    
    # Find lines where content starts with * (could be YAML alias)
    problems = []
    for i, line in enumerate(lines):
        # Check if line has ID: * something pattern
        if ': * ' in line or ': *"' in line:
            problems.append((i+1, line[:150]))
    
    f.write(f'Lines with ": * " pattern: {len(problems)}\n\n')
    for ln, txt in problems[:10]:
        f.write(f'  Line {ln}: {repr(txt)}\n')
    
    # Check for unquoted * at start of value
    f.write('\n--- Lines where value starts with * ---\n')
    for i, line in enumerate(lines):
        if ': *' in line and not line.strip().startswith('#'):
            f.write(f'Line {i+1}: {repr(line[:120])}\n')

print(f'Output written to {out_path}')
print(f'Total lines: {len(lines)}')