import os

th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'

# Method 1: text mode with encoding (like validate_check.py)
with open(th_path, 'r', encoding='utf-8', errors='replace') as f:
    content1 = f.read()
lines1 = content1.split('\n')
print('Method 1 (text mode):', len(lines1), 'lines')

# Method 2: binary mode, manual decode
with open(th_path, 'rb') as f:
    raw = f.read()
content2 = raw.decode('utf-8', errors='replace')
lines2 = content2.split('\n')
print('Method 2 (binary+decode):', len(lines2), 'lines')

# Check LF count
print('LF count in raw:', raw.count(b'\n'))
print('CRLF count in raw:', raw.count(b'\r\n'))
print('CR count in raw:', raw.count(b'\r'))

# Check raw ends
print('Raw ends with \\n:', raw.endswith(b'\n'))
print('Raw ends with \\r\\n:', raw.endswith(b'\r\n'))

# Show line 813 (index 812) content
print()
print('Line 813 content (text mode):')
try:
    line = lines1[812]
    print('  Length:', len(line))
    print('  First 20 chars:', line[:20])
except:
    print('  Out of range, total lines:', len(lines1))

# Show line 814 content
print('Line 814 content (text mode):')
try:
    line = lines1[813]
    print('  Length:', len(line))
    print('  First 20 chars:', repr(line[:20]))
except Exception as e:
    print('  Out of range:', e)