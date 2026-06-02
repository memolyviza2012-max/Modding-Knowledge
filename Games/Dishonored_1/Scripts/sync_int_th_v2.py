# sync_int_th_v2.py
# Sync TH file format to match INT exactly
# Key: Match section headers [SectionName] and property lines
import os
import re

INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
REPORT_PATH = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\sync_int_th_v2_report.txt'

def detect_encoding(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] in [b'\xff\xfe', b'\xfe\xff']:
        return 'utf-16-le' if raw[:2] == b'\xff\xfe' else 'utf-16-be'
    if raw.startswith(b'\xef\xbb\xbf'):
        return 'utf-8-sig'
    try:
        raw.decode('utf-8')
        return 'utf-8'
    except:
        return 'cp1252'

def read_lines(path):
    enc = detect_encoding(path)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode(enc, errors='replace')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text, enc

def get_section_id(line):
    """Extract section ID from [SectionName Tweaks_...] or property=ID"""
    line = line.strip()
    if not line:
        return None
    # [SectionName ClassName]
    m = re.match(r'\[([^\]]+)\]', line)
    if m:
        return m.group(1)
    # property=value
    if '=' in line:
        return line.split('=')[0].strip()
    return None

def get_int_structure(int_lines):
    """Build structure: section -> list of property IDs"""
    sections = {}
    current_section = None
    for line in int_lines:
        line = line.rstrip('\n')
        sid = get_section_id(line)
        if sid:
            current_section = sid
            if current_section not in sections:
                sections[current_section] = []
        elif current_section and line.strip():
            prop_id = get_section_id(line)
            if prop_id:
                sections[current_section].append(prop_id)
    return sections

def sync_file(th_path, int_path):
    """Sync TH file to match INT structure exactly"""
    
    th_text, th_enc = read_lines(th_path)
    int_text, int_enc = read_lines(int_path)
    
    th_lines = th_text.split('\n')
    int_lines = int_text.split('\n')
    
    th_count = len(th_lines)
    int_count = len(int_lines)
    
    if th_count == int_count:
        return 'OK', 0, 'already matched'
    
    int_struct = get_int_structure(int_lines)
    int_total_sections = len(int_struct)
    
    # Build TH structure
    th_struct = {}
    current_section = None
    th_extra_sections = []
    for line in th_lines:
        line = line.rstrip('\n')
        sid = get_section_id(line)
        if sid:
            if sid not in int_struct:
                th_extra_sections.append(sid)
            current_section = sid
            if current_section not in th_struct:
                th_struct[current_section] = []
        elif current_section and line.strip():
            prop_id = get_section_id(line)
            if prop_id:
                th_struct[current_section].append(prop_id)
    
    if th_count > int_count:
        diff = th_count - int_count
        return 'TH_EXTRA_LINES', diff, f'TH has {diff} more lines'
    
    diff = int_count - th_count
    return 'INT_EXTRA_LINES', diff, f'INT has {diff} more lines'

def process_all():
    results = {
        'ok': 0,
        'th_extra': 0,
        'int_extra': 0,
    }
    details = []
    problems = []
    
    int_files = sorted([f for f in os.listdir(INT_DIR) if f.endswith('.int')])
    th_files = set([f for f in os.listdir(TH_DIR) if f.endswith('.int')])
    
    for f in int_files:
        th_path = os.path.join(TH_DIR, f)
        int_path = os.path.join(INT_DIR, f)
        
        if f not in th_files:
            results['int_extra'] += 1
            details.append(f'{f}: TH not found')
            problems.append(f'{f}: TH file missing')
            continue
        
        result = sync_file(th_path, int_path)
        status = result[0]
        
        if status == 'OK':
            results['ok'] += 1
            details.append(f'{f}: OK')
        elif status == 'TH_EXTRA_LINES':
            results['th_extra'] += 1
            details.append(f'{f}: TH_EXTRA_LINES - {result[2]}')
            problems.append(f'{f}: {result[2]}')
        elif status == 'INT_EXTRA_LINES':
            results['int_extra'] += 1
            details.append(f'{f}: INT_EXTRA_LINES - {result[2]}')
            problems.append(f'{f}: {result[2]}')
    
    total = len(int_files)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as rep:
        rep.write('SYNC INT vs TH FORMAT RESULTS (v2)\n')
        rep.write('=' * 50 + '\n')
        rep.write(f'Total INT files: {total}\n')
        rep.write(f'TH missing (no sync needed): {results["int_extra"]}\n')
        rep.write(f'TH OK: {results["ok"]}\n')
        rep.write(f'TH has extra lines: {results["th_extra"]}\n')
        rep.write('\nPROBLEMS:\n')
        rep.write('-' * 50 + '\n')
        for p in problems:
            rep.write('PROBLEM: ' + p + '\n')
        rep.write('\nALL DETAILS:\n')
        rep.write('-' * 50 + '\n')
        for d in details:
            rep.write(d + '\n')
    
    print(f'Results: OK={results["ok"]}, TH_EXTRA={results["th_extra"]}, INT_EXTRA={results["int_extra"]}')
    print(f'Total: {total} files')
    print(f'Problems: {len(problems)} files')
    print(f'Report: {REPORT_PATH}')
    return results, problems, details

if __name__ == '__main__':
    process_all()
