import os

th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'

with open(th_path, 'rb') as f:
    raw = f.read()

CR = b'\r'
LF = b'\n'
CRLF = b'\r\n'

total_cr = raw.count(CR)
total_lf = raw.count(LF)
total_crlf = raw.count(CRLF)
bare_cr = total_cr - total_crlf

print('Total CR:', total_cr)
print('Total LF:', total_lf)
print('Total CRLF:', total_crlf)
print('Bare CR (CR not followed by LF):', bare_cr)

if bare_cr > 0:
    print()
    print('Bare CR found! This causes extra lines in text mode on Windows.')
    print()
    # Show first few bare CR positions
    pos = 0
    count = 0
    while count < 5:
        pos = raw.find(CR, pos)
        if pos == -1:
            break
        if pos + 1 >= len(raw) or raw[pos+1:pos+2] != LF:
            print('Bare CR at position', pos, ':', repr(raw[pos-5:pos+10]))
        pos += 1
        count += 1
else:
    print()
    print('No bare CR found. This is strange...')