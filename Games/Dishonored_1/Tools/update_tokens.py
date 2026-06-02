with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored_translator.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"max_tokens": 500', '"max_tokens": 2048')

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored_translator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Updated max_tokens to 2048')
