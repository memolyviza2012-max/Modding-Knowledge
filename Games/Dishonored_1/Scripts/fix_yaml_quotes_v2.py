# fix_yaml_quotes_v2.py
# Fix YAML values with embedded double-quotes
# Pattern: key: value with "quotes" inside value breaks YAML parsing
# Fix: escape all double-quotes inside the value
import os, re

WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"

def escape_yaml_value(value):
    """Escape a YAML value that may contain embedded double-quotes."""
    # Remove surrounding quotes if already present
    stripped = value.strip()
    if stripped.startswith('"') and stripped.endswith('"'):
        # Already quoted - extract inner content
        inner = stripped[1:-1]
    else:
        inner = stripped

    # Count quotes in inner content
    quote_count = inner.count('"')
    if quote_count == 0:
        return value  # No change needed

    # If there are quotes inside, we need to escape them
    # But we need to determine: is this one quoted string with embedded quotes?
    # or is this broken (closing quote in wrong place)?
    #
    # Valid YAML: "This is a \"quoted\" word" -> escaped internal quotes
    # Invalid: "text"more text -> missing closing quote
    #
    # Our values: dialogue that may start with " and contain " as punctuation
    # The safest fix: escape ALL double-quotes inside the value
    escaped_inner = inner.replace('"', '\\"')

    # Re-quote the whole thing
    return '"' + escaped_inner + '"'

def fix_file(folder, th_filename):
    th_path = os.path.join(WORK_DIR, folder, th_filename)
    if not os.path.exists(th_path):
        return 0

    with open(th_path, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    fixed = 0
    new_lines = []

    for line in lines:
        original = line
        line = line.rstrip('\n\r')

        # Parse: key: value
        if ': ' not in line:
            new_lines.append(line)
            continue

        idx = line.index(': ')
        key = line[:idx]
        value = line[idx+2:]  # after ': '

        # Count quotes in value
        quote_count = value.count('"')

        if quote_count > 2:
            # Too many quotes - likely embedded quotes not escaped
            escaped_value = escape_yaml_value(value)
            if escaped_value != value:
                new_lines.append(key + ': ' + escaped_value)
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
