import os, shutil, subprocess, yaml

SOURCE_DIR = 'D:\\Mod_Workspace\\Dishonored_Mod_Workspace\\01_source'
MANUAL_DIR = 'D:\\Mod_Workspace\\Dishonored_Mod_Workspace\\03_working_manual'
TOOL_SUBEDIT = 'D:\\Mod_Workspace\\Tool\\UE3\\dishonored-toolkit-main\\subedit.py'

FOLDER_MAP = [
    ('CookedPCConsole\\unpacked', 'CookedPCConsole'),
    ('DLC\\PCConsole\\DLC05\\unpacked', 'DLC\\DLC05'),
    ('DLC\\PCConsole\\DLC06\\unpacked', 'DLC\\DLC06'),
    ('DLC\\PCConsole\\DLC07\\unpacked', 'DLC\\DLC07'),
]

def run_cmd(cmd, cwd=None):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)
    return path

def process_upk(upk_name, src_unpacked, work_folder):
    base_name = upk_name[:-4]
    upk_path = src_unpacked + '\\' + upk_name
    work_dir = ensure_dir(MANUAL_DIR + '\\' + work_folder + '\\' + base_name)
    int_file = work_dir + '\\' + base_name + '._INT'
    th_file = work_dir + '\\' + base_name + '._TH'
    if os.path.exists(int_file) and os.path.exists(th_file):
        return 'skip', 0
    yaml_path = work_dir + '\\' + base_name + '.yaml'
    if not os.path.exists(yaml_path):
        ensure_dir(work_dir)
        cmd = 'python "' + TOOL_SUBEDIT + '" --output "' + yaml_path + '" --langCode INT "' + upk_path + '"'
        run_cmd(cmd, cwd=work_dir)
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            print(f"      [WARN] YAML parse error: {e}")
            return 'fail', 0
        if data:
            lines = []
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        lines.append(key + ': ' + item)
                else:
                    lines.append(key + ': ' + value)
            with open(int_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            shutil.copy(int_file, th_file)
            return 'ok', len(lines)
    return 'fail', 0

total = 0
for src_sub, _ in FOLDER_MAP:
    path = SOURCE_DIR + '\\' + src_sub
    if os.path.exists(path):
        total += len([f for f in os.listdir(path) if f.endswith('.upk')])
print('Total UPKs:', total)

for src_sub, work_folder in FOLDER_MAP:
    src_path = SOURCE_DIR + '\\' + src_sub
    if not os.path.exists(src_path):
        continue
    upk_files = [f for f in os.listdir(src_path) if f.endswith('.upk')]
    print('Processing', len(upk_files), 'UPKs from', src_sub + '...')
    ok = sk = fa = 0
    for idx, upk_name in enumerate(upk_files, 1):
        res, lines = process_upk(upk_name, src_path, work_folder)
        if res == 'ok': ok += 1; print(f'[{idx}/{len(upk_files)}] OK - {upk_name} ({lines} lines)')
        elif res == 'skip': sk += 1; print(f'[{idx}/{len(upk_files)}] SKIP - {upk_name}')
        else: fa += 1; print(f'[{idx}/{len(upk_files)}] FAIL - {upk_name}')
    print(f'Result: {ok} ok, {sk} skipped, {fa} failed')
print('ALL DONE')