import os

th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'

with open(th_path, 'rb') as f:
    raw = f.read()

CR = b'\r'
LF = b'\n'

# Find CR positions
cr_positions = []
pos = 0
while True:
    pos = raw.find(CR, pos)
    if pos == -1:
        break
    cr_positions.append(pos)
    pos += 1

print('Total CR:', len(cr_positions))
print('First 5 CR positions:', cr_positions[:5])

# Check each CR: is it followed by LF?
bare_cr = 0
crlf_count = 0
for p in cr_positions:
    if p + 1 < len(raw) and raw[p+1] == 0x0A:
        crlf_count += 1
    else:
        bare_cr += 1

print('CRLF:', crlf_count)
print('Bare CR:', bare_cr)

# Show context around first few CR
print()
for i, p in enumerate(cr_positions[:3]):
    print(f'CR at {p}: {raw[max(0,p-5):p+6].hex()} = {raw[max(0,p-5):p+6]}')