import sys; sys.stdout.reconfigure(encoding='utf-8')

src = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT\DishonoredGame.int"
target = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame.int"

def get_key(line):
    for sep in ('=', ':', ': '):
        if sep in line:
            return line[:line.index(sep)].strip(), sep
    return None, None

# Step 1: Build key mapping from SOURCE
with open(src, 'r', encoding='utf-16-le', newline='') as f:
    src_content = f.read()
src_lines = src_content.split('\r\n')  # SOURCE uses CRLF
src_enc = 'utf-16-le'

src_key_to_key = {}  # key without backslash -> key with backslash
for line in src_lines:
    k, _ = get_key(line)
    if k:
        if '\_' in k:
            src_key_to_key[k.replace('\_', '_')] = k
        else:
            src_key_to_key[k] = k

# Step 2: Load TARGET (it uses LF based on how it was saved)
with open(target, 'r', encoding='utf-16-le', newline='') as f:
    target_content = f.read()
target_lines = target_content.split('\n')  # TARGET was saved with LF

print(f"SOURCE (CRLF): {len(src_lines)} lines")
print(f"TARGET (LF): {len(target_lines)} lines")

# Step 3: Fix backslash in TARGET keys, preserve line endings as-is
fixed = 0
for i, line in enumerate(target_lines):
    k, sep = get_key(line)
    if k and k in src_key_to_key and k != src_key_to_key[k]:
        new_key = src_key_to_key[k]
        # Reconstruct the line with new key
        if sep:
            sep_pos = line.index(sep)
            value_part = line[sep_pos:]  # includes sep and everything after
            target_lines[i] = new_key + value_part
            fixed += 1

print(f"Fixed: {fixed} lines")

# Step 4: Write back with LF (TARGET's original format)
with open(target, 'w', encoding='utf-16-le', newline='') as f:
    f.write('\n'.join(target_lines))

print(f"Saved: {target}")

# Verify
with open(target, 'r', encoding='utf-16-le', newline='') as f:
    verify = f.read()
verify_lines = verify.split('\n')
print(f"Verify: {len(verify_lines)} lines")
print(f"First 5 lines:")
for i, l in enumerate(verify_lines[:5]):
    print(f"  {i+1}: {repr(l[:80])}")
