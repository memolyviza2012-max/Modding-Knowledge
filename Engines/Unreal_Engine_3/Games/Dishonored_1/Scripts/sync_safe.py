# sync_safe.py (V2)
import os, re, shutil

INT_DIR     = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
TH_DIR      = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
REPORT_PATH = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\sync_safe_report.txt'

def decode_file(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if not raw:
        return '', 'utf-16-le'
    if raw[:2] == b'\xff\xfe':
        return raw.decode('utf-16-le', errors='replace'), 'utf-16-le'
    if raw[:2] == b'\xfe\xff':
        return raw.decode('utf-16-be', errors='replace'), 'utf-16-be'
    if raw[:3] == b'\xef\xbb\xbf':
        return raw.decode('utf-8-sig', errors='replace'), 'utf-8-sig'
    try:
        return raw.decode('utf-8', errors='replace'), 'utf-8'
    except Exception:
        return raw.decode('utf-8', errors='replace'), 'utf-8'

def get_line_type(line):
    s = line.strip()
    if not s:
        return 'blank'
    if s.startswith('[') and ']' in s:
        return 'section'
    if s.startswith(';'):
        return 'comment'
    if '=' in s:
        return 'property'
    return 'other'

def parse_lines(path):
    text, enc = decode_file(path)
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return [l.rstrip() for l in lines], enc

def extract_th_content(th_lines):
    th_map = {}
    current_section = None
    for line in th_lines:
        lt = get_line_type(line)
        if lt == 'section':
            m = re.match(r'\[([^\]]+)', line.strip())
            if m:
                current_section = m.group(1)
                th_map.setdefault(current_section, {})
        elif lt == 'property' and current_section and '=' in line:
            key = line.split('=', 1)[0].strip()
            val = line.split('=', 1)[1]
            th_map[current_section][key] = val
    return th_map

def build_th_from_int(int_lines, th_content):
    new_lines = []
    current_section = None
    for line in int_lines:
        lt = get_line_type(line)
        if lt == 'blank':
            new_lines.append('')
        elif lt == 'section':
            new_lines.append(line)
            m = re.match(r'\[([^\]]+)', line.strip())
            if m:
                current_section = m.group(1)
        elif lt == 'comment':
            new_lines.append(line)
        elif lt == 'property' and current_section and '=' in line:
            key = line.split('=', 1)[0].strip()
            if current_section in th_content and key in th_content[current_section]:
                new_lines.append(f"{key}={th_content[current_section][key]}")
            else:
                new_lines.append(line)  # fallback: คง INT ไว้
        else:
            new_lines.append(line)
    return new_lines

def write_file(path, lines, encoding):
    text = '\n'.join(lines)
    # utf-16 (ไม่ใช่ utf-16-le) เพื่อให้ Python เขียน BOM อัตโนมัติ
    enc_write = 'utf-16' if encoding in ('utf-16-le', 'utf-16-be') else encoding
    with open(path, 'w', encoding=enc_write, newline='\n') as f:
        f.write(text)

def process_file(fname):
    int_path = os.path.join(INT_DIR, fname)
    th_path  = os.path.join(TH_DIR, fname)

    int_lines, int_enc = parse_lines(int_path)
    int_count = len(int_lines)

    # ตรวจสอบ TH
    if not os.path.exists(th_path) or os.path.getsize(th_path) == 0:
        return {'status': 'CORRUPT', 'enc': int_enc, 'int_lines': int_lines}

    th_lines, _ = parse_lines(th_path)
    if len(th_lines) <= 1 and int_count > 1:
        return {'status': 'CORRUPT', 'enc': int_enc, 'int_lines': int_lines}

    try:
        th_content = extract_th_content(th_lines)
    except Exception as e:
        return {'status': 'PARSE_ERROR', 'enc': int_enc, 'error': str(e)}

    new_th_lines = build_th_from_int(int_lines, th_content)
    new_count    = len(new_th_lines)

    base = {'enc': int_enc, 'lines': new_th_lines, 'int_count': int_count, 'new_count': new_count}

    if new_count == int_count:
        return {**base, 'status': 'OK'}
    else:
        return {**base, 'status': 'LINE_MISMATCH'}

def process_all():
    results = {'ok': 0, 'corrupt': 0, 'parse_error': 0, 'line_mismatch': 0, 'fail': 0}
    details        = []
    corrupt_files  = []
    mismatch_files = []

    int_files = sorted(f for f in os.listdir(INT_DIR) if f.endswith('.int'))

    for fname in int_files:
        th_path = os.path.join(TH_DIR, fname)
        r = process_file(fname)
        status = r['status']

        if status == 'OK':
            write_file(th_path, r['lines'], r['enc'])
            results['ok'] += 1
            details.append(f"{fname}: OK ({r['new_count']} lines)")

        elif status == 'CORRUPT':
            results['corrupt'] += 1
            details.append(f"{fname}: CORRUPT — needs fresh translation")
            corrupt_files.append(fname)

        elif status == 'PARSE_ERROR':
            results['parse_error'] += 1
            details.append(f"{fname}: PARSE_ERROR — {r.get('error','')}")
            corrupt_files.append(fname)

        elif status == 'LINE_MISMATCH':
            # Backup ก่อนเขียนทับ — TH มี Thai content อยู่
            if os.path.exists(th_path):
                bak = th_path + '.bak'
                if not os.path.exists(bak):
                    shutil.copy2(th_path, bak)
            write_file(th_path, r['lines'], r['enc'])
            results['line_mismatch'] += 1
            details.append(f"{fname}: LINE_MISMATCH — INT={r['int_count']} TH={r['new_count']}")
            mismatch_files.append((fname, r['int_count'], r['new_count']))

        else:
            results['fail'] += 1
            details.append(f"{fname}: FAIL")

    # เขียน report
    with open(REPORT_PATH, 'w', encoding='utf-8') as rep:
        rep.write('SYNC SAFE RESULTS\n' + '=' * 50 + '\n')
        rep.write(f"Total INT files   : {len(int_files)}\n")
        rep.write(f"OK (synced)       : {results['ok']}\n")
        rep.write(f"CORRUPT           : {results['corrupt']}\n")
        rep.write(f"PARSE_ERROR       : {results['parse_error']}\n")
        rep.write(f"LINE_MISMATCH     : {results['line_mismatch']}\n")
        rep.write(f"FAIL              : {results['fail']}\n")
        rep.write(f"\nCORRUPT FILES ({len(corrupt_files)}):\n" + '-' * 50 + '\n')
        for f in corrupt_files:
            rep.write(f"  {f}\n")
        if mismatch_files:
            rep.write(f"\nLINE_MISMATCH FILES:\n" + '-' * 50 + '\n')
            for f, ic, tc in mismatch_files:
                rep.write(f"  {f}: INT={ic} TH={tc}\n")
        rep.write(f"\nALL DETAILS:\n" + '-' * 50 + '\n')
        for d in details:
            rep.write(d + '\n')

    print(f"OK={results['ok']} | CORRUPT={results['corrupt']} | "
          f"PARSE_ERR={results['parse_error']} | MISMATCH={results['line_mismatch']}")
    print(f"Total: {len(int_files)} files | Report: {REPORT_PATH}")
    return results, corrupt_files, mismatch_files

if __name__ == '__main__':
    process_all()