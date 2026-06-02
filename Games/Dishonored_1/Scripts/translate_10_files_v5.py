# translate_10_files_v5.py
import os, urllib.request, json, time

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = 'AIzaSyDR_4LQTf__v1-8WKLbs42fYQjcT6Ibx7o'
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
        raw = f.read(8)
    # Check for BOMs
    if raw[:2] == b'\xff\xfe': return 'utf-16-le'
    if raw[:2] == b'\xfe\xff': return 'utf-16-be'
    if raw[:3] == b'\xef\xbb\xbf': return 'utf-8-sig'
    # Check for null bytes pattern (UTF-16 without BOM)
    if len(raw) >= 4:
        # UTF-16-LE typically has null bytes at odd positions for ASCII content
        null_count = sum(1 for i in range(1, len(raw), 2) if raw[i:i+1] == b'\x00')
        if null_count >= 2:
            return 'utf-16-le'
    return 'utf-8'

def read_file_clean(path):
    enc = detect_enc(path)
    with open(path, 'rb') as f:
        raw = f.read()
    text = raw.decode(enc, errors='replace')
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
    print(f'Processing {fname}...')
    log.append(f'=== {fname} ===')
    
    int_path = os.path.join(INT_DIR, fname)
    th_path = os.path.join(TH_DIR, fname)
    
    enc = detect_enc(int_path)
    print(f'  Encoding: {enc}')
    log.append(f'Encoding: {enc}')
    
    int_text = read_file_clean(int_path)
    int_lines = int_text.split('\n')
    
    entries = []
    for i, line in enumerate(int_lines):
        stripped = line.strip()
        if stripped and ':' in stripped:
            tid = get_id(line)
            eng = get_val(line)
            if tid and eng and len(tid) > 1 and len(eng) > 1:
                entries.append((i, tid, eng))
    
    print(f'  Entries: {len(entries)}')
    log.append(f'Entries: {len(entries)}')
    
    if not entries:
        print(f'  No entries - skipped')
        log.append('No entries - skipped')
        continue
    
    # Build prompt
    prompt = "Translate to Thai. Output: 'ID: Thai'\nTHAI SPACING between words. Dark tone.\n\n"
    for i, tid, eng in entries:
        prompt += f"{tid}: {eng}\n"
    
    try:
        result = translate(prompt, API_KEY)
        
        trans = {}
        for line in result.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                trans[parts[0].strip()] = parts[1].strip()
        
        print(f'  Translations: {len(trans)}')
        log.append(f'Translations: {len(trans)}')
        
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
        
        print(f'  Written: {len(new_lines)} lines')
        log.append(f'Written: {len(new_lines)} lines')
        
    except Exception as e:
        err_str = str(e)
        print(f'  Error: {err_str[:80]}')
        log.append(f'Error: {err_str[:100]}')
    
    time.sleep(3)

with open(OUT_LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))

print('Done!')