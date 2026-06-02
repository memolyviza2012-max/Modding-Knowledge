import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, re
from openai import OpenAI

client = OpenAI(base_url='http://localhost:1234/v1', api_key='lm-studio', timeout=30)

SYSTEM = """/no_think
Dishonored Translator (EN->TH). Dark Victorian game, Mature-rated.
RULES: "ID: English" → "ID: Thai" | exact line count | no commentary | preserve %s %d {0} \\n <font...> | space between Thai phrases
TONE: street Thai for thugs | formal Thai for nobility | archaic Thai for The Outsider
GLOSSARY: Corvo Attano=คอร์โว อัตตาโน|Emily Kaldwin=เอมิลี่ คาลด์วิน|The Outsider=ดิ เอาท์ไซเดอร์|Lord Regent=อัครมหาเสนาบดี|High Overseer=ไฮโอเวอร์เซียร์|Overseer=โอเวอร์เซียร์|Weepers=วีปเปอร์|Dunwall=ดันวอลล์|Daud=ดาวด์|Blink=บลิงก์|Bonecharm=เครื่องราง|Rat Plague=กาฬโรคหนู|Granny Rags=แกรนนี่แร็กส์"""

path = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole\L_Pub_FromPrison_Script\L_Pub_FromPrison_Script_INT.yaml'

def read_yaml(p):
    for enc in ('utf-8-sig', 'utf-8'):
        try:
            d = {}
            with open(p, 'r', encoding=enc) as f:
                for line in f:
                    if ': ' in line:
                        k, v = line.split(': ', 1)
                        d[k.strip()] = v.strip()
            return d
        except:
            continue
    return {}

int_data = read_yaml(path)
th_path = path.replace('_INT', '_TH')
th_data = read_yaml(th_path) if os.path.exists(th_path) else {}

RE_THAI = re.compile(r'[\u0e00-\u0e7f]')
RE_ENG = re.compile(r'[a-zA-Z]')

keys = [k for k, v_int in int_data.items()
        if RE_ENG.search(v_int)
        and (k not in th_data or th_data[k] == v_int or not RE_THAI.search(th_data.get(k, '')))]

print(f'Keys to fix: {len(keys)}')

# Prompt exactly like sniper_translate.py
lines = [f"{k}: {int_data[k]}\n" for k in keys]
prompt = ''.join(lines) + "\n[OUTPUT TRANSLATED LINES ONLY]"

print(f'Prompt preview:')
print(repr(prompt[:200]))
print()

print('Calling LM Studio...')
try:
    res = client.chat.completions.create(
        model='qwen/qwen3-14b',
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=1024,
    )
    raw = res.choices[0].message.content
    print(f'Raw response ({len(raw)} chars):')
    print(raw[:300])
    print()
    # Parse like sniper
    valid = set(keys)
    parsed = {}
    for line in raw.split('\n'):
        line = line.strip()
        if ': ' not in line:
            continue
        k, v = line.split(': ', 1)
        v = v.strip()
        if k.strip() in valid and v and len(v) > 0:
            parsed[k.strip()] = v
    print(f'Parsed: {len(parsed)}/{len(keys)}')
    for k, v in parsed.items():
        print(f'  {k[:50]}: {v[:50]}')
except Exception as e:
    print(f'Error: {e}')
