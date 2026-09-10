import os

def fix_line_endings(th_path):
    """Fix line endings: remove bare CR, normalize to LF only"""
    with open(th_path, 'rb') as f:
        raw = f.read()
    
    CR = b'\r'
    LF = b'\n'
    CRLF = b'\r\n'
    
    bare_cr = raw.count(CR) - raw.count(CRLF)
    
    if bare_cr == 0:
        print('  No bare CR in ' + os.path.basename(th_path))
        return False
    
    # Remove bare CR
    fixed = raw.replace(b'\r\n', b'\n')  # Normalize CRLF to LF
    fixed = fixed.replace(b'\r', b'')  # Remove bare CR
    
    # Write back as UTF-8
    text = fixed.decode('utf-8', errors='replace')
    with open(th_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print('  Fixed ' + str(bare_cr) + ' bare CRs in ' + os.path.basename(th_path))
    return True

print('=== Fixing L_Pub_FromFlooded_Script ===')
th_path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromFlooded_Script\L_Pub_FromFlooded_Script_TH.yaml'
fix_line_endings(th_path)

# Verify
with open(th_path, 'rb') as f:
    raw = f.read()
LF_count = raw.count(b'\n')
CR_count = raw.count(b'\r')
print('  After fix: size=' + str(len(raw)) + ', LF=' + str(LF_count) + ', CR=' + str(CR_count))

# Check text mode
with open(th_path, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.read().split('\n')
print('  Text mode lines: ' + str(len(lines)))