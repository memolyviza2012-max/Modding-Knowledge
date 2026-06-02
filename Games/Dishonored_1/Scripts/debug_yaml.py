import yaml, re

files = [
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml', 'DLC06_DaudBase_Script'),
    (r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC07\DLC07_Twk_Inv_Seekfree_SF\DLC07_Twk_Inv_Seekfree_SF_TH.yaml', 'DLC07_Twk_Inv_Seekfree_SF'),
]

for path, name in files:
    with open(path, 'rb') as f:
        raw = f.read()
    
    # Try UTF-8 first, then UTF-16
    for enc in ['utf-8', 'utf-16-le', 'utf-16-be', 'utf-8-sig']:
        try:
            text = raw.decode(enc)
            break
        except:
            continue
    
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    
    with open(name + '_debug.txt', 'w', encoding='utf-8') as f:
        f.write(name + '\n')
        f.write('Encoding detected: ' + enc + '\n')
        f.write('Total lines: ' + str(len(lines)) + '\n')
        
        try:
            yaml.safe_load(text)
            f.write('YAML: VALID\n')
        except yaml.YAMLError as e:
            err_str = str(e)
            f.write('YAML: INVALID\n')
            f.write('Error: ' + err_str[:300] + '\n')
            
            m = re.search(r'line (\d+)', err_str)
            if m:
                line_num = int(m.group(1))
                f.write('Error at line: ' + str(line_num) + '\n')
                if line_num <= len(lines):
                    problem_line = lines[line_num-1]
                    f.write('Problem line (first 300 chars):\n')
                    f.write(problem_line[:300] + '\n')
                    # Count colons
                    colon_count = problem_line.count(':')
                    f.write('Colon count: ' + str(colon_count) + '\n')
                    # Find the second colon (after key:value pattern)
                    first_colon = problem_line.find(':')
                    if first_colon > 0:
                        second_colon = problem_line.find(':', first_colon + 1)
                        if second_colon > 0:
                            f.write('Second colon at position: ' + str(second_colon) + '\n')
                            f.write('Content around second colon:\n')
                            start = max(0, second_colon - 20)
                            f.write(problem_line[start:second_colon+50] + '\n')

print('Done - check *_debug.txt files')