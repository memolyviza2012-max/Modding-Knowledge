# merge_partial.py
# Merge TH files - keep existing Thai, add missing lines, remove extra lines
import os
import re
import time
import yaml

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = 'AIzaSyCyW-M_-dyfOEeDevVpZLQnIFfD99efyOw'

PARTIAL_FILES = [
    'AudioGraph_Twk.int',
    'Blueprints_twk_Abst.int',
    'Boyle_AbstractInv_Assets.int',
    'Boyle_AbstractInv_MS.int',
    'Boyle_Objectives.int',
    'Boyle_Twk.int',
    'Bridge_Abstract.int',
    'Bridge_Objectives.int',
    'Bridge_Twk.int',
    'Brothel_Objectives.int',
]

def detect_encoding(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] in [b'\xff\xfe', b'\xfe\xff']:
        return 'utf-16-le' if raw[:2] == b'\xff\xfe' else 'utf-16-be'
    if raw.startswith(b'\xef\xbb\xbf'):
        return 'utf-8-sig'
    try:
        raw.decode('utf-8')
        return 'utf-8'
    except:
        return 'cp1252'

def read_lines(path):
    enc = detect_encoding(path)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode(enc, errors='replace')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text, enc

def extract_id(line):
    if ':' not in line:
        return None
    return line.split(':')[0].strip()

def get_value(line):
    if ':' not in line:
        return ''
    parts = line.split(':', 1)
    return parts[1].strip() if len(parts) > 1 else ''

def translate_missing(missing_lines, api_key):
    """Translate missing lines using Gemini API"""
    if not missing_lines:
        return {}
    
    # Build prompt for batch translation
    examples = [
        ("DisConv_Blurb.1000", "This is a test line.", "นี่คือบรรทัดทดสอบ"),
    ]
    
    prompt = "Translate these English lines to Thai. Keep IDs unchanged. Output format: 'ID: Thai translation'\n\n"
    prompt += "Rules:\n"
    prompt += "1. Match dark, gritty tone of Dishonored\n"
    prompt += "2. Use THAI SPACING between words (use PyThaiNLP word_tokenize style)\n"
    prompt += "3. Preserve SOUND EFFECTS in '* ... *' format\n"
    prompt += "4. Keep character names from glossary\n"
    prompt += "\n"
    
    for line_id, eng in missing_lines:
        prompt += f"{line_id}: {eng}\n"
    
    # Call Gemini API
    import urllib.request
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2000
        },
        "safetySettings": [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
        ]
    }
    
    import json
    body = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            translations = {}
            for l in text.split('\n'):
                if ':' in l:
                    parts = l.split(':', 1)
                    tid = parts[0].strip()
                    val = parts[1].strip() if len(parts) > 1 else ''
                    translations[tid] = val
            return translations
    except Exception as e:
        print(f'API error: {e}')
        return {}

def process_file(filename):
    print(f'\n=== Processing {filename} ===')
    
    th_path = os.path.join(TH_DIR, filename)
    int_path = os.path.join(INT_DIR, filename)
    
    if not os.path.exists(th_path):
        print(f'TH not found: {th_path}')
        return 'FAIL'
    
    if not os.path.exists(int_path):
        print(f'INT not found: {int_path}')
        return 'FAIL'
    
    # Read both files
    int_text, int_enc = read_lines(int_path)
    th_text, th_enc = read_lines(th_path)
    
    int_lines = int_text.split('\n')
    th_lines = th_text.split('\n')
    
    print(f'INT lines: {len(int_lines)}, TH lines: {len(th_lines)}')
    
    # Build ID maps
    int_ids = []
    for line in int_lines:
        if line.strip():
            int_ids.append(extract_id(line))
    
    th_ids = []
    th_content = {}
    for line in th_lines:
        if line.strip():
            tid = extract_id(line)
            th_ids.append(tid)
            th_content[tid] = line
    
    # Find missing and extra
    int_id_set = set(int_ids)
    th_id_set = set(th_ids)
    
    missing_ids = int_id_set - th_id_set
    extra_ids = th_id_set - int_id_set
    
    print(f'Missing IDs: {len(missing_ids)}, Extra IDs: {len(extra_ids)}')
    
    if len(missing_ids) == 0 and len(extra_ids) == 0:
        print('Already matched - skip')
        return 'SKIP'
    
    # Get English text for missing IDs
    missing_lines = []
    for line in int_lines:
        tid = extract_id(line)
        if tid in missing_ids:
            eng = get_value(line)
            missing_lines.append((tid, eng))
    
    # Translate missing
    translations = {}
    if missing_lines:
        print(f'Translating {len(missing_lines)} missing lines...')
        translations = translate_missing(missing_lines, API_KEY)
        print(f'Got {len(translations)} translations')
    
    # Build new TH content
    new_lines = []
    for line in int_lines:
        tid = extract_id(line)
        if not tid:
            continue
        
        if tid in th_content:
            # Keep existing Thai
            new_lines.append(th_content[tid])
        elif tid in translations:
            # Use new translation
            new_lines.append(f'{tid}: {translations[tid]}')
        else:
            # Use original English as fallback
            eng_val = get_value(line)
            new_lines.append(f'{tid}: {eng_val}')
    
    print(f'New TH lines: {len(new_lines)}')
    
    # Write back
    new_text = '\n'.join(new_lines)
    with open(th_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    
    return 'OK'

def main():
    print('Merging 10 PARTIAL files...')
    print(f'TH dir: {TH_DIR}')
    print(f'INT dir: {INT_DIR}')
    
    results = []
    for filename in PARTIAL_FILES:
        result = process_file(filename)
        results.append((filename, result))
    
    print('\n=== RESULTS ===')
    for fname, result in results:
        print(f'{result}: {fname}')
    
    # Save report
    with open(r'E:\Mod_Workspace\Dishonored_Mod_Workspace\merge_report.txt', 'w', encoding='utf-8') as f:
        f.write('MERGE RESULTS\n')
        for fname, result in results:
            f.write(f'{result}: {fname}\n')
    
    print('\nDone! Report saved to merge_report.txt')

if __name__ == '__main__':
    main()