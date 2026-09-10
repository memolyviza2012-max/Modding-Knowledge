import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os, re
from openai import OpenAI

LM_STUDIO_URL = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen3-14b"
client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio", timeout=30)

def has_thai(t): return bool(re.search(r'[\u0e00-\u0e7f]', t))
def has_english(t): return bool(re.search(r'[a-zA-Z]', t))

def read_yaml(path):
    for enc in ('utf-8-sig', 'utf-8'):
        try:
            data = {}
            with open(path, 'r', encoding=enc) as f:
                for line in f:
                    if ': ' in line:
                        k, v = line.split(': ', 1)
                        data[k.strip()] = v.strip()
            return data
        except: continue
    return {}

folder = 'L_Bridge_Part1c_Script'
base = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole'
int_path = os.path.join(base, folder, folder + '_INT.yaml')
th_path = int_path.replace('_INT', '_TH')

int_data = read_yaml(int_path)
th_data = read_yaml(th_path)

targets = [k for k,v_int in int_data.items()
           if has_english(v_int)
           and (not th_data.get(k) or th_data[k] == v_int or not has_thai(th_data.get(k,'')))]

print('Targets found:', len(targets))
for k in targets:
    lines = [f"{k}: {int_data[k]}\n"]
    resp = client.chat.completions.create(
        model=LM_STUDIO_MODEL,
        messages=[
            {"role": "system", "content": "Translate to Thai. Output only ID: Thai. No markdown."},
            {"role": "user", "content": "".join(lines) + "\n\n[CRITICAL: OUTPUT ONLY THE TRANSLATED LINES.]"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    print(f'  ID: {k}')
    print(f'  INT: {int_data[k]}')
    print(f'  TH:  {resp.choices[0].message.content.strip()}')
    print()
