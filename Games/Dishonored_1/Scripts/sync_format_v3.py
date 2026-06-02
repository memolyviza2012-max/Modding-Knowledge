# sync_format_v3.py
# Sync TH format to match INT exactly - preserve Thai content, match structure
import os
import re
from difflib import SequenceMatcher

INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
REPORT_PATH = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\sync_format_v3_report.txt'

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

def is_section_header(line):
    return line.strip().startswith('[') and ']' in line

def is_property(line):
    return '=' in line and not line.strip().startswith(';')

def is_comment(line):
    return line.strip().startswith(';')

def get_section_name(line):
    m = re.match(r'\[([^\]]+)\]', line.strip())
    return m.group(1) if m else None

def get_property_name(line):
    if '=' in line:
        return line.split('=')[0].strip()
    return None

def get_line_type(line):
    if not line.strip():
        return 'blank'
    if is_section_header(line):
        return 'section'
    if is_property(line):
        return 'property'
    if is_comment(line):
        return 'comment'
    return 'other'

def build_structure_index(lines):
    """Build index: section -> {properties: [], comments: [], blanks: count}"""
    struct = {}
    current_section = None
    
    for line in lines:
        lt = get_line_type(line)
        
        if lt == 'section':
            sec_name = get_section_name(line)
            if sec_name:
                current_section = sec_name
                if current_section not in struct:
                    struct[current_section] = {'lines': [], 'prop_order': []}
            struct[current_section]['lines'].append(('section', line))
        
        elif lt == 'property':
            prop_name = get_property_name(line)
            if current_section and prop_name:
                struct[current_section]['lines'].append(('property', line))
                struct[current_section]['prop_order'].append(prop_name)
        
        elif current_section is not None:
            struct[current_section]['lines'].append((lt, line))
        else:
            pass  # Global non-property lines
    
    return struct

def sync_file(th_path, int_path, report_lines):
    """Sync TH to match INT structure"""
    
    th_text, th_enc = read_lines(th_path)
    int_text, int_enc = read_lines(int_path)
    
    th_lines = th_text.split('\n')
    int_lines = int_text.split('\n')
    
    th_count = len(th_lines)
    int_count = len(int_lines)
    
    if th_count == int_count:
        # Check format match by comparing section headers and property order
        th_struct = build_structure_index(th_lines)
        int_struct = build_structure_index(int_lines)
        
        th_sections = list(th_struct.keys())
        int_sections = list(int_struct.keys())
        
        if th_sections == int_sections:
            return 'OK', 0, 'no changes needed'
        else:
            return 'SECTION_MISMATCH', 0, f'sections differ: TH={len(th_sections)}, INT={len(int_sections)}'
    
    # INT target structure
    int_struct = build_structure_index(int_lines)
    int_sections = list(int_struct.keys())
    
    # Build TH section list
    th_sections_order = []
    th_section_props = {}
    current_section = None
    
    for line in th_lines:
        lt = get_line_type(line)
        if lt == 'section':
            sn = get_section_name(line)
            if sn:
                current_section = sn
                if current_section not in th_sections_order:
                    th_sections_order.append(current_section)
                th_section_props[current_section] = []
        elif lt == 'property' and current_section:
            pn = get_property_name(line)
            if pn:
                th_section_props[current_section].append(pn)
    
    extra_sections = [s for s in th_sections_order if s not in int_sections]
    
    if extra_sections:
        # Remove extra sections from TH
        new_lines = []
        skip = False
        skip_section = None
        
        for line in th_lines:
            lt = get_line_type(line)
            
            if lt == 'section':
                sn = get_section_name(line)
                if sn in extra_sections:
                    skip = True
                    skip_section = sn
                    continue
                else:
                    skip = False
                    new_lines.append(line)
            elif skip:
                # Still inside extra section - check if we exited
                if lt == 'section':
                    sn = get_section_name(line)
                    if sn in extra_sections:
                        continue  # Stay in skip mode
                    else:
                        skip = False
                        new_lines.append(line)
                else:
                    continue  # Skip this line
            else:
                new_lines.append(line)
        
        removed = len(th_lines) - len(new_lines)
        
        # Check if line count now matches
        if len(new_lines) == int_count:
            return 'REMOVED_SECTIONS', removed, new_lines, th_enc, extra_sections
        elif len(new_lines) < int_count:
            # Need to add blank lines
            diff = int_count - len(new_lines)
            for _ in range(diff):
                new_lines.append('')
            return 'REMOVED_ADDED', removed, new_lines, th_enc, diff
        else:
            # Still too many - need deeper analysis
            return 'PARTIAL', 0, new_lines, th_enc, extra_sections
    else:
        return 'LINE_COUNT_DIFF', th_count, int_count, f'TH={th_count}, INT={int_count}'

