# Fix encoding: Convert all TH files to proper UTF-16-LE
import os, glob

th_dir = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\TH'
files = glob.glob(os.path.join(th_dir, '*.int'))

fixed = []
errors = []

for f in files:
    name = os.path.basename(f)
    try:
        with open(f, 'rb') as fh:
            raw = fh.read()
        
        if len(raw) == 0:
            errors.append((name, 'empty file'))
            continue
        
        # Detect encoding
        bom = raw[:3] if len(raw) >= 3 else raw
        
        if raw[:2] == b'\xff\xfe':
            # Already UTF-16-LE, just ensure proper
            fixed.append((name, 'already UTF-16-LE', 'skipped'))
            continue
        
        # Try to find actual text encoding
        decoded = None
        src_encoding = None
        
        # Try UTF-8 with BOM
        if bom == b'\xef\xbb\xbf':
            try:
                decoded = raw[3:].decode('utf-8-sig')
                src_encoding = 'UTF-8-BOM'
            except:
                pass
        
        # Try raw UTF-8
        if decoded is None:
            try:
                decoded = raw.decode('utf-8')
                src_encoding = 'UTF-8'
            except:
                pass
        
        # Try UTF-16-BE
        if decoded is None:
            try:
                decoded = raw.decode('utf-16-be')
                src_encoding = 'UTF-16-BE'
            except:
                pass
        
        if decoded is None:
            errors.append((name, 'could not decode'))
            continue
        
        # Verify decoded text is valid (contains Thai or meaningful content)
        has_thai = any('\u0e00' <= c <= '\u0e7f' for c in decoded)
        has_english = any('a' <= c <= 'z' or 'A' <= c <= 'Z' for c in decoded)
        
        if not has_thai and not has_english:
            errors.append((name, 'no readable content'))
            continue
        
        # Write as proper UTF-16-LE with BOM
        with open(f, 'w', encoding='utf-16-le') as fh:
            fh.write(decoded)
        
        fixed.append((name, src_encoding, 'converted'))
        
    except Exception as e:
        errors.append((name, str(e)))

# Report
print(f'Fixed: {len([x for x in fixed if x[2] == "converted"])}')
print(f'Skipped: {len([x for x in fixed if x[2] == "skipped"])}')
print(f'Errors: {len(errors)}')

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\_encoding_fix_report.txt', 'w', encoding='utf-8') as out:
    out.write('=== CONVERTED ===\n')
    for name, src, action in fixed:
        if action == 'converted':
            out.write(f'  [{src}] -> UTF-16-LE: {name}\n')
    out.write('\n=== SKIPPED ===\n')
    for name, src, action in fixed:
        if action == 'skipped':
            out.write(f'  [{src}]: {name}\n')
    out.write('\n=== ERRORS ===\n')
    for name, err in errors:
        out.write(f'  [{err}]: {name}\n')

print('Report written')