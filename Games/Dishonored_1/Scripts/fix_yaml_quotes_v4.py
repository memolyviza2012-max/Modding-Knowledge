# fix_yaml_quotes_v4.py
# Fix YAML values with embedded double-quotes
# Pattern: value has opening " and embedded " that closes the string prematurely
# Fix: escape the internal quote(s) and wrap the entire value in outer quotes
import os, yaml

WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"

def is_valid_yaml(key, value):
    """Test if key: value parses correctly."""
    try:
        yaml.safe_load(f"{key}: {value}")
        return True
    except:
        return False

def fix_value(value):
    """
    Fix values where quotes inside the value break YAML parsing.
    The value starts with " and has embedded " that closes the string too early.
    Fix: escape the embedded quotes, then wrap in outer quotes.
    """
    stripped = value.strip()

    # Count quotes
    qc = stripped.count('"')
    if qc < 2:
        return value

    # If starts with " and ends with " (outer quotes)
    if stripped.startswith('"') and stripped.endswith('"'):
        # Check if there are quotes INSIDE (not just outer)
        inner = stripped[1:-1]
        if '"' not in inner:
            # Just outer quotes, OK
            return value
        # Has embedded quotes - escape them
        inner_escaped = inner.replace('"', '\\"')
        return '"' + inner_escaped + '"'

    # Doesn't start with quote - check if it has quotes in the middle
    # that might be closing early
    if '"' in stripped:
        # Escape all quotes in the value and wrap in quotes
        escaped = stripped.replace('"', '\\"')
        return '"' + escaped + '"'

    return value

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
        line = line.rstrip('\n\r')
        if ': ' not in line:
            new_lines.append(line)
            continue

        idx = line.index(': ')
        key = line[:idx]
        value = line[idx+2:]

        if not is_valid_yaml(key, value):
            fixed_val = fix_value(value)
            if fixed_val != value and is_valid_yaml(key, fixed_val):
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
