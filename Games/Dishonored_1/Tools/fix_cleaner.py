import re

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored_translator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the function
start = content.find('def clean_llm_output')
end = content.find('\ndef ', start + 1)
func_text = content[start:end]

with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\debug\old_func.txt', 'w', encoding='utf-8') as f:
    f.write(f"Start: {start}, End: {end}\n\n")
    f.write(func_text)

# Check if there's a newline in the problematic regex
if '\n' in func_text:
    with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\debug\old_func_hex.txt', 'w', encoding='utf-8') as f:
        f.write(f"Length: {len(func_text)}\n\n")
        for i, c in enumerate(func_text):
            if ord(c) > 127 or c == '\n' or c == '\\':
                f.write(f"Pos {i}: ord={ord(c)}, char={repr(c)}\n")
