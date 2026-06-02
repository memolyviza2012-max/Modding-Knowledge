import os, shutil, subprocess, yaml

MANUAL_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual"
TOOL_SUBEDIT = r"D:\Mod_Workspace\Tool\UE3\dishonored-toolkit-main\subedit.py"

upk_name = "Startup.upk"
src_path = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\CookedPCConsole\unpacked"
work_folder = "CookedPCConsole"
base_name = upk_name[:-4]
work_dir = os.path.join(MANUAL_DIR, work_folder, base_name)
os.makedirs(work_dir, exist_ok=True)

upk_path = os.path.join(src_path, upk_name)
yaml_path = os.path.join(work_dir, base_name + ".yaml")
int_file = os.path.join(work_dir, base_name + "._INT")
th_file = os.path.join(work_dir, base_name + "._TH")

print("UPK:", upk_path)
print("Output YAML:", yaml_path)

cmd = 'python "' + TOOL_SUBEDIT + '" --output "' + yaml_path + '" --langCode INT "' + upk_path + '"'
print("CMD:", cmd)
print("CWD:", work_dir)

result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=work_dir)
print("Return code:", result.returncode)
print("STDOUT:", result.stdout[:200] if result.stdout else "(empty)")
print("STDERR:", result.stderr[:200] if result.stderr else "(empty)")

print()
print("YAML exists after run:", os.path.exists(yaml_path))