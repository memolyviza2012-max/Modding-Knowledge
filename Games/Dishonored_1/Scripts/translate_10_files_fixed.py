# translate_10_files_fixed.py
import os, urllib.request, json, time

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = __import__("os").environ.get("GEMINI_API_KEY", "")

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
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
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
    print(f'Processing {fname}...')
    
    int_path = os.path.join(INT_DIR, fname)
    th_path = os.path.join(TH_DIR, fname)
    
    # Read INT as UTF-16-LE
    with open(int_path, 'rb') as f:
        raw = f.read()
    int_text = raw.decode('utf-16-le', errors='replace')
    int_text = int_text.replace('\r\n', '\n').replace('\r', '\n').replace('\x00', '')
    int_lines = int_text.split('\n')
    
    # Extract clean entries
    entries = []
    for line in int_lines:
        stripped = line.strip()
        if stripped and ':' in stripped:
            tid = get_id(line)
            eng = get_val(line)
            if tid and eng and len(tid) > 1 and len(eng) > 1:
                entries.append((tid, eng))
    
    print(f'  Found {len(entries)} entries')
    
    if not entries:
        print(f'  No entries - skipped')
        continue
    
    try:
        # Build prompt
        prompt = "Translate to Thai. Format: ID: Thai\nTHAI SPACING (space between words). Dark gritty tone.\n\n"
        for tid, eng in entries:
            prompt += f"{tid}: {eng}\n"
        
        result = translate(prompt, API_KEY)
        
        trans = {}
        for line in result.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                trans[parts[0].strip()] = parts[1].strip()
        
        print(f'  Got {len(trans)} translations')
        
        # Build new TH file
        new_lines = []
        for tid, eng in entries:
            th_val = trans.get(tid, eng)
            new_lines.append(f'{tid}: {th_val}')
        
        with open(th_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f'  Written {len(new_lines)} lines')
        
    except Exception as e:
        print(f'  Error: {str(e)[:80]}')
    
    time.sleep(3)

print('Done!')