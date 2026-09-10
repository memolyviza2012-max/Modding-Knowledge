import yaml

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml'
with open(path, 'rb') as f:
    raw = f.read()
text = raw.decode('utf-8', errors='replace')
lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

with open('dlc07_check.txt', 'w', encoding='utf-8') as f:
    f.write('Lines: ' + str(len(lines)) + '\n')
    f.write('Line 1: ' + repr(lines[0][:80]) + '\n')
    f.write('Line 2: ' + repr(lines[1][:80]) + '\n')
    f.write('Line 3: ' + repr(lines[2][:80]) + '\n')
    try:
        yaml.safe_load(text)
        f.write('YAML: Valid\n')
    except yaml.YAMLError as e:
        f.write('YAML: ERROR - ' + str(e)[:200] + '\n')