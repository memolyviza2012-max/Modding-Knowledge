import os

th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'

# Read as raw UTF-8
with open(th_path, 'rb') as f:
    raw = f.read()

print('Raw size:', len(raw))
print('LF count:', raw.count(b'\n'))
print('CRLF count:', raw.count(b'\r\n'))
print('CR count:', raw.count(b'\r'))

# Check for UTF-16 signature
if raw.startswith(b'\xff\xfe'):
    print('Has UTF-16-LE BOM (FF FE)')
elif raw.startswith(b'\xfe\xff'):
    print('Has UTF-16-BE BOM (FE FF)')
elif raw.startswith(b'\xef\xbb\xbf'):
    print('Has UTF-8 BOM (EF BB BF)')
else:
    print('No BOM')

# Check first 32 bytes
print('First 32 bytes:', raw[:32].hex())

# Decode and count lines
text = raw.decode('utf-8', errors='replace')
lines = text.split('\n')
print('Lines when split by \\n:', len(lines))

# Check if maybe split by \r\n?
lines2 = text.split('\r\n')
print('Lines when split by \\r\\n:', len(lines2))

# Check line endings
if '\r\n' in text:
    print('Contains \\r\\n: YES')
if '\r' in text:
    print('Contains \\r: YES')
if '\n' in text:
    print('Contains \\n: YES')

# What is the actual last character?
print('Last 4 characters (repr):', repr(text[-4:]))