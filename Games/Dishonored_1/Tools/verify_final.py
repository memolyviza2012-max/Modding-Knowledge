import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Twk_UI_MainMenu.int', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print('Total lines:', len(lines))
for l in lines:
    if '=' in l and not l.startswith('['):
        print(l.rstrip())
