# sync_int_th.py
# Sync TH file format to match INT in 03_working\Localization
# Line count must match exactly, format must be identical
import os

INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
REPORT_PATH = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\sync_int_th_report.txt'

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

def get_id(line):
    """Extract ID from line like 'ID: content' or 'ID:KEY: content'"""
    if ':' not in line:
        return None
    return line.split(':')[0].strip()

def sync_file(th_path, int_path):
    """Sync TH file to match INT line count exactly"""
    
    th_text, th_enc = read_lines(th_path)
    int_text, int_enc = read_lines(int_path)
    
    th_lines = th_text.split('\n')
    int_lines = int_text.split('\n')
    
    th_count = len(th_lines)
    int_count = len(int_lines)
    
    if th_count == int_count:
        # Already match - check if format is EXACTLY the same
        identical = True
        for i, (th_line, int_line) in enumerate(zip(th_lines, int_lines)):
            # Check if IDs match (format-wise)
            th_id = get_id(th_line)
            int_id = get_id(int_line)
            if th_id != int_id:
                identical = False
                break
        
        if identical:
            return 'OK', 0, th_lines, th_enc
        else:
            return 'FORMAT_MISMATCH', 0, th_lines, th_enc
    
    diff = th_count - int_count
    
    if diff > 0:
        # TH has MORE lines - need to remove extra lines
        # Strategy: find TH lines that don't have matching IDs in INT
        int_ids = set()
        for line in int_lines:
            if line.strip():
                int_ids.add(get_id(line))
        
        new_th_lines = []
        removed = 0
        problem_lines = []
        
        for line in th_lines:
            line_id = get_id(line)
            if line_id and line_id not in int_ids:
                # Extra line - skip it
                removed += 1
                problem_lines.append(line[:60])
            else:
                new_th_lines.append(line)
        
        if removed >= diff and len(new_th_lines) == int_count:
            return 'REMOVED', removed, new_th_lines, th_enc
        elif removed > 0 and removed != diff:
            # Partial - some extra lines removed but not enough/exact
            return 'PARTIAL_REMOVED', removed, new_th_lines, th_enc, problem_lines
        else:
            return 'FAIL', 0, None, None, f'TH has {diff} extra lines but cannot sync cleanly'
    
    elif diff < 0:
        # TH has FEWER lines - report as problem
        return 'MISSING_LINES', abs(diff), None, None, f'TH missing {abs(diff)} lines vs INT'
    
    return 'DONE', 0

def process_all():
    results = {
        'ok': 0, 'format_mismatch': 0,
        'removed': 0, 'partial_removed': 0,
        'missing_lines': 0, 'fail': 0
    }
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
            continue
        
        result = sync_file(th_path, int_path)
        status = result[0]
        
        if status == 'OK':
            results['ok'] += 1
            details.append(f'{f}: OK (already matched)')
        
        elif status == 'REMOVED':
            # Write fixed TH
            enc = result[3]
            fixed_text = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed_text)
            results['removed'] += 1
            results['ok'] += 1
            details.append(f'{f}: REMOVED {result[1]} extra lines')
        
        elif status == 'PARTIAL_REMOVED':
            # Write partial fix but report problem
            enc = result[3]
            fixed_text = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed_text)
            results['partial_removed'] += 1
            results['ok'] += 1
            details.append(f'{f}: PARTIAL_REMOVED {result[1]} lines - written but may have issues')
            problems.append(f'{f}: extra lines removed: {result[4]}')
        
        elif status == 'FORMAT_MISMATCH':
            results['format_mismatch'] += 1
            details.append(f'{f}: FORMAT_MISMATCH - IDs differ')
            problems.append(f'{f}: line IDs do not match INT (format differs)')
        
        elif status == 'MISSING_LINES':
            results['missing_lines'] += 1
            details.append(f'{f}: MISSING_LINES - TH has {result[1]} fewer lines')
            problems.append(f'{f}: cannot sync - TH missing {result[1]} lines')
        
        elif status == 'FAIL':
            results['fail'] += 1
            details.append(f'{f}: FAIL - {result[4]}')
            problems.append(f'{f}: {result[4]}')
    
    total = sum(results.values())
    
    # Write report
    with open(REPORT_PATH, 'w', encoding='utf-8') as rep:
        rep.write('SYNC INT vs TH FORMAT RESULTS\n')
        rep.write('=' * 50 + '\n')
        rep.write(f'Total files: {total}\n')
        rep.write(f'OK (no fix needed): {results["ok"]}\n')
        rep.write(f'OK (REMOVED extra lines): {results["removed"]}\n')
        rep.write(f'PARTIAL_REMOVED: {results["partial_removed"]}\n')
        rep.write(f'FORMAT_MISMATCH: {results["format_mismatch"]}\n')
        rep.write(f'MISSING_LINES: {results["missing_lines"]}\n')
        rep.write(f'FAIL: {results["fail"]}\n')
        rep.write('\nPROBLEMS (files that cannot cleanly sync):\n')
        rep.write('-' * 50 + '\n')
        for p in problems:
            rep.write('PROBLEM: ' + p + '\n')
        rep.write('\nALL DETAILS:\n')
        rep.write('-' * 50 + '\n')
        for d in details:
            rep.write(d + '\n')
    
    print(f'Results: OK={results["ok"]}, REMOVED={results["removed"]}, PARTIAL={results["partial_removed"]}, FORMAT_MISMATCH={results["format_mismatch"]}, MISSING={results["missing_lines"]}, FAIL={results["fail"]}')
    print(f'Total: {total} files')
    print(f'Problems: {len(problems)} files')
    print(f'Report saved to: {REPORT_PATH}')
    return results, problems

if __name__ == '__main__':
    process_all()
