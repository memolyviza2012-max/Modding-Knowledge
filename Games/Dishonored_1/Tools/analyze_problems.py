import os
import re
import sys

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

# Check the specific problem files in detail
problem_files = [
    'DLC06_Twk_Store.int',
    'DLC07_Twk_Store.int',
    'DLC05_movable_twk.int',
    'DLC07_Twk_Player_Daud.int',
    'DLC06_Twk_Player_Daud.int',
]

print('='*70)
print('DETAILED PROBLEM FILE ANALYSIS')
print('='*70)

for fname in problem_files:
    src_path = os.path.join(SOURCE_DIR, fname)
    tgt_path = os.path.join(TARGET_DIR, fname)
    
    if not os.path.exists(tgt_path):
        print('\n[NOT FOUND] ' + fname)
        continue
    
    src_lines = read_lines(src_path)
    tgt_lines = read_lines(tgt_path)
    
    print('\n' + fname)
    print('-' * len(fname))
    print('Source lines: {0} | Target lines: {1}'.format(len(src_lines), len(tgt_lines)))
    
    # Find problematic lines
    for i in range(min(len(src_lines), len(tgt_lines))):
        src = src_lines[i].strip()
        tgt = tgt_lines[i].strip()
        
        # Skip non-translatable
        if not src or src.startswith((';', '[', '#')) or '=' not in src:
            continue
        
        # Check for issues
        has_question_marks = '?' in tgt and not any('\u0e00' <= c <= '\u0e7f' for c in tgt)
        has_cyrillic = any('\u0400' <= c <= '\u04FF' for c in tgt)
        has_structural_error = (tgt.count('=') > 1 and 'm_Description' not in src and 'ระดับ' in tgt)
        has_embedded_quote = (tgt.count('"') > 4 and ('ชื่อ=' in tgt or 'm_คำ' in tgt))
        
        if has_question_marks or has_cyrillic or has_structural_error or has_embedded_quote:
            print('')
            print('  L{0} [ISSUE]'.format(i))
            print('    SRC: {0}'.format(src[:80]))
            print('    TGT: {0}'.format(tgt[:100]))

print('\n' + '='*70)
print('SUMMARY OF ISSUES FOUND:')
print('='*70)
print('''
1. **DLC06_Twk_Store.int / DLC07_Twk_Store.int**: 
   - Problem: m_Description values contain embedded quotes and structural errors
   - Cause: Multi-line or complex string format not handled properly
   - Fix needed: Re-translate with better string boundary detection

2. **DLC05_movable_twk.int**:
   - Problem: Contains Cyrillic characters (п = U+043F) indicating encoding corruption
   - Cause: Possibly API returned garbled response for specific lines
   - Fix needed: Re-translate specific corrupted lines

3. **DLC07_Twk_Player_Daud.int / DLC06_Twk_Player_Daud.int**:
   - Problem: "ระดับ=((m_Name=" prefix showing structural corruption
   - Cause: Complex nested format (Level=((m_Name=...,m_Text=...))) confused the translator
   - Fix needed: Re-translate these files

4. **Button prompts (GBA_Block, GBA_Primary, etc.)**:
   - These are GAME VARIABLE names that MUST stay in English
   - NOT an error - the button bindings are correct to keep in English
   - Example: `GBA_Block` = the game's button input name
   - OK to leave as-is

5. **Hub_Twk.int, Overseer_Twk.int, etc.**:
   - Minor mixed English (place names like "Rudshore")
   - Low priority - these are proper nouns
''')