# merge_partial_v2.py
import os, urllib.request, json

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = 'AIzaSyDR_4LQTf__v1-8WKLbs42fYQjcT6Ibx7o'

FILES = ['AudioGraph_Twk.int', 'Boyle_Objectives.int']

def get_id(line):
    if ':' not in line: return None
    return line.split(':')[0].strip()

def get_val(line):
    if ':' not in line: return ''
    return line.split(':', 1)[1].strip()

def translate(missing_list):
    if not missing_list: return {}
    
    prompt = "Translate to Thai. Format: ID: Thai\nTHAI SPACING between words.\nDark gritty tone.\n\n"
    for tid, eng in missing_list:
        prompt += f"{tid}: {eng}\n"
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}'
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4000},
        "safetySettings": [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
        ]
    }
    
    try:
        body = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            return {l.split(':')[0].strip(): l.split(':', 1)[1].strip() 
                    for l in text.split('\n') if ':' in l}
    except Exception as e:
        print(f'API error: {e}')
        return {}

for fname in FILES:
    print(f'\n=== {fname} ===')
    th_path = os.path.join(TH_DIR, fname)
    int_path = os.path.join(INT_DIR, fname)
    
    with open(int_path, 'rb') as f:
        int_lines = f.read().decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n').split('\n')
    with open(th_path, 'rb') as f:
        th_text = f.read().decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')
    
    int_ids = [get_id(l) for l in int_lines]
    th_lines = th_text.split('\n')
    th_content = {get_id(l): get_val(l) for l in th_lines if get_id(l)}
    th_ids = set(th_content.keys())
    int_ids_set = set(int_ids)
    
    missing = int_ids_set - th_ids
    extra = th_ids - int_ids_set
    
    print(f'Missing: {len(missing)}, Extra: {len(extra)}')
    
    if not missing:
        print('No missing - skip')
        continue
    
    # Get missing translations
    missing_list = []
    for line in int_lines:
        tid = get_id(line)
        if not tid:
            continue
        if tid in missing:
            missing_list.append((tid, get_val(line)))
    
    print(f'Translating {len(missing_list)} lines...')
    translations = translate(missing_list)
    print(f'Got {len(translations)} translations')
    
    # Build new content using INT as template
    new_lines = []
    for line in int_lines:
        tid = get_id(line)
        if not tid:
            new_lines.append('')
            continue
        th_val = th_content.get(tid, '') or translations.get(tid, '') or get_val(line)
        new_lines.append(f'{tid}: {th_val}')
    
    with open(th_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    print(f'Written {len(new_lines)} lines')

print('\nDone!')