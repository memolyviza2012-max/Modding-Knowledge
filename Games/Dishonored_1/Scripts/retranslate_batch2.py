# retranslate_batch2.py
import os, urllib.request, json, time

TH_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\TH'
INT_DIR = r'E:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\Localization\INT'
API_KEY = 'AIzaSyDR_4LQTf__v1-8WKLbs42fYQjcT6Ibx7o'

FILES = {
    'AudioGraph_Twk.int': 9,
    'Boyle_Objectives.int': 41,
    'Bridge_Objectives.int': 16,
    'Brothel_Objectives.int': 23,
}

BATCH_SIZE = 2

def translate(text, api_key):
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    data = {
        "contents": [{"parts": [{"text": text}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 2000},
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

for fname, total in FILES.items():
    print(f'\n=== {fname} ({total} entries) ===')
    
    int_path = os.path.join(INT_DIR, fname)
    th_path = os.path.join(TH_DIR, fname)
    
    with open(int_path, 'rb') as f:
        raw = f.read()
    int_text = raw.decode('utf-16-le', errors='replace')
    int_text = int_text.replace('\r\n', '\n').replace('\r', '\n').replace('\x00', '')
    int_lines = int_text.split('\n')
    
    entries = []
    for line in int_lines:
        stripped = line.strip()
        if stripped and ':' in stripped:
            tid = get_id(line)
            eng = get_val(line)
            if tid and eng and len(tid) > 1 and len(eng) > 1:
                entries.append((tid, eng))
    
    print(f'Entries: {len(entries)}')
    
    if not entries:
        continue
    
    existing = {}
    if os.path.exists(th_path):
        with open(th_path, 'rb') as f:
            th_text = f.read().decode('utf-8', errors='replace').replace('\r\n', '\n').replace('\r', '\n')
        for line in th_text.split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                existing[parts[0].strip()] = parts[1].strip()
    
    print(f'Existing: {len(existing)}')
    
    all_trans = dict(existing)
    batches = [entries[i:i+BATCH_SIZE] for i in range(0, len(entries), BATCH_SIZE)]
    
    for batch_num, batch in enumerate(batches, 1):
        print(f'  Batch {batch_num}/{len(batches)} ({len(batch)} entries)...')
        
        prompt = "Translate to Thai. Output: ID: Thai\nTHAI SPACING. Dark tone.\n\n"
        for tid, eng in batch:
            prompt += f"{tid}: {eng}\n"
        
        try:
            result = translate(prompt, API_KEY)
            result_lines = result.split('\n')
            
            for line in result_lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    tid_key = parts[0].strip()
                    val = parts[1].strip()
                    if tid_key:
                        all_trans[tid_key] = val
            
            print(f'    Got {len(result_lines)} lines, total: {len(all_trans)}')
        except Exception as e:
            print(f'    Error: {str(e)[:50]}')
        
        time.sleep(1)
    
    new_lines = [f"{tid}: {all_trans.get(tid, eng)}" for tid, eng in entries]
    with open(th_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f'Written {len(new_lines)} lines, {len(all_trans)} translations')

print('\nDone!')