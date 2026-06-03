# merge_partial_fixed.py
# Merge TH files - keep existing Thai, add missing lines, remove extra lines
import os
import urllib.request
import json

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")

PARTIAL_FILES = [
    'AudioGraph_Twk.int',
    'Boyle_Objectives.int',
]

def get_id(line):
    if ':' not in line:
        return None
    return line.split(':')[0].strip()

def get_value(line):
    if ':' not in line:
        return ''
    parts = line.split(':', 1)
    return parts[1].strip() if len(parts) > 1 else ''

def translate_batch(missing_list, api_key):
    """Translate missing lines via Gemini API"""
    if not missing_list:
        return {}
    
    prompt = "Translate to Thai. Output format: ID: Thai\nUse THAI SPACING (space between words). Dark gritty tone.\n\n"
    for tid, eng in missing_list:
        prompt += f"{tid}: {eng}\n"
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2000},
        "safetySettings": [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
        ]
    }
    
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            translations = {}
            for line in text.split('\n'):
                if ':' in line:
                    parts = line.split(':', 1)
                    tid = parts[0].strip()
                    val = parts[1].strip()
                    translations[tid] = val
            return translations
    except Exception as e:
        print(f'API Error: {e}')
        return {}

def process_file(filename):
    print(f'\n=== {filename} ===')
    
    th_path = os.path.join(TH_DIR, filename)
    int_path = os.path.join(INT_DIR, filename)
    
    # Read INT
    with open(int_path, 'rb') as f:
        int_raw = f.read()
    int_text = int_raw.decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')
    int_lines = int_text.split('\n')
    int_ids = [get_id(l) for l in int_lines]
    int_content = {get_id(l): get_value(l) for l in int_lines if get_id(l)}
    
    # Read TH
    with open(th_path, 'rb') as f:
        th_raw = f.read()
    th_text = th_raw.decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')
    th_lines = th_text.split('\n')
    th_content = {get_id(l): get_value(l) for l in th_lines if get_id(l)}
    
    # Find missing and extra
    int_id_set = set(int_ids)
    th_id_set = set(th_content.keys())
    
    missing_ids = int_id_set - th_id_set
    extra_ids = th_id_set - int_id_set
    
    print(f'INT: {len(int_ids)} lines, {len(int_content)} IDs')
    print(f'TH: {len(th_lines)} lines, {len(th_content)} IDs')
    print(f'Missing: {len(missing_ids)}, Extra: {len(extra_ids)}')
    
    if len(missing_ids) == 0 and len(extra_ids) == 0:
        print('Already matched - skip')
        return 'SKIP'
    
    # Build missing list for API
    missing_list = []
    for i, line in enumerate(int_lines):
        tid = get_id(line)
        if tid in missing_ids:
            eng = get_value(line)
            missing_list.append((tid, eng))
    
    # Translate missing
    translations = {}
    if missing_list:
        print(f'Translating {len(missing_list)} missing lines...')
        translations = translate_batch(missing_list, API_KEY)
        print(f'Got {len(translations)} translations')
    
    # Build new TH - use INT as template, fill with TH Thai or translations
    new_lines = []
    for line in int_lines:
        tid = get_id(line)
        if not tid:
            new_lines.append('')
            continue
        
        # Get English from INT
        eng_val = get_value(line)
        
        # Try to get Thai from TH
        th_val = th_content.get(tid, '')
        
        # If no Thai in TH, use translation
        if not th_val and tid in translations:
            th_val = translations[tid]
        
        # If still no Thai, use English as fallback
        if not th_val:
            th_val = eng_val
        
        new_lines.append(f'{tid}: {th_val}')
    
    # Verify line count
    if len(new_lines) != len(int_lines):
        print(f'WARNING: Line count mismatch! {len(new_lines)} vs {len(int_lines)}')
    
    # Write back
    new_text = '\n'.join(new_lines)
    with open(th_path, 'w', encoding='utf-8') as f:
        f.write(new_text)
    
    print(f'Written: {len(new_lines)} lines')
    return 'OK'

def main():
    for filename in PARTIAL_FILES:
        result = process_file(filename)
        print(f'Result: {result}')

if __name__ == '__main__':
    main()