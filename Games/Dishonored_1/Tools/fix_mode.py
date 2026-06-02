with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored_translator.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_text = 'process_int_file(input_file, output_file, dry_run=True)\n\n        # REAL MODE\n        print("\\n[REAL MODE - Writing file]")\n        process_int_file(input_file, output_file, dry_run=False)'

new_text = '        process_int_file(input_file, output_file, dry_run=False)'

if old_text in content:
    content = content.replace(old_text, new_text)
    print('Replaced dry-run with real mode only')
else:
    print('Pattern not found')
    # Try to find what's actually there
    idx = content.find('dry_run=True')
    if idx != -1:
        print(f'Found dry_run=True at {idx}')
        print(repr(content[idx:idx+300]))

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored_translator.py', 'w', encoding='utf-8') as f:
    f.write(content)
