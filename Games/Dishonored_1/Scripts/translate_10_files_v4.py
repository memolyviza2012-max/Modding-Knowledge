# translate_10_files_v4.py
import os, urllib.request, json, time

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")
OUT_LOG = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\translate_log.txt'

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

def read_file_clean(path):
    """Read file and remove null bytes"""
    enc = detect_enc(path)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode(enc, errors='replace')
    # Remove null bytes (from UTF-16)
    text = text.replace('\x00', '')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    return text

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

log = []

for fname in FILES:
    log.append(f'=== {fname} ===')
    print(f'Processing {fname}...')
    
    int_path = os.path.join(INT_DIR, fname)
    th_path = os.path.join(TH_DIR, fname)
    
    int_text = read_file_clean(int_path)
    int_lines = int_text.split('\n')
    
    entries = []
    for i, line in enumerate(int_lines):
        stripped = line.strip()
        if stripped and ':' in stripped:
            tid = get_id(line)
            eng = get_val(line)
            if tid and eng and len(tid) > 1:
                entries.append((i, tid, eng))
    
    log.append(f'INT entries: {len(entries)}')
    print(f'  Entries: {len(entries)}')
    
    if not entries:
        log.append('No entries - skipped')
        print(f'  No entries - skipped')
        continue
    
    prompt = "Translate to Thai. Output: 'ID: Thai'\nTHAI SPACING. Dark tone.\n\n"
    for i, tid, eng in entries[:50]:  # Limit to 50 for safety
        prompt += f"{tid}: {eng}\n"
    
    try:
        result = translate(prompt, API_KEY)
        
        trans = {}
        for line in result.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                trans[parts[0].strip()] = parts[1].strip()
        
        log.append(f'Translations: {len(trans)}')
        print(f'  Translations: {len(trans)}')
        
        new_lines = []
        for line in int_lines:
            if not line.strip():
                new_lines.append('')
                continue
            tid = get_id(line)
            if tid and len(tid) > 1:
                th_val = trans.get(tid, get_val(line))
                new_lines.append(f'{tid}: {th_val}')
            else:
                new_lines.append('')
        
        with open(th_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        log.append(f'Written: {len(new_lines)} lines')
        print(f'  Written: {len(new_lines)} lines')
        
    except Exception as e:
        log.append(f'Error: {str(e)}')
        print(f'  Error: {str(e)[:50]}')
    
    time.sleep(3)

with open(OUT_LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))

print('Done! Check translate_log.txt')