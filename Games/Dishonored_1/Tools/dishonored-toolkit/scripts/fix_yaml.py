#!/usr/bin/env python3
"""
Extract missing DisConv entries by searching for readable ASCII strings in raw binary.
DisConv_Blurb.6946 and similar entries have text stored in non-standard fields.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, '.')

def extract_readable_strings(data, min_len=10):
    """Extract readable ASCII strings from binary data."""
    strings = []
    current = b''
    for b in data:
        if 32 <= b <= 126:
            current += bytes([b])
        else:
            if len(current) >= min_len:
                strings.append(current.decode('ascii'))
            current = b''
    if len(current) >= min_len:
        strings.append(current.decode('ascii'))
    return strings

def find_dialogue_string(strings):
    """Find the most likely dialogue string from a list."""
    # Filter: ignore strings that are mostly uppercase (likely names/headers)
    # and strings that look like code or metadata
    candidates = []
    for s in strings:
        s = s.strip()
        if len(s) < 15:
            continue
        # Skip if mostly uppercase abbreviations
        upper_ratio = sum(1 for c in s if c.isupper()) / len(s)
        if upper_ratio > 0.6 and len(s) < 20:
            continue
        # Skip if contains many numbers (likely metadata)
        digit_ratio = sum(1 for c in s if c.isdigit()) / len(s)
        if digit_ratio > 0.3:
            continue
        # Prefer strings with lowercase letters (likely natural language)
        lower_ratio = sum(1 for c in s if c.islower()) / len(s)
        if lower_ratio < 0.2:
            continue
        candidates.append(s)
    
    if candidates:
        # Return longest candidate
        return max(candidates, key=len)
    return None

def process_disconv_file(filepath):
    """Process a single DisConv binary file and extract dialogue text."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    strings = extract_readable_strings(data)
    dialogue = find_dialogue_string(strings)
    return dialogue

def rebuild_yaml(upkName, yamlPath):
    """Rebuild YAML with all entries including missing ones."""
    import yaml
    
    # Read existing YAML if it exists
    if os.path.isfile(yamlPath):
        with open(yamlPath, 'r', encoding='utf8') as f:
            existing = yaml.safe_load(f) or {}
    else:
        existing = {}
    
    print(f"Existing entries: {len(existing)}")
    
    # Get all DisConv files from _DYextracted
    extDir = Path(f"_DYextracted/{upkName}")
    if not extDir.exists():
        print(f"_DYextracted/{upkName} not found!")
        return
    
    all_files = list(extDir.glob('DisConv_Blurb.*.DisConv_Blurb'))
    all_files.extend(list(extDir.glob('DisConv_PlayerChoice.*.DisConv_PlayerChoice')))
    all_files.extend(list(extDir.glob('DisConv_NonWord.*.DisConv_NonWord')))
    print(f"Total DisConv files found: {len(all_files)}")
    
    # Get IDs of existing entries
    existing_ids = set()
    for key in existing.keys():
        parts = key.split('.')
        if len(parts) >= 3:
            try:
                existing_ids.add(int(parts[1]))
            except:
                pass
    
    # Process each file
    missing = 0
    updated = 0
    
    for filepath in sorted(all_files):
        parts = filepath.name.split('.')
        try:
            entry_id = int(parts[1])
        except:
            continue
        
        # Try to get text from existing YAML first
        entry_name = filepath.name
        if entry_name in existing:
            continue  # Already has text
        
        # Try to extract from binary
        text = process_disconv_file(filepath)
        if text:
            existing[entry_name] = text
            updated += 1
            if entry_id == 6946:
                print(f"  [6946 RECOVERED] DisConv_Blurb.6946: '{text[:60]}...'")
        else:
            missing += 1
            if entry_id == 6946:
                print(f"  [6946 STILL MISSING]")
    
    print(f"New entries added: {updated}, Still missing: {missing}")
    
    # Sort by entry type and ID
    def sort_key(key):
        parts = key.split('.')
        try:
            entry_type = parts[0]
            entry_id = int(parts[1])
            type_order = 0 if 'Blurb' in entry_type else 1 if 'Player' in entry_type else 2
            return (type_order, entry_id)
        except:
            return (3, key)
    
    od_sorted = {k: existing[k] for k in sorted(existing.keys(), key=sort_key)}
    
    # Write back
    with open(yamlPath, 'w', encoding='utf8') as f:
        yaml.dump(od_sorted, f, allow_unicode=True, width=4096)
    
    print(f"YAML written to: {yamlPath} ({len(od_sorted)} total entries)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_yaml.py <upk_name> <yaml_path>")
        sys.exit(1)
    
    upkName = sys.argv[1]
    yamlPath = sys.argv[2]
    
    os.chdir(Path(sys.argv[0]).parent)
    rebuild_yaml(upkName, yamlPath)
