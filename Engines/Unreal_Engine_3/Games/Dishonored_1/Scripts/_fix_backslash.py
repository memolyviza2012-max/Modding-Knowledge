import sys; sys.stdout.reconfigure(encoding='utf-8')

src = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT\DishonoredGame.int"
trans = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame.int"
output = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame_fixed.int"

def load_with_keys(path, enc):
    with open(path, 'r', encoding=enc) as f:
        lines = f.readlines()
    # Build key -> line mapping
    key_to_line = {}
    for i, l in enumerate(lines):
        for sep in ('=', ':'):
            if sep in l:
                idx = l.index(sep)
                key = l[:idx].strip()
                key_to_line[key] = i
                break
    return lines, key_to_line

src_lines, src_key_to_line = load_with_keys(src, 'utf-16-le')
trans_lines, trans_key_to_line = load_with_keys(trans, 'utf-16-le')

# Find keys that need backslash fixed
# In src: m\_key -> in trans: m_key
src_keys_set = set(src_key_to_line.keys())
trans_keys_set = set(trans_key_to_line.keys())

# Keys in src with backslash (\_)
backslash_keys = [k for k in src_keys_set if '\\_' in k]

print(f"SOURCE keys with backslash: {len(backslash_keys)}")

fixed_lines = list(trans_lines)
fixed_count = 0

for key in backslash_keys:
    # The translated key without backslash
    no_bs_key = key.replace('\\_', '_')
    if no_bs_key in trans_key_to_line and key not in trans_key_to_line:
        # Fix the line in trans
        line_idx = trans_key_to_line[no_bs_key]
        line = trans_lines[line_idx]
        # Replace the key in the line
        if '=' in line:
            idx = line.index('=')
            new_line = line[:idx].replace(no_bs_key, key) + line[idx:]
        elif ':' in line:
            idx = line.index(':')
            new_line = line[:idx].replace(no_bs_key, key) + line[idx:]
        else:
            continue
        fixed_lines[line_idx] = new_line
        fixed_count += 1

print(f"Fixed {fixed_count} lines")

# Write output
with open(output, 'w', encoding='utf-16-le') as f:
    f.write('\n'.join(fixed_lines))

print(f"Saved to: {output}")

# Verify
with open(output, 'r', encoding='utf-16-le') as f:
    new_lines = f.readlines()

new_keys, _ = load_with_keys(output, 'utf-16-le')
new_keys_set = set(new_keys)

still_missing = [k for k in src_keys_set if k not in new_keys_set]
print(f"Still missing keys: {len(still_missing)}")
