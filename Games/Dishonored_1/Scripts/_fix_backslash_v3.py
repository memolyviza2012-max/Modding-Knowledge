import sys; sys.stdout.reconfigure(encoding='utf-8')

src = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT\DishonoredGame.int"
target = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame.int"

def get_key(line):
    for sep in ('=', ':'):
        if sep in line:
            return line[:line.index(sep)].strip()
    return None

# Load source file (for key reference)
for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig'):
    try:
        with open(src, 'r', encoding=enc) as f:
            src_lines = f.readlines()
        src_enc = enc
        break
    except:
        continue

# Build source key -> key mapping (for backslash fix)
src_key_map = {}  # no-backslash -> with-backslash
for line in src_lines:
    k = get_key(line)
    if k:
        if '\_' in k:
            src_key_map[k.replace('\_', '_')] = k
        else:
            src_key_map[k] = k

print(f"SOURCE keys: {len(src_key_map)}")

# Load target file (in-place edit)
for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
    try:
        with open(target, 'r', encoding=enc) as f:
            content = f.read()
        target_enc = enc
        break
    except:
        continue

# Convert content to lines preserving original line endings
lines = content.split('\n')
print(f"TARGET lines (split): {len(lines)}")

# Fix line by line - replace key only, preserve everything else exactly
fixed_lines = []
fixed = 0

for i, line in enumerate(lines):
    k = get_key(line)
    if k and k in src_key_map and k != src_key_map[k]:
        # Key needs backslash fix
        new_key = src_key_map[k]
        # Find separator and reconstruct
        for sep in ('=', ':'):
            if sep in line:
                sep_pos = line.index(sep)
                # key separator value
                value_part = line[sep_pos:]  # includes sep and everything after
                new_line = new_key + value_part
                fixed_lines.append(new_line)
                fixed += 1
                break
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

print(f"Fixed: {fixed} lines")

# Write back to same file, preserving exact encoding
output_content = '\n'.join(fixed_lines)
with open(target, 'w', encoding=target_enc) as f:
    f.write(output_content)

# If original didn't end with newline, we need to handle that
# But source ended with \n, so we're good

print(f"Saved to: {target} ({target_enc})")

# Verify
with open(target, 'r', encoding=target_enc) as f:
    verify = f.read()
verify_lines = verify.split('\n')
print(f"Verify: {len(verify_lines)} lines")

# Check key format
import re
keys_fixed = [get_key(l) for l in verify_lines if get_key(l)]
keys_with_bs = [k for k in keys_fixed if '\_' in k]
print(f"Keys with backslash: {len(keys_with_bs)}")
