import sys; sys.stdout.reconfigure(encoding='utf-8')

src = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT\DishonoredGame.int"
trans = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame.int"
output = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame_fixed.int"

def parse_int_file(path):
    """Parse .int file, return list of (key, value, line_idx) for keyed lines."""
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig'):
        try:
            with open(path, 'r', encoding=enc) as f:
                lines = f.readlines()
            return lines, enc
        except:
            continue
    return [], None

def get_key_value(line):
    """Extract key and value from a line. Returns (key, value, separator)."""
    for sep in ('=', ': '):
        if sep in line:
            idx = line.index(sep)
            key = line[:idx].strip()
            value = line[idx+len(sep):].rstrip('\n\r')
            return key, value, sep
    return None, None, None

# Load files
src_lines, src_enc = parse_int_file(src)
trans_lines, trans_enc = parse_int_file(trans)

print(f"SOURCE: {len(src_lines)} lines ({src_enc})")
print(f"TRANSLATED: {len(trans_lines)} lines ({trans_enc})")

# Build key -> value dict from translated file
trans_dict = {}
for line in trans_lines:
    k, v, _ = get_key_value(line)
    if k and v is not None:
        trans_dict[k] = v

print(f"Translated keys: {len(trans_dict)}")

# Build new lines by replacing values in SOURCE using TRANSLATED values
new_lines = []
fixed = 0
skipped = 0

for i, line in enumerate(src_lines):
    k, src_val, sep = get_key_value(line)
    if k and k in trans_dict:
        # Replace source value with translated value, preserving line ending
        new_val = trans_dict[k]
        if sep == ': ':
            new_line = f"{k}: {new_val}\n"
        else:
            new_line = f"{k}={new_val}\n"
        new_lines.append(new_line)
        fixed += 1
    else:
        # Preserve blank lines and comments exactly
        new_lines.append(line)
        skipped += 1

print(f"Fixed: {fixed} | Preserved: {skipped}")
print(f"New total lines: {len(new_lines)}")

# Write output with same encoding as source
with open(output, 'w', encoding=src_enc) as f:
    f.writelines(new_lines)

print(f"Saved: {output}")

# Quick verify
with open(output, 'r', encoding=src_enc) as f:
    verify_lines = f.readlines()
print(f"Verify: {len(verify_lines)} lines (should be {len(src_lines)})")

# Check key counts match
src_keys = set()
trans_out_keys = set()
for l in verify_lines:
    k, _, _ = get_key_value(l)
    if k: src_keys.add(k)
for l in trans_lines:
    k, _, _ = get_key_value(l)
    if k: trans_out_keys.add(k)
print(f"Output keys: {len(src_keys)} | Trans keys: {len(trans_out_keys)}")
