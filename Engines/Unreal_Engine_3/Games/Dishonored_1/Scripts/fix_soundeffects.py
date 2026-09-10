# Fix sound effects wrapper in TH test file
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
INT_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Brothel_P\L_Brothel_P_INT.yaml"
TH_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH_test.yaml"
OUTPUT_PATH = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Brothel_P\L_Brothel_P_TH_fixed.yaml"

# Read INT — collect NonWord entries that have '* ... *' wrapper (lines 473-526, 1-indexed)
int_nonword = {}
int_lines = []
with open(INT_PATH, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 472 <= i <= 525 and ': ' in line:
            key, val = line.split(': ', 1)
            val = val.strip()
            if val.startswith("'* ") and val.endswith(" *'"):
                int_nonword[key.strip()] = val

print(f"INT NonWord entries with '* ... *' wrapper: {len(int_nonword)}")

# Read TH
th_lines = []
with open(TH_PATH, 'r', encoding='utf-8-sig') as f:
    th_lines = [l.rstrip('\n\r') for l in f.readlines()]

# Fix TH lines 473-526 (indices 472-525)
fixed_count = 0
for i in range(472, 526):
    if i >= len(th_lines):
        break
    line = th_lines[i]
    if ': ' not in line:
        continue
    key, val = line.split(': ', 1)
    key = key.strip()
    val = val.strip()
    
    if key in int_nonword:
        orig = int_nonword[key]
        if orig.startswith("'* ") and orig.endswith(" *'"):
            # Check if TH is missing the wrapper
            if not val.startswith("'* ") and not val.startswith("* "):
                inner = val
                th_lines[i] = f"{key}: '* {inner} *'"
                fixed_count += 1
                print(f"  Fixed [{i+1}]: '{key}' → '* {inner} *'")
            elif val.startswith("'* ") and val.endswith(" *'"):
                print(f"  OK   [{i+1}]: '{key}' already wrapped")
            else:
                print(f"  ??   [{i+1}]: '{key}' val='{val}'")

# Write output
with open(OUTPUT_PATH, 'w', encoding='utf-8-sig') as f:
    for line in th_lines:
        f.write(line + '\n')

print(f"\nFixed {fixed_count} sound effect entries")
print(f"Output: {OUTPUT_PATH}")
