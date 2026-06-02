import os

th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'

# Read file
with open(th_path, 'rb') as f:
    raw = f.read()

print('File size:', len(raw))
print()

# Count LF, CR, CRLF
LF = b'\n'
CR = b'\r'

lf_count = raw.count(LF)
cr_count = raw.count(CR)
crlf_count = raw.count(b'\r\n')

print('LF:', lf_count)
print('CR:', cr_count)
print('CRLF:', crlf_count)

# Check if CRs are all followed by LF
cr_positions = []
pos = 0
while True:
    pos = raw.find(CR, pos)
    if pos == -1:
        break
    cr_positions.append(pos)
    pos += 1

bare_cr = 0
for p in cr_positions:
    if p + 1 >= len(raw) or raw[p+1] != 0x0A:
        bare_cr += 1

print('Bare CR:', bare_cr)
print()

# Read as text and count newlines
with open(th_path, 'r', encoding='utf-8', errors='replace') as f:
    text = f.read()

lines_split_n = text.split('\n')
lines_split_rn = text.split('\r\n')
lines_split_r = text.split('\r')

print('split by \\n:', len(lines_split_n))
print('split by \\r\\n:', len(lines_split_rn))
print('split by \\r:', len(lines_split_r))
print()

# Check raw bytes again
with open(th_path, 'rb') as f:
    raw2 = f.read()
print('Read again - size:', len(raw2))
print('Read again - LF:', raw2.count(b'\n'))