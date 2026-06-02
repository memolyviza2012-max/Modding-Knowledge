# sync_th_int.py
# Sync TH to match INT line count by removing extra lines
import os

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'

def get_id(line):
    if ':' not in line: return None
    return line.split(':')[0].strip()

def get_val(line):
    if ':' not in line: return ''
    return line.split(':', 1)[1].strip()

ok_count = 0
sync_count = 0
skip_count = 0

for f in sorted(os.listdir(TH_DIR)):
    if not f.endswith('.int'): continue
    
    th_path = os.path.join(TH_DIR, f)
    int_path = os.path.join(INT_DIR, f)
    if not os.path.exists(int_path): continue
    
    with open(th_path, 'rb') as fh:
        th_raw = fh.read()
    with open(int_path, 'rb') as fh:
        int_raw = fh.read()
    
    th_text = th_raw.decode('utf-16-le', errors='replace').replace('\r\n', '\n').replace('\r', '\n').replace('\x00', '')
    int_text = int_raw.decode('utf-16-le', errors='replace').replace('\r\n', '\n').replace('\r', '\n').replace('\x00', '')
    
    th_lines = th_text.split('\n')
    int_lines = int_text.split('\n')
    
    if len(th_lines) == len(int_lines):
        ok_count += 1
        continue
    
    # TH has extra lines - sync by removing extras
    # Build ID map from INT
    int_ids = []
    int_id_set = set()
    for line in int_lines:
        if line.strip():
            tid = get_id(line)
            if tid:
                int_ids.append(tid)
                int_id_set.add(tid)
    
    # Find extra TH lines (by ID)
    extra_count = len(th_lines) - len(int_lines)
    
    # Keep TH lines that match INT IDs, remove extras
    new_lines = []
    removed = 0
    for line in th_lines:
        if not line.strip():
            new_lines.append(line)
            continue
        tid = get_id(line)
        if tid in int_id_set:
            new_lines.append(line)
        else:
            removed += 1
    
    # If still wrong count, just truncate to match INT
    if len(new_lines) > len(int_lines):
        new_lines = new_lines[:len(int_lines)]
    
    # Write synced TH
    with open(th_path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(new_lines))
    
    sync_count += 1
    print(f'SYNC: {f} ({len(th_lines)} -> {len(new_lines)}, removed={removed})')

print()
print(f'Result: {ok_count} OK, {sync_count} SYNCED, {skip_count} SKIP')