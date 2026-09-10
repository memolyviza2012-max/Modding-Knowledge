# fix_yaml_quotes.py
# Quote YAML values that contain special characters (: # & * ! > | <)
# to prevent YAML parse errors in subedit.py
import os, re

WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"
YAML_SPECIAL = re.compile(r'[:\#\&\*\!\<\>\|]')

def needs_quoting(value):
    """Check if value needs double-quoting for YAML safety."""
    return bool(YAML_SPECIAL.search(value))

def safe_value(value):
    """Return a YAML-safe quoted string."""
    # Escape backslashes first, then double-quote
    return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'

def fix_file(folder, th_filename):
    th_path = os.path.join(WORK_DIR, folder, th_filename)
    if not os.path.exists(th_path):
        return 0

    with open(th_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    fixed = 0
    new_lines = []
    for line in lines:
        line = line.rstrip('\n\r')
        if ': ' not in line:
            new_lines.append(line)
            continue
        parts = line.split(': ', 1)
        if len(parts) != 2:
            new_lines.append(line)
            continue
        key, value = parts[0].strip(), parts[1]

        if needs_quoting(value):
            new_value = safe_value(value)
            new_lines.append(f"{key}: {new_value}")
            fixed += 1
        else:
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
            print(f"  Fixed {n} values in {folder}")
            total_fixed += n
    print(f"\nTotal: {total_fixed} values quoted")

if __name__ == "__main__":
    main()
