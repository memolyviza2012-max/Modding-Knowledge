import codecs
import re

# Read the translated file
filepath = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\INT\movable_twk.int'
with open(filepath, 'rb') as f:
    raw = f.read()

# Check BOM
if raw.startswith(b'\xff\xfe'):
    encoding = 'utf-16-le'
elif raw.startswith(b'\xef\xbb\xbf'):
    encoding = 'utf-8-sig'
else:
    encoding = 'utf-8'

print('Encoding detected:', encoding)

# Decode and show lines
content = raw.decode(encoding)
lines = content.split('\n')

print('Total lines:', len(lines))
print('')
print('=== First 20 translatable lines with Thai check ===')
for i, line in enumerate(lines[:40]):
    if '=' in line and not line.strip().startswith((';', '[', '#')):
        key = line.split('=')[0] if '=' in line else ''
        val = line.split('=', 1)[1] if '=' in line else ''
        
        # Check for Thai characters
        has_thai = any('\u0e00' <= c <= '\u0e7f' for c in val)
        # Check for backtick variables
        has_backtick = '`' in val
        # Check for English letters (a-zA-Z)
        has_english = bool(re.search(r'[a-zA-Z]{3,}', val))
        
        if has_thai:
            # Extract Thai portion
            thai_chars = ''.join(c for c in val if '\u0e00' <= c <= '\u0e7f' or c in ' .,!?-()[]')
            print('THAI L{0}: {1}= [{2}]'.format(i, key[:20], thai_chars[:60]))
        elif len(val.strip()) > 0 and val.strip() not in ('""', "''"):
            # Non-empty value without Thai
            print('ENG-ONLY? L{0}: {1}= [{2}]'.format(i, key[:20], val[:50]))

print('')
print('=== Summary: counting Thai vs English-only lines ===')
thai_count = 0
eng_count = 0
empty_count = 0
for line in lines:
    if '=' in line and not line.strip().startswith((';', '[', '#')):
        val = line.split('=', 1)[1] if '=' in line else ''
        has_thai = any('\u0e00' <= c <= '\u0e7f' for c in val)
        if has_thai:
            thai_count += 1
        elif len(val.strip()) > 0 and val.strip() not in ('""', "''"):
            eng_count += 1
        else:
            empty_count += 1

print('Lines with Thai: {0}'.format(thai_count))
print('Lines with English only: {0}'.format(eng_count))
print('Empty/blank lines: {0}'.format(empty_count))