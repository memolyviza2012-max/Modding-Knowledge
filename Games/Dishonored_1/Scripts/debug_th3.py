import os

th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'

with open(th_path, 'rb') as f:
    raw = f.read()

# Check raw structure around line 813
# LF at 813 means lines 0-812 (814 total)
# But text mode shows 1626 - that's because \r is being treated as line separator

# Let's find position of LF at index 812
lf_positions = []
pos = 0
while True:
    pos = raw.find(b'\n', pos)
    if pos == -1:
        break
    lf_positions.append(pos)
    pos += 1

print(f'Total LFs: {len(lf_positions)}')
print(f'LF at index 812 position: {lf_positions[812]}')
print(f'Around that area (bytes {lf_positions[812]-10} to {lf_positions[812]+10}):')
print(raw[lf_positions[812]-10:lf_positions[812]+10].hex())
print('Context:', raw[lf_positions[812]-10:lf_positions[812]+10])

# The issue: LF at index 812 has \r before it?
print()
print(f'Bytes before LF at 812: {raw[lf_positions[812]-1:lf_positions[812]+1].hex()}')
print(f'Bytes before that: {raw[lf_positions[812]-2:lf_positions[812]].hex()}')