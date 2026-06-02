import os
import re
import sys

# Set UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

SOURCE_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\INT'
TARGET_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\INT'

def detect_encoding(filepath):
    with open(filepath, 'rb') as f:
        raw = f.read()
    if raw.startswith(b'\xff\xfe'):
        return 'utf-16-le'
    elif raw.startswith(b'\xfe\xff'):
        return 'utf-16-be'
    else:
        return 'utf-8-sig'

def read_lines(filepath):
    enc = detect_encoding(filepath)
    with open(filepath, 'r', encoding=enc, errors='ignore') as f:
        return f.readlines()

def check_file(filename):
    src_path = os.path.join(SOURCE_DIR, filename)
    tgt_path = os.path.join(TARGET_DIR, filename)
    
    if not os.path.exists(tgt_path):
        return None, 'NOT FOUND'
    
    src_lines = read_lines(src_path)
    tgt_lines = read_lines(tgt_path)
    
    issues = []
    thai_count = 0
    eng_only_count = 0
    
    for i in range(min(len(src_lines), len(tgt_lines))):
        src_line = src_lines[i].strip()
        tgt_line = tgt_lines[i].strip()
        
        # Skip non-translatable lines
        if not src_line or src_line.startswith((';', '[', '#')):
            continue
        if '=' not in src_line:
            continue
        
        # Get source value
        src_val = src_line.split('=', 1)[1] if '=' in src_line else ''
        # Remove quotes from source
        src_val_clean = src_val.strip('"').strip()
        
        # Skip empty source values
        if not src_val_clean:
            continue
        
        # Get target value
        tgt_val = tgt_line.split('=', 1)[1] if '=' in tgt_line else ''
        tgt_val_clean = tgt_val.strip('"').strip()
        
        # Check if target has Thai
        has_thai = any('\u0e00' <= c <= '\u0e7f' for c in tgt_val_clean)
        
        # Check for untranslated English (exclude backtick vars)
        has_backtick = '`' in src_val
        has_english = bool(re.search(r'[a-zA-Z]{2,}', tgt_val_clean))
        
        if has_thai:
            thai_count += 1
            # Check for remaining English words
            english_words = re.findall(r'[a-zA-Z]{3,}', tgt_val_clean)
            # Filter out known OK English (game terms that might stay in English)
            bad_english = [w for w in english_words if w.lower() not in 
                         ['gba', 'use', 'key', 'ui', 'msg', 'int', 'the', 'and', 'for']]
            if bad_english:
                issues.append(('MIXED', i, src_val_clean[:40], tgt_val_clean[:60], bad_english))
        elif has_english and not has_backtick:
            # Has English but no Thai - might be untranslated
            eng_only_count += 1
            issues.append(('NO_THAI', i, src_val_clean[:40], tgt_val_clean[:60], []))
    
    return {
        'thai': thai_count,
        'eng_only': eng_only_count,
        'issues': issues[:5]  # First 5 issues only
    }, None

# Check all translated files
files = sorted(os.listdir(TARGET_DIR))

print('='*70)
print('TIER 2 TRANSLATION QUALITY REPORT')
print('='*70)
print('')

problem_files = []
for filename in files:
    if not filename.lower().endswith('.int'):
        continue
    
    result, err = check_file(filename)
    if err:
        print('ERROR {0}: {1}'.format(filename, err))
        continue
    
    if result['eng_only'] > 0 or (result['issues'] and any(x[0] == 'MIXED' for x in result['issues'])):
        problem_files.append((filename, result))

print('Files with potential issues: {0}/{1}'.format(len(problem_files), len(files)))
print('')

if problem_files:
    print('=== PROBLEM FILES ===')
    for fname, res in problem_files[:20]:
        print('')
        print('[WARN] {0} - Thai:{1} Eng-only:{2}'.format(fname, res['thai'], res['eng_only']))
        for issue in res['issues'][:3]:
            if issue[0] == 'NO_THAI':
                print('  L{0} [NO_THAI] SRC: {1}'.format(issue[1], issue[2]))
                print('  L{0}         TGT: {1}'.format(issue[1], issue[3]))
            elif issue[0] == 'MIXED':
                print('  L{0} [MIXED ENG] TGT: {1}'.format(issue[1], issue[3]))
else:
    print('All files look good!')

print('')
print('='*70)