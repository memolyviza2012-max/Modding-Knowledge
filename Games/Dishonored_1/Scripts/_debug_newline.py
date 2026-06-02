import sys; sys.stdout.reconfigure(encoding='utf-8')
src = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Localization\INT\DishonoredGame.int'
target = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame.int'

for path, name in [(src, 'SOURCE'), (target, 'TARGET')]:
    with open(path, 'rb') as f:
        raw = f.read(500)

    crlf = 0
    lf_only = 0
    cr_only = 0
    for i in range(len(raw) - 3):
        if raw[i] == 0x0d and raw[i+2] == 0x0a:
            crlf += 1
    for i in range(len(raw) - 1):
        if raw[i] == 0x0a and raw[i+1] == 0x00:
            lf_only += 1
        if raw[i] == 0x0d and raw[i+1] != 0x0a:
            cr_only += 1

    print(name + ': CRLF=' + str(crlf) + ' LF_only=' + str(lf_only) + ' CR_only=' + str(cr_only))
