# translate_10_files_v2.py
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

def detect_enc(path):
    with open(path, 'rb') as f:
        raw = f.read(4)
    if raw[:2] == b'\xff\xfe': return 'utf-16-le'
    if raw[:2] == b'\xfe\xff': return 'utf-16-be'
    return 'utf-8'

def read_file(path):
    enc = detect_enc(path)
    with open(path, 'rb') as f:
        return f.read().decode(enc, errors='replace').replace('\r\n', '\n').replace('\r', '\n')

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
    
    int_text = read_file(int_path)
    int_lines = int_text.split('\n')
    
    entries = []
    for i, line in enumerate(int_lines):
        stripped = line.strip()
        if stripped and ':' in stripped:
            tid = get_id(line)
            eng = get_val(line)
            if tid and eng:
                entries.append((i, tid, eng))
    
    print(f'INT entries: {len(entries)}')
    if not entries:
        print('No entries found - skipping')
        continue
    
    prompt = "Translate to Thai. Output: 'ID: Thai'\nTHAI SPACING. Dark tone.\n\n"
    for i, tid, eng in entries:
        prompt += f"{tid}: {eng}\n"
    
    try:
        result = translate(prompt, API_KEY)
        trans = {}
        for line in result.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                trans[parts[0].strip()] = parts[1].strip()
        
        print(f'Translations: {len(trans)}')
        
        new_lines = []
        for line in int_lines:
            if not line.strip():
                new_lines.append('')
                continue
            tid = get_id(line)
            if tid:
                th_val = trans.get(tid, get_val(line))
                new_lines.append(f'{tid}: {th_val}')
            else:
                new_lines.append(line)
        
        with open(th_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f'Written: {len(new_lines)} lines')
        
    except Exception as e:
        print(f'Error: {e}')
        time.sleep(5)

print('\nDone!')