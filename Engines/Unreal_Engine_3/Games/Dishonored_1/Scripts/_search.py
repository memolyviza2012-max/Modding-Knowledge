import sys; sys.stdout.reconfigure(encoding='utf-8')
import glob, os

search = 'ระบุตัวตน'
base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT'

results = []
for path in glob.glob(base + '\\*.int'):
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                content = f.read()
            if search in content:
                lines = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
                for i, l in enumerate(lines):
                    if search in l:
                        results.append((os.path.basename(path), i+1, l[:120]))
            break
        except:
            continue

if results:
    for fname, line, content in results:
        print(fname + ':' + str(line))
        print('  ' + content[:120])
        print()
else:
    print('ไม่พบคำว่า ระบุตัวตน ในไฟล์ใดๆ')
