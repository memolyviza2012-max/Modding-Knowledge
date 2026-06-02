# sync_format_v4.py
# Sync TH format to match INT exactly
# Strategy: line-by-line matching by ID
import os
import re

INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
REPORT_PATH = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\sync_format_v4_report.txt'

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

def parse_line(line):
    """Return (type, id_key, content) for a line"""
    s = line.strip()
    if not s:
        return ('blank', '', '')
    if s.startswith('[') and ']' in s:
        m = re.match(r'\[([^\]]+)\]', s)
        return ('section', m.group(1), s)
    if '=' in s:
        idx = s.index('=')
        key = s[:idx].strip()
        val = s[idx+1:]
        return ('property', key, val)
    if s.startswith(';'):
        return ('comment', s[:20], s)
    return ('other', s[:30], s)

def build_id_map(lines):
    """Build list of (type, id_key) for each line"""
    result = []
    for line in lines:
        t, k, _ = parse_line(line)
        result.append((t, k))
    return result

def sync_file(th_path, int_path):
    """Sync TH to match INT structure by matching line types/keys"""
    
    th_text, th_enc = read_lines(th_path)
    int_text, int_enc = read_lines(int_path)
    
    th_lines = th_text.split('\n')
    int_lines = int_text.split('\n')
    
    th_count = len(th_lines)
    int_count = len(int_lines)
    
    if th_count == int_count:
        # Check if structure already matches
        th_ids = build_id_map(th_lines)
        int_ids = build_id_map(int_lines)
        if th_ids == int_ids:
            return 'OK', 0, th_lines, th_enc
        else:
            return 'STRUCT_DIFF', 0, None, None
    
    int_ids = build_id_map(int_lines)
    int_id_set = set(int_ids)
    
    diff = th_count - int_count
    
    if diff > 0:
        # TH has extra lines - build new TH by removing extras
        new_lines = []
        removed = 0
        problem_removed = []
        
        for i, line in enumerate(th_lines):
            th_id = parse_line(line)
            if th_id[0] == 'blank':
                # Skip blank lines that INT doesn't have in same position
                # Check if this position exists in INT
                if i < len(int_ids):
                    int_id = int_ids[i]
                    if int_id[0] == 'blank':
                        new_lines.append(line)
                    else:
                        # Extra blank - skip
                        removed += 1
                        problem_removed.append(f'blank at {i}')
                else:
                    # Beyond INT length - check if INT has blanks at end
                    new_lines.append(line)
            elif th_id in int_id_set:
                new_lines.append(line)
            else:
                # Extra line - skip
                removed += 1
                problem_removed.append(f'extra: {th_id[0]}={th_id[1][:40]}')
        
        # After removal check if counts match
        if len(new_lines) == int_count:
            return 'CLEANED', removed, new_lines, th_enc
        elif len(new_lines) > int_count:
            # Still too many - try to match by structure
            # Rebuild line by line trying to match INT structure
            new_lines2 = []
            int_ptr = 0
            for line in th_lines:
                if int_ptr >= int_count:
                    continue
                th_id = parse_line(line)
                int_id = int_ids[int_ptr]
                
                if th_id == int_id:
                    new_lines2.append(line)
                    int_ptr += 1
                elif th_id[0] == 'blank' and int_id[0] == 'blank':
                    new_lines2.append(line)
                    int_ptr += 1
                elif th_id[0] == int_id[0]:
                    # Same type but different key - might be OK, include it
                    new_lines2.append(line)
                    int_ptr += 1
                else:
                    # Try to find this id later in INT
                    try_idx = int_ids.index(th_id, int_ptr)
                    if try_idx >= 0:
                        # Insert blanks for missing lines
                        blanks_needed = try_idx - int_ptr
                        for _ in range(blanks_needed):
                            if len(new_lines2) < int_count:
                                new_lines2.append('')
                        new_lines2.append(line)
                        int_ptr = try_idx + 1
                    else:
                        removed += 1
            
            if len(new_lines2) == int_count:
                return 'ALIGNED', removed, new_lines2, th_enc
            elif len(new_lines2) < int_count:
                # Add blanks at end
                diff = int_count - len(new_lines2)
                for _ in range(diff):
                    new_lines2.append('')
                return 'ALIGNED_PAD', removed + diff, new_lines2, th_enc
            else:
                return 'COMPLEX', 0, new_lines2[:int_count], th_enc
        else:
            return 'SHORTENED', removed, new_lines, th_enc
    
    else:
        # TH has fewer lines - report
        return 'TH_SHORT', abs(diff), None, None

