import requests

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "google/gemma-4-e4b"

lines = ["DisConv_Blurb.4009.DisConv_Blurb: Trespass and we will feed your guts to the hagfish.",
"DisConv_Blurb.4010.DisConv_Blurb: Ring the alarm!"]

text = "\n".join(lines)
prompt = f"""You are a Thai translator for the game Dishonored.
Keep format: ID: Thai translation
Translate to Thai:

{text}

THAI:"""

payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3, "max_tokens": 500}

print("Sending...")
r = requests.post(LM_URL, json=payload, timeout=60)
print("Status:", r.status_code)
result = r.json()["choices"][0]["message"]["content"]
print("Result:")
print(result)