import os

def validate_folder(folder):
    results = []
    int_files = []
    
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith('_INT.yaml'):
                int_files.append(os.path.join(root, f))
    
    for int_path in int_files:
        base = os.path.basename(int_path).replace('_INT.yaml','')
        dir_path = os.path.dirname(int_path)
        th_path = os.path.join(dir_path, base + '_TH.yaml')
        
        if not os.path.exists(th_path):
            results.append({'base': base, 'status': 'NO_TH', 'int_lines': 0, 'th_lines': 0, 'missing': 0, 'missing_ids': set()})
            continue
            
        with open(int_path, 'r', encoding='utf-8', errors='replace') as f:
            int_lines = f.read().split('\n')
        with open(th_path, 'r', encoding='utf-8', errors='replace') as f:
            th_lines = f.read().split('\n')
        
        int_count = len(int_lines)
        th_count = len(th_lines)
        diff = int_count - th_count
        
        int_ids = set()
        for line in int_lines:
            if ':' in line:
                int_ids.add(line.split(':')[0])
        th_ids = set()
        for line in th_lines:
            if ':' in line:
                th_ids.add(line.split(':')[0])
        
        missing_ids = int_ids - th_ids
        
        if diff == 0:
            status = 'OK'
        else:
            status = 'LINE_MISMATCH'
        
        results.append({
            'base': base,
            'status': status,
            'int_lines': int_count,
            'th_lines': th_count,
            'missing': diff,
            'missing_ids': missing_ids
        })
    
    return results

print('=== CookedPCConsole ===')
ccc = validate_folder(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole')
ok_c = sum(1 for r in ccc if r['status'] == 'OK')
no_th_c = sum(1 for r in ccc if r['status'] == 'NO_TH')
mismatch_c = sum(1 for r in ccc if r['status'] == 'LINE_MISMATCH')
print(f'Total: {len(ccc)} | OK: {ok_c} | NO_TH: {no_th_c} | LINE_MISMATCH: {mismatch_c}')

mm_c = [r for r in ccc if r['status'] == 'LINE_MISMATCH']
if mm_c:
    print()
    print('--- CookedPCConsole MISMATCH Details ---')
    for r in mm_c:
        print(f'  {r["base"]}: INT={r["int_lines"]} TH={r["th_lines"]} diff={r["missing"]} missingIDs={len(r["missing_ids"])}')

print()
print('=== DLC ===')
dlc = validate_folder(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC')
ok_d = sum(1 for r in dlc if r['status'] == 'OK')
no_th_d = sum(1 for r in dlc if r['status'] == 'NO_TH')
mismatch_d = sum(1 for r in dlc if r['status'] == 'LINE_MISMATCH')
print(f'Total: {len(dlc)} | OK: {ok_d} | NO_TH: {no_th_d} | LINE_MISMATCH: {mismatch_d}')

mm_d = [r for r in dlc if r['status'] == 'LINE_MISMATCH']
if mm_d:
    print()
    print('--- DLC MISMATCH Details ---')
    for r in mm_d:
        print(f'  {r["base"]}: INT={r["int_lines"]} TH={r["th_lines"]} diff={r["missing"]} missingIDs={len(r["missing_ids"])}')