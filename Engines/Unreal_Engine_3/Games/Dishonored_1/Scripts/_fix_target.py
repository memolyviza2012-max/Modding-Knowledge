import sys; sys.stdout.reconfigure(encoding='utf-8')

src = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT\DishonoredGame.int"
target = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame.int"

def get_key(line):
    for sep in ('=', ': '):
        if sep in line:
            return line[:line.index(sep)].strip(), sep
    return None, None

# Load SOURCE (CRLF)
with open(src, 'r', encoding='utf-16-le', newline='') as f:
    src_content = f.read()
src_lines = src_content.split('\r\n')
src_enc = 'utf-16-le'
print(f"SOURCE: {len(src_lines)} lines (CRLF)")

# Load TARGET (LF)
with open(target, 'r', encoding='utf-16-le', newline='') as f:
    target_content = f.read()
target_lines = target_content.split('\n')
target_enc = 'utf-16-le'
print(f"TARGET: {len(target_lines)} lines (LF)")

# Build key mapping: key without backslash -> key with backslash
key_map = {}
for line in src_lines:
    k, _ = get_key(line)
    if k:
        if '\_' in k:
            key_map[k.replace('\_', '_')] = k
        else:
            key_map[k] = k

print(f"SOURCE key map: {len(key_map)} keys")

# Fix TARGET lines - fix backslash in keys only
fixed = 0
for i, line in enumerate(target_lines):
    k, sep = get_key(line)
    if k and k in key_map and k != key_map[k]:
        new_key = key_map[k]
        sep_pos = line.index(sep)
        value_part = line[sep_pos:]  # includes sep and everything after
        target_lines[i] = new_key + value_part
        fixed += 1

print(f"Fixed: {fixed} lines")

# Write back with LF (TARGET's original line ending)
with open(target, 'w', encoding=target_enc, newline='') as f:
    f.write('\n'.join(target_lines))

print(f"Saved: {target}")

# Verify
with open(target, 'r', encoding='utf-16-le', newline='') as f:
    verify = f.read()
verify_lines = verify.split('\n')
print(f"Verify: {len(verify_lines)} lines")

# Check key formats
keys_with_bs = [k for k in get_key.__name__ if '\_' in k]
src_bs = sum(1 for l in src_lines if get_key(l)[0] and '\_' in get_key(l)[0])
target_bs = sum(1 for l in target_lines if get_key(l)[0] and '\_' in get_key(l)[0])
print(f"SOURCE keys with backslash: {src_bs}")
print(f"TARGET keys with backslash: {target_bs}")

print()
print("First 5 lines of TARGET after fix:")
for i, l in enumerate(target_lines[:5]):
    print(f"  {i+1}: {repr(l[:80])}")