def process_all():
    results = {'ok': 0, 'removed': 0, 'removed_added': 0, 'partial': 0, 'section_mismatch': 0, 'line_diff': 0, 'fail': 0}
    details = []
    problems = []
    
    int_files = sorted([f for f in os.listdir(INT_DIR) if f.endswith('.int')])
    th_files = set([f for f in os.listdir(TH_DIR) if f.endswith('.int')])
    
    for f in int_files:
        th_path = os.path.join(TH_DIR, f)
        int_path = os.path.join(INT_DIR, f)
        
        if f not in th_files:
            results['fail'] += 1
            details.append(f'{f}: TH not found')
            problems.append(f'{f}: TH file missing')
            continue
        
        result = sync_file(th_path, int_path, details)
        status = result[0]
        
        if status == 'OK':
            results['ok'] += 1
            details.append(f'{f}: OK')
        
        elif status == 'REMOVED_SECTIONS':
            enc = result[3]
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['removed'] += 1
            results['ok'] += 1
            details.append(f'{f}: REMOVED {result[1]} lines (extra sections: {result[4]})')
        
        elif status == 'REMOVED_ADDED':
            enc = result[3]
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['removed_added'] += 1
            results['ok'] += 1
            details.append(f'{f}: REMOVED {result[1]} lines + added {result[4]} blanks')
        
        elif status == 'PARTIAL':
            enc = result[3]
            # Write partial to see what we get
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['partial'] += 1
            results['ok'] += 1
            details.append(f'{f}: PARTIAL - written but may have issues')
            problems.append(f'{f}: PARTIAL - extra lines removed, needs manual check')
        
        elif status == 'SECTION_MISMATCH':
            results['section_mismatch'] += 1
            details.append(f'{f}: SECTION_MISMATCH - {result[2]}')
            problems.append(f'{f}: SECTION_MISMATCH - {result[2]}')
        
        elif status == 'LINE_COUNT_DIFF':
            results['line_diff'] += 1
            details.append(f'{f}: LINE_DIFF - {result[3]}')
            problems.append(f'{f}: LINE_DIFF - {result[3]}')
        
        else:
            results['fail'] += 1
            details.append(f'{f}: FAIL - {status}')
            problems.append(f'{f}: FAIL - {status}')
    
    total = len(int_files)
    ok_total = results['ok']
    problem_count = len(problems)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as rep:
        rep.write('SYNC FORMAT v3 RESULTS\n')
        rep.write('=' * 50 + '\n')
        rep.write(f'Total INT files: {total}\n')
        rep.write(f'OK (synced or no change): {ok_total}\n')
        rep.write(f'REMOVED extra sections: {results["removed"]}\n')
        rep.write(f'REMOVED + ADDED blanks: {results["removed_added"]}\n')
        rep.write(f'PARTIAL (written but needs check): {results["partial"]}\n')
        rep.write(f'SECTION_MISMATCH: {results["section_mismatch"]}\n')
        rep.write(f'LINE_DIFF: {results["line_diff"]}\n')
        rep.write(f'FAIL: {results["fail"]}\n')
        rep.write(f'\nPROBLEMS ({problem_count} files):\n')
        rep.write('-' * 50 + '\n')
        for p in problems:
            rep.write('PROBLEM: ' + p + '\n')
        rep.write('\nALL DETAILS:\n')
        rep.write('-' * 50 + '\n')
        for d in details:
            rep.write(d + '\n')
    
    print(f'Results: OK={ok_total}, REMOVED={results["removed"]}, REM_ADD={results["removed_added"]}, PARTIAL={results["partial"]}')
    print(f'SECTION_MISMATCH={results["section_mismatch"]}, LINE_DIFF={results["line_diff"]}, FAIL={results["fail"]}')
    print(f'Total: {total} files, Problems: {problem_count}')
    print(f'Report: {REPORT_PATH}')

if __name__ == '__main__':
    process_all()
