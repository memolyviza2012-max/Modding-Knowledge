# translate_10_files.py
# Translate 10 PARTIAL files from INT using API
import os, urllib.request, json, time

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = 'AIzaSyDR_4LQTf__v1-8WKLbs42fYQjcT6Ibx7o'

FILES = [
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

def translate(text, api_key):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    data = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 8000},
        "safetySettings": [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
        ]
    }
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        return result['candidates'][0]['content']['parts'][0]['text']

def get_id(line):
    if ':' not in line: return None
    return line.split(':')[0].strip()

def get_val(line):
    if ':' not in line: return ''
    return line.split(':', 1)[1].strip()

for fname in FILES:
    print(f'\n=== {fname} ===')
    int_path = os.path.join(INT_DIR, fname)
    th_path = os.path.join(TH_DIR, fname)
    
    # Read INT
    with open(int_path, 'rb') as f:
        int_raw = f.read().decode('utf-8', errors='replace')
    int_lines = int_raw.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    
    # Build entries
    entries = []
    for i, line in enumerate(int_lines):
        if line.strip():
            tid = get_id(line)
            eng = get_val(line)
            if tid:
                entries.append((i, tid, eng))
    
    print(f'INT entries: {len(entries)}')
    
    # Build translation prompt
    prompt = "Translate to Thai. Output ONE line per entry: 'ID: Thai'\nSpacing between Thai words. Dark gritty tone.\n\n"
    for i, tid, eng in entries:
        prompt += f"{tid}: {eng}\n"
    
    # Translate via API
    try:
        result = translate(prompt, API_KEY)
        print(f'Result length: {len(result)} chars')
        
        # Parse translations
        trans = {}
        for line in result.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                tid = parts[0].strip()
                val = parts[1].strip()
                trans[tid] = val
        
        print(f'Translations: {len(trans)}')
        
        # Build new TH file
        new_lines = []
        for i, line in enumerate(int_lines):
            if not line.strip():
                new_lines.append('')
                continue
            tid = get_id(line)
            if tid:
                th_val = trans.get(tid, get_val(line))
                new_lines.append(f'{tid}: {th_val}')
            else:
                new_lines.append(line)
        
        # Write TH
        with open(th_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f'Written: {len(new_lines)} lines')
        
    except Exception as e:
        print(f'Error: {e}')
        time.sleep(5)

print('\nDone!')