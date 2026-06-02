# fix_yaml_quotes_v3.py
# Fix YAML values with embedded double-quotes
# Strategy: if value starts with " and has >2 quotes total,
# treat it as having embedded quotes that need escaping
import os, re, yaml

WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"

def fix_embedded_quotes(value):
    """Fix values where embedded quotes break YAML parsing."""
    stripped = value.strip()
    if not stripped.startswith('"'):
        return value

    # Count quotes
    qc = stripped.count('"')
    if qc <= 2:
        return value

    # Has embedded quotes - fix by properly escaping
    # Split by quote (not escaped)
    parts = stripped.split('"')
    # parts[0] = '' (empty before first ")
    # parts[1] = content before internal quote
    # parts[2] = content between quotes
    # etc.
    # We need to escape every " that's NOT the opening/closing delimiter

    # Rebuild: the first " is opening, escape internal ones, last " is closing
    # But we don't know which is which - use heuristic:
    # If qc > 2, there are embedded quotes
    # Escape all " except the first and last
    inner_parts = stripped[1:-1].split('"')  # remove outer quotes, split
    escaped_inner = '\\"'.join(inner_parts)
    return '"' + escaped_inner + '"'

def test_yaml(key, value):
    """Test if a key:value parses correctly in YAML."""
    try:
        line = f"{key}: {value}"
        data = yaml.safe_load(line)
        return True
    except:
        return False

def fix_file(folder, th_filename):
    th_path = os.path.join(WORK_DIR, folder, th_filename)
    if not os.path.exists(th_path):
        return 0

    with open(th_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()

    lines = content.split('\n')
    fixed = 0
    new_lines = []

    for line in lines:
        line_orig = line
        line = line.rstrip('\n\r')
        if ': ' not in line:
            new_lines.append(line)
            continue

        idx = line.index(': ')
        key = line[:idx]
        value = line[idx+2:]

        if not test_yaml(key, value):
            fixed_val = fix_embedded_quotes(value)
            if fixed_val != value and test_yaml(key, fixed_val):
                new_lines.append(key + ': ' + fixed_val)
                fixed += 1
                continue

        new_lines.append(line)

    if fixed > 0:
        with open(th_path, 'w', encoding='utf-8-sig') as f:
            f.write('\n'.join(new_lines) + '\n')

    return fixed

def main():
    folders = [d for d in os.listdir(WORK_DIR) if os.path.isdir(os.path.join(WORK_DIR, d))]
    total_fixed = 0
    for folder in sorted(folders):
        th_file = f"{folder}_TH.yaml"
        n = fix_file(folder, th_file)
        if n > 0:
            print(f"  Fixed {n} in {folder}")
            total_fixed += n
    print(f"\nTotal: {total_fixed} values fixed")

if __name__ == "__main__":
    main()
