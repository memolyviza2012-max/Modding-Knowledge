import sys; sys.stdout.reconfigure(encoding='utf-8')
import os, re
from openai import OpenAI

client = OpenAI(base_url='http://localhost:1234/v1', api_key='lm-studio', timeout=30)

SYSTEM = """/no_think
Dishonored Translator (EN->TH).
RULES: ID: English -> ID: Thai | no commentary | preserve variables
GLOSSARY: Corvo Attano=คอร์โว อัตตาโน|The Outsider=ดิ เอาท์ไซเดอร์|Blink=บลิงก์"""

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

print('Keys to fix:', len(keys))
for k in keys[:5]:
    print(' ', k[:60])
    print('  INT:', int_data[k][:40])
    print('  TH:', th_data.get(k, '')[:40])

# Test translate
lines = [f"{k}: {int_data[k]}\n" for k in keys]
prompt = ''.join(lines) + '\n[OUTPUT TRANSLATED LINES ONLY]'

print('\nCalling LM Studio...')
res = client.chat.completions.create(
    model='qwen/qwen3-14b',
    messages=[{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': prompt}],
    temperature=0.1, max_tokens=512,
)
raw = res.choices[0].message.content
print('\nRaw response:')
print(raw[:500])
print()

valid = set(keys)
parsed = {}
for line in raw.split('\n'):
    line = line.strip()
    if ': ' not in line:
        continue
    k, v = line.split(': ', 1)
    if k.strip() in valid and v.strip():
        parsed[k.strip()] = v.strip()

print('Parsed:', parsed)