def process_all():
    results = {'ok': 0, 'cleaned': 0, 'aligned': 0, 'aligned_pad': 0, 'shortened': 0, 'complex': 0, 'struct_diff': 0, 'th_short': 0, 'fail': 0}
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
        
        result = sync_file(th_path, int_path)
        status = result[0]
        
        if status == 'OK':
            results['ok'] += 1
            details.append(f'{f}: OK')
        
        elif status == 'CLEANED':
            enc = result[3]
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['cleaned'] += 1
            results['ok'] += 1
            details.append(f'{f}: CLEANED - removed {result[1]} lines')
        
        elif status == 'ALIGNED':
            enc = result[3]
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['aligned'] += 1
            results['ok'] += 1
            details.append(f'{f}: ALIGNED - removed {result[1]} lines')
        
        elif status == 'ALIGNED_PAD':
            enc = result[3]
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['aligned_pad'] += 1
            results['ok'] += 1
            details.append(f'{f}: ALIGNED_PAD')
        
        elif status == 'SHORTENED':
            enc = result[3]
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['shortened'] += 1
            results['ok'] += 1
            details.append(f'{f}: SHORTENED')
        
        elif status == 'COMPLEX':
            enc = result[3]
            fixed = '\n'.join(result[2])
            with open(th_path, 'w', encoding=enc, newline='') as fw:
                fw.write(fixed)
            results['complex'] += 1
            results['ok'] += 1
            details.append(f'{f}: COMPLEX - written truncated')
            problems.append(f'{f}: COMPLEX - structure issues remain')
        
        elif status == 'STRUCT_DIFF':
            results['struct_diff'] += 1
            details.append(f'{f}: STRUCT_DIFF')
            problems.append(f'{f}: STRUCT_DIFF - line structure differs from INT')
        
        elif status == 'TH_SHORT':
            results['th_short'] += 1
            details.append(f'{f}: TH_SHORT - {result[1]} lines missing')
            problems.append(f'{f}: TH_SHORT - {result[1]} lines fewer than INT')
        
        else:
            results['fail'] += 1
            details.append(f'{f}: FAIL - {status}')
            problems.append(f'{f}: FAIL - {status}')
    
    total = len(int_files)
    ok_total = sum([results[k] for k in ['ok', 'cleaned', 'aligned', 'aligned_pad', 'shortened', 'complex']])
    problem_count = len(problems)
    
    with open(REPORT_PATH, 'w', encoding='utf-8') as rep:
        rep.write('SYNC FORMAT v4 RESULTS\n')
        rep.write('=' * 50 + '\n')
        rep.write(f'Total INT files: {total}\n')
        rep.write(f'OK: {results["ok"]}\n')
        rep.write(f'CLEANED (extra blanks/lines removed): {results["cleaned"]}\n')
        rep.write(f'ALIGNED: {results["aligned"]}\n')
        rep.write(f'ALIGNED_PAD: {results["aligned_pad"]}\n')
        rep.write(f'SHORTENED: {results["shortened"]}\n')
        rep.write(f'COMPLEX: {results["complex"]}\n')
        rep.write(f'STRUCT_DIFF: {results["struct_diff"]}\n')
        rep.write(f'TH_SHORT: {results["th_short"]}\n')
        rep.write(f'FAIL: {results["fail"]}\n')
        rep.write(f'\nPROBLEMS ({problem_count} files):\n')
        rep.write('-' * 50 + '\n')
        for p in problems:
            rep.write('PROBLEM: ' + p + '\n')
        rep.write('\nALL DETAILS:\n')
        rep.write('-' * 50 + '\n')
        for d in details:
            rep.write(d + '\n')
    
    print(f'Results: OK={results["ok"]}, CLEANED={results["cleaned"]}, ALIGNED={results["aligned"]}, ALIGNED_PAD={results["aligned_pad"]}')
    print(f'SHORTENED={results["shortened"]}, COMPLEX={results["complex"]}, STRUCT_DIFF={results["struct_diff"]}')
    print(f'TH_SHORT={results["th_short"]}, FAIL={results["fail"]}')
    print(f'Total: {total}, OK_total: {ok_total}, Problems: {problem_count}')
    print(f'Report: {REPORT_PATH}')

if __name__ == '__main__':
    process_all()
