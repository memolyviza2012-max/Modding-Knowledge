import requests, time

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"

TEST_LINES = [
    "DisConv_Blurb.4009.DisConv_Blurb: Trespass and we'll feed your guts to the hagfish.",
    "DisConv_Blurb.4010.DisConv_Blurb: Ring the alarm!",
    "DisConv_Blurb.4011.DisConv_Blurb: Cut that shit out.",
]

for MODEL in ["qwen/qwen3.6-35b-a3b", "qwen/qwen3-14b"]:
    print(f"\n=== Testing {MODEL} ===")
    text = "\n".join(TEST_LINES)
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": f"Translate to Thai. Keep format:\n{text}\n\nTHAI:"}],
        "temperature": 0.3,
        "max_tokens": 300
    }
    try:
        r = requests.post(LM_URL, json=payload, timeout=120)
        result = r.json()["choices"][0]["message"]["content"]
        lines = [l.strip() for l in result.split("\n") if ":" in l and l.strip()]
        print(f"Lines returned: {len(lines)}")
        for l in lines[:5]:
            print(f"  {l[:80]}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(2)