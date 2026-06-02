import requests
import time

LM_URL = 'http://127.0.0.1:1234/v1/chat/completions'

TEST_LINES = """DisConv_Blurb.4009.DisConv_Blurb: Trespass and we'll feed your guts to the hagfish.
DisConv_Blurb.4010.DisConv_Blurb: Ring the alarm!
DisConv_Blurb.4011.DisConv_Blurb: Cut that shit out."""

models = ['qwen/qwen3.6-35b-a3b', 'qwen/qwen3-14b']

for MODEL in models:
    print(f"=== {MODEL} ===")
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": f"Translate to Thai:\n{TEST_LINES}"}],
        "temperature": 0.3,
        "max_tokens": 500
    }
    try:
        r = requests.post(LM_URL, json=payload, timeout=180)
        data = r.json()
        if 'choices' in data:
            result = data['choices'][0]['message']['content']
            print("OK:", result[:200])
        else:
            print("No choices:", str(data)[:200])
    except Exception as e:
        print(f"Error: {e}")
    print()
    time.sleep(2)