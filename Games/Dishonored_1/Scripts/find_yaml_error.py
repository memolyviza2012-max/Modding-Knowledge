import yaml

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC\PCConsole\DLC06\DLC06_DaudBase_Script\DLC06_DaudBase_Script_TH.yaml'

with open(path, 'rb') as f:
    raw = f.read()

text = raw.decode('utf-8', errors='replace')
lines = text.split('\n')

msg = 'Total lines: ' + str(len(lines)) + '\n\n'

if len(lines) >= 852:
    line_852 = lines[851]
    msg += 'Line 852:\n'
    msg += '  Length: ' + str(len(line_852)) + '\n'
    
    first_colon = line_852.find(':')
    if first_colon > 0:
        value_part = line_852[first_colon+1:]
        msg += '  Key: ' + line_852[:first_colon] + '\n'
        msg += '  Value length: ' + str(len(value_part)) + '\n'
        msg += '  Value starts: ' + repr(value_part[:80]) + '\n'
        
        in_quote = False
        quote_char = None
        colon_count = 0
        for i, c in enumerate(value_part):
            if c == '"' or c == "'":
                if not in_quote:
                    in_quote = True
                    quote_char = c
                elif c == quote_char:
                    in_quote = False
                    quote_char = None
            elif c == ':' and not in_quote:
                colon_count += 1
        
        msg += '  Unquoted colons in value: ' + str(colon_count) + '\n'
    
    msg += '\nFirst 5 lines:\n'
    for i in range(min(5, len(lines))):
        msg += '  ' + str(i+1) + ': ' + repr(lines[i][:100]) + '\n'

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\line852_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(msg)

print('Done')