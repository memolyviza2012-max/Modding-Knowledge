import os

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml'

with open(path, 'rb') as f:
    raw = f.read()

# Properly decode - file has CRLF
text = raw.decode('utf-8', errors='replace')
# Only replace CRLF with LF, not bare CR
text = text.replace('\r\n', '\n')
lines = text.split('\n')

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\dlc06_first5.txt', 'w', encoding='utf-8') as f:
    f.write(f'Total lines (LF split): {len(lines)}\n\n')
    f.write('First 5 lines:\n')
    for i in range(min(5, len(lines))):
        f.write(f'{i+1}: {lines[i][:100]}\n')
    f.write('\nLine 395:\n')
    if 395 <= len(lines):
        f.write(f'{395}: {lines[394][:100]}\n')

print('Written to dlc06_first5.txt')
print('Total lines:', len(lines))