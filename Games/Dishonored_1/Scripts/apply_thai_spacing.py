# apply_thai_spacing.py
# Apply Thai word tokenization (per-word spacing) to Thai lines in .int file
# This makes UE2/UE3 render Thai text correctly (without spaces, words join together)
import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

INPUT = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame.int"
OUTPUT = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT\DishonoredGame_TH.int"

RE_THAI = re.compile(r'[\u0e00-\u0e7f]')
RE_ENG = re.compile(r'[a-zA-Z]')

def add_thai_spacing(text):
    """Add spaces between distinct Thai phrases for UE compatibility."""
    from pythainlp import word_tokenize
    tokenized = ' '.join(word_tokenize(text, engine='newmm'))
    # Clean up double spaces
    while '  ' in tokenized:
        tokenized = tokenized.replace('  ', ' ')
    return tokenized

def process_file(input_path, output_path):
    # Detect encoding
    for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
        try:
            with open(input_path, 'r', encoding=enc) as f:
                content = f.read()
            detected_enc = enc
            print(f"Detected encoding: {enc}")
            break
        except:
            continue

    lines = content.split('\n')
    modified = 0
    new_lines = []

    for line in lines:
        # Check if line has Thai text
        if not RE_THAI.search(line):
            new_lines.append(line)
            continue

        # Check if it's a key=value or key:value line
        # Pattern: key=value or key:value
        # For int files: m_MissionNames[0]=text or m_MissionNames[0]: text
        eq_idx = line.find('=')
        colon_idx = line.find(':')
        
        if eq_idx > 0 and (colon_idx == -1 or colon_idx > eq_idx):
            # key=value format
            key = line[:eq_idx]
            value = line[eq_idx+1:]
            if RE_THAI.search(value):
                value_spaced = add_thai_spacing(value.strip())
                new_lines.append(key + '=' + value_spaced)
                modified += 1
            else:
                new_lines.append(line)
        elif colon_idx > 0:
            # key:value format
            key = line[:colon_idx]
            value = line[colon_idx+1:]
            if RE_THAI.search(value):
                value_spaced = add_thai_spacing(value.strip())
                new_lines.append(key + ': ' + value_spaced)
                modified += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    print(f"Modified {modified} lines out of {len(lines)} total")

    # Write in same encoding
    output_content = '\n'.join(new_lines)
    with open(output_path, 'w', encoding=detected_enc) as f:
        f.write(output_content)

    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    process_file(INPUT, OUTPUT)
