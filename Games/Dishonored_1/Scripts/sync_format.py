# sync_format.py
# Sync TH file format to match INT (preserve Thai content, match line count)
import os

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\00_BackUP\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\00_BackUP\Localization\INT'

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
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text, enc

def get_id(line):
    """Extract ID from line like 'ID: content' or 'ID:KEY: content'"""
    if ':' not in line:
        return None
    return line.split(':')[0].strip()

def sync_file(th_path, int_path):
    """Sync TH file to match INT line count while preserving Thai content"""
    
    th_text, th_enc = read_lines(th_path)
    int_text, int_enc = read_lines(int_path)
    
    th_lines = th_text.split('\n')
    int_lines = int_text.split('\n')
    
    if len(th_lines) == len(int_lines):
        return 'SKIP', 0
    
    # Build ID list from INT
    int_ids = []
    for line in int_lines:
        if line.strip():
            int_ids.append(get_id(line))
    
    # Build ID list from TH  
    th_ids = []
    for line in th_lines:
        if line.strip():
            th_ids.append(get_id(line))
    
    # Find extra TH lines (by ID matching)
    extra_count = len(th_ids) - len(int_ids)
    
    if extra_count > 0:
        # TH has more lines - try to find and remove extra lines
        # Strategy: find TH lines that don't have matching IDs in INT
        new_th_lines = []
        removed = 0
        
        for line in th_lines:
            line_id = get_id(line)
            if line_id and line_id not in int_ids:
                # This line is extra - remove it
                removed += 1
                if removed > extra_count:
                    new_th_lines.append(line)
            else:
                new_th_lines.append(line)
        
        if removed >= extra_count and len(new_th_lines) == len(int_lines):
            # Success - we can sync
            return 'REMOVED', removed, new_th_lines, th_enc
        else:
            return 'PARTIAL', 0
    
    elif extra_count < 0:
        # TH has fewer lines - add blank lines to match
        diff = abs(extra_count)
        new_th_lines = th_lines[:]
        
        # Try to find where to insert blank lines (at ends of sections)
        for _ in range(diff):
            new_th_lines.append('')
        
        if len(new_th_lines) == len(int_lines):
            return 'ADDED', diff, new_th_lines, th_enc
        else:
            return 'FAIL', 0
    
    return 'DONE', 0

def process_all():
    results = {'ok': 0, 'removed': 0, 'added': 0, 'skip': 0, 'fail': 0, 'partial': 0}
    details = []
    
    th_files = [f for f in os.listdir(TH_DIR) if f.endswith('.int')]
    
    for f in sorted(th_files):
        th_path = os.path.join(TH_DIR, f)
        int_path = os.path.join(INT_DIR, f)
        
        if not os.path.exists(int_path):
            results['fail'] += 1
            details.append(f'{f}: INT not found')
            continue
        
        result = sync_file(th_path, int_path)
        
        if result[0] == 'SKIP':
            results['skip'] += 1
        elif result[0] == 'REMOVED':
            # Write fixed content
            enc = result[3]
            fixed_text = '\n'.join(result[2])
            # Preserve original line endings if possible
            with open(th_path, 'w', encoding=enc) as fw:
                fw.write(fixed_text)
            results['removed'] += 1
            results['ok'] += 1
            details.append(f'{f}: removed {result[1]} lines')
        elif result[0] == 'ADDED':
            enc = result[3]
            fixed_text = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc) as fw:
                fw.write(fixed_text)
            results['added'] += 1
            results['ok'] += 1
            details.append(f'{f}: added {result[1]} blank lines')
        elif result[0] == 'PARTIAL':
            results['partial'] += 1
            details.append(f'{f}: partial fix - needs manual review')
        elif result[0] == 'DONE':
            results['ok'] += 1
        else:
            results['fail'] += 1
            details.append(f'{f}: {result[0]}')
    
    # Write report
    with open(r'E:\Mod_Workspace\Dishonored_Mod_Workspace\sync_report.txt', 'w', encoding='utf-8') as f:
        f.write('SYNC FORMAT RESULTS\n')
        f.write('=' * 40 + '\n')
        f.write(f'OK: {results["ok"]}\n')
        f.write(f'SKIP (already match): {results["skip"]}\n')
        f.write(f'REMOVED (extra lines deleted): {results["removed"]}\n')
        f.write(f'ADDED (blank lines added): {results["added"]}\n')
        f.write(f'PARTIAL (needs review): {results["partial"]}\n')
        f.write(f'FAIL: {results["fail"]}\n')
        f.write('\nDETAILS:\n')
        f.write('-' * 40 + '\n')
        for d in details:
            f.write(d + '\n')
    
    print(f'Results: OK={results["ok"]}, SKIP={results["skip"]}, REMOVED={results["removed"]}, ADDED={results["added"]}, PARTIAL={results["partial"]}, FAIL={results["fail"]}')
    print('Report saved to sync_report.txt')
    return results

if __name__ == '__main__':
    process_all()