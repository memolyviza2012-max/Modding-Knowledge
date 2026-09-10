# fix_yaml_yaml.py
# Use yaml library to properly quote YAML values
import os, yaml

WORK_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"

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

        # Use yaml to properly quote the value
        try:
            test = yaml.safe_load(f"{key}: {value}")
            if test and key in test:
                v = test[key]
                if isinstance(v, str) and v != value.strip():
                    # yaml normalized the value, rewrite with proper quoting
                    quoted = yaml.dump({key: v}, allow_unicode=True, default_flow_style=False, allow_unicode=True).rstrip('\n')
                    new_lines.append(quoted)
                    fixed += 1
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        except:
            # YAML parse failed, try to fix manually
            # Escape double-quotes inside value
            new_val = value.replace('"', '\\"')
            if new_val != value:
                new_lines.append(f"{key}: \"{new_val}\"")
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
            print(f"  Fixed {n} in {folder}")
            total_fixed += n
    print(f"\nTotal: {total_fixed} values rewritten with proper YAML quoting")

if __name__ == "__main__":
    main()
