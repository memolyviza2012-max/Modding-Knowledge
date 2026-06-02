#!/usr/bin/env python3
"""
Fix missing DisConv entries in YAML by reading directly from _DYextracted binary files.
DisConv_Blurb.6946 and similar entries have text in a non-standard field that gets skipped.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, '.')

def parse_disconv_binary(subFile, dNames):
    """Parse DisConv binary file and extract all text fields."""
    from binary import BinaryStream
    from upkElements import UpkElements
    
    with open(subFile, 'r+b') as f:
        reader = BinaryStream(f)
        reader.seek(0)
        e = UpkElements(dNames, reader)
        return e.elements

def extract_text_from_elements(elements):
    """Extract text from various possible fields in DisConv element."""
    fields_to_try = [
        'm_Text',           # standard text field
        'm_Choices_Static',  # player choice text
        'm_SubtitleText',   # subtitle variant
        'm_MultiChoiceText', # multi-choice variant
        'Text',             # generic
        'subtitle',          # lowercase variant
        'choice',           # choice variant
    ]
    
    text = None
    is_choices = False
    
    # Check standard fields first
    if 'm_Choices_Static' in elements:
        text = elements['m_Choices_Static']['value']
        is_choices = True
    elif 'm_Text' in elements:
        text = elements['m_Text']['value']
    
    # If still nothing, try to find any field that looks like text
    if text is None:
        for key in elements.keys():
            if 'text' in key.lower() or 'choice' in key.lower():
                val = elements[key]
                if isinstance(val, dict) and 'value' in val:
                    text = val['value']
                    if 'choice' in key.lower():
                        is_choices = True
                    break
    
    return text, is_choices

def fix_missing_entries(upkName, yamlPath):
    """Find missing DisConv entries and add them to YAML."""
    from upkElements import UpkElements
    from unpack import unpack
    from binary import BinaryStream
    import yaml
    
    print(f"Fixing missing entries for {upkName}")
    
    # Read existing YAML
    if os.path.isfile(yamlPath):
        with open(yamlPath, 'r', encoding='utf8') as f:
            od = yaml.safe_load(f) or {}
    else:
        print(f"YAML file {yamlPath} not found, creating new")
        od = {}
    
    # Get existing entry IDs
    existing_ids = set()
    for key in od.keys():
        if key.startswith('DisConv_'):
            parts = key.split('.')
            if len(parts) >= 3:
                try:
                    existing_ids.add(int(parts[1]))
                except:
                    pass
    
    print(f"Existing entries in YAML: {len(existing_ids)}")
    
    # Unpack to get dNames (needed for parsing)
    rr = unpack(Path(yamlPath).parent / f"{upkName}.upk", "DisConv_", True, True)
    
    # Find DisConv files in _DYextracted that might be missing
    extDir = Path(f"_DYextracted/{upkName}")
    if not extDir.exists():
        print(f"_DYextracted/{upkName} not found")
        return
    
    # Get all DisConv_Blurb files
    all_blurb_files = list(extDir.glob('DisConv_Blurb.*.DisConv_Blurb'))
    print(f"Total DisConv_Blurb files: {len(all_blurb_files)}")
    
    # Find missing entries
    all_ids = set()
    for f in all_blurb_files:
        parts = f.name.split('.')
        try:
            all_ids.add(int(parts[1]))
        except:
            pass
    
    missing_ids = all_ids - existing_ids
    print(f"Missing entries: {len(missing_ids)}")
    print(f"Missing IDs (sample): {sorted(list(missing_ids))[:20]}")
    
    # Process missing files
    added = 0
    for subFile in all_blurb_files:
        parts = subFile.name.split('.')
        try:
            entry_id = int(parts[1])
        except:
            continue
        
        if entry_id not in missing_ids:
            continue
        
        # Try to extract text
        try:
            elements = parse_disconv_binary(subFile, rr['dNames'])
        except Exception as e:
            print(f"Error parsing {subFile.name}: {e}")
            continue
        
        text, is_choices = extract_text_from_elements(elements)
        
        if text is None:
            # Last resort: search raw binary for readable text
            with open(subFile, 'rb') as f:
                raw = f.read()
            
            strings = []
            current = b''
            for b in raw:
                if 32 <= b <= 126:
                    current += bytes([b])
                else:
                    if len(current) > 10:
                        try:
                            s = current.decode('ascii')
                            if any(c.isalpha() for c in s):
                                strings.append(s)
                        except:
                            pass
                    current = b''
            
            # Filter to likely dialogue strings
            dialogue_strings = [s for s in strings if len(s) > 15 and not s.startswith('!')]
            if dialogue_strings:
                # Use the longest string as the text
                text = max(dialogue_strings, key=len)
                print(f"  {subFile.name}: extracted via raw binary: '{text[:50]}...'")
            else:
                print(f"  {subFile.name}: NO TEXT FOUND")
                continue
        
        # Format text for YAML
        if is_choices:
            # Player choices - format as list
            if isinstance(text, list):
                formatted = text
            else:
                formatted = [text]
            od[subFile.name] = formatted
        else:
            if isinstance(text, list) and len(text) == 1:
                od[subFile.name] = text[0]
            elif isinstance(text, list):
                od[subFile.name] = text
            else:
                od[subFile.name] = text
        
        added += 1
        if added <= 10:
            print(f"  Added {subFile.name}: '{str(text)[:60]}'")
    
    print(f"\nTotal entries added: {added}")
    
    # Sort the YAML by entry ID
    def sort_key(key):
        if key.startswith('DisConv_'):
            parts = key.split('.')
            try:
                return (0, int(parts[1]))
            except:
                return (1, key)
        return (2, key)
    
    od_sorted = {k: od[k] for k in sorted(od.keys(), key=sort_key)}
    
    # Write back
    with open(yamlPath, 'w', encoding='utf8') as f:
        yaml.dump(od_sorted, f, allow_unicode=True, width=4096)
    
    print(f"Updated YAML written to: {yamlPath}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_missing_entries.py <upk_name> <yaml_path>")
        print("Example: python fix_missing_entries.py L_Tower_Script ../03_working/CookedPCConsole/L_Tower_Script/L_Tower_Script_INT.yaml")
        sys.exit(1)
    
    upkName = sys.argv[1]
    yamlPath = sys.argv[2]
    
    os.chdir(Path(sys.argv[0]).parent)
    fix_missing_entries(upkName, yamlPath)
