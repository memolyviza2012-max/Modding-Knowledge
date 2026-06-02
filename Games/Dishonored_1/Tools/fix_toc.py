import re

toc_path = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\PCConsoleTOC.txt"
new_size = "340666"

with open(toc_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the size for DisFonts_SF.upk
pattern = r'(DisFonts_SF\.upk\s+)(\d+)(\s+)'
match = re.search(pattern, content)
if match:
    old_size = match.group(2)
    content = re.sub(pattern, r'\g<1>' + new_size + r'\g<3>', content)
    with open(toc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"TOC updated: {old_size} -> {new_size}")
else:
    print("Pattern not found in TOC")